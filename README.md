# CENTINELA — Agentic Fraud Dispute Case Manager for Instant Payments

## Overview
**CENTINELA** is an agentic fraud dispute case manager for instant payments. 

In a LATAM banking context, when a customer reports a suspicious transfer and provides evidence (e.g., a receipt, bank statement screenshot, or chat screenshot), the process of investigating the fraud claim is often disjointed and manual. 

CENTINELA orchestrates this long-running case using UiPath Maestro Case, agents, mock banking APIs, human approval gates, retries, exception handling, and auditability. It proves what happens when a real banking case breaks — and how UiPath keeps it alive until resolution.

## Why UiPath Maestro Case?
Most agents work in the happy path, but fraud investigation is inherently complex, error-prone, and involves multi-step validation. UiPath Maestro Case is perfectly suited because it provides the robust state management, exception handling, and human-in-the-loop orchestration required for these mission-critical, long-running processes.

## Intended UiPath Components
- UiPath Maestro Case
- Agent Builder / Low-code Agents
- Coded Agent
- API Workflows
- Action Center
- Document Understanding
- Automation Cloud

## Agent Types Planned
- **Intake Agent**: Receives the initial claim and extracts relevant data from the customer's communication.
- **Evidence Agent**: Analyzes provided evidence (receipts, screenshots) using Document Understanding and validates it against banking records.
- **Fraud Investigator Agent**: Correlates the data, interfaces with mock banking APIs, handles exceptions, and recommends a resolution.

## Evidence-First Approach
We prioritize an evidence-first approach, generating robust synthetic data and simulating real-world failures to demonstrate the resilience of the system before fully connecting the UI and banking APIs.

## Current Integration Status
- Published Maestro Case v1.0.0.
- Runtime API publicly deployed on Render.
- Maestro connector validated in Debug mode in the cloud.
- Connected publish is currently blocked by a UiPath Labs connector packaging issue (see `docs/UIPATH_PRODUCT_FEEDBACK.md`).
- Runtime hardening v2 is available, introducing retry mechanics, deterministic SLA calculation, and policy-driven human gating.

## Setup Instructions
1. Clone the repository.
2. Ensure you have Python 3 installed.
3. Install the minimal requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the chaos simulation script to generate synthetic cases:
   ```bash
   python evidence/run_chaos.py --cases 50 --fail-rate 0.3 --seed 42
   ```

### Running the Mock Banking APIs

Start the Core Banking API (simulates the victim's bank):
```bash
python -m uvicorn mock_services.core_banking_api.main:app --reload --port 8010
```

Start the Receiver Bank API (simulates the receiving bank):
```bash
python -m uvicorn mock_services.receiver_bank_api.main:app --reload --port 8020
```

### Running the Fraud Investigator Agent

Start the Fraud Investigator Agent:
```bash
python -m uvicorn agents.fraud_investigator.main:app --reload --port 8030
```

### Running the Case Orchestrator

Start the local Case Orchestrator:
```bash
python -m uvicorn orchestrator.case_orchestrator.main:app --reload --port 8040
```

### Running the Chaos Console (Demo UI)

Start the local Chaos Console:
```bash
python -m uvicorn apps.chaos_console.main:app --reload --port 8050
```

### Running All Smoke Tests

With all five services running (Core Banking, Receiver Bank, Fraud Investigator, Case Orchestrator, and Chaos Console), open a new terminal and run the full suite:
```bash
python scripts/run_all_smoke_tests.py
```

## CENTINELA Runtime API
This is the deployable backend intended for UiPath integration. The Runtime API is the integration target for UiPath. It provides public HTTP endpoints, persistence, auditability, and OpenAPI specifications. 
The local multi-service mode (mock banking APIs, local orchestrator, chaos console) remains available for technical review, but the Runtime API is the unified service to be connected to the cloud.

### Maestro Direct Connector Integration
To avoid the "No solution tool factory is registered" error during Maestro packaging, the API exposes a single-call Maestro endpoint (`/uipath/maestro-investigation`). This allows Maestro to call the runtime directly via a Connector Activity or HTTP connector instead of requiring a separate API Workflow project. To bypass body serialization issues in UiPath Labs Integration Service, the runtime also exposes a Maestro no-body connector endpoint (`GET /uipath/maestro-investigation-default`) that uses default parameters.

Start the Runtime API locally:
```bash
python -m uvicorn apps.centinela_runtime.main:app --reload --port 8070
```

## Evidence Pack
We prioritize an evidence-first approach. All capabilities claimed during the hackathon are backed by reproducible code, logs, and screenshots available in the `evidence/` directory.
- **[Evidence Report](evidence/EVIDENCE_REPORT.md)**: Generated metrics and run summary.
- **[Metrics Summary](evidence/metrics_summary.json)**: Raw JSON snapshot of chaos metrics.
- **[Claims Mapping](docs/CLAIMS.md)**: Honest accounting of claims vs. local implementations.
- **[UiPath Execution Evidence](docs/UIPATH_EXECUTION_EVIDENCE.md)**: Details on the Maestro Case execution in Automation Cloud.
- **[Logs](evidence/logs/)**: Raw smoke test outputs and JSONL orchestrator audits.
- **[Screenshots](evidence/manual-screenshots/)**: Visual verification of UI capabilities and UiPath execution.
