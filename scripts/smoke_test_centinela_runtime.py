import requests
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8070")
    args = parser.parse_args()
    
    base_url = args.base_url
    print(f"Testing CENTINELA Runtime API at {base_url}")
    
    all_passed = True

    try:
        # 1. /health
        print("\n1. Testing /health...")
        r = requests.get(f"{base_url}/health")
        if r.status_code == 200 and r.json().get("status") == "ok":
            print("PASS")
        else:
            print("FAIL")
            all_passed = False

        # 2. POST /cases normal
        print("\n2. Testing POST /cases (normal)...")
        case_payload = {
            "customer_id": "CUST-001",
            "transaction_id": "TX-001",
            "amount_cop": 78000,
            "evidence_quality": "high",
            "reported_reason": "test",
            "simulate_receiver_failure": "none"
        }
        r = requests.post(f"{base_url}/cases", json=case_payload)
        if r.status_code == 200:
            case_id_normal = r.json().get("case_id")
            print("PASS", case_id_normal)
        else:
            print("FAIL", r.text)
            all_passed = False
            return

        # 3. POST /cases/{case_id}/run-investigation
        print(f"\n3. Testing POST /cases/{case_id_normal}/run-investigation...")
        r = requests.post(f"{base_url}/cases/{case_id_normal}/run-investigation")
        if r.status_code == 200 and r.json().get("status") == "auto_resolved":
            print("PASS")
        else:
            print("FAIL", r.text)
            all_passed = False

        # 4. POST /uipath/start-fraud-dispute high-risk conflict
        print("\n4. Testing POST /uipath/start-fraud-dispute (high-risk conflict)...")
        conflict_payload = {
            "customer_id": "CUST-002",
            "transaction_id": "TX-002",
            "amount_cop": 1500000,
            "evidence_quality": "high",
            "reported_reason": "high risk test",
            "simulate_receiver_failure": "conflicting_evidence"
        }
        r = requests.post(f"{base_url}/uipath/start-fraud-dispute", json=conflict_payload)
        if r.status_code == 200:
            case_id_conflict = r.json().get("case_id")
            print("PASS", case_id_conflict)
        else:
            print("FAIL", r.text)
            all_passed = False
            return

        # 5. POST /uipath/run-investigation
        print(f"\n5. Testing POST /uipath/run-investigation for {case_id_conflict}...")
        r = requests.post(f"{base_url}/uipath/run-investigation", json={"case_id": case_id_conflict})
        res = r.json()
        if r.status_code == 200:
            print("PASS")
            # 6. Verify it waits for human
            print("\n6. Verifying it waits for human...")
            if res.get("human_review_required") == True and res.get("status") == "waiting_for_human":
                print("PASS")
            else:
                print("FAIL", res)
                all_passed = False
        else:
            print("FAIL", r.text)
            all_passed = False

        # 7. POST /uipath/submit-human-decision approve_refund
        print("\n7. Testing POST /uipath/submit-human-decision approve_refund...")
        decision_payload = {
            "case_id": case_id_conflict,
            "decision": "approve_refund",
            "analyst": "smoke-test-analyst",
            "notes": "Approved via smoke test"
        }
        r = requests.post(f"{base_url}/uipath/submit-human-decision", json=decision_payload)
        if r.status_code == 200 and r.json().get("status") == "resolved_by_human":
            print("PASS")
        else:
            print("FAIL", r.text)
            all_passed = False

        # 8. GET /uipath/export/{case_id}
        print(f"\n8. Testing GET /uipath/export/{case_id_conflict}...")
        r = requests.get(f"{base_url}/uipath/export/{case_id_conflict}")
        if r.status_code == 200 and r.json().get("case_id") == case_id_conflict:
            print("PASS")
        else:
            print("FAIL", r.text)
            all_passed = False

        # 9. POST /uipath/maestro-investigation
        print("\n9. Testing POST /uipath/maestro-investigation...")
        maestro_payload = {
            "customer_id": "CUST-001",
            "transaction_id": "TX-MAESTRO-001",
            "amount_cop": 2400000,
            "evidence_quality": "clear",
            "reported_reason": "Customer reports unauthorized high-value instant payment with inconsistent receiver information",
            "simulate_receiver_failure": "conflicting_response",
            "source": "uipath-maestro"
        }
        r = requests.post(f"{base_url}/uipath/maestro-investigation", json=maestro_payload)
        res = r.json()
        if r.status_code == 200 and res.get("status") == "waiting_for_human" and res.get("human_review_required") == True:
            maestro_case_id = res.get("case_id")
            print("PASS", maestro_case_id)
        else:
            print("FAIL", r.text)
            all_passed = False
            return

        # 10. GET /uipath/maestro-export/{case_id}
        print(f"\n10. Testing GET /uipath/maestro-export/{maestro_case_id}...")
        r = requests.get(f"{base_url}/uipath/maestro-export/{maestro_case_id}")
        if r.status_code == 200 and r.json().get("case_id") == maestro_case_id:
            print("PASS")
        else:
            print("FAIL", r.text)
            all_passed = False

        # 11. GET /uipath/maestro-investigation-default
        print("\n11. Testing GET /uipath/maestro-investigation-default...")
        r = requests.get(f"{base_url}/uipath/maestro-investigation-default")
        res = r.json()
        if r.status_code == 200 and res.get("status") == "waiting_for_human" and res.get("human_review_required") == True:
            maestro_default_case_id = res.get("case_id")
            print("PASS", maestro_default_case_id)
        else:
            print("FAIL", r.text)
            all_passed = False

        # 12. GET /uipath/maestro-export-latest
        print("\n12. Testing GET /uipath/maestro-export-latest...")
        r = requests.get(f"{base_url}/uipath/maestro-export-latest")
        if r.status_code == 200:
            export_data = r.json()
            if export_data.get("case_id") == maestro_default_case_id:
                # Verify hardening fields
                if all(k in export_data for k in ["policy_summary", "sla_summary", "analyst_brief", "customer_response_draft"]):
                    print("PASS (with hardening fields)")
                else:
                    print("FAIL: Missing hardening fields in export", export_data)
                    all_passed = False
            else:
                print("FAIL", r.text)
                all_passed = False
        else:
            print("FAIL", r.text)
            all_passed = False

        # 13. GET /uipath/maestro-api-down-default
        print("\n13. Testing GET /uipath/maestro-api-down-default...")
        r = requests.get(f"{base_url}/uipath/maestro-api-down-default")
        res = r.json()
        if r.status_code == 200 and res.get("status") == "waiting_for_human" and res.get("human_review_required") == True:
            api_down_case_id = res.get("case_id")
            print("PASS", api_down_case_id)
        else:
            print("FAIL", r.text)
            all_passed = False

        # 14. Verify api_down audit events
        print(f"\n14. Testing GET /cases/{api_down_case_id}/audit for retry events...")
        r = requests.get(f"{base_url}/cases/{api_down_case_id}/audit")
        if r.status_code == 200:
            audit = r.json()
            event_types = [event.get("event_type") for event in audit]
            if "ReceiverBankRetryAttempted" in event_types and "ReceiverBankRetryExhausted" in event_types:
                print("PASS (Found retry events)")
            else:
                print("FAIL: Missing retry events", event_types)
                all_passed = False
        else:
            print("FAIL", r.text)
            all_passed = False
            
        # 15. GET /uipath/maestro-approve-latest
        print("\n15. Testing GET /uipath/maestro-approve-latest...")
        r = requests.get(f"{base_url}/uipath/maestro-approve-latest")
        res = r.json()
        if r.status_code == 200 and res.get("status") == "resolved_by_human" and res.get("human_decision") == "approve_refund":
            print("PASS (Approve latest case)")
        else:
            print("FAIL", r.text)
            all_passed = False
            
        # 16. GET /uipath/maestro-export-latest (after approve)
        print("\n16. Testing GET /uipath/maestro-export-latest (post-approve)...")
        r = requests.get(f"{base_url}/uipath/maestro-export-latest")
        if r.status_code == 200:
            export_data = r.json()
            if export_data.get("case_id") == api_down_case_id and export_data.get("status") == "resolved_by_human" and export_data.get("human_decision") == "approve_refund":
                print("PASS (Export post-approve matches)")
            else:
                print("FAIL: Export mismatch", export_data)
                all_passed = False
        else:
            print("FAIL", r.text)
            all_passed = False

    except Exception as e:
        print(f"Exception during tests: {e}")
        all_passed = False

    if all_passed:
        print("\n=== SUMMARY: RUNTIME SMOKE TESTS PASSED ===")
        sys.exit(0)
    else:
        print("\n=== SUMMARY: RUNTIME SMOKE TESTS FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
