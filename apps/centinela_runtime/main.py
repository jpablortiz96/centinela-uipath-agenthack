import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Any, Dict, Optional

from .schemas import (
    CaseCreateInput, HumanDecisionInput, CaseState, 
    UiPathRunInvestigationInput, UiPathHumanDecisionInput, 
    UiPathCompactOutput, AuditExportOutput
)
from .case_store import init_store, save_case, get_case, get_all_cases
from .audit_store import init_audit_store, log_event, get_case_audit
from .services.case_management import process_investigation, process_human_decision

app = FastAPI(
    title="CENTINELA Runtime API",
    description="Deployable backend runtime for UiPath Maestro Case integration.",
    version="1.0.0"
)

import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
def startup_event():
    init_store()
    init_audit_store()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "centinela-runtime-api"}

@app.post("/cases", response_model=CaseState)
def create_case(input_data: CaseCreateInput):
    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
    case_data = input_data.dict()
    case_data["case_id"] = case_id
    case_data["status"] = "new"
    case_data["current_stage"] = "Intake"
    
    save_case(case_data)
    log_event(case_id, "CaseCreated", case_data)
    
    return case_data

@app.post("/cases/{case_id}/run-investigation", response_model=CaseState)
def run_investigation(case_id: str):
    case_data = get_case(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found")
        
    return process_investigation(case_data)

@app.post("/cases/{case_id}/human-decision", response_model=CaseState)
def human_decision(case_id: str, input_data: HumanDecisionInput):
    case_data = get_case(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found")
        
    valid_decisions = ["approve_refund", "reject_refund", "request_more_evidence", "escalate_fraud_ops"]
    if input_data.decision not in valid_decisions:
        raise HTTPException(status_code=400, detail="Invalid decision")
        
    return process_human_decision(case_data, input_data.decision, input_data.analyst, input_data.notes)

@app.get("/cases/{case_id}", response_model=CaseState)
def get_case_state(case_id: str):
    case_data = get_case(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found")
    return case_data

@app.get("/cases/{case_id}/audit")
def get_audit(case_id: str):
    return get_case_audit(case_id)

@app.get("/cases/{case_id}/export", response_model=AuditExportOutput)
def export_case(case_id: str):
    case_data = get_case(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found")
    audit = get_case_audit(case_id)
    
    return {
        "case_id": case_data["case_id"],
        "status": case_data["status"],
        "current_stage": case_data["current_stage"],
        "risk_score": case_data.get("risk_score"),
        "risk_level": case_data.get("risk_level"),
        "recommended_action": case_data.get("recommended_action"),
        "human_decision": case_data.get("human_decision"),
        "case_summary": {
            "customer_id": case_data.get("customer_id"),
            "transaction_id": case_data.get("transaction_id"),
            "amount_cop": case_data.get("amount_cop")
        },
        "risk_summary": {
            "evidence_quality": case_data.get("evidence_quality"),
            "risk_score": case_data.get("risk_score"),
            "risk_level": case_data.get("risk_level")
        },
        "policy_summary": {
            "policy_result": case_data.get("policy_result"),
            "policy_reasons": case_data.get("policy_reasons", []),
            "required_human_gate": case_data.get("required_human_gate")
        },
        "sla_summary": {
            "sla_target_minutes": case_data.get("sla_target_minutes"),
            "elapsed_minutes": case_data.get("elapsed_minutes"),
            "sla_status": case_data.get("sla_status"),
            "stage_sla_status": case_data.get("stage_sla_status")
        },
        "analyst_brief": case_data.get("analyst_brief"),
        "evidence_summary": case_data.get("evidence_summary"),
        "risk_explanation": case_data.get("risk_explanation"),
        "recommended_questions_for_analyst": case_data.get("recommended_questions_for_analyst"),
        "allowed_decisions": case_data.get("allowed_decisions"),
        "customer_response_draft": case_data.get("customer_response_draft"),
        "timeline": audit,
        "limitations_notice": "This is a deterministic runtime for UiPath integration. Not a production banking API."
    }

# UiPath-friendly endpoints

def get_latest_uipath_waiting_case() -> Optional[Dict[str, Any]]:
    cases = get_all_cases()
    if not cases:
        return None
        
    # Prefer uipath-maestro, then uipath
    for case in reversed(cases):
        if case.get("status") == "waiting_for_human" and "uipath" in case.get("source", ""):
            return case
    return None

def to_uipath_compact(case_data: Dict[str, Any]) -> UiPathCompactOutput:
    audit = get_case_audit(case_data["case_id"])
    return {
        "case_id": case_data["case_id"],
        "status": case_data["status"],
        "current_stage": case_data["current_stage"],
        "risk_score": case_data.get("risk_score"),
        "risk_level": case_data.get("risk_level"),
        "recommended_action": case_data.get("recommended_action"),
        "human_review_required": case_data["status"] == "waiting_for_human",
        "next_required_action": "human_decision" if case_data["status"] == "waiting_for_human" else "none",
        "audit_event_count": len(audit)
    }

@app.post("/uipath/start-fraud-dispute", response_model=CaseState)
def uipath_start_dispute(input_data: CaseCreateInput):
    input_data.source = "uipath"
    return create_case(input_data)

@app.post("/uipath/run-investigation", response_model=UiPathCompactOutput)
def uipath_run_investigation(input_data: UiPathRunInvestigationInput):
    case_data = get_case(input_data.case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found")
    case_data = process_investigation(case_data)
    return to_uipath_compact(case_data)

@app.post("/uipath/submit-human-decision", response_model=UiPathCompactOutput)
def uipath_human_decision(input_data: UiPathHumanDecisionInput):
    case_data = get_case(input_data.case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found")
        
    case_data = process_human_decision(case_data, input_data.decision, input_data.analyst, input_data.notes)
    return to_uipath_compact(case_data)

@app.get("/uipath/export/{case_id}", response_model=AuditExportOutput)
def uipath_export(case_id: str):
    return export_case(case_id)

from fastapi import Request
from .schemas import UiPathMaestroOutput

@app.post("/uipath/maestro-investigation", response_model=UiPathMaestroOutput)
def uipath_maestro_investigation(input_data: CaseCreateInput, request: Request):
    input_data.source = "uipath-maestro"
    
    # 1. Create case
    case_data = create_case(input_data)
    
    # 2. Run investigation
    case_data = process_investigation(case_data)
    
    # 3. Compact output
    compact = to_uipath_compact(case_data)
    
    # 4. Message
    msg = "Investigation completed. Human decision required." if compact["human_review_required"] else "Investigation completed. Case auto-resolved."
    
    return {
        **compact,
        "runtime_url": str(request.base_url).rstrip('/'),
        "message": msg
    }

@app.get("/uipath/maestro-export/{case_id}", response_model=AuditExportOutput)
def uipath_maestro_export(case_id: str):
    return export_case(case_id)

@app.get("/uipath/maestro-investigation-default", response_model=UiPathMaestroOutput)
def uipath_maestro_investigation_default():
    input_data = CaseCreateInput(
        customer_id="CUST-001",
        transaction_id="TX-MAESTRO-DEFAULT-001",
        amount_cop=2400000,
        evidence_quality="clear",
        reported_reason="Customer reports unauthorized high-value instant payment with inconsistent receiver information",
        simulate_receiver_failure="conflicting_response",
        source="uipath-maestro"
    )
    
    # 1. Create case
    case_data = create_case(input_data)
    
    # 2. Run investigation
    case_data = process_investigation(case_data)
    
    # 3. Compact output
    compact = to_uipath_compact(case_data)
    
    # 4. Message
    msg = "Investigation completed. Human decision required." if compact["human_review_required"] else "Investigation completed. Case auto-resolved."
    
    return {
        **compact,
        "message": msg
    }

def apply_maestro_decision(decision: str, notes: str):
    case_data = get_latest_uipath_waiting_case()
    if not case_data:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={
            "error": "Not Found",
            "message": "No case found waiting for human decision.",
            "suggested_action": "Run /uipath/maestro-investigation-default or /uipath/maestro-api-down-default first."
        })
        
    case_data = process_human_decision(
        case_data, 
        decision=decision, 
        analyst="uipath-maestro-human-analyst", 
        notes=notes
    )
    compact = to_uipath_compact(case_data)
    
    return {
        **compact,
        "human_decision": case_data.get("human_decision"),
        "message": f"Applied decision {decision} from UiPath Maestro."
    }

@app.get("/uipath/maestro-approve-latest")
def uipath_maestro_approve_latest():
    return apply_maestro_decision("approve_refund", "Approved from UiPath Maestro Resolution stage after human review.")

@app.get("/uipath/maestro-reject-latest")
def uipath_maestro_reject_latest():
    return apply_maestro_decision("reject_refund", "Rejected from UiPath Maestro Resolution stage after human review.")

@app.get("/uipath/maestro-request-more-evidence-latest")
def uipath_maestro_request_more_evidence_latest():
    return apply_maestro_decision("request_more_evidence", "Requested more evidence from UiPath Maestro Evidence Review stage.")

@app.get("/uipath/maestro-escalate-latest")
def uipath_maestro_escalate_latest():
    return apply_maestro_decision("escalate_fraud_ops", "Escalated to fraud ops from UiPath Maestro Human Decision stage.")

@app.get("/uipath/maestro-export-latest")
def uipath_maestro_export_latest():
    cases = get_all_cases()
    if not cases:
        raise HTTPException(status_code=404, detail="No cases found")
    
    # Find latest uipath case
    for case in reversed(cases):
        if "uipath" in case.get("source", ""):
            return export_case(case["case_id"])
            
    # Fallback to the last case if no uipath case
    latest_case_id = cases[-1]["case_id"]
    return export_case(latest_case_id)

@app.get("/uipath/maestro-api-down-default", response_model=UiPathMaestroOutput)
def uipath_maestro_api_down_default():
    input_data = CaseCreateInput(
        customer_id="CUST-002",
        transaction_id="TX-MAESTRO-APIDOWN-001",
        amount_cop=500000,
        evidence_quality="high",
        reported_reason="Testing receiver bank API down scenario.",
        simulate_receiver_failure="api_down",
        source="uipath-maestro-test"
    )
    
    # 1. Create case
    case_data = create_case(input_data)
    
    # 2. Run investigation (which will retry 3 times and fail)
    case_data = process_investigation(case_data)
    
    # 3. Compact output
    compact = to_uipath_compact(case_data)
    
    # 4. Message
    msg = "Investigation completed. Human decision required." if compact["human_review_required"] else "Investigation completed. Case auto-resolved."
    
    return {
        **compact,
        "message": msg
    }

# Analyst Console Endpoints

@app.get("/analyst", response_class=HTMLResponse)
def analyst_console():
    with open(os.path.join(static_dir, "analyst.html"), "r") as f:
        return f.read()

@app.get("/api/analyst/cases")
def analyst_get_cases():
    cases = get_all_cases()
    # newest first
    reversed_cases = reversed(cases)
    result = []
    for c in reversed_cases:
        result.append({
            "case_id": c.get("case_id"),
            "status": c.get("status"),
            "current_stage": c.get("current_stage"),
            "customer_id": c.get("customer_id"),
            "transaction_id": c.get("transaction_id"),
            "amount_cop": c.get("amount_cop"),
            "risk_score": c.get("risk_score"),
            "risk_level": c.get("risk_level"),
            "human_decision": c.get("human_decision"),
            "created_at": c.get("created_at"),
            "source": c.get("source")
        })
    return result

@app.get("/api/analyst/cases/{case_id}")
def analyst_get_case(case_id: str):
    return export_case(case_id)

@app.get("/api/analyst/latest")
def analyst_get_latest():
    cases = get_all_cases()
    if not cases:
        raise HTTPException(status_code=404, detail="No cases found")
    return export_case(cases[-1]["case_id"])

@app.get("/api/analyst/export-latest")
def analyst_export_latest():
    return uipath_maestro_export_latest()

@app.get("/api/analyst/run-api-down-case")
def analyst_run_api_down():
    return uipath_maestro_api_down_default()

@app.get("/api/analyst/approve-latest")
def analyst_approve_latest():
    return uipath_maestro_approve_latest()
