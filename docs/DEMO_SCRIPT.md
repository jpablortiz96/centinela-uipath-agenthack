# Demo Script

**Target Duration**: 5 minutes

## 1. Introduction (0:00 - 0:30)
- Briefly introduce the business problem: Fraud dispute resolution for instant payments in LATAM is complex and error-prone.
- Introduce CENTINELA and the core thesis: We test what happens when the case breaks and how UiPath Maestro Case keeps it alive.

## 2. Create Fraud Dispute (0:30 - 1:15)
- Show a synthetic customer submitting a fraud claim via a mock chat/portal.
- The **Intake Agent** captures the details.

## 3. Process Evidence (1:15 - 2:00)
- The **Evidence Agent** uses Document Understanding to parse the submitted receipt.
- Show the extraction results and confidence scores.

## 4. Inject Failure & Investigation (2:00 - 3:00)
- The **Fraud Investigator Agent** queries the mock Receiver Bank API.
- **INJECT FAILURE**: Trigger a `receiver_bank_api_down` or `investigator_timeout` error.
- Show Maestro Case catching the exception, updating the case state, and initiating a retry mechanism.

## 5. Human Decision (3:00 - 4:00)
- The failure cannot be automatically resolved or hits a `high_risk_refund_gate`.
- The case escalates to a human.
- Open **UiPath Action Center**, review the summarized case data, and click "Approve Refund".

## 6. Audit & Conclusion (4:00 - 5:00)
- Show the case successfully resolving.
- Display the exported Audit Trail, highlighting every step, failure, retry, and the human action.
- Conclude with the value proposition of Maestro Case for long-running, resilient workflows.
