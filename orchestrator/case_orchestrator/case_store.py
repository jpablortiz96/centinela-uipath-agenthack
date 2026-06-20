from typing import Dict
from orchestrator.case_orchestrator.schemas import CaseState

# In-memory store
cases_db: Dict[str, CaseState] = {}

def get_case(case_id: str) -> CaseState:
    return cases_db.get(case_id)

def save_case(case: CaseState):
    cases_db[case.case_id] = case
