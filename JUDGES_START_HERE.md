# Judges Start Here

Welcome to CENTINELA! If you only have 60 seconds, here is your path:

## 1. What to Read First
Read the `README.md` for a high-level overview of the problem and our solution. Then, take a look at `docs/ARCHITECTURE.md` to understand the case lifecycle.

## 2. How to Run the Evidence Script
To see our evidence-first approach in action, run our chaos simulation script. It requires no heavy dependencies, just Python 3:
```bash
python evidence/run_chaos.py --cases 50 --fail-rate 0.3 --seed 42
```
This generates `evidence/chaos_runs.json` with synthetic cases and prints out summary metrics of simulated failures and recoveries.

## 3. What the Demo Will Show
Our 5-minute demo will cover:
- Creating a fraud dispute.
- Processing evidence.
- Injecting a failure (e.g., receiver bank API down).
- Showing retry/escalation managed by UiPath.
- A human approving or rejecting the case via Action Center.
- An audit trail export.

*(For the full script, see `docs/DEMO_SCRIPT.md`)*

## 4. What is Real Now vs. Planned
- **Real Now**: The repository foundation, the evidence-first chaos simulation script (`evidence/run_chaos.py`), and the synthetic case generation logic.
- **Planned**: Connection to UiPath Maestro Case, Action Center integration, actual mock banking APIs, and Document Understanding. We are currently at Step 1 of the build.
