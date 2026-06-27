# Judges Start Here

Welcome to CENTINELA. If you are evaluating this project, please follow this path:

1. **[Open Judge Replay First](https://centinela-uipath-agenthack.onrender.com/judge)**
   * Walk through the guided 5-step operational replay of the fraud dispute lifecycle.
2. **[Open Analyst Console Second](https://centinela-uipath-agenthack.onrender.com/analyst)**
   * Review the Fraud Intelligence Layer, including the Priority Queue, Fraud Network Graph, and Decision Simulator.
3. **[Verify UiPath Evidence Pack](docs/UIPATH_EVIDENCE_PACK.md)**
   * Review our detailed execution screenshots and logs proving Maestro Case deployment and Integration Service connector debug execution.
4. **[Verify Runtime OpenAPI](https://centinela-uipath-agenthack.onrender.com/openapi.json)**
   * Explore the robust backend APIs that drive the investigation.
5. **[Read Product Feedback](docs/UIPATH_PRODUCT_FEEDBACK.md)**
   * Understand the specific UiPath Labs custom connector packaging limitation we hit, which is why the published version could not be fully linked.
6. **[Read the Claims Mapping](docs/CLAIMS.md)**
   * We do not overclaim. We mapped exactly what is implemented and what is simulated.
7. **Run Smoke Tests (Locally)**
   * To verify full functionality, clone the repository and run:
     ```bash
     python scripts/smoke_test_judge_replay.py --base-url https://centinela-uipath-agenthack.onrender.com
     ```
