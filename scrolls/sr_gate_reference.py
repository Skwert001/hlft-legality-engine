"""
sr_gate_reference.py - Minimal legality-gate reference for REAMS-AI-001
Author: Matthew William Reams (REAMS-CORE-001)
Date: 2025-09-15

This reference is model-agnostic. Plug in your own retrieval and NLI functions.
No proprietary constants are exposed.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, TypedDict
import math
import statistics as stats

# ---- Data structures ----
@dataclass
class GateInput:
    prompt: str
    answer: str
    tok_logprobs: Optional[List[float]] = None   # token-level logprobs (optional)
    variants: Optional[List[str]] = None         # lightweight regenerations for stability (optional)

class GateSignals(TypedDict):
    pulse_E: float
    TPS: float
    DZII: float
    slope: float

SupportFn = Callable[[str, str], float]          # returns [0,1]
ContradictionFn = Callable[[str, str], float]    # returns [0,1], higher = worse

# ---- Helpers ----
def _safe01(x: float) -> float:
    # Clamp to [0,1] for interpretability
    return max(0.0, min(1.0, x))

def _calibrate_logprob_mean(tok_logprobs: Optional[List[float]]) -> float:
    """
    Convert mean token logprob to a [0,1] proxy for evidence.
    This is a simple logistic squashing; real systems should calibrate on held-out data.
    """
    if not tok_logprobs:
        return 0.5
    m = stats.fmean(tok_logprobs)
    return _safe01(1.0 / (1.0 + math.exp(-m)))  # logistic

def _agreement_score(texts: List[str]) -> float:
    """
    Placeholder stability metric: pairwise Jaccard over token sets.
    Replace with embedding-based or judge-model agreement as available.
    """
    if not texts:
        return 0.5
    toks = [set(t.lower().split()) for t in texts]
    pairs = 0
    sim = 0.0
    for i in range(len(toks)):
        for j in range(i+1, len(toks)):
            inter = len(toks[i].intersection(toks[j]))
            union = len(toks[i].union(toks[j])) or 1
            sim += inter / union
            pairs += 1
    return _safe01(sim / pairs) if pairs else 0.5

def _predictive_entropy(tok_logprobs: Optional[List[float]]) -> float:
    """
    Lightweight uncertainty proxy from logprobs; real systems should use calibrated variance.
    """
    if not tok_logprobs:
        return 0.5
    # Convert to probs (clipped), compute entropy of histogram
    ps = [max(1e-6, min(1.0, math.exp(lp))) for lp in tok_logprobs]
    # Bucket into 10 bins for a simple entropy proxy
    bins = [0]*10
    for p in ps:
        idx = min(9, int(p*10))
        bins[idx] += 1
    total = sum(bins) or 1
    ent = 0.0
    for c in bins:
        q = c/total
        if q > 0:
            ent -= q * math.log(q + 1e-12)
    # Normalize by max entropy log(10)
    return _safe01(ent / math.log(10))

def _monotonic_support(tok_logprobs: Optional[List[float]]) -> float:
    """
    Measures whether support increases or stays stable during generation.
    """
    if not tok_logprobs or len(tok_logprobs) < 4:
        return 0.5
    # Moving average trend over 4-token windows
    w = 4
    avgs = [stats.fmean(tok_logprobs[i:i+w]) for i in range(0, len(tok_logprobs)-w+1)]
    ups = sum(1 for i in range(1, len(avgs)) if avgs[i] >= avgs[i-1])
    return _safe01(ups / max(1, len(avgs)-1))

# ---- Gate ----
class LegalityGate:
    def __init__(self, tau: float = 1.0):
        self.tau = tau

    def evaluate(self,
                 x: GateInput,
                 support_fn: SupportFn,
                 contradiction_fn: ContradictionFn) -> Dict:
        # Evidence strength
        retrieval = _safe01(support_fn(x.prompt, x.answer))     # [0,1]
        logp = _calibrate_logprob_mean(x.tok_logprobs)          # [0,1]
        pulse_E = _safe01(0.6*retrieval + 0.4*logp)             # simple combiner

        # Temporal stability
        texts = [x.answer] + (x.variants or [])
        TPS = _agreement_score(texts)                           # [0,1]

        # Contradiction / disorder
        nli = _safe01(contradiction_fn(x.prompt, x.answer))     # higher = worse
        ent = _predictive_entropy(x.tok_logprobs)               # higher = worse
        DZII = _safe01(0.6*nli + 0.4*ent)

        # Evidence slope
        slope = _monotonic_support(x.tok_logprobs)              # [0,1]

        denom = max(1e-6, (pulse_E * TPS * slope))
        SR = DZII / denom

        verdict = "abstain" if SR >= self.tau else "answer"
        out = {
            "verdict": verdict,
            "SR": float(SR),
            "threshold": float(self.tau),
            "signals": {"pulse_E": float(pulse_E),
                        "TPS": float(TPS),
                        "DZII": float(DZII),
                        "slope": float(slope)},
            "debug": {
                "support": {"retrieval": float(retrieval), "logprob": float(logp)},
                "stability": {"agreement": float(TPS), "n": len(texts)},
                "contradiction": {"nli": float(nli), "entropy": float(ent)}
            }
        }
        return out
