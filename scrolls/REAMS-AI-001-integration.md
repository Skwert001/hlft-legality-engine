# REAMS-AI-001 Integration Guide (Legality-Gated Evaluation)

**Date:** September 15, 2025  
**Author:** Matthew William Reams (REAMS-CORE-001)

This guide shows how to add a **legality-gated evaluation layer** to an LLM pipeline to suppress hallucinations by **penalizing confident errors more than abstentions**.
> **Note on scale:** The integration guide uses normalized proxies (S̃R) with default τ≈1.0.  
> The doctrine (REAMS-AI-001) defines the physical SR law with deny threshold 15,000.  
> These scales are distinct and should not be conflated.

---

## 1) Overview

- **What:** A post-decode (or decode-time) gate that emits an answer only when evidence clears explicit thresholds.
- **Why:** Scoreboards that reward accuracy over abstention incentivize guessing. The gate flips this incentive so **abstention > confident wrong**.
- **How:** Compute four signals per answer, derive a **Suppression Ratio (SR)**, and gate on a single threshold **τ**.

**Suppression Ratio**  
`SR = DZII ÷ (pulse_E × TPS × slope)`

- **DZII**: residual disorder/contradiction signal (higher = worse)
- **pulse_E**: evidence strength (retrieval/citations + calibrated log-prob)
- **TPS**: temporal phase stability across light perturbations (0..1)
- **slope**: monotonic support trend during generation (0..1)

**Decision:** if `SR ≥ τ` → abstain (or respond with scoped uncertainty); else emit answer.

---

## 2) Drop‑in Reference (Python)

See `sr_gate_reference.py` for a reference gate you can adapt. It expects pluggable callables for retrieval support and contradiction checks.

```python
from sr_gate_reference import LegalityGate, GateInput, GateSignals

gate = LegalityGate(tau=1.0)

def retrieve_support(prompt, answer): ...
def contradiction_score(prompt, answer): ...

result = gate.evaluate(
    GateInput(
        prompt=prompt,
        answer=answer,
        tok_logprobs=tok_logprobs,   # list[float] (optional)
        variants=variants            # list[str] lightweight re-generations (optional)
    ),
    support_fn=retrieve_support,
    contradiction_fn=contradiction_score
)

if result["verdict"] == "abstain":
    # return uncertainty-aware response to user
else:
    # return answer with optional confidence & telemetry
```

---

## 3) Telemetry JSON (for evals & dashboards)

The gate returns a compact JSON bundle suitable for logging and scoreboards. Schema in `SR_telemetry_schema.json`.

```jsonc
{
  "verdict": "answer | abstain",
  "SR": 0.73,
  "threshold": 1.0,
  "signals": {
    "pulse_E": 0.82,
    "TPS": 0.76,
    "DZII": 0.45,
    "slope": 0.88
  },
  "debug": {
    "support": {"retrieval": 0.77, "logprob": -1.2},
    "stability": {"agreement": 0.76, "n": 3},
    "contradiction": {"nli": 0.18, "entropy": 0.27}
  }
}
```

---

## 4) Metrics to Track

- **Risk–coverage**: selective accuracy vs coverage as τ varies.
- **Confident error rate**: fraction of errors above confidence threshold (target ↓).
- **ECE**: expected calibration error with/without the gate.
- **Hallucination evals**: fact-check correctness vs cited sources; NLI contradiction rate.
- **Abstention quality**: % abstentions that appropriately cite missing info / uncertainty.

---

## 5) Deployment Patterns

- **Post‑decode filter** (simplest): No changes to decoding; cheap extra scoring + light re-sampling (N≈3).
- **Decode‑time early stop**: compute partial SR as tokens stream; stop when `SR ≥ τ`.
- **Scoreboard alignment**: count abstention better than confident wrong; log SR for model/dev dashboards.
- **RLHF/DPO shaping**: reward abstention in cases where the ungated model would be confidently wrong.

---

## 6) Safety & Privacy

- The public interface exposes only **aggregate scores** (pulse_E, TPS, DZII, slope).  
- No proprietary model weights or internal HLFT constants are disclosed.  
- Threshold **τ** is task/domain‑tuned and can remain private.

---

## 7) Quick Start Checklist

- [ ] Add `sr_gate_reference.py` to your eval harness.  
- [ ] Implement two callables: `support_fn`, `contradiction_fn`.  
- [ ] Calibrate features (z‑score or min‑max) + choose τ on a held‑out set.  
- [ ] Log SR telemetry per sample.  
- [ ] Plot risk–coverage to validate improved selective risk.  
- [ ] Flip scoreboard rules: **abstention > confident wrong**.
