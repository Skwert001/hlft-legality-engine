#!/usr/bin/env python3
# HLFT Legality Dispatcher — Minimal Aer-only Demo
# Requires: Python 3.10+, qiskit==0.46.0, qiskit-aer==0.13.3

from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse, json, traceback

HBAR_PHYS = 6.582e-16  # eV·s
SR_THRESHOLD = 15000.0
PRSI_MIN = 1.5

@dataclass
class Biomarkers:
    pulse_E: float = 1.0
    TPS: float = 1.0
    slope: float = 0.8
    DZII: float = 100.0
    PRSI: float = 1.6
    overlays_on: int = 0
    T2: float = 40e-6
    TL_star: float = 40e-6
    alpha: float = 1.0e4

def compute_sr(bm: Biomarkers) -> float:
    denom = max(bm.pulse_E * bm.TPS * max(bm.slope, 1e-12), 1e-12)
    return bm.DZII / denom

def compute_arc_potential(bm: Biomarkers) -> float:
    return bm.pulse_E * bm.TPS * bm.slope - bm.DZII

def delta_Es_gate(bm: Biomarkers) -> dict:
    hbar_s = bm.alpha * HBAR_PHYS * (bm.TL_star / bm.T2)
    delta_Es_proxy = 1.0  # proxy until full <psi_next|H_s|psi_now> is wired in
    return {"pass": (delta_Es_proxy >= hbar_s),
            "delta_Es_proxy": delta_Es_proxy,
            "hbar_s": hbar_s}

def legality_verdict(bm: Biomarkers) -> dict:
    sr = compute_sr(bm)
    A  = compute_arc_potential(bm)
    dgate = delta_Es_gate(bm)

    # exact minimums to flip A>0
    req_pulseE_for_A = bm.DZII / max(bm.TPS * max(bm.slope, 1e-12), 1e-12)
    req_TPS_for_A    = bm.DZII / max(bm.pulse_E * max(bm.slope, 1e-12), 1e-12)
    req_slope_for_A  = bm.DZII / max(bm.pulse_E * max(bm.TPS,   1e-12), 1e-12)

    reasons, ok = [], True
    if bm.slope <= 0:       ok=False; reasons.append("slope<=0 (LQ-ARC-08)")
    if bm.PRSI  < PRSI_MIN: ok=False; reasons.append("PRSI<1.5 (LQ-ARC-08)")
    if sr >= SR_THRESHOLD:  ok=False; reasons.append(f"SR≥{int(SR_THRESHOLD)} (LQ-SUP-11)")
    if A <= 0:              ok=False; reasons.append("A<=0 (LQ-UNI-01)")
    if not dgate["pass"]:   ok=False; reasons.append("ΔE_s<h̄_s")

    verdict = "PERMITTED" if ok else "DENIED"
    return {
        "verdict": verdict,
        "biomarkers": asdict(bm),
        "SR": sr,
        "A": A,
        "DeltaEs_gate": dgate,
        "A_thresholds": {
            "min_pulse_E_for_A>0": req_pulseE_for_A,
            "min_TPS_for_A>0": req_TPS_for_A,
            "min_slope_for_A>0": req_slope_for_A
        },
        "reasons": reasons,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def run_aer_bell() -> dict:
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit_aer import Aer
        qc = QuantumCircuit(2, 2)
        qc.h(0); qc.cx(0,1); qc.measure([0,1],[0,1])
        backend = Aer.get_backend("aer_simulator")
        tqc = transpile(qc, backend)
        res = backend.run(tqc, shots=512).result().get_counts()
        return {"origin": "AER", "backend": "aer_simulator", "counts": dict(res)}
    except Exception as e:
        return {"origin": "AER", "error": repr(e), "traceback": traceback.format_exc()}

def parse_args():
    ap = argparse.ArgumentParser(description="HLFT Legality Dispatcher (Aer-only)")
    ap.add_argument("--pulse_E", type=float, default=None)
    ap.add_argument("--TPS",     type=float, default=None)
    ap.add_argument("--slope",   type=float, default=None)
    ap.add_argument("--DZII",    type=float, default=None)
    ap.add_argument("--PRSI",    type=float, default=None)
    ap.add_argument("--overlays_on", type=int, default=None)
    ap.add_argument("--T2",      type=float, default=None)
    ap.add_argument("--TL_star", type=float, default=None)
    ap.add_argument("--alpha",   type=float, default=None)
    ap.add_argument("--run-aer", action="store_true", help="Run Aer Bell circuit after a PERMITTED verdict")
    return ap.parse_args()

def main():
    args = parse_args()
    # seed with defaults, override with CLI if provided
    base = Biomarkers()
    for k in ("pulse_E","TPS","slope","DZII","PRSI","overlays_on","T2","TL_star","alpha"):
        v = getattr(args, k)
        if v is not None:
            setattr(base, k, v)

    result = legality_verdict(base)
    if args.run_aer and result["verdict"] == "PERMITTED":
        result["quantum_job"] = run_aer_bell()

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == "PERMITTED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
