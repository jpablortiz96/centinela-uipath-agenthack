# Product Claims & Evidence Mapping

This document maps our hackathon claims to the specific evidence artifacts supporting them, maintaining an honest accounting of our current capabilities versus future intended architecture.

| Claim | Evidence Artifact | Status | Notes |
| :--- | :--- | :--- | :--- |
| CENTINELA can process a normal fraud dispute end-to-end locally. | `scripts/smoke_test_case_orchestrator.py`, `evidence/logs/step4_case_orchestrator_smoke.txt` | Supported locally | Local orchestration, not UiPath Maestro Case yet. |
| CENTINELA handles receiver bank API failure paths. | `scripts/smoke_test_mock_apis.py`, `scripts/smoke_test_fraud_investigator.py` | Supported locally | Failure is synthetic but deterministic. |
| CENTINELA includes a human decision gate. | `scripts/smoke_test_case_orchestrator.py`, Chaos Console flow | Supported locally | Local simulated human endpoint; will map to UiPath Action Center. |
| CENTINELA provides an immutable, auditable timeline of events. | `evidence/logs/case_orchestrator_runs.jsonl`, `apps/chaos_console` Export feature | Supported locally | Currently stored in a JSONL file; will migrate to Maestro Case native audit logging. |
| CENTINELA Maestro Case was published and executed in UiPath Automation Cloud. | UiPath screenshots under `evidence/manual-screenshots/` | Supported | Case skeleton execution; local APIs/agents demonstrated separately. |
