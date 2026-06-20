import requests
import sys

ORCH_URL = "http://127.0.0.1:8040"

def print_result(name, passed):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] - {name}")

def main():
    print("--- Running Smoke Tests for Case Orchestrator ---")
    
    # 1. Health Check
    try:
        r_health = requests.get(f"{ORCH_URL}/health")
        print_result("Orchestrator Health", r_health.status_code == 200)
    except requests.exceptions.ConnectionError:
        print_result("Orchestrator Health (Connection Error)", False)
        print("   -> Make sure Case Orchestrator is running on port 8040")
        sys.exit(1)
        
    # 2. Start a normal case
    try:
        payload_normal = {
            "customer_id": "CUST-NOR",
            "transaction_id": "TX-NOR",
            "amount_cop": 500000,
            "evidence_quality": "clear",
            "reported_reason": "Unauthorized transaction",
            "simulate_receiver_failure": "none"
        }
        r_start = requests.post(f"{ORCH_URL}/cases/start", json=payload_normal)
        case_id = r_start.json().get("case_id")
        passed = (r_start.status_code == 200 and case_id is not None)
        print_result("Start Normal Case", passed)
        
        # 3. Run the case
        r_run = requests.post(f"{ORCH_URL}/cases/{case_id}/run")
        passed_run = (r_run.status_code == 200 and r_run.json().get("status") == "auto_resolved")
        print_result("Run Normal Case (Auto Resolved)", passed_run)
    except Exception as e:
        print_result(f"Normal Case Flow Error: {e}", False)

    # 4. Start a high-risk case
    try:
        payload_high = {
            "customer_id": "CUST-HIGH",
            "transaction_id": "TX-HIGH",
            "amount_cop": 2500000,
            "evidence_quality": "clear",
            "reported_reason": "Unauthorized transaction",
            "simulate_receiver_failure": "conflicting_response"
        }
        r_start_high = requests.post(f"{ORCH_URL}/cases/start", json=payload_high)
        high_case_id = r_start_high.json().get("case_id")
        print_result("Start High-Risk Case", r_start_high.status_code == 200)
        
        # 5. Run high-risk case and verify it waits for human
        r_run_high = requests.post(f"{ORCH_URL}/cases/{high_case_id}/run")
        passed_run_high = (r_run_high.status_code == 200 and r_run_high.json().get("status") == "waiting_for_human")
        print_result("Run High-Risk Case (Waits for Human)", passed_run_high)
        
        # 6. Submit human decision
        decision_payload = {
            "decision": "approve_refund",
            "analyst": "human-analyst-demo",
            "notes": "Refund approved after manual review."
        }
        r_dec = requests.post(f"{ORCH_URL}/cases/{high_case_id}/human-decision", json=decision_payload)
        passed_dec = (r_dec.status_code == 200 and r_dec.json().get("status") == "resolved_by_human")
        print_result("Submit Human Decision", passed_dec)
        
        # 7. Export audit
        r_export = requests.get(f"{ORCH_URL}/cases/{high_case_id}/export")
        passed_exp = (r_export.status_code == 200 and "timeline" in r_export.json())
        print_result("Export Audit", passed_exp)
        
    except Exception as e:
        print_result(f"High-Risk Case Flow Error: {e}", False)

if __name__ == "__main__":
    main()
