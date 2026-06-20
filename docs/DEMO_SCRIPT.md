# Demo Script

**Target Duration**: 5 minutes

## 1. Setup & Introduction (0:00 - 1:00)
- Briefly introduce the business problem: Fraud dispute resolution for instant payments in LATAM is complex and error-prone.
- Introduce CENTINELA and the core thesis: We test what happens when the case breaks and how UiPath Maestro Case keeps it alive.
- Open the **Chaos Console** at `http://127.0.0.1:8050`.
- Click **Refresh Status** to verify that the core simulated APIs (Core Banking, Receiver Bank, Fraud Investigator, Case Orchestrator) are healthy.

## 2. Run Normal Case (1:00 - 2:00)
- Click **Run Normal Case**.
- Explain: A typical, low-risk fraud dispute is ingested and handled automatically.
- Show: The timeline populates, the risk level remains low/medium, and the case auto-resolves.

## 3. Inject Failure & Investigation (2:00 - 3:00)
- Click **Break Case: Receiver Bank Conflict**.
- Explain: Here is where CENTINELA handles chaos. A high-value case enters, and the mock Receiver Bank API returns conflicting information (simulating a flagged account).
- Show: The Fraud Investigator calculates a `critical` risk score. The Case Orchestrator intelligently pauses and sets the status to `waiting_for_human`.

## 4. Human Decision (3:00 - 4:00)
- Explain: In production, this maps to **UiPath Action Center**.
- Click **Human Decision: Approve Refund**.
- Show: The orchestrator logs the human intervention and progresses the case to `resolved_by_human`.

## 5. Audit & Conclusion (4:00 - 5:00)
- Click **Export Audit**.
- Show the raw, judge-friendly JSON output in the console. Highlight how every step, failure, and human action is immutably logged with timestamps.
- Conclude: This transparent, end-to-end resilience is exactly what we will integrate into UiPath Maestro Case next.
