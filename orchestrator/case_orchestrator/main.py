from fastapi import FastAPI, HTTPException
import requests
import uuid
from orchestrator.case_orchestrator.schemas import CaseStartRequest, HumanDecisionRequest, CaseState
from orchestrator.case_orchestrator.case_store import get_case, save_case
from orchestrator.case_orchestrator.audit import create_audit_event

app = FastAPI(title="Case Orchestrator Service")

CORE_URL = "http://127.0.0.1:8010"
FRAUD_INV_URL = "http://127.0.0.1:8030"

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "case-orchestrator"}

@app.post("/cases/start", response_model=CaseState)
def start_case(req: CaseStartRequest):
    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
    
    case = CaseState(
        case_id=case_id,
        customer_id=req.customer_id,
        transaction_id=req.transaction_id,
        amount_cop=req.amount_cop,
        evidence_quality=req.evidence_quality,
        reported_reason=req.reported_reason,
        simulate_receiver_failure=req.simulate_receiver_failure,
        current_stage="intake",
        status="open",
        audit_events=[]
    )
    
    # Audit Event
    case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "case_started", req.model_dump()))
    
    # Try calling Core Banking API
    try:
        core_payload = {
            "customer_id": case.customer_id,
            "transaction_id": case.transaction_id,
            "reported_reason": case.reported_reason,
            "evidence_items": ["uploaded_evidence.jpg"]
        }
        resp = requests.post(f"{CORE_URL}/disputes", json=core_payload, timeout=5)
        if resp.status_code == 200:
            case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "core_dispute_created", resp.json()))
        else:
            case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "core_dispute_creation_failed", {"status": resp.status_code}))
    except Exception as e:
        case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "core_api_error", {"error": str(e)}))

    save_case(case)
    return case

@app.post("/cases/{case_id}/run", response_model=CaseState)
def run_case(case_id: str):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if case.current_stage not in ["intake", "evidence_review"]:
        raise HTTPException(status_code=400, detail=f"Cannot run from stage {case.current_stage}")

    # Move to Evidence Review
    case.current_stage = "evidence_review"
    case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "stage_transition", {"to": "evidence_review"}))
    
    # Move to Investigation
    case.current_stage = "investigation"
    case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "stage_transition", {"to": "investigation"}))
    
    # Call Fraud Investigator
    try:
        inv_payload = {
            "case_id": case.case_id,
            "customer_id": case.customer_id,
            "transaction_id": case.transaction_id,
            "amount_cop": case.amount_cop,
            "evidence_quality": case.evidence_quality,
            "reported_reason": case.reported_reason,
            "simulate_receiver_failure": case.simulate_receiver_failure
        }
        resp = requests.post(f"{FRAUD_INV_URL}/investigate-and-freeze", json=inv_payload, timeout=10)
        
        if resp.status_code == 200:
            inv_result = resp.json()
            case.investigation_result = inv_result
            case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "investigation_completed", {"risk_level": inv_result.get("risk_level")}))
            
            if inv_result.get("human_review_required"):
                case.current_stage = "human_decision"
                case.status = "waiting_for_human"
                case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "stage_transition", {"to": "human_decision"}))
            else:
                case.current_stage = "resolution"
                case.status = "auto_resolved"
                case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "stage_transition", {"to": "resolution", "action": inv_result.get("recommended_action")}))
        else:
            case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "investigation_api_failed", {"status": resp.status_code}))
    except Exception as e:
        case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "investigation_api_error", {"error": str(e)}))

    save_case(case)
    return case

@app.post("/cases/{case_id}/human-decision", response_model=CaseState)
def human_decision(case_id: str, req: HumanDecisionRequest):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if case.current_stage != "human_decision":
        raise HTTPException(status_code=400, detail="Case is not waiting for human decision")
        
    valid_decisions = ["approve_refund", "reject_refund", "request_more_evidence", "escalate_fraud_ops"]
    if req.decision not in valid_decisions:
        raise HTTPException(status_code=400, detail="Invalid decision")
        
    case.human_decision = req.model_dump()
    case.audit_events.append(create_audit_event(case_id, case.current_stage, req.analyst, "human_decision_submitted", case.human_decision))
    
    if req.decision == "request_more_evidence":
        case.current_stage = "evidence_review"
        case.status = "open"
        case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "stage_transition", {"to": "evidence_review"}))
    else:
        case.current_stage = "resolution"
        case.status = "resolved_by_human"
        case.audit_events.append(create_audit_event(case_id, case.current_stage, "orchestrator", "stage_transition", {"to": "resolution"}))
        
    save_case(case)
    return case

@app.get("/cases/{case_id}", response_model=CaseState)
def get_case_state(case_id: str):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.get("/cases/{case_id}/audit")
def get_case_audit(case_id: str):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.audit_events

@app.get("/cases/{case_id}/export")
def export_audit(case_id: str):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    export_data = {
        "case_id": case.case_id,
        "status": case.status,
        "current_stage": case.current_stage,
        "final_decision": case.human_decision.get("decision") if case.human_decision else (case.investigation_result.get("recommended_action") if case.investigation_result else "none"),
        "investigation_summary": case.investigation_result.get("explanation") if case.investigation_result else [],
        "human_decision": case.human_decision,
        "timeline": [
            f"{evt.timestamp} | {evt.actor} | {evt.event}" for evt in case.audit_events
        ],
        "limitations_notice": "This is a synthetic audit trail from a local Orchestrator simulation. It is not connected to UiPath Maestro Case yet."
    }
    return export_data
