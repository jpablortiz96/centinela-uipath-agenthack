# Case Orchestrator (Mock)

This is a local orchestration service that coordinates a fraud dispute case through stages: Intake → Evidence Review → Investigation → Human Decision → Resolution → Audit Export.
It simulates the future UiPath Maestro Case lifecycle for Step 4 of the CENTINELA project.

## Running the Service

```bash
python -m uvicorn orchestrator.case_orchestrator.main:app --reload --port 8040
```
