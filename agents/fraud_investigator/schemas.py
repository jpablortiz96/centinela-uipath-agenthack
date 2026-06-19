from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class InvestigationRequest(BaseModel):
    case_id: str
    customer_id: str
    transaction_id: str
    amount_cop: float
    evidence_quality: str
    reported_reason: str
    simulate_receiver_failure: Optional[str] = "none"

class AuditEvent(BaseModel):
    timestamp: str
    actor: str
    event: str
    details: Dict[str, Any]

class InvestigationResponse(BaseModel):
    case_id: str
    transaction_id: str
    risk_score: int
    risk_level: str
    recommended_action: str
    human_review_required: bool
    receiver_trace_status: str
    audit_events: List[AuditEvent]
    explanation: List[str]
    freeze_response: Optional[Dict[str, Any]] = None
