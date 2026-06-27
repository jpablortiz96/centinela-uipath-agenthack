# Judges Start Here

Welcome to CENTINELA. If you are evaluating this project, please follow this fast path:

1. **[Start here: Judge Replay](https://centinela-uipath-agenthack.onrender.com/judge)**
   * Walk through the guided 5-step operational replay of the fraud dispute lifecycle safely.
2. **[Then: Analyst Console](https://centinela-uipath-agenthack.onrender.com/analyst)**
   * Review the Fraud Intelligence Layer, including the Priority Queue, Fraud Network Graph, and Decision Simulator.
3. **[Then: UiPath Evidence Pack](docs/UIPATH_EVIDENCE_PACK.md)**
   * Review our detailed execution screenshots and logs proving Maestro Case deployment and Integration Service connector debug execution.
4. **[Then: Product Feedback](docs/UIPATH_PRODUCT_FEEDBACK.md)**
   * Understand the specific UiPath Labs custom connector packaging limitation we hit, which is why the published version could not be fully linked.
5. **Then: Smoke test commands**
   * To verify full public functionality, run:
     ```bash
     python scripts/smoke_test_judge_replay.py --base-url https://centinela-uipath-agenthack.onrender.com
     python scripts/smoke_test_analyst_console.py --base-url https://centinela-uipath-agenthack.onrender.com
     python scripts/smoke_test_centinela_runtime.py --base-url https://centinela-uipath-agenthack.onrender.com
     ```

*Note: Connected publish limitation is documented; connected debug execution is validated.*
