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
| CENTINELA exposes a no-body Maestro connector endpoint to support direct UiPath Maestro integration. | `apps/centinela_runtime/main.py` | Supported | Workarounds UiPath Integration Services body serialization bugs. |
| CENTINELA implements deterministic api-down retry handling. | `apps/centinela_runtime/services/fraud_investigation.py` | Supported | Retries up to 3 times before escalating. |
| CENTINELA uses a decision policy engine for human gating. | `apps/centinela_runtime/services/case_management.py` | Supported | Forces human review for critical risk or receiver conflict. |
| CENTINELA calculates SLA status deterministically. | `apps/centinela_runtime/services/case_management.py` | Supported | Included in export payload. |
| CENTINELA generates deterministic Analyst Briefs and Customer Response Drafts. | `apps/centinela_runtime/services/case_management.py` | Supported | Elevates the realism of the human decision stage. |
| CENTINELA UiPath debug connector integration was successful. | Code/Logs | Supported | Maestro executed the connector activity in Debug mode on cloud. |
| Connected Maestro solution publish is blocked by UiPath Labs limitation. | `docs/UIPATH_PRODUCT_FEEDBACK.md` | Pending UiPath Fix | Packaging fails with 'elements unknown' for custom connectors. |
