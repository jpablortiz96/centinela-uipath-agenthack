import requests
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Smoke test for Judge Replay")
    parser.add_argument("--base-url", default="http://127.0.0.1:8070", help="Base URL of the Runtime API")
    args = parser.parse_args()
    
    base_url = args.base_url
    all_passed = True
    
    print(f"Testing Judge Replay at {base_url}\n")
    
    try:
        # 1. GET /judge
        print("1. Testing GET /judge...")
        r = requests.get(f"{base_url}/judge")
        if r.status_code == 200 and "CENTINELA Judge Replay" in r.text:
            print("PASS (HTML returned)")
        else:
            print("FAIL", r.text[:200])
            all_passed = False
            
        # 2. GET /api/judge/replay
        print("\n2. Testing GET /api/judge/replay...")
        r = requests.get(f"{base_url}/api/judge/replay")
        if r.status_code == 200:
            export = r.json()
            required_keys = ["case_id", "risk_score", "status", "human_decision", "retry_event_count", "full_export"]
            missing = [k for k in required_keys if k not in export]
            if not missing:
                print("PASS (Replay returned case: " + export["case_id"] + ")")
                
                # 3. Validate final export includes intelligence fields
                print("\n3. Testing export package fields...")
                fe = export["full_export"]
                fe_reqs = ["policy_summary", "sla_summary", "fraud_network", "decision_simulator", "evidence_checklist", "linked_case_signals", "timeline"]
                fe_miss = [k for k in fe_reqs if k not in fe]
                if not fe_miss:
                    print("PASS (All intelligence fields present in export)")
                else:
                    print("FAIL (Missing fields in full_export: " + str(fe_miss) + ")")
                    all_passed = False
            else:
                print("FAIL (Missing keys in replay response: " + str(missing) + ")")
                all_passed = False
        else:
            print("FAIL", r.text)
            all_passed = False
            
    except Exception as e:
        print(f"Exception during tests: {e}")
        all_passed = False
        
    print("\n=== SUMMARY: " + ("JUDGE REPLAY SMOKE TESTS PASSED" if all_passed else "SOME TESTS FAILED") + " ===")
    if not all_passed:
        sys.exit(1)
    
if __name__ == "__main__":
    main()
