# Changelog

## [v0.2.0] - 2025-09-15
### Added
- **REAMS-AI-001 (Hallucinations as Collapse Illegality)**:
  - Technical note, polished PDF, and one-page summary.
  - Defines hallucinations as unlawful outputs under Suppression Ratio law.
  - Introduces gating rule: `SR = DZII ÷ (pulse_E × TPS × slope)` → abstain if SR ≥ τ.
  - Implements verdict system: 🟢 lawful, ⚠️ partial, 🔴 hallucination.

- **Integration Package**:
  - `REAMS-AI-001-integration.md` – eval harness guide.
  - `sr_gate_reference.py` – reference legality gate.
  - `SR_telemetry_schema.json` – telemetry schema for dashboards.

### Why It Matters
- Directly addresses OpenAI’s recent findings: models are incentivized to guess.  
- Provides a **structural fix**: abstention > confident wrong.  
- Model-agnostic evaluation layer; no weight changes required.
