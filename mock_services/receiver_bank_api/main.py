from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
import time

app = FastAPI(title="Receiver Bank API (Mock)")

class TraceTransferRequest(BaseModel):
    transaction_id: str
    amount_cop: float
    receiver_bank: str
    simulate_failure: Optional[str] = "none"

class FreezeFundsRequest(BaseModel):
    transaction_id: str
    receiver_account: str
    amount_cop: float
    risk_level: str

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "receiver-bank-api"}

@app.post("/trace-transfer")
def trace_transfer(req: TraceTransferRequest, response: Response):
    if req.simulate_failure == "api_down":
        response.status_code = 503
        return {"error": "Service Unavailable"}
    elif req.simulate_failure == "timeout":
        time.sleep(3) # Simulate a short delay then timeout
        response.status_code = 504
        return {"error": "Gateway Timeout"}
    elif req.simulate_failure == "not_found":
        response.status_code = 404
        return {"error": "Transaction not found at receiver bank"}
    elif req.simulate_failure == "conflicting_response":
        return {
            "transaction_id": req.transaction_id,
            "status": "flagged",
            "amount_received_cop": req.amount_cop,
            "account_status": "suspicious",
            "notes": "Receiver account has multiple recent fraud flags."
        }
    
    # Default success scenario ("none")
    return {
        "transaction_id": req.transaction_id,
        "status": "credited",
        "amount_received_cop": req.amount_cop,
        "account_status": "active",
        "cleared_at": "2026-06-19T10:05:00Z"
    }

@app.post("/freeze-funds")
def freeze_funds(req: FreezeFundsRequest):
    if req.risk_level.lower() in ["high", "critical"]:
        return {
            "freeze_requested": True,
            "status": "funds_frozen",
            "transaction_id": req.transaction_id
        }
    else:
        return {
            "freeze_requested": False,
            "reason": "Risk level not sufficient for immediate freeze",
            "transaction_id": req.transaction_id
        }
