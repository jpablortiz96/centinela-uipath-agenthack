import requests
import sys
import time

CORE_URL = "http://127.0.0.1:8010"
RECEIVER_URL = "http://127.0.0.1:8020"

def print_result(name, passed):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] - {name}")

def main():
    print("--- Running Smoke Tests for CENTINELA Mock APIs ---")
    
    # 1. Health Checks
    try:
        r_core = requests.get(f"{CORE_URL}/health")
        print_result("Core Banking API Health", r_core.status_code == 200)
    except requests.exceptions.ConnectionError:
        print_result("Core Banking API Health (Connection Error)", False)
        print("   -> Make sure Core Banking API is running on port 8010")
        sys.exit(1)
        
    try:
        r_recv = requests.get(f"{RECEIVER_URL}/health")
        print_result("Receiver Bank API Health", r_recv.status_code == 200)
    except requests.exceptions.ConnectionError:
        print_result("Receiver Bank API Health (Connection Error)", False)
        print("   -> Make sure Receiver Bank API is running on port 8020")
        sys.exit(1)
        
    # 2. Normal Core Banking Flow
    try:
        # Create Dispute
        payload = {
            "customer_id": "CUST-123",
            "transaction_id": "TXN-999",
            "reported_reason": "unauthorized_transfer",
            "evidence_items": ["receipt_img_01.jpg"]
        }
        r_create = requests.post(f"{CORE_URL}/disputes", json=payload)
        passed_create = r_create.status_code == 200
        print_result("Create Dispute", passed_create)
        
        if passed_create:
            case_id = r_create.json().get("case_id")
            
            # Get Dispute
            r_get = requests.get(f"{CORE_URL}/disputes/{case_id}")
            print_result("Get Dispute", r_get.status_code == 200 and r_get.json().get("status") == "open")
            
            # Update Dispute
            r_update = requests.patch(f"{CORE_URL}/disputes/{case_id}/status", json={"status": "in_progress"})
            print_result("Update Dispute Status", r_update.status_code == 200 and r_update.json().get("status") == "in_progress")
    except Exception as e:
        print_result(f"Core Banking Flow Error: {e}", False)

    # 3. Normal Receiver Flow
    try:
        trace_payload = {
            "transaction_id": "TXN-999",
            "amount_cop": 1500000,
            "receiver_bank": "BANCO_DESTINO",
            "simulate_failure": "none"
        }
        r_trace = requests.post(f"{RECEIVER_URL}/trace-transfer", json=trace_payload)
        print_result("Receiver Bank Trace (Success)", r_trace.status_code == 200 and r_trace.json().get("status") == "credited")
    except Exception as e:
        print_result(f"Receiver Trace Normal Error: {e}", False)
        
    # 4. Receiver API Error Injection (api_down)
    try:
        trace_payload["simulate_failure"] = "api_down"
        r_trace_fail = requests.post(f"{RECEIVER_URL}/trace-transfer", json=trace_payload)
        print_result("Receiver Bank Trace (API Down)", r_trace_fail.status_code == 503)
    except Exception as e:
        print_result(f"Receiver Trace Error Injection Error: {e}", False)

if __name__ == "__main__":
    main()
