# CENTINELA Runtime API

This is the deployable backend intended for UiPath integration. It provides public HTTP endpoints, persistence, auditability, OpenAPI, and UiPath-friendly operations.

## Running Locally

```bash
python -m uvicorn apps.centinela_runtime.main:app --reload --port 8070
```

## Cloud Deployment

A standard `Dockerfile` and `render.yaml` are provided in the root directory to deploy this service to Render or any standard container host.
