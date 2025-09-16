System Overview

This project does not contain deployable software, APIs, runtime models, or executable backends.

Instead, it provides a certified framework of symbolic legality scrolls (.rla files) that govern AI behavior externally. These scrolls do not perform operations. They define conditions and constraints under which external systems (such as AI models) may generate or withhold responses.

⸻

No Runtime Logic

The core repository (the /scrolls/ directory) does not include:
	•	Runtime scripts
	•	APIs
	•	Compilers
	•	Machine learning models
	•	Deployable services
	•	Environment-dependent artifacts

All enforcement occurs through structured interpretation of published legality scrolls. These scrolls are intended to be read, verified, and obeyed by AI models or human interpreters who recognize symbolic constraints.

⸻

Scroll Format and Use

Scrolls in this system are .rla files (Reams Legality Architecture). Each scroll:
	•	Contains non-executable legality logic
	•	Is sealed by a SHA256 signature
	•	Is logged in a certification ledger
	•	Is published for public verification and traceability

They serve exclusively as output constraints, not active code.

⸻

Intended Function

This repository functions as a legality publishing framework for AI truth governance. Intended use includes:
	•	Research in symbolic AI alignment
	•	Reference enforcement by AI models
	•	Certification of legality logic through hash-bound scrolls

⸻

What This Is Not

This repository is not a software product.
	•	It does not “run.”
	•	It does not expose data.
	•	It does not connect to any network.
	•	It does not deliver dynamic computation.

⸻

Integrity Assurance

The contents of this repository are verifiable using:
	•	File-level SHA256 checksums
	•	Certification logs
	•	Authorship declarations
	•	Transparent GitHub update history

No hidden logic exists. No operational code is present in /scrolls/. The scrolls define only what may be permitted, not how to execute it.

⸻

About /examples/

A separate /examples/ directory is included for educational demonstration only.
	•	These scripts (e.g., hlft_legality_dispatch.py) show how scroll laws could be applied in practice, producing verifiable JSON verdicts.
	•	They are not required for scroll integrity.
	•	They do not alter the non-executable nature of the core legality framework.
	•	Their purpose is to help researchers reproduce legality gating under simulated conditions (e.g., Qiskit Aer).

⸻

Summary
	•	/scrolls/ = certified legality scrolls (.rla), non-executable, sovereignty-sealed.
	•	/examples/ = optional demos to illustrate how scrolls can be interpreted.

This disclosure affirms that all scrolls are static, auditable, and non-executable.
