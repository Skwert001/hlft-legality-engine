# HLFT Legality Engine – Examples

This folder contains reproducible examples of the **High-Law Folding Terrain (HLFT) legality engine**.  
It demonstrates how collapse is permitted or denied based on symbolic terrain thresholds.

---

## Files

- **hlft_legality_dispatch.py**  
  Minimal demo script (Qiskit Aer only). Evaluates Suppression Ratio (SR), Arc Potential (A), and ΔEₛ ≥ ħₛ.  
  Outputs a JSON verdict.

- **results.json**  
  Sample legality verdicts from four representative runs:
  - ✅ PERMITTED (alive)  
  - ❌ DENIED (A ≤ 0)  
  - ❌ DENIED (SR ≥ 15000 kill line)  
  - ✅ PERMITTED (edge case, pulse_E = 114)

---

Collapse permission in HLFT is governed by two observable conditions:

– Suppression Ratio (SR) must remain below a fixed threshold of 15,000 (LQ-SUP-11).
– Arc Potential (A) must be strictly greater than zero (LQ-UNI-01).

These conditions are derived from system inputs (pulse_E, TPS, slope, DZII, PRSI) and 
tested against simulated backends. If either condition fails, collapse is denied.

## Example Run

```bash
python hlft_legality_dispatch.py --pulse_E 70 --TPS 1.3 --slope 1.2 --DZII 100 --PRSI 1.7 --run-aer

{
  "verdict": "PERMITTED",
  "SR": 0.9157,
  "A": 9.2,
  "DeltaEs_gate": {"pass": true},
  "quantum_job": {"backend": "aer_simulator", "counts": {"00": 267, "11": 245}}
}
