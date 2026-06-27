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
    
    # SLA Fields
    sla_target_minutes: Optional[int] = None
    elapsed_minutes: Optional[int] = None
    sla_status: Optional[str] = None
    stage_sla_status: Optional[str] = None
    
    # Retry Policy Fields
    retry_attempts: int = 0
    max_retries: int = 3
    
    # Decision Policy Engine Fields
    policy_result: Optional[str] = None
    policy_reasons: Optional[List[str]] = None
    required_human_gate: Optional[bool] = None
    
    # Analyst Brief & Outputs
    analyst_brief: Optional[str] = None
    evidence_summary: Optional[str] = None
    risk_explanation: Optional[str] = None
    recommended_questions_for_analyst: Optional[List[str]] = None
    allowed_decisions: Optional[List[str]] = None
    customer_response_draft: Optional[str] = None
    
    # Fraud Intelligence Layer
    fraud_network: Optional[Dict[str, Any]] = None
    priority_summary: Optional[Dict[str, Any]] = None
    decision_simulator: Optional[Dict[str, Any]] = None
    evidence_checklist: Optional[Dict[str, Any]] = None
    linked_case_signals: Optional[Dict[str, Any]] = None

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
    
    case_summary: Optional[Dict[str, Any]] = None
    risk_summary: Optional[Dict[str, Any]] = None
    policy_summary: Optional[Dict[str, Any]] = None
    sla_summary: Optional[Dict[str, Any]] = None
    analyst_brief: Optional[str] = None
    evidence_summary: Optional[str] = None
    risk_explanation: Optional[str] = None
    recommended_questions_for_analyst: Optional[List[str]] = None
    allowed_decisions: Optional[List[str]] = None
    customer_response_draft: Optional[str] = None
    fraud_network: Optional[Dict[str, Any]] = None
    priority_summary: Optional[Dict[str, Any]] = None
    decision_simulator: Optional[Dict[str, Any]] = None
    evidence_checklist: Optional[Dict[str, Any]] = None
    linked_case_signals: Optional[Dict[str, Any]] = None
    timeline: List[Dict[str, Any]]
    limitations_notice: str = "This is a deterministic runtime for UiPath integration. Not a production banking API."
