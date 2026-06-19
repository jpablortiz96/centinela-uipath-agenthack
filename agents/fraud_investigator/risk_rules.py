def evaluate_risk(amount_cop: float, evidence_quality: str, receiver_trace_status: str, trace_data: dict = None):
    risk_score = 0
    explanation = []
    
    # 1. Amount
    if amount_cop >= 1000000:
        risk_score += 40
        explanation.append(f"High transaction amount: {amount_cop} COP.")
    else:
        risk_score += 10
        explanation.append(f"Normal transaction amount: {amount_cop} COP.")
        
    # 2. Evidence
    if evidence_quality == "unreadable":
        risk_score += 30
        explanation.append("Provided evidence is unreadable.")
    elif evidence_quality == "missing":
        risk_score += 40
        explanation.append("No evidence provided.")
    else:
        explanation.append("Evidence is clear and readable.")
        
    # 3. Receiver Trace
    if receiver_trace_status != "success":
        risk_score += 30
        explanation.append(f"Receiver bank API check failed or timed out (Status: {receiver_trace_status}).")
    elif trace_data and trace_data.get("status") == "flagged":
        risk_score += 40
        explanation.append(f"Receiver bank flagged the transaction: {trace_data.get('notes', 'Suspicious activity')}")
    else:
        explanation.append("Receiver bank confirmed the transaction without flags.")
        
    # Normalize risk score to 0-100
    risk_score = min(max(risk_score, 0), 100)
    
    # Determine risk level
    if risk_score >= 80:
        risk_level = "critical"
    elif risk_score >= 60:
        risk_level = "high"
    elif risk_score >= 30:
        risk_level = "medium"
    else:
        risk_level = "low"
        
    return risk_score, risk_level, explanation

def determine_action(risk_level: str, receiver_trace_status: str, evidence_quality: str):
    human_review_required = False
    
    if receiver_trace_status != "success":
        recommended_action = "retry_receiver_bank_trace"
        human_review_required = True
    elif risk_level in ["high", "critical"]:
        if evidence_quality in ["unreadable", "missing"]:
            recommended_action = "request_more_evidence"
            human_review_required = True
        else:
            recommended_action = "request_funds_freeze"
            human_review_required = True
    elif risk_level == "medium":
        recommended_action = "escalate_to_human_analyst"
        human_review_required = True
    else:
        recommended_action = "approve_low_value_refund"
        
    return recommended_action, human_review_required
