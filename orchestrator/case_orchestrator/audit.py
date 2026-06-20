import os
from datetime import datetime, timezone
from orchestrator.case_orchestrator.schemas import AuditEvent

LOG_FILE = "evidence/logs/case_orchestrator_runs.jsonl"

def create_audit_event(case_id: str, stage: str, actor: str, event_name: str, details: dict) -> AuditEvent:
    event = AuditEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        case_id=case_id,
        stage=stage,
        actor=actor,
        event=event_name,
        details=details
    )
    
    # Append to file
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(event.model_dump_json() + "\n")
    except Exception as e:
        print(f"Failed to write audit log: {e}")
        
    return event
