# Evidence Directory

This directory contains the artifacts, logs, and reproducible metrics for the CENTINELA project.

## How to Regenerate `chaos_runs.json`
Run the chaos simulator to generate a deterministic batch of cases:
```bash
python evidence/run_chaos.py --cases 50 --fail-rate 0.3 --seed 42
```

## How to Regenerate `EVIDENCE_REPORT.md`
After running the chaos simulator, aggregate the metrics and available logs into a judge-friendly report:
```bash
python evidence/generate_evidence_report.py
```

## How to Run All Smoke Tests
Make sure all 5 services (Core Banking, Receiver Bank, Fraud Investigator, Case Orchestrator, Chaos Console) are running locally, then execute:
```bash
python scripts/run_all_smoke_tests.py
```

## What Each Evidence Artifact Means
- **`chaos_runs.json`**: A deterministic log of synthetic cases and their simulated outcomes.
- **`EVIDENCE_REPORT.md`**: A summary of metrics, constraints, limitations, and reproducible test outcomes.
- **`metrics_summary.json`**: A machine-readable snapshot of the chaos metrics.
- **`logs/`**: Raw output files, including the Orchestrator's `case_orchestrator_runs.jsonl` audit trail and smoke test output dumps.
- **`manual-screenshots/`**: Visual evidence of the local web UIs (e.g., Chaos Console).
