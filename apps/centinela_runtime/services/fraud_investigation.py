from typing import Dict, Any
from ..adapters.core_banking import CoreBankingAdapter
from ..adapters.receiver_bank import ReceiverBankAdapter
from ..audit_store import log_event

def run_fraud_investigation(case_data: Dict[str, Any]) -> Dict[str, Any]:
    case_id = case_data["case_id"]
    
    log_event(case_id, "InvestigationStarted", {"message": "Starting fraud investigation"})
    
    core_banking = CoreBankingAdapter()
    receiver_bank = ReceiverBankAdapter()
    
    # 1. Call Core Banking
    txn_details = core_banking.get_transaction_details(case_data["customer_id"], case_data["transaction_id"])
    log_event(case_id, "CoreBankingCheck", txn_details)
    
    # 2. Call Receiver Bank with Retries
    simulate_failure = case_data.get("simulate_receiver_failure", "none")
    receiver_status = None
    
    if simulate_failure in ["api_down", "receiver_bank_api_down"]:
        case_data["max_retries"] = 3
        while case_data.get("retry_attempts", 0) < case_data["max_retries"]:
            case_data["retry_attempts"] = case_data.get("retry_attempts", 0) + 1
            log_event(case_id, "ReceiverBankRetryScheduled", {"attempt": case_data["retry_attempts"]})
            log_event(case_id, "ReceiverBankRetryAttempted", {"attempt": case_data["retry_attempts"]})
            
            # Still fails deterministically
            receiver_status = receiver_bank.check_receiver_status("receiver_bank_api_down")
            if case_data["retry_attempts"] == case_data["max_retries"]:
                log_event(case_id, "ReceiverBankRetryExhausted", {"max_retries": case_data["max_retries"]})
                break
    else:
        receiver_status = receiver_bank.check_receiver_status(simulate_failure)
    
    log_event(case_id, "ReceiverBankCheck", receiver_status)
    
    # Calculate Risk deterministically
    risk_score = 0
    risk_level = "low"
    recommended_action = "auto_resolve"
    
    if case_data["amount_cop"] > 1000000:
        risk_score += 40
        
    if receiver_status["status"] == "error":
        risk_score += 100
        recommended_action = "escalate_to_human"
    else:
        if receiver_status.get("account_flagged"):
            risk_score += 50
        if simulate_failure == "conflicting_evidence":
            risk_score += 60
            
    if case_data["evidence_quality"] == "low":
        risk_score += 30
        
    if risk_score > 80:
        risk_level = "critical"
        recommended_action = "escalate_to_human"
    elif risk_score > 50:
        risk_level = "high"
        recommended_action = "escalate_to_human"
    elif risk_score > 20:
        risk_level = "medium"
        
    case_data["risk_score"] = risk_score
    case_data["risk_level"] = risk_level
    case_data["recommended_action"] = recommended_action
    
    log_event(case_id, "InvestigationCompleted", {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommended_action": recommended_action
    })
    
    return case_data
