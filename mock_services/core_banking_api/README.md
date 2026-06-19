# Core Banking API (Mock)

This mock service simulates the victim's bank/core banking system for the CENTINELA project.

## Running the service

```bash
python -m uvicorn mock_services.core_banking_api.main:app --reload --port 8010
```

## Endpoints

* `GET /health`: Returns service status.
* `GET /customers/{customer_id}`: Returns a synthetic customer profile.
* `GET /transactions/{transaction_id}`: Returns a synthetic instant-payment transaction.
* `POST /disputes`: Creates a synthetic fraud dispute.
* `GET /disputes/{case_id}`: Returns dispute details.
* `PATCH /disputes/{case_id}/status`: Updates dispute status.
