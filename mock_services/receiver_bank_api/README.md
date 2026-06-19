# Receiver Bank API (Mock)

This mock service simulates the receiving bank in an instant payment fraud dispute for the CENTINELA project.

## Running the service

```bash
python -m uvicorn mock_services.receiver_bank_api.main:app --reload --port 8020
```

## Endpoints

* `GET /health`: Returns service status.
* `POST /trace-transfer`: Checks the destination account and optionally simulates an API failure using the `simulate_failure` field.
* `POST /freeze-funds`: Evaluates risk level and freezes funds accordingly.
