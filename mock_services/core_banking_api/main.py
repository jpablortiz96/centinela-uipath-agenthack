from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="Core Banking API (Mock)")

# In-memory storage for mock data
disputes_db = {}

class DisputeCreate(BaseModel):
    customer_id: str
    transaction_id: str
    reported_reason: str
    evidence_items: List[str]

class DisputeStatusUpdate(BaseModel):
    status: str

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "core-banking-api"}

@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    return {
        "customer_id": customer_id,
        "name": "Jane Doe",
        "account_status": "active",
        "risk_score": 12,
        "kyc_verified": True
    }

@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: str):
    return {
        "transaction_id": transaction_id,
        "amount_cop": 1500000,
        "currency": "COP",
        "timestamp": "2026-06-19T10:00:00Z",
        "sender_account": "1234567890",
        "receiver_account": "0987654321",
        "receiver_bank": "BANCO_DESTINO",
        "status": "completed"
    }

@app.post("/disputes")
def create_dispute(dispute: DisputeCreate):
    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
    dispute_record = {
        "case_id": case_id,
        "customer_id": dispute.customer_id,
        "transaction_id": dispute.transaction_id,
        "reported_reason": dispute.reported_reason,
        "evidence_items": dispute.evidence_items,
        "status": "open",
        "created_at": "2026-06-19T12:00:00Z"
    }
    disputes_db[case_id] = dispute_record
    return dispute_record

@app.get("/disputes/{case_id}")
def get_dispute(case_id: str):
    if case_id not in disputes_db:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return disputes_db[case_id]

@app.patch("/disputes/{case_id}/status")
def update_dispute_status(case_id: str, update: DisputeStatusUpdate):
    if case_id not in disputes_db:
        raise HTTPException(status_code=404, detail="Dispute not found")
    disputes_db[case_id]["status"] = update.status
    return disputes_db[case_id]
