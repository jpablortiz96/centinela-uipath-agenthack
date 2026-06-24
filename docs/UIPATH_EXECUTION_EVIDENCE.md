# UiPath Execution Evidence

This document honestly outlines the current state of UiPath integration for the CENTINELA project, separating what runs in the UiPath Automation Cloud from what runs locally.

## 1. Summary of what runs in UiPath Automation Cloud
We have successfully set up and executed the foundational case management skeleton within UiPath Labs:
- A Maestro Case project named **"CENTINELA - Fraud Dispute Case Manager"** was created.
- Case stages were modeled exactly matching the local simulation (Intake, Evidence Review, Investigation, Human Decision, Resolution, Audit Export).
- Human action tasks, SLAs, descriptions, and auto-generated routing rules were configured.
- The case was published (v1.0.0) and the Orchestrator deployment is active.
- Two case instances were executed successfully (Completed: 2, Failed: 0, Total: 2).

## 2. Summary of what runs locally
The underlying business logic and API integrations are currently demonstrated locally:
- **Core Banking API** (Port 8010)
- **Receiver Bank API** (Port 8020)
- **Fraud Investigator Agent** (Port 8030)
- **Local Case Orchestrator** (Port 8040)
- **Chaos Console** (Port 8050)
These local services provide deterministic failure simulation and prove the agentic logic before full API connection in UiPath.

## 3. Exact UiPath components used
- **UiPath Studio Web**: For building the automation workflows.
- **UiPath Maestro Case**: For defining the long-running case stages and state machine.
- **UiPath Orchestrator**: For managing the deployment and execution of the automation.
- **Human Actions**: Built-in Maestro task assignments for human-in-the-loop review.
- **SLAs**: Configured within the Maestro Case to handle escalation.
- **Auto-generated Rules**: Configured within the Maestro Case to route between stages.

## 4. Evidence Screenshots List
The following screenshots (located in `evidence/manual-screenshots/`) provide visual proof of the UiPath execution:
- `step7_maestro_home.png`
- `step7_agents_home.png`
- `step7_studio_home.png`
- `step8_maestro_case_created.png`
- `step9_maestro_case_tasks.png`
- `step10_maestro_case_slas.png`
- `step11_maestro_case_rules.png`
- `step12_maestro_case_published.png`
- `step12_orchestrator_deployment_active.png`
- `step13_orchestrator_job_running.png`
- `step13_maestro_case_instances_completed.png`

## 5. Honest Limitations
- Local APIs are not yet deployed as public services.
- The current UiPath Maestro Case skeleton demonstrates case modeling, SLAs, human actions, publication, deployment, and execution, but does not yet call out to the local APIs.
- The full API/agent execution (including the failure injection) is currently demonstrated locally through the Chaos Console.
- No real banking data is used in any environment.

## 6. Judge Interpretation
- **UiPath is the Orchestrator:** UiPath is used as the official case-management and governance layer.
- **Local deterministic logic:** Local services provide deterministic, reproducible business logic and failure simulation.
- **Not production ready:** The submission does not claim production banking readiness. It successfully demonstrates a resilient architectural proof-of-concept for handling instant payment fraud.
