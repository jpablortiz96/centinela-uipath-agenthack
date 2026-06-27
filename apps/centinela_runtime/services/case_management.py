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
    risk_level = case_data.get("risk_level", "unknown")
    reasons = case_data.get("policy_reasons", [])
    reason_str = reasons[0] if reasons else f"of an undetermined risk factor"
    stage = case_data.get("current_stage", "Unknown Stage")
    decision = case_data.get("human_decision")
    
    brief = f"This case reached {risk_level} risk because {reason_str.lower()}."
    if case_data.get("required_human_gate"):
        brief += f" CENTINELA escalated the case to Human Decision according to policy."
    else:
        brief += f" CENTINELA auto-resolved the case according to policy."
        
    if decision:
        decision_map = {
            "approve_refund": "approved the refund",
            "reject_refund": "rejected the refund",
            "request_more_evidence": "requested more evidence",
            "escalate_fraud_ops": "escalated to fraud ops"
        }
        human_act = decision_map.get(decision, "processed the case")
        brief += f" The human analyst {human_act} after reviewing the retry history, risk score, and audit trail."
    elif case_data.get("status") == "waiting_for_human":
        brief += " The case is currently pending human review."
        
    case_data["analyst_brief"] = brief
    
    # Improve other fields
    case_data["evidence_quality"] = case_data.get("evidence_quality", "unknown")
    case_data["evidence_summary"] = f"Initial evidence quality was '{case_data['evidence_quality']}'. Receiver failure mode: {case_data.get('simulate_receiver_failure', 'none')}. Retry attempts: {case_data.get('retry_attempts', 0)}."
    case_data["risk_explanation"] = f"Risk score is {case_data.get('risk_score')}/100. Amount involved is {case_data.get('amount_cop')} COP."
    if reasons:
        case_data["risk_explanation"] += f" Policy triggers: {', '.join(reasons)}."
        
    case_data["recommended_questions_for_analyst"] = [
        "Was the customer identity verified?", 
        "Does the customer evidence match the disputed transaction?",
        "Was the receiver bank unavailable after all retry attempts?",
        "Should the refund be approved, rejected, or escalated to fraud operations?"
    ]
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
    generate_fraud_intelligence(case_data)
    
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
    
    if decision in ["approve_refund", "reject_refund"]:
        case_data["status"] = "resolved_by_human"
        case_data["current_stage"] = "Resolution"
        log_event(case_data["case_id"], "ResolutionApplied", {"decision": decision})
    elif decision == "request_more_evidence":
        case_data["status"] = "waiting_for_evidence"
        case_data["current_stage"] = "Evidence Review"
    elif decision == "escalate_fraud_ops":
        case_data["status"] = "escalated_to_fraud_ops"
        case_data["current_stage"] = "Human Decision" # keeping it in Human Decision makes sense, or could be Escalate. We'll stick to Human Decision.
    else:
        case_data["status"] = "resolved_by_human"
        case_data["current_stage"] = "Resolution"
    
    # Update customer response draft after decision
    generate_customer_response_draft(case_data)
    generate_analyst_brief(case_data)
    generate_fraud_intelligence(case_data)
    
    log_event(case_data["case_id"], "StageTransition", {"new_stage": case_data["current_stage"], "reason": f"Human decision applied: {decision}"})
    
    save_case(case_data)
    return case_data

