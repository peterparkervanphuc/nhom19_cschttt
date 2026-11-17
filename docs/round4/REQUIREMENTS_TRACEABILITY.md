# Research to implementation traceability

P denotes the paper and R3.6 the locked implementation contracts. The [coverage table](TECHNICAL_REPORT.md#coverage-by-benchmark) tracks full benchmark runs, and the [experimental record](EXPERIMENTAL_RESULTS.md) identifies their evidence artifacts.

| ID | Requirement and source | Implementation location | Verification | Status |
|---|---|---|---|---|
| C01 | P data setup, R3.6 S1 event schema/train-only vocab/70-30 split | data/pipeline.py, data/preparation.py | test_data.py, test_preparation.py; counts and hashes in [Dataset provenance](DATASET_PROVENANCE.md) | Implemented; twelve input gates verified. Full execution tracked separately. |
| C02 | P Fig. 1/PL1, R3.6 S2 H4/model36/head9/FFN64 | model/transformer.py | tests/test_model.py, JUnit artifacts/s0/component-tests.xml | Core unit-tested |
| C03 | P PL1 10 epochs/batch12/lr.001 | model/training.py | test_training.py exact resume; base/run.json and checkpoint artifacts per log | Fixture and real baselines executed; results in EXPERIMENTAL_RESULTS.md |
| C04 | P predictions and attention | model/predictor.py | test_training.py; predictions.json with exact prepared IDs and checkpoint hashes | Full prediction coverage for reported baselines |
| C05 | P pp.14–16 E1, R3.6 D03/N05 | experiments/studies.py e1_prefix; experiments/e1_streaming.py | test_e1_streaming.py mid-prefix replay, exact variant counts and audited real and synthetic ledgers | Implemented. Per-log verification and measured workload limits are in the coverage table. |
| C06 | P pp.16–20 E2, R3.6 D12/N01 | experiments/studies.py e2_pair/run_study; experiments/streaming.py | test_experiments.py, test_streaming.py, ten training/checkpoint receipts and audits of all model–prefix pairs for completed runs | Implemented. Primary real and synthetic executions are in the coverage table. AC and UNI executed on the fixture. |
| C07 | P pp.20–22 E3, R3.6 D05 | experiments/studies.py e3_prefix; experiments/streaming.py | tests/test_experiments.py, test_streaming.py, complete and resumed ledgers on real and synthetic logs | Implemented. Per-log verification is in the coverage table. |
| C08 | P pp.22–24 BE, R3.6 D06 | explain/algorithms.py backward; explain/runner.py run_explainers | test_explainers.py, test_explainer_runner.py; completed graph receipts for Sepsis and BPIC13-CP | Integrated, fixture and full log graph verification |
| C09 | P pp.25–28 AE, R3.6 D07/D08 | explain/algorithms.py ae_contexts/ae_matrices; explain/runner.py | Repeated positions, signed votes, durable context dedup, exact resumed matrices and graph. Baseline and candidate ledgers audited on Helpdesk, Sequence and Long-Dist-Dep. | Exhaustive fixture and three benchmark runs verified. Exact pending workloads are in the coverage table. |
| C10 | P Table 2, R3.6 S6 | evaluate/metrics.py predictive_metrics | Unseen-label hand fixture and independent metric checks on all twelve baselines. Separate archived CPU replay and target-convention audit. | All independent predictive runs verified. Archived Helpdesk and Sepsis discrepancies remain open. |
| C11 | P pp.30–35, R3.6 N04 | evaluate/xai.py run_evaluation/evaluate_prefix/paired_method_differences | test_xai.py all nine components, Co03 selection, nulls and paired intersection. Both graph ledgers and all nine outputs audited on three logs. | Fixture, Helpdesk, Sequence and Long-Dist-Dep paired results verified. BPIC13-CP BE-only verified. |
| C12 | P graphs/BPMN, R3.6 graph contracts | graphs/relations.py, graphs/export.py | Direction, self-loop, pruning, GraphML round-trip, transactional export, visual SVG QA. Sequence direct-flow comparison and Long-Dist-Dep branch relation checks. | Graph export and two BPMN diagnostics verified. |

The source reference tree is `D:/transformer-explainability` at `494b315a555e713bdd61f0edd7d033c31d5850bf`. Detailed author source disagreements and line references remain in the Round 3.6 decision closure.
