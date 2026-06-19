import requests
import sys

FRAUD_INV_URL = "http://127.0.0.1:8030"

def print_result(name, passed):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] - {name}")

def main():
    print("--- Running Smoke Tests for Fraud Investigator Agent ---")
    
    # 1. Health Check
    try:
        r_health = requests.get(f"{FRAUD_INV_URL}/health")
        print_result("Fraud Investigator Health", r_health.status_code == 200 and r_health.json().get("status") == "ok")
    except requests.exceptions.ConnectionError:
        print_result("Fraud Investigator Health (Connection Error)", False)
        print("   -> Make sure Fraud Investigator Agent is running on port 8030")
        sys.exit(1)
        
    # 2. Normal investigation
    try:
        payload = {
            "case_id": "CASE-100",
            "customer_id": "CUST-100",
            "transaction_id": "TX-100",
            "amount_cop": 500000,
            "evidence_quality": "clear",
            "reported_reason": "Unauthorized transaction",
            "simulate_receiver_failure": "none"
        }
        r_norm = requests.post(f"{FRAUD_INV_URL}/investigate", json=payload)
        passed = (r_norm.status_code == 200 and 
                  r_norm.json().get("risk_level") in ["low", "medium"] and
                  r_norm.json().get("receiver_trace_status") == "success")
        print_result("Normal Investigation (Clear Evidence)", passed)
    except Exception as e:
        print_result(f"Normal Investigation Error: {e}", False)

    # 3. Investigation with receiver API down
    try:
        payload_down = payload.copy()
        payload_down["simulate_receiver_failure"] = "api_down"
        r_down = requests.post(f"{FRAUD_INV_URL}/investigate", json=payload_down)
        passed = (r_down.status_code == 200 and 
                  r_down.json().get("human_review_required") == True and
                  r_down.json().get("recommended_action") == "retry_receiver_bank_trace")
        print_result("Investigation with Receiver API Down", passed)
    except Exception as e:
        print_result(f"Investigation API Down Error: {e}", False)

    # 4. Investigation-and-freeze
    try:
        payload_high = payload.copy()
        payload_high["amount_cop"] = 2500000 # High amount
        payload_high["simulate_receiver_failure"] = "conflicting_response" # + Conflict -> critical risk
        r_freeze = requests.post(f"{FRAUD_INV_URL}/investigate-and-freeze", json=payload_high)
        data = r_freeze.json()
        passed = (r_freeze.status_code == 200 and 
                  data.get("risk_level") in ["high", "critical"] and
                  data.get("freeze_response") is not None and
                  data.get("freeze_response").get("freeze_requested") == True)
        print_result("Investigation & Freeze (High Amount + Conflict)", passed)
    except Exception as e:
        print_result(f"Investigation & Freeze Error: {e}", False)

if __name__ == "__main__":
    main()
