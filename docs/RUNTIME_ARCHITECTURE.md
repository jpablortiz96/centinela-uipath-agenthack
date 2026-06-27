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
To avoid complex API Workflow project packaging in Maestro, the recommended integration path is via a Connector Activity or HTTP/OpenAPI connector. The service exposes specific `/uipath/*` endpoints, including a single-call Maestro-friendly endpoint:
1. Maestro Case triggers a Connector Activity pointing to `/uipath/maestro-investigation-default`. (Note: This GET endpoint exists to avoid UiPath Labs body serialization issues in Connector Activity).
2. The endpoint creates the case, runs the investigation, and immediately returns the required state.
3. If `human_review_required` is true, Maestro creates an Action Center task based on the response.
4. The human completes the task in UiPath.
5. The case continues its lifecycle in Maestro.

### Maestro No-Body End-to-End Lifecycle
Due to body serialization issues in UiPath Integration Services, we implemented a complete stateless/no-body REST path for Maestro Connector integration:
1. **Investigation**: `GET /uipath/maestro-api-down-default` (or `GET /uipath/maestro-investigation-default`) creates and runs the investigation automatically.
2. **Fraud Intelligence Layer**: Automatically generated after investigation to provide network, priority, simulator, checklist, and linked signals.
3. **Resolution (Human Decision)**: `GET /uipath/maestro-approve-latest`, `GET /uipath/maestro-reject-latest`, `GET /uipath/maestro-request-more-evidence-latest`, or `GET /uipath/maestro-escalate-latest`.
4. **Audit Export**: `GET /uipath/maestro-export-latest` fetches the updated state of the latest Maestro case.

### Analyst Console
The Runtime API also includes a lightweight web console (`GET /analyst`) serving as an operational surface for analysts or judges. This console provides a visual representation of case states, risk profiles, SLA status, policy outcomes, retry events, and full audit exports, all without requiring external dependencies like React or CDNs.

## Deployment Strategy
- **No Real Banking Data**: All data is synthetic.
- **Local Persistence**: JSONL files are used instead of a relational database to keep deployment complexity low.
- **Deterministic**: LLM calls are omitted to ensure predictable behavior during the integration phase.


