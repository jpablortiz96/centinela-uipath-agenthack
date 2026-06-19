from fastapi import FastAPI
import requests
from datetime import datetime, timezone
from agents.fraud_investigator.schemas import InvestigationRequest, InvestigationResponse, AuditEvent
from agents.fraud_investigator.risk_rules import evaluate_risk, determine_action

app = FastAPI(title="Fraud Investigator Agent")

CORE_URL = "http://127.0.0.1:8010"
RECEIVER_URL = "http://127.0.0.1:8020"

def create_audit_event(event_name: str, details: dict):
    return AuditEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        actor="fraud-investigator-agent",
        event=event_name,
        details=details
    )

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "fraud-investigator-agent"}

@app.post("/investigate", response_model=InvestigationResponse)
def investigate(req: InvestigationRequest):
    return run_investigation(req, freeze_if_high_risk=False)

@app.post("/investigate-and-freeze", response_model=InvestigationResponse)
def investigate_and_freeze(req: InvestigationRequest):
    return run_investigation(req, freeze_if_high_risk=True)

def run_investigation(req: InvestigationRequest, freeze_if_high_risk: bool):
    audit_events = [create_audit_event("investigation_started", {"case_id": req.case_id, "amount_cop": req.amount_cop})]
    
    # 1. Get Transaction from Core Banking API
    receiver_bank = "UNKNOWN"
    receiver_account = "UNKNOWN"
    try:
        core_resp = requests.get(f"{CORE_URL}/transactions/{req.transaction_id}", timeout=5)
        core_resp.raise_for_status()
        txn_data = core_resp.json()
        receiver_bank = txn_data.get("receiver_bank", "UNKNOWN")
        receiver_account = txn_data.get("receiver_account", "UNKNOWN")
        audit_events.append(create_audit_event("core_banking_check_success", {"transaction_id": req.transaction_id}))
    except Exception as e:
        audit_events.append(create_audit_event("core_banking_check_failed", {"error": str(e)}))
        
    # 2. Trace Transfer at Receiver Bank API
    trace_status = "success"
    trace_data = None
    try:
        trace_payload = {
            "transaction_id": req.transaction_id,
            "amount_cop": req.amount_cop,
            "receiver_bank": receiver_bank,
            "simulate_failure": req.simulate_receiver_failure
        }
        trace_resp = requests.post(f"{RECEIVER_URL}/trace-transfer", json=trace_payload, timeout=5)
        if trace_resp.status_code == 200:
            trace_data = trace_resp.json()
            audit_events.append(create_audit_event("receiver_bank_trace_success", trace_data))
        else:
            trace_status = f"failed_http_{trace_resp.status_code}"
            audit_events.append(create_audit_event("receiver_bank_trace_failed", {"status_code": trace_resp.status_code}))
    except Exception as e:
        trace_status = "error_or_timeout"
        audit_events.append(create_audit_event("receiver_bank_trace_error", {"error": str(e)}))
        
    # 3. Calculate Risk
    risk_score, risk_level, explanation = evaluate_risk(req.amount_cop, req.evidence_quality, trace_status, trace_data)
    audit_events.append(create_audit_event("risk_evaluated", {"risk_score": risk_score, "risk_level": risk_level}))
    
    # 4. Determine Action
    recommended_action, human_review_required = determine_action(risk_level, trace_status, req.evidence_quality)
    audit_events.append(create_audit_event("action_determined", {
        "recommended_action": recommended_action, 
        "human_review_required": human_review_required
    }))
    
    # 5. Freeze Funds if required
    freeze_response = None
    if freeze_if_high_risk and risk_level in ["high", "critical"] and trace_status == "success":
        try:
            freeze_payload = {
                "transaction_id": req.transaction_id,
                "receiver_account": receiver_account,
                "amount_cop": req.amount_cop,
                "risk_level": risk_level
            }
            freeze_resp = requests.post(f"{RECEIVER_URL}/freeze-funds", json=freeze_payload, timeout=5)
            if freeze_resp.status_code == 200:
                freeze_response = freeze_resp.json()
                audit_events.append(create_audit_event("funds_freeze_requested", freeze_response))
            else:
                audit_events.append(create_audit_event("funds_freeze_failed", {"status_code": freeze_resp.status_code}))
        except Exception as e:
            audit_events.append(create_audit_event("funds_freeze_error", {"error": str(e)}))

    audit_events.append(create_audit_event("investigation_completed", {"case_id": req.case_id}))
    
    return InvestigationResponse(
        case_id=req.case_id,
        transaction_id=req.transaction_id,
        risk_score=risk_score,
        risk_level=risk_level,
        recommended_action=recommended_action,
        human_review_required=human_review_required,
        receiver_trace_status=trace_status,
        audit_events=audit_events,
        explanation=explanation,
        freeze_response=freeze_response
    )
