import argparse
import json
import random
import uuid
import time
from datetime import datetime

FAILURE_TYPES = [
    "none",
    "receiver_bank_api_down",
    "unreadable_document",
    "conflicting_evidence",
    "investigator_timeout",
    "high_risk_refund_gate"
]

CHANNELS = ["app", "web", "call_center", "whatsapp"]

def generate_case(fail_rate):
    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
    amount_cop = round(random.uniform(50000, 5000000), 2)
    channel = random.choice(CHANNELS)
    
    # Determine if this case will have a failure injected
    has_failure = random.random() < fail_rate
    injected_failure_type = random.choice(FAILURE_TYPES[1:]) if has_failure else "none"
    
    evidence_quality = "high" if injected_failure_type != "unreadable_document" else "low"
    if injected_failure_type == "conflicting_evidence":
        evidence_quality = "medium"
        
    retries = 0
    escalated_to_human = False
    recovered = True
    time_to_recover_s = random.randint(1, 5)
    audit_complete = True
    
    # Simulate Maestro Case logic handling failures
    if injected_failure_type == "receiver_bank_api_down":
        retries = random.randint(1, 3)
        time_to_recover_s += retries * 10
        if random.random() < 0.05: # 5% unrecoverable
            recovered = False
    elif injected_failure_type in ["unreadable_document", "conflicting_evidence", "high_risk_refund_gate"]:
        escalated_to_human = True
        time_to_recover_s += random.randint(300, 3600) # Human delay
    elif injected_failure_type == "investigator_timeout":
        retries = random.randint(1, 2)
        time_to_recover_s += 120
        # 15% chance it doesn't recover from timeout
        if random.random() < 0.15:
            recovered = False
            audit_complete = False if random.random() < 0.5 else True
            
    deadline_breached = time_to_recover_s > 1800
    
    final_status = "resolved" if recovered else "failed"
    
    return {
        "case_id": case_id,
        "amount_cop": amount_cop,
        "channel": channel,
        "evidence_quality": evidence_quality,
        "injected_failure_type": injected_failure_type,
        "recovered": recovered,
        "retries": retries,
        "escalated_to_human": escalated_to_human,
        "deadline_breached": deadline_breached,
        "audit_complete": audit_complete,
        "time_to_recover_s": time_to_recover_s,
        "final_status": final_status
    }

def main():
    parser = argparse.ArgumentParser(description="CENTINELA Chaos Simulator")
    parser.add_argument("--cases", type=int, default=50, help="Number of cases to simulate")
    parser.add_argument("--fail-rate", type=float, default=0.3, help="Probability of injecting a failure (0.0 to 1.0)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for determinism")
    parser.add_argument("--out", type=str, default="evidence/chaos_runs.json", help="Output JSON file path")
    
    args = parser.parse_args()
    
    random.seed(args.seed)
    
    print(f"Starting chaos simulation with {args.cases} cases, {args.fail_rate*100}% fail rate, seed {args.seed}...")
    
    cases = []
    for _ in range(args.cases):
        cases.append(generate_case(args.fail_rate))
        
    # Write output
    with open(args.out, "w") as f:
        json.dump(cases, f, indent=2)
        
    # Summary Metrics
    total_failures = sum(1 for c in cases if c["injected_failure_type"] != "none")
    total_recovered = sum(1 for c in cases if c["recovered"] and c["injected_failure_type"] != "none")
    total_escalated = sum(1 for c in cases if c["escalated_to_human"])
    total_deadline_breaches = sum(1 for c in cases if c["deadline_breached"])
    total_audits_complete = sum(1 for c in cases if c["audit_complete"])
    avg_time = sum(c["time_to_recover_s"] for c in cases) / max(1, len(cases))
    
    recovery_rate = (total_recovered / total_failures * 100) if total_failures > 0 else 100.0
    escalation_rate = (total_escalated / len(cases) * 100)
    breach_rate = (total_deadline_breaches / len(cases) * 100)
    audit_rate = (total_audits_complete / len(cases) * 100)
    
    print("\n--- Simulation Metrics ---")
    print(f"total_cases: {args.cases}")
    print(f"injected_failures: {total_failures}")
    print(f"recovery_rate_from_failures: {recovery_rate:.1f}%")
    print(f"human_escalation_rate: {escalation_rate:.1f}%")
    print(f"deadline_breach_rate: {breach_rate:.1f}%")
    print(f"audit_completion_rate: {audit_rate:.1f}%")
    print(f"average_time_to_recover_s: {avg_time:.1f}")
    
    print(f"\nOutput written to: {args.out}")

if __name__ == "__main__":
    main()
