import requests
import sys

CONSOLE_URL = "http://127.0.0.1:8050"

def print_result(name, passed):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] - {name}")

def main():
    print("--- Running Smoke Tests for Chaos Console ---")
    
    # 1. Health Check
    try:
        r_health = requests.get(f"{CONSOLE_URL}/health")
        print_result("Chaos Console Health", r_health.status_code == 200)
    except requests.exceptions.ConnectionError:
        print_result("Chaos Console Health (Connection Error)", False)
        print("   -> Make sure Chaos Console is running on port 8050")
        sys.exit(1)
        
    # 2. Services Health
    try:
        r_svc = requests.get(f"{CONSOLE_URL}/api/services/health")
        print_result("Services Health Check Proxy", r_svc.status_code == 200)
    except Exception as e:
        print_result(f"Services Health Proxy Error: {e}", False)

    # 3. Normal Scenario
    try:
        r_norm = requests.post(f"{CONSOLE_URL}/api/scenarios/normal")
        passed = (r_norm.status_code == 200 and r_norm.json().get("status") == "auto_resolved")
        print_result("Normal Case Scenario", passed)
    except Exception as e:
        print_result(f"Normal Scenario Error: {e}", False)

    # 4. Conflict Scenario
    high_case_id = None
    try:
        r_conf = requests.post(f"{CONSOLE_URL}/api/scenarios/receiver-conflict")
        high_case_id = r_conf.json().get("case_id")
        passed = (r_conf.status_code == 200 and r_conf.json().get("status") == "waiting_for_human")
        print_result("Receiver Conflict Scenario", passed)
    except Exception as e:
        print_result(f"Conflict Scenario Error: {e}", False)

    # 5. Human Decision
    if high_case_id:
        try:
            payload = {
                "decision": "approve_refund",
                "analyst": "human-analyst-demo",
                "notes": "Refund approved."
            }
            r_dec = requests.post(f"{CONSOLE_URL}/api/cases/{high_case_id}/human-decision", json=payload)
            passed = (r_dec.status_code == 200 and r_dec.json().get("status") == "resolved_by_human")
            print_result("Human Decision (Approve Refund)", passed)
        except Exception as e:
            print_result(f"Human Decision Error: {e}", False)
            
    # 6. Export Audit
    if high_case_id:
        try:
            r_exp = requests.get(f"{CONSOLE_URL}/api/cases/{high_case_id}/export")
            passed = (r_exp.status_code == 200 and "timeline" in r_exp.json())
            print_result("Export Audit", passed)
        except Exception as e:
            print_result(f"Export Audit Error: {e}", False)

if __name__ == "__main__":
    main()
