import json
import os
from typing import Dict, Any, List
from datetime import datetime

AUDIT_FILE = "runtime_data/audit.jsonl"

def init_audit_store():
    os.makedirs(os.path.dirname(AUDIT_FILE), exist_ok=True)
    if not os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, "w") as f:
            pass

def log_event(case_id: str, event_type: str, details: Dict[str, Any]):
    event = {
        "case_id": case_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "details": details
    }
    with open(AUDIT_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

def get_case_audit(case_id: str) -> List[Dict[str, Any]]:
    if not os.path.exists(AUDIT_FILE):
        return []
    events = []
    with open(AUDIT_FILE, "r") as f:
        for line in f:
            if line.strip():
                evt = json.loads(line)
                if evt.get("case_id") == case_id:
                    events.append(evt)
    return events
