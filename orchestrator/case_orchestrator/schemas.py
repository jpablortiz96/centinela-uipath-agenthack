from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class CaseStartRequest(BaseModel):
    customer_id: str
    transaction_id: str
    amount_cop: float
    evidence_quality: str
    reported_reason: str
    simulate_receiver_failure: Optional[str] = "none"

class HumanDecisionRequest(BaseModel):
    decision: str
    analyst: str
    notes: str

class AuditEvent(BaseModel):
    timestamp: str
    case_id: str
    stage: str
    actor: str
    event: str
    details: Dict[str, Any]

class CaseState(BaseModel):
    case_id: str
    customer_id: str
    transaction_id: str
    amount_cop: float
    evidence_quality: str
    reported_reason: str
    simulate_receiver_failure: str
    current_stage: str
    status: str
    investigation_result: Optional[Dict[str, Any]] = None
    human_decision: Optional[Dict[str, Any]] = None
    audit_events: List[AuditEvent] = []
