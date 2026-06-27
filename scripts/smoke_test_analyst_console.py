import requests
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Smoke test for Analyst Console")
    parser.add_argument("--base-url", default="http://127.0.0.1:8070", help="Base URL of the Runtime API")
    args = parser.parse_args()
    
    base_url = args.base_url
    all_passed = True
    
    print(f"Testing Analyst Console at {base_url}\n")
    
    try:
        # 1. GET /analyst
        print("1. Testing GET /analyst...")
        r = requests.get(f"{base_url}/analyst")
        if r.status_code == 200 and "CENTINELA Analyst Console" in r.text:
            print("PASS (HTML returned)")
        else:
            print("FAIL", r.text[:200])
            all_passed = False
            
        # 2. GET /api/analyst/cases
        print("\n2. Testing GET /api/analyst/cases...")
        r = requests.get(f"{base_url}/api/analyst/cases")
        if r.status_code == 200 and isinstance(r.json(), list):
            print(f"PASS (Returned {len(r.json())} cases)")
        else:
            print("FAIL", r.text)
            all_passed = False
            
        # 3. GET /api/analyst/run-api-down-case
        print("\n3. Testing GET /api/analyst/run-api-down-case...")
        r = requests.get(f"{base_url}/api/analyst/run-api-down-case")
        res = r.json()
        if r.status_code == 200 and res.get("status") == "waiting_for_human" and res.get("risk_level") == "critical":
            print("PASS", res.get("case_id"))
        else:
            print("FAIL", r.text)
            all_passed = False
            
        # 4. GET /api/analyst/approve-latest
        print("\n4. Testing GET /api/analyst/approve-latest...")
        r = requests.get(f"{base_url}/api/analyst/approve-latest")
        res = r.json()
        if r.status_code == 200 and res.get("status") == "resolved_by_human":
            print("PASS (Resolved latest case)")
        else:
            print("FAIL", r.text)
            all_passed = False
            
        # 5. GET /api/analyst/export-latest
        print("\n5. Testing GET /api/analyst/export-latest...")
        r = requests.get(f"{base_url}/api/analyst/export-latest")
        if r.status_code == 200:
            export = r.json()
            required_keys = ["policy_summary", "sla_summary", "analyst_brief", "customer_response_draft", "timeline", "evidence_summary", "risk_explanation", "recommended_questions_for_analyst", "allowed_decisions"]
            missing = [k for k in required_keys if k not in export]
            if not missing:
                brief = export.get("analyst_brief", "")
                if "Deterministic brief generated for analyst" in brief:
                    print("FAIL: Analyst brief is the old generic one.")
                    all_passed = False
                else:
                    print("PASS (All required summaries included and brief is dynamic)")
            else:
                print("FAIL: Missing keys", missing)
                all_passed = False
        else:
            print("FAIL", r.text)
            all_passed = False
            
    except Exception as e:
        print(f"Exception during tests: {e}")
        all_passed = False
        
    print("\n=== SUMMARY: " + ("ANALYST SMOKE TESTS PASSED" if all_passed else "SOME TESTS FAILED") + " ===")
    if not all_passed:
        sys.exit(1)
    
if __name__ == "__main__":
    main()
