# CENTINELA Runtime Architecture

The CENTINELA Runtime API provides a deterministic, deployable backend for UiPath integration.

## Architecture
This is a single deployable FastAPI service that acts as the source of truth for the case state and business logic during integration. It replaces the local multi-service orchestration (which was used for conceptual testing) with a production-ready HTTP API surface that UiPath Maestro Case can reliably consume.

## Adapters
The architecture uses an adapter pattern to isolate external system calls:
- **`CoreBankingAdapter`**: Simulates customer and transaction lookups.
- **`ReceiverBankAdapter`**: Simulates trace-transfer and freeze-funds actions.
Currently, these return synthetic deterministic responses based on input flags. Later, they can be swapped with real HTTP clients pointing to bank APIs without changing the core domain logic.

## Persistence
- **Case Store**: Cases are persisted locally in `runtime_data/cases.jsonl`.
- **Audit Store**: All stage transitions, adapter calls, and human decisions are appended immutably to `runtime_data/audit.jsonl`.
This lightweight JSONL approach survives restarts and is ideal for early-stage integration testing.

## UiPath Integration Path
The service exposes specific `/uipath/*` endpoints designed to return compact outputs suitable for UiPath API Workflows and External Workflows.
1. UiPath calls `/uipath/start-fraud-dispute`.
2. UiPath calls `/uipath/run-investigation`. If `human_review_required` is true, the UiPath workflow suspends and creates an Action Center task.
3. The human completes the task in UiPath.
4. UiPath resumes and calls `/uipath/submit-human-decision`.

## Limitations
- **No Real Banking Data**: All data is synthetic.
- **Local Persistence**: JSONL files are used instead of a relational database to keep deployment complexity low.
- **Deterministic**: LLM calls are omitted to ensure predictable behavior during the integration phase.
