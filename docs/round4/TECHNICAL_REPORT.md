# Round 4 technical report

Status: in progress. This report records verified Round 4 evidence and the remaining acceptance criteria as of 2026-11-17.

The independent Python package implements next-activity prediction, the three attention experiments, BE and AE, and predictive and explanation metrics. The integrated command has executed every stage on the committed synthetic fixture. On official event logs, BPIC13-CP has completed E1, E2, E3 and BE. Sepsis has completed prediction, E3 and BE. The resource measurements below prevent interpreting those runs as complete coverage of the paper's evaluation.

## Architecture and research fidelity

| Component | Independent implementation | Verification |
|---|---|---|
| Input and split | `data/pipeline.py`, `data/preparation.py` preserve event ordering, make a case-level train/test split and record input hashes | CSV/XES and filter tests. Verified public Sepsis and BPIC13 data, with BPIC12 variants listed separately in [Dataset provenance](DATASET_PROVENANCE.md) |
| Predictor | `model/transformer.py`, `model/training.py`, `model/predictor.py` handle embeddings, attention, masking, pooling, output head and replay | Frozen projections, masking invariance, shape and exact epoch resume tests |
| E1–E3 | `experiments/studies.py` defines the mathematics. `perturbations.py` generates the DFG-based variants. The streaming runners record results with input and checkpoint identity | BPIC13-CP E1 replay matches 15,569 ordered variant records, E2 has 15,740 complete paired records, and E3 has 1,574 complete records |
| BE and AE | `explain/algorithms.py` carries occurrence identities and applies pruning or signed score aggregation. `explain/runner.py` persists contexts and supports BE-only execution | Complete fixture matrices and graph replay. Complete BE on BPIC13-CP and Sepsis |
| Evaluation and export | `evaluate/metrics.py`, `evaluate/xai.py`, `graphs/export.py` implement predictive metrics, the six explanation properties over nine outputs, and directed graph export | Hand-calculated cases, null handling, paired intersections, GraphML direction and verified SVGs |
| Integration | `__main__.py` and `workflow.py` expose component commands and the nine-stage fixture workflow | Stage publication and interrupted resume tests, including checksum validation of child artifacts |