def generate_fraud_intelligence(case_data: Dict[str, Any]) -> None:
    # 1. Priority Scoring
    risk_score = case_data.get("risk_score", 0) or 0
    score = risk_score
    if case_data.get("required_human_gate"):
        score += 15
    retries = case_data.get("retry_attempts", 0)
    if retries >= 3:
        score += 10
    sla = case_data.get("sla_status", "")
    if sla == "at_risk":
        score += 10
    elif sla == "breached":
        score += 20
    amt = case_data.get("amount_cop", 0) or 0
    score += min(amt / 100000, 20)
    
    score = min(int(score), 100)
    level = "P3 Low"
    if score >= 90: level = "P0 Critical"
    elif score >= 75: level = "P1 High"
    elif score >= 50: level = "P2 Medium"
    
    case_data["priority_summary"] = {
        "priority_score": score,
        "priority_level": level,
        "priority_reasons": ["Derived from risk score, SLA, retries, and amount."]
    }
    
    # 2. Fraud Network Graph
    nodes = []
    edges = []
    
    c_id = case_data.get("customer_id", "Unknown")
    nodes.append({"id": f"customer:{c_id}", "label": f"Customer {c_id}", "type": "customer", "risk": "medium"})
    
    t_id = case_data.get("transaction_id", "Unknown")
    t_risk = case_data.get("risk_level", "low")
    nodes.append({"id": f"transaction:{t_id}", "label": "Instant Payment", "type": "transaction", "risk": t_risk})
    edges.append({"from": f"customer:{c_id}", "to": f"transaction:{t_id}", "label": "initiated"})
    
    r_id = "RCV-7781"
    nodes.append({"id": f"receiver:{r_id}", "label": "Receiver Account", "type": "receiver_account", "risk": "critical" if t_risk == "critical" else "high"})
    edges.append({"from": f"transaction:{t_id}", "to": f"receiver:{r_id}", "label": "sent_to"})
    
    nodes.append({"id": "bank:receiver-bank", "label": "Receiver Bank", "type": "bank", "risk": "high"})
    edges.append({"from": f"receiver:{r_id}", "to": "bank:receiver-bank", "label": "hosted_by"})
    
    if retries >= 3:
        nodes.append({"id": "signal:api_down", "label": "API Down After Retries", "type": "risk_signal", "risk": "critical"})
        edges.append({"from": "bank:receiver-bank", "to": "signal:api_down", "label": "retry_exhausted"})
        
    if case_data.get("required_human_gate"):
        nodes.append({"id": "signal:human_gate", "label": "Human Gate Required", "type": "control", "risk": "high"})
        edges.append({"from": f"transaction:{t_id}", "to": "signal:human_gate", "label": "requires_review"})
        
    case_data["fraud_network"] = {"nodes": nodes, "edges": edges}
    
    # 3. Decision Simulator
    case_data["decision_simulator"] = {
        "approve_refund": {
            "customer_impact": "Customer protected",
            "financial_impact_cop": amt,
            "operational_impact": "Requires refund processing and fraud ops monitoring",
            "risk": "May create loss if dispute is not valid",
            "recommended_when": "Evidence is strong and customer risk is high"
        },
        "reject_refund": {
            "customer_impact": "Customer assumes liability",
            "financial_impact_cop": 0,
            "operational_impact": "No financial transaction needed",
            "risk": "Customer dissatisfaction, regulatory risk if genuine fraud",
            "recommended_when": "Evidence is weak or first-party fraud suspected"
        },
        "request_more_evidence": {
            "customer_impact": "Customer delayed",
            "financial_impact_cop": 0,
            "operational_impact": "Pauses SLA clock, requires analyst follow-up",
            "risk": "SLA breach if not handled",
            "recommended_when": "Missing critical documentation"
        },
        "escalate_fraud_ops": {
            "customer_impact": "Customer delayed",
            "financial_impact_cop": 0,
            "operational_impact": "Transfers case to Level 2 Fraud Ops",
            "risk": "Higher operational cost",
            "recommended_when": "Complex network pattern or organized fraud suspected"
        }
    }
    
    # 4. Evidence Checklist
    fail_mode = case_data.get("simulate_receiver_failure", "none")
    trace_status = "failed" if fail_mode != "none" else "present"
    retry_status = "present" if retries > 0 else "not_applicable"
    
    case_data["evidence_checklist"] = {
        "evidence_score": 85 if trace_status == "present" else 60,
        "evidence_items": {
            "customer_statement": {"status": "present", "note": case_data.get("reported_reason", "Included")},
            "transaction_receipt": {"status": "present", "note": "Verified in core banking"},
            "bank_statement": {"status": "not_applicable", "note": "Not requested"},
            "device_or_ip_signal": {"status": "present", "note": "Location mismatch detected"},
            "receiver_trace": {"status": trace_status, "note": f"Receiver API mode: {fail_mode}"},
            "retry_history": {"status": retry_status, "note": f"{retries} retries logged"}
        }
    }
    
    # 5. Linked Case Signals
    case_data["linked_case_signals"] = {
        "same_receiver_seen_before": {"active": True, "note": "Receiver RCV-7781 seen in 2 other disputes."},
        "similar_amount_pattern": {"active": False, "note": "Amount does not match known burst patterns."},
        "retry_failure_cluster": {"active": retries >= 3, "note": "Multiple API failures to this receiver bank today."},
        "possible_mule_account_pattern": {"active": True, "note": "Instant payment followed by immediate withdrawal."}
    }
