# UiPath Components

CENTINELA leverages the following UiPath components to orchestrate the fraud dispute lifecycle:

1. **UiPath Maestro Case**
   - The core orchestrator. Manages the long-running state of the fraud dispute, ensuring the process survives system failures, timeouts, and human wait times.

2. **Agent Builder / Low-code Agents**
   - Used to quickly assemble the Intake and Evidence agents, connecting them to predefined AI skills.

3. **Coded Agent**
   - Deployed for complex logic within the Fraud Investigator Agent (implemented as a Python FastAPI service). It calculates deterministic risk, recommends actions, and integrates with the chaos simulator. It is intended to be orchestrated by Maestro Case.

4. **API Workflows**
   - Handles the communication with our mock banking microservices (Core Banking API, Receiver Bank API).

5. **Action Center**
   - Provides the human-in-the-loop interface. Used when a case requires a manager's approval or when evidence is conflicting and requires manual review.

6. **Document Understanding**
   - Extracts data from customer-provided evidence, such as bank transfer receipts or chat screenshots.

7. **Automation Cloud**
   - The underlying platform hosting and managing the deployment of all agents, queues, and assets.

## Local-to-UiPath Mapping

The Step 4 local Case Orchestrator simulates the future UiPath implementation. Here is how the local mock maps to the actual UiPath stack:

* **Local case stage transitions** → UiPath Maestro Case stages
* **Human decision endpoint** → UiPath Action Center / human task
* **API calls** → UiPath API Workflows
* **Fraud Investigator Agent** → Coded Agent
* **Audit events** → Maestro visibility/audit trail
