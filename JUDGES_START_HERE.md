# Judges Start Here

Welcome to CENTINELA. If you are evaluating this project, please follow this fast path:

1. **[Open Judge Replay First](https://centinela-uipath-agenthack.onrender.com/judge)**
   * Walk through the guided 5-step operational replay of the fraud dispute lifecycle safely.
2. **[Open Analyst Console Second](https://centinela-uipath-agenthack.onrender.com/analyst)**
   * Review the Fraud Intelligence Layer, including the Priority Queue, Fraud Network Graph, and Decision Simulator.
3. **[Read UiPath Evidence Pack](docs/UIPATH_EVIDENCE_PACK.md)**
   * Review our detailed execution screenshots and logs proving Maestro Case deployment and Integration Service connector debug execution.
4. **Review Known Limitation & Product Feedback**
   * The connected Maestro + custom connector flow runs successfully in cloud debug. Publishing the connected version is blocked by a UiPath Labs custom connector packaging/export limitation. Details in `docs/UIPATH_PRODUCT_FEEDBACK.md`.
5. **Run Smoke Tests (Locally)**
   * To verify full public functionality, clone the repository and run:
     ```bash
     python scripts/smoke_test_judge_replay.py --base-url https://centinela-uipath-agenthack.onrender.com
     ```
6. **[Inspect Claims](docs/CLAIMS.md)**
   * Understand exactly what is implemented and what is not claimed (e.g. we do *not* claim production banking readiness or autonomous refund approval). We prioritize honesty and transparency.
