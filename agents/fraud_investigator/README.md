# Fraud Investigator Agent

This is a coded fraud investigation agent for the CENTINELA project. It calculates risk, calls mock banking APIs, and determines next actions.

## Running the Agent

```bash
python -m uvicorn agents.fraud_investigator.main:app --reload --port 8030
```