The paper and locked Round 3.6 decisions define the baseline. The sibling author repository at `494b315a555e713bdd61f0edd7d033c31d5850bf` supplied read-only code and configuration evidence. The independent package runs without importing the original runtime. The archived BPIC13-CP test file shares 129 of 447 test cases with the independent split. Archived configurations, metrics and saved models are available for investigation. Exact linkage from saved model through split and individual predictions to Table 2 remains unverified. [Requirements traceability](REQUIREMENTS_TRACEABILITY.md) · [Dataset provenance](DATASET_PROVENANCE.md) · [Paper](https://link.springer.com/article/10.1007/s44311-025-00018-4)

## Experimental evidence

| Scope | Measured result | Interpretation |
|---|---|---|
| BPIC13-CP predictive performance | Accuracy .565438 and weighted F1 .521779 on all 1,574 prefixes | The published figures are .83 and .76. The pinned source schedule of 5 epochs and batch 50 produced .559720 and .517447 with the independent model. Schedule alone did not explain the gap. |
| BPIC13-CP E1 | Mean tau-b .245327 over 856 valid results, with 718 undefined | Nulls stay excluded from the mean. The independent workload counter matches all 15,569 evaluated variants. |
| BPIC13-CP E2 | Five BASE and five frozen-constant comparisons. Mean JSD per seed .007405–.024901 for BASE and .00482464–.00482480 for frozen-constant | Descriptive results for the locked comparison and this split. |
| BPIC13-CP E3 | Mean prefix TVD .222190 over 1,574 prefixes | Paper masking profile. |
| BPIC13 incidents predictive performance | Accuracy .697104 and weighted F1 .669383 on all 17,402 prefixes | Independently checked against sklearn. The paper reports .69 and .57, respectively, with historical run linkage still unverified. |
| BPIC13 incidents E1 | Mean tau-b .699499 over 12,498 valid results, out of 17,402 prefixes | Completed all 304,355 variants across two sessions. |
| BPIC13-CP BE evaluation | Mean completeness F1 .777019 on 1,259 scheduled prefixes. Correctness −.093826 over 643 valid prefixes. | All nine BE outputs are available. AE and method differences remain unevaluated on this cohort. |
| BPIC12_O predictive performance | Accuracy .819142 and weighted F1 .799364 on 7,763 prefixes | The project CLI reproduced the expected filtered dataset counts and sklearn reproduced the metrics. |
| BPIC12_WC predictive performance | Accuracy .787733 and weighted F1 .770420 on 18,472 prefixes | Complete ordered `W_` and `COMPLETE` filters with expected counts. Sklearn reproduced the metrics. |
| Helpdesk predictive performance | Accuracy .796709 and weighted F1 .751614 on 4,983 prefixes | Official CSV and pinned XES agree on the fields used by the model. Sklearn reproduced the metrics. |
| Sepsis predictive performance | Accuracy .607055 and weighted F1 .575063 on all 4,479 prefixes | The published figures are .51 and .46. The comparison does not control for historical checkpoints or protocol differences. |
| Sepsis E3 and BE | Mean prefix TVD .157010. BE graph has 14 nodes and 16 directed edges | Complete on the local test prefix set. The graph represents model behavior. |
| AE workload | BPIC13-CP: 809,189,178 scheduled contexts. Sepsis: approximately 9.58 × 10^52 | The locked exhaustive procedure makes full execution infeasible at measured local resources. An incomplete run does not supply a full-log AE graph or paired XAI metrics. |
| Sepsis E1 workload | 15,000 of 2,425,371,457 variants persisted across two sessions | A rough extrapolation from the early prefix records gives 3.58 TB and 16.2 days. No full-log correlation is established. |

The [experimental results record](EXPERIMENTAL_RESULTS.md) gives artifact paths, denominators, exact values and limitations. Model fidelity, alignment to a known process model and human interpretability are separate claims. A baseline accuracy difference does not establish any of the three.

## Acceptance and handoff

| Requirement | Status | Evidence or remaining check |
|---|---|---|
| Independent Transformer and three attention methods | PASS | Unit tests and completed research runs on the fixture and BPIC13-CP |
| Independent BE and AE | PASS for implementation | Full fixture graph/matrix coverage and resumption tests. Real exhaustive coverage is listed separately below. |
| Predictive and XAI evaluation, integrated workflow | PASS for fixtures | Predictive evaluation on official logs, all nine XAI outputs on the fixture, and directed export with artifact receipts |
| Reference and baseline boundaries | PASS | Read-only author repository. Sampling diagnostics are separate from primary schedules. |
| Environment and dependency recreation | PASS | CPU lock installed in a second uv Python 3.11.15 environment, tests and `pip check` verified |
| Data pipeline and twelve-log scope | PASS for the input gate | Twelve log variants have verified input provenance and counts. The author archive supplies the four synthetic XES files and reference BPMNs. Full pipeline execution remains tracked separately. |
| Tests and end-to-end checks | PASS | 54 tests in `artifacts/s0/filtered-xes-suite.xml`. Complete fixture pipeline, interrupted E1 resume, BE-only evaluation parity, trace-wise filter audit, and checksum checks on full E2/E3 runs. |
| Full feasible real experiments and comparison | PARTIAL | Six predictive baselines, several complete attention studies and one real BE evaluation are verified. Remaining feasible studies and the real paired AE–BE benchmark are open. Author execution is not yet established. |
| Full exhaustive AE on Sepsis | BLOCKED for execution | A single prefix has 174 eligible positions. Adding ordinary local or cloud resources cannot make this schedule feasible. |
| Commands, configuration, seeds, checkpoints | PASS for reported runs | [Commands](COMMANDS.md), versioned configs, source hashes and sealed run receipts |
| Plan, progress, traceability and experimental record | PASS | Maintained in `docs/round4/` |
| Final technical report and Round 5 handoff | PARTIAL | This is a working report. Full acceptance and a final handoff still depend on unresolved coverage and provenance. |

Round 5 can use the checked fixture as a software regression baseline. Published-result reproduction and real paired explanation benchmarks remain unverified. Any later approximation of AE or E1 must have a separate experiment ID and comparison design.

To continue, use [the recorded commands](COMMANDS.md) with the same prepared file, checkpoint, output path and source version for a partial run. The current experimental priority is to finish feasible studies on verified official logs and retain precise workload and provenance evidence for each study that cannot complete.
