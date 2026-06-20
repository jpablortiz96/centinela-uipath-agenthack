from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os

app = FastAPI(title="Chaos Console Backend")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

ORCHESTRATOR_URL = "http://127.0.0.1:8040"
CORE_URL = "http://127.0.0.1:8010"
RECEIVER_URL = "http://127.0.0.1:8020"
FRAUD_INV_URL = "http://127.0.0.1:8030"

class HumanDecisionRequest(BaseModel):
    decision: str
    analyst: str
    notes: str

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "chaos-console"}

@app.get("/api/services/health")
def check_services_health():
    services = {
        "core_banking": CORE_URL,
        "receiver_bank": RECEIVER_URL,
        "fraud_investigator": FRAUD_INV_URL,
        "case_orchestrator": ORCHESTRATOR_URL
    }
    status = {}
    for name, url in services.items():
        try:
            r = requests.get(f"{url}/health", timeout=2)
            status[name] = "ok" if r.status_code == 200 else "error"
        except Exception:
            status[name] = "down"
    return status

@app.post("/api/scenarios/normal")
def run_normal_scenario():
    payload = {
        "customer_id": "CUST-001",
        "transaction_id": "TX-001",
        "amount_cop": 780000,
        "evidence_quality": "clear",
        "reported_reason": "Customer reports unauthorized instant payment",
        "simulate_receiver_failure": "none"
    }
    return execute_scenario(payload)

@app.post("/api/scenarios/receiver-conflict")
def run_conflict_scenario():
    payload = {
        "customer_id": "CUST-001",
        "transaction_id": "TX-002",
        "amount_cop": 2400000,
        "evidence_quality": "clear",
        "reported_reason": "Customer reports unauthorized high-value instant payment with inconsistent receiver information",
        "simulate_receiver_failure": "conflicting_response"
    }
    return execute_scenario(payload)

@app.post("/api/scenarios/receiver-api-down")
def run_api_down_scenario():
    payload = {
        "customer_id": "CUST-001",
        "transaction_id": "TX-003",
        "amount_cop": 1200000,
        "evidence_quality": "clear",
        "reported_reason": "Customer reports unauthorized instant payment and receiver bank is unavailable",
        "simulate_receiver_failure": "api_down"
    }
    return execute_scenario(payload)

def execute_scenario(payload):
    try:
        # Start case
        r_start = requests.post(f"{ORCHESTRATOR_URL}/cases/start", json=payload, timeout=5)
        r_start.raise_for_status()
        case_id = r_start.json().get("case_id")
        
        # Run case
        r_run = requests.post(f"{ORCHESTRATOR_URL}/cases/{case_id}/run", timeout=10)
        r_run.raise_for_status()
        return r_run.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cases/{case_id}/human-decision")
def submit_human_decision(case_id: str, req: HumanDecisionRequest):
    try:
        r = requests.post(f"{ORCHESTRATOR_URL}/cases/{case_id}/human-decision", json=req.model_dump(), timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cases/{case_id}/export")
def export_audit(case_id: str):
    try:
        r = requests.get(f"{ORCHESTRATOR_URL}/cases/{case_id}/export", timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
