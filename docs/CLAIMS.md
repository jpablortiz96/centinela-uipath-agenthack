# Product Claims & Evidence Mapping

This document maps our hackathon claims to the specific evidence artifacts supporting them, maintaining an honest accounting of our current capabilities versus future intended architecture. We do not overclaim.

### Supported Claims (What works today)

| Claim | Evidence Artifact | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Published Maestro Case v1.0.0** | `evidence/manual-screenshots/step12_maestro_case_published.png` | Supported | The baseline case orchestration definition is successfully published to Orchestrator. |
| **Connected cloud debug with Runtime API** | `evidence/manual-screenshots/step28_maestro_end_to_end_connected_debug.png` | Supported | Maestro executed the connector activity in Debug mode on the UiPath cloud. |
| **Runtime API is public** | `evidence/logs/step37_runtime_render_smoke.txt` | Supported | Deployed continuously on Render, accessible globally. |
| **Analyst Console** | `evidence/manual-screenshots/step35_analyst_console_v3_render.png` | Supported | Enterprise-grade UI rendering deterministic case insights. |
| **Judge Replay** | `evidence/manual-screenshots/step36_judge_replay_render.png` | Supported | Guided evaluator flow safely replicating the Maestro integration logic. |
| **Fraud Intelligence Layer** | `evidence/manual-screenshots/step35_analyst_console_v3_render.png` | Supported | Generates Priority Queue, Fraud Network, Simulator, Checklist, and Signals. |
| **Retry handling** | `apps/centinela_runtime/services/fraud_investigation.py` | Supported | Deterministically retries failing external APIs up to 3 times before escalating. |
| **Human gate** | `apps/centinela_runtime/services/case_management.py` | Supported | Policy forces cases with critical risk or retry exhaustion into manual review. |
| **Audit export** | `evidence/logs/step28_maestro_latest_export_after_debug.json` | Supported | Generates a rich, immutable v2 audit JSON package. |

---

### Explicit Non-Claims (What we DO NOT claim)

| Claim | Status | Notes |
| :--- | :--- | :--- |
| **Connected publish/deployment** | Not Claimed / Blocked | Publishing the connected connector flow fails with `elements unknown` (a UiPath Labs limitation). See `docs/UIPATH_PRODUCT_FEEDBACK.md`. |
| **Real banking production system** | Not Claimed | Adapters are deterministic synthetics built for safe, reproducible evaluation. |
| **Real fraud detection on real users** | Not Claimed | All PII, cases, and financial amounts are synthetically generated. |
| **Autonomous refund approval** | Not Claimed | We deliberately avoid letting the system approve refunds; financial decisions remain with the human. |
