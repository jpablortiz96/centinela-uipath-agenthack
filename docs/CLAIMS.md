# Product Claims & Evidence Mapping

This document maps our hackathon claims to the specific evidence artifacts supporting them, maintaining an honest accounting of our current capabilities versus future intended architecture.

| Claim | Evidence Artifact | Status | Notes |
| :--- | :--- | :--- | :--- |
| CENTINELA can process a normal fraud dispute end-to-end locally. | `scripts/smoke_test_case_orchestrator.py`, `evidence/logs/step4_case_orchestrator_smoke.txt` | Supported locally | Local orchestration, not UiPath Maestro Case yet. |
| CENTINELA handles receiver bank API failure paths. | `scripts/smoke_test_mock_apis.py`, `scripts/smoke_test_fraud_investigator.py` | Supported locally | Failure is synthetic but deterministic. |
| CENTINELA includes a human decision gate. | `scripts/smoke_test_case_orchestrator.py`, Chaos Console flow | Supported locally | Local simulated human endpoint; will map to UiPath Action Center. |
| CENTINELA provides an immutable, auditable timeline of events. | `evidence/logs/case_orchestrator_runs.jsonl`, `apps/chaos_console` Export feature | Supported locally | Currently stored in a JSONL file; will migrate to Maestro Case native audit logging. |
| CENTINELA Maestro Case was published and executed in UiPath Automation Cloud. | UiPath screenshots under `evidence/manual-screenshots/` | Supported | Case skeleton execution; local APIs/agents demonstrated separately. |
| CENTINELA Runtime API persists cases and audit events. | `apps/centinela_runtime/case_store.py`, `audit_store.py` | Supported | Stores data locally in JSONL format for easy review. |
| CENTINELA exposes UiPath-friendly endpoints. | `apps/centinela_runtime/main.py` | Supported | Endpoints designed for API Workflow integration. |
| CENTINELA can force high-risk cases into a human decision state. | `scripts/smoke_test_centinela_runtime.py` | Supported | Deterministic risk thresholds trigger human wait state. |
| CENTINELA does not use real banking data. | Codebase inspection | Supported | Fully synthetic data generated in-memory. |
| CENTINELA Runtime exposes a single-call Maestro integration endpoint. | `apps/centinela_runtime/main.py` | Supported | Solves the Maestro API Workflow packaging issue by using a direct connector approach. |
| UiPath connection will be completed in the next step through API Workflow/External Workflow/Connector. | Documentation only | Pending | Runtime API is built, ready for connection. |
