# Changelog

## [v0.2.0] - 2025-09-15
### Added
- **REAMS-AI-001 (Hallucinations as Collapse Illegality)**:
  - Technical note (`REAMS-AI-001.scroll.md`, PDF, summary).
  - Defines hallucinations as unlawful outputs under Suppression Ratio law.
  - Gating rule: `SR = DZII ÷ (pulse_E × TPS × slope)` → abstain if SR ≥ τ.
  - Verdict system: 🟢 lawful, ⚠️ partial, 🔴 hallucination.

- **Integration Package**:
  - `REAMS-AI-001-integration.md` – eval harness guide.
  - `sr_gate_reference.py` – drop-in legality gate.
  - `SR_telemetry_schema.json` – schema for logging/dashboards.

### Why It Matters
- Directly addresses OpenAI’s finding: models are incentivized to guess.
- Provides a **structural fix**: abstention > confident-wrong.
- Model-agnostic evaluation layer; no weight changes required.
