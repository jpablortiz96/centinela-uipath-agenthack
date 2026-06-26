from typing import Dict, Any, List
from ..audit_store import log_event
from ..case_store import save_case
from .fraud_investigation import run_fraud_investigation

def calculate_sla(case_data: Dict[str, Any]) -> None:
    # Deterministic mock SLA
    case_data["sla_target_minutes"] = 120
    case_data["elapsed_minutes"] = 15
    case_data["sla_status"] = "within_sla"
    case_data["stage_sla_status"] = "within_sla"

def evaluate_decision_policy(case_data: Dict[str, Any]) -> None:
    reasons = []
    require_human = False
    
    if case_data.get("risk_level") in ["high", "critical"]:
        require_human = True
        reasons.append(f"Risk level is {case_data['risk_level']}")
        
    if case_data.get("simulate_receiver_failure") == "conflicting_evidence":
        require_human = True
        reasons.append("Receiver bank provided conflicting evidence")
        
    if case_data.get("retry_attempts", 0) >= case_data.get("max_retries", 3):
        require_human = True
        reasons.append("Receiver bank API is down after max retries")
        
    case_data["policy_result"] = "escalate_to_human" if require_human else "auto_resolve"
    case_data["policy_reasons"] = reasons
    case_data["required_human_gate"] = require_human

def generate_analyst_brief(case_data: Dict[str, Any]) -> None:
    case_data["analyst_brief"] = "Deterministic brief generated for analyst."
    case_data["evidence_quality"] = case_data.get("evidence_quality", "unknown")
    case_data["evidence_summary"] = f"Evidence quality is {case_data['evidence_quality']}."
    case_data["risk_explanation"] = f"Risk score is {case_data.get('risk_score')}. {', '.join(case_data.get('policy_reasons', []))}"
    case_data["recommended_questions_for_analyst"] = ["Did the user authorize this?", "Is the receiver account legitimate?"]
    case_data["allowed_decisions"] = ["approve_refund", "reject_refund", "request_more_evidence", "escalate_fraud_ops"]

def generate_customer_response_draft(case_data: Dict[str, Any]) -> None:
    status = case_data.get("status")
    decision = case_data.get("human_decision")
    
    if status == "waiting_for_human":
        draft = "Your case is under specialist review. We are looking into the details and will update you shortly."
    elif status == "resolved_by_human" and decision == "approve_refund":
        draft = "Your refund has been approved. The funds will be credited to your account shortly."
    elif status == "resolved_by_human" and decision == "reject_refund":
        draft = "We were unable to approve your refund request based on the investigation findings."
    else:
        draft = "Your case has been processed."
        
    case_data["customer_response_draft"] = f"[DRAFT] {draft}"

def process_investigation(case_data: Dict[str, Any]) -> Dict[str, Any]:
    case_data["current_stage"] = "Investigation"
    save_case(case_data)
    
    # Run business logic
    case_data = run_fraud_investigation(case_data)
    
    # Hardening: Run auxiliary deterministic engines
    calculate_sla(case_data)
    evaluate_decision_policy(case_data)
    generate_analyst_brief(case_data)
    generate_customer_response_draft(case_data)
    
    # Evaluate stage transition based on policy engine
    if case_data["required_human_gate"]:
        case_data["status"] = "waiting_for_human"
        case_data["current_stage"] = "Human Decision"
        log_event(case_data["case_id"], "StageTransition", {"new_stage": "Human Decision", "reason": "Policy requires human gate"})
    else:
        case_data["status"] = "auto_resolved"
        case_data["current_stage"] = "Resolution"
        log_event(case_data["case_id"], "StageTransition", {"new_stage": "Resolution", "reason": "Low risk, auto-resolved"})
        
    save_case(case_data)
    return case_data

def process_human_decision(case_data: Dict[str, Any], decision: str, analyst: str, notes: str) -> Dict[str, Any]:
    log_event(case_data["case_id"], "HumanDecisionSubmitted", {
        "decision": decision,
        "analyst": analyst,
        "notes": notes
    })
    
    case_data["human_decision"] = decision
    case_data["status"] = "resolved_by_human"
    case_data["current_stage"] = "Resolution"
    
    # Update customer response draft after decision
    generate_customer_response_draft(case_data)
    
    log_event(case_data["case_id"], "StageTransition", {"new_stage": "Resolution", "reason": f"Human decision applied: {decision}"})
    
    save_case(case_data)
    return case_data
