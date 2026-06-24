import subprocess
import sys

def main():
    print("=== CENTINELA Full Smoke Test Suite ===\n")
    print("Assumes all 5 local services are running on ports 8010-8050.\n")
    
    scripts = [
        "scripts/smoke_test_mock_apis.py",
        "scripts/smoke_test_fraud_investigator.py",
        "scripts/smoke_test_case_orchestrator.py",
        "scripts/smoke_test_chaos_console.py"
    ]
    
    all_passed = True
    
    for script in scripts:
        print(f"--- Running {script} ---")
        result = subprocess.run(["python", script], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        if result.returncode != 0:
            print(f"[ERROR] {script} failed with exit code {result.returncode}")
            all_passed = False
        else:
            # Also check if the output contains "[FAIL]"
            if "[FAIL]" in result.stdout:
                print(f"[ERROR] {script} completed but contains failed tests.")
                all_passed = False
                
        print("\n" + "="*40 + "\n")
        
    if all_passed:
        print("\n=== SUMMARY: ALL SMOKE TESTS PASSED ===")
        sys.exit(0)
    else:
        print("\n=== SUMMARY: SOME SMOKE TESTS FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
