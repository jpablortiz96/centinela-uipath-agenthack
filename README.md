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

## Current Status
**Step 1 Foundation**: The initial repository foundation is built. Synthetic data and chaos simulation scripts are available. It is *not yet* connected to UiPath Labs.

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

### Running the Smoke Tests

With all APIs running (Core Banking, Receiver Bank, and Fraud Investigator), open a new terminal and run the tests:
```bash
python scripts/smoke_test_mock_apis.py
python scripts/smoke_test_fraud_investigator.py
```
