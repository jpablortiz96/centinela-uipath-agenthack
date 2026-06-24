from typing import Dict, Any
from ..audit_store import log_event
from ..case_store import save_case
from .fraud_investigation import run_fraud_investigation

def process_investigation(case_data: Dict[str, Any]) -> Dict[str, Any]:
    case_data["current_stage"] = "Investigation"
    save_case(case_data)
    
    # Run business logic
    case_data = run_fraud_investigation(case_data)
    
    # Evaluate stage transition based on investigation result
    if case_data["recommended_action"] == "escalate_to_human":
        case_data["status"] = "waiting_for_human"
        case_data["current_stage"] = "Human Decision"
        log_event(case_data["case_id"], "StageTransition", {"new_stage": "Human Decision", "reason": "High risk or conflict detected"})
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
    
    log_event(case_data["case_id"], "StageTransition", {"new_stage": "Resolution", "reason": f"Human decision applied: {decision}"})
    
    save_case(case_data)
    return case_data
