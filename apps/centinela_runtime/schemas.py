from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class CaseCreateInput(BaseModel):
    customer_id: str
    transaction_id: str
    amount_cop: float
    evidence_quality: str
    reported_reason: str
    simulate_receiver_failure: str = "none"
    source: str = "manual"

class HumanDecisionInput(BaseModel):
    decision: str
    analyst: str
    notes: str

class UiPathRunInvestigationInput(BaseModel):
    case_id: str

class UiPathHumanDecisionInput(BaseModel):
    case_id: str
    decision: str
    analyst: str
    notes: str

class CaseState(BaseModel):
    case_id: str
    customer_id: str
    transaction_id: str
    amount_cop: float
    evidence_quality: str
    reported_reason: str
    simulate_receiver_failure: str
    source: str
    status: str
    current_stage: str
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    recommended_action: Optional[str] = None
    human_decision: Optional[str] = None

class UiPathCompactOutput(BaseModel):
    case_id: str
    status: str
    current_stage: str
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    recommended_action: Optional[str] = None
    human_review_required: bool
    next_required_action: Optional[str] = None
    audit_event_count: int

class UiPathMaestroOutput(BaseModel):
    case_id: str
    status: str
    current_stage: str
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    recommended_action: Optional[str] = None
    human_review_required: bool
    next_required_action: Optional[str] = None
    audit_event_count: int
    runtime_url: Optional[str] = None
    message: str

class AuditExportOutput(BaseModel):
    case_id: str
    status: str
    current_stage: str
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    recommended_action: Optional[str] = None
    human_decision: Optional[str] = None
    timeline: List[Dict[str, Any]]
    limitations_notice: str = "This is a deterministic runtime for UiPath integration. Not a production banking API."
