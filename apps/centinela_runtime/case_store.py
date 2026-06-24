import json
import os
from typing import Dict, Any, List

STORE_FILE = "runtime_data/cases.jsonl"

def init_store():
    os.makedirs(os.path.dirname(STORE_FILE), exist_ok=True)
    if not os.path.exists(STORE_FILE):
        with open(STORE_FILE, "w") as f:
            pass

def save_case(case_data: Dict[str, Any]):
    # Read all, update or append, then write all to keep it simple
    cases = get_all_cases()
    found = False
    for i, c in enumerate(cases):
        if c["case_id"] == case_data["case_id"]:
            cases[i] = case_data
            found = True
            break
    if not found:
        cases.append(case_data)
        
    with open(STORE_FILE, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

def get_case(case_id: str) -> Dict[str, Any]:
    for c in get_all_cases():
        if c["case_id"] == case_id:
            return c
    return None

def get_all_cases() -> List[Dict[str, Any]]:
    if not os.path.exists(STORE_FILE):
        return []
    cases = []
    with open(STORE_FILE, "r") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    return cases
