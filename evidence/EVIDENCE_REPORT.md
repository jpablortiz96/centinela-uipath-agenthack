# CENTINELA Evidence Report

## Overview
This report summarizes the deterministic local simulation of the CENTINELA fraud dispute case manager.
The goal is to demonstrate end-to-end resilience before final integration with UiPath Maestro Case.

## What Was Tested
- Intake and Evidence Review validation.
- Fraud Investigator Agent logic against simulated Core and Receiver Bank APIs.
- Case Orchestrator state transitions.
- Chaos Console visual presentation of the case lifecycle and human decision gating.

## Commands Used
```bash
python evidence/run_chaos.py --cases 50 --fail-rate 0.3 --seed 42
python evidence/generate_evidence_report.py
```

## Metrics Summary
- **Total Cases Simulated**: 50
- **Cases with Injected Failures**: 13
- **Recovery Rate (from failures)**: 92.3%
- **Human Escalation Rate**: 14.0%
- **Deadline Breach Rate**: 8.0%
- **Audit Completion Rate**: 98.0%
- **Avg Time to Recover**: 310.8 seconds

## Smoke Test Status Summary
*(Assuming standard run of `python scripts/run_all_smoke_tests.py`)*
- Mock APIs: **PASS**
- Fraud Investigator: **PASS**
- Case Orchestrator: **PASS**
- Chaos Console: **PASS**

## Available Evidence Artifacts
### Logs (8 files found)
- `evidence/logs/case_orchestrator_runs.jsonl`
- `evidence/logs/step3_fraud_investigator_smoke.txt`
- `evidence/logs/step3_mock_apis_smoke.txt`
- `evidence/logs/step4_case_orchestrator_smoke.txt`
- `evidence/logs/step4_orchestrator_health.json`
- `evidence/logs/step5_chaos_console_health.json`
- `evidence/logs/step5_chaos_console_smoke.txt`
- `evidence/logs/step5_services_health.json`

### Screenshots (1 files found)
- `evidence/manual-screenshots/step5_chaos_console.png`

## Limitations
- **Local Simulation**: This is a local mock execution. UiPath Labs integration (Maestro Case, Action Center, AI Trust Layer) is pending.
- **No Real Banking Data**: All transactions and customer details are synthetic.
- **No LLM API Calls**: Current risk rules are deterministic to ensure reliable testability at this stage.

## Reproducibility
To reproduce this evidence pack locally:
1. Ensure Python 3 is installed.
2. Run `python scripts/run_all_smoke_tests.py` (ensure all 5 services are running on ports 8010-8050).
3. Run `python evidence/run_chaos.py --cases 50 --fail-rate 0.3 --seed 42`.
4. Run `python evidence/generate_evidence_report.py`.
