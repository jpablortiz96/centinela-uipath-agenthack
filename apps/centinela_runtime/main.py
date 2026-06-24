import uuid
from fastapi import FastAPI, HTTPException
from typing import Any, Dict

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
        "timeline": audit,
        "limitations_notice": "This is a deterministic runtime for UiPath integration. Not a production banking API."
    }

# UiPath-friendly endpoints

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
