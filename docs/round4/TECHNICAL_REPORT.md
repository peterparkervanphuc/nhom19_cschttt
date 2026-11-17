# Round 4 technical report

Status: in progress. This report records verified Round 4 evidence and the remaining acceptance criteria as of 2026-11-17.

The independent Python package implements next-activity prediction, the three attention experiments, BE and AE, and predictive and explanation metrics. The integrated command has executed every stage on the committed fixture and the complete Sequence benchmark. The Sequence repeat reproduced the standalone results through all stages and passed receipt, context and metric audits. Helpdesk and the author-supplied Sequence and Long-Dist-Dep logs completed E1–E3, exhaustive BE/AE and all nine paired explanation outputs. Targeted structural comparisons cover all four synthetic BPMNs.

## Architecture and research fidelity

| Component | Independent implementation | Verification |
|---|---|---|
| Input and split | `data/pipeline.py`, `data/preparation.py` preserve event ordering, make a case-level train/test split and record input hashes | CSV/XES and filter tests. Verified public Sepsis and BPIC13 data, with BPIC12 variants listed separately in [Dataset provenance](DATASET_PROVENANCE.md) |
| Predictor | `model/transformer.py`, `model/training.py`, `model/predictor.py` handle embeddings, attention, masking, pooling, output head and replay | Frozen projections, masking invariance, shape and exact epoch resume tests |
| E1–E3 | `experiments/studies.py` defines the mathematics. `perturbations.py` generates the DFG-based variants. The streaming runners record results with input and checkpoint identity | BPIC13-CP E1 replay matches 15,569 ordered variant records, E2 has 15,740 complete paired records, and E3 has 1,574 complete records |
| BE and AE | `explain/algorithms.py` carries occurrence identities and applies pruning or signed score aggregation. `explain/runner.py` persists contexts and supports BE-only execution | Complete fixture matrices and graph replay. Complete BE on BPIC13-CP and Sepsis |
| Evaluation and export | `evaluate/metrics.py`, `evaluate/xai.py`, `graphs/export.py` implement predictive metrics, the six explanation properties over nine outputs, and directed graph export | Hand-calculated cases, null handling, paired intersections, GraphML direction and verified SVGs |
| Integration | `__main__.py` and `workflow.py` expose component commands, the nine-stage paired workflow and the distinct BE-only scope | Interrupted stage tests recover atomic outputs, resume streaming E1 and verify E2 checkpoints and SQLite ledger receipts |

The paper and locked Round 3.6 decisions define the baseline. The sibling author repository at `494b315a555e713bdd61f0edd7d033c31d5850bf` supplied read-only code and configuration evidence. The independent package runs without importing the original runtime. The archived BPIC13-CP test file shares 129 of 447 test cases with the independent split. A separate CPU replay of all twelve archived checkpoints reproduced every stored aggregate on ten logs using the configured last-prefix target. The Helpdesk and Sepsis mismatches persisted under two Keras paths, including `Model.predict` with the author's custom model class. A fixed relabeling of the observed CPU predictions cannot recover the archived Sepsis accuracy. [Requirements traceability](REQUIREMENTS_TRACEABILITY.md) · [Dataset provenance](DATASET_PROVENANCE.md) · [Paper](https://link.springer.com/article/10.1007/s44311-025-00018-4)

The isolated author replay uses the pinned Python 3.7.12, TensorFlow 2.6.5 and Keras 2.6.0 on CPU. The author attention layer delegates to Keras Softmax, which adds a finite `−1e9` to masked float32 logits before normalization. Running the pinned Keras layer on the fully masked row `[.5, .2, 1]` confirmed the uniform row `[1/3, 1/3, 1/3]` predicted by the arithmetic diagnostic. E3-PAPER zeros the masked query row after softmax. The separate replay evidence is in `artifacts/author-runtime/bpic13-cp-saved-model-audit-v2.json`. [Author environment](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/env.yaml) · [Author attention layer](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/models/multi_head_attention.py#L401-L432) · [Pinned Keras Softmax](https://github.com/keras-team/keras/blob/v2.6.0/keras/layers/advanced_activations.py#L256-L324)

The locked D02 decision also preserves a dimensional difference. The independent primary architecture has four nine-dimensional heads, so each head output is `n × 9`, concatenation is `n × 36`, the output projection is `n × 36` and the score divisor is `√9`. The pinned author constructor sets `key_dim=embed_dim`, giving 36 dimensions per head at embedding width 36, concatenation width 144 and a projection back to 36. These different projection shapes prevent direct weight transfer between the two architectures. They also limit attribution of predictive and explanation differences to any single method choice. [Locked D02 decision](../round4_preflight/decision_closure/TECHNICAL_DECISION_CLOSURE.md) · [Pinned author constructor](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/models/transformer.py#L37-L44)

## Experimental evidence

| Scope | Measured result | Interpretation |
|---|---|---|
| BPIC13-CP predictive performance | Accuracy .565438 and weighted F1 .521779 on all 1,574 prefixes | The archived configuration and pinned evaluation use last-prefix labels. On those labels a constant Accepted baseline reproduces .831763 accuracy, .755370 weighted F1 and all eight other archived aggregates. The archived test cohort also differs from the independent one. |
| BPIC13-CP E1 | Mean tau-b .245327 over 856 valid results, with 718 undefined | Nulls stay excluded from the mean. The independent workload counter matches all 15,569 evaluated variants. |
| BPIC13-CP E2 | Five BASE and five frozen-constant comparisons. Mean JSD per seed .007405–.024901 for BASE and .00482464–.00482480 for frozen-constant | Descriptive results for the locked comparison and this split. |
| BPIC13-CP E3 | Mean prefix TVD .222190 over 1,574 prefixes | Paper masking profile. |
| BPIC13 incidents predictive performance | Accuracy .697104 and weighted F1 .669383 on all 17,402 prefixes | Independently checked against sklearn. The paper reports .69 and .57, respectively, with historical run linkage still unverified. |
| BPIC13 incidents E1 | Mean tau-b .699499 over 12,498 valid results, out of 17,402 prefixes | Completed all 304,355 variants across two sessions. |
| BPIC13-CP BE evaluation | Mean completeness F1 .777019 on 1,259 scheduled prefixes. Correctness −.093826 over 643 valid prefixes. | All nine BE outputs are available. AE and method differences remain unevaluated on this cohort. |
| Sequence paired BE/AE evaluation | 2,640 scheduled prefixes. AE F1 .200579 and BE F1 .295173. Paired AE-minus-BE consistency .405572 on 1,944 valid pairs. | Exhaustive baseline and candidate graphs. Every comparison is descriptive. |
| Sequence reference structure | BE shares 10 of 11 direct BPMN edges with 3 extras. AE shares all 11 with 34 extras. | Direct-flow agreement on the verified sequence. |
| Long-Dist-Dep paired evaluation | 1,565 scheduled prefixes. AE F1 .249826 and BE F1 .343773. Paired AE-minus-BE consistency .630256 on 1,209 valid pairs. | AE has both selected BPMN branch edges. BE has neither. Both graph ledgers are exhaustive. |
| BPIC12 full predictive performance | Accuracy .829771 and weighted F1 .802612 on 73,742 prefixes | An independent raw XES scan validated the split, every prefix ID and target, the checkpoint identity and sklearn metrics. |
| BPIC12_O predictive performance | Accuracy .819142 and weighted F1 .799364 on 7,763 prefixes | The project CLI reproduced the expected filtered dataset counts and sklearn reproduced the metrics. |
| BPIC12_W predictive performance | Accuracy .882128 and weighted F1 .880374 on 47,280 prefixes | A separate XES scan reproduced the split and all next-activity targets. Sklearn reproduced the metrics. |
| BPIC12_WC predictive performance | Accuracy .787733 and weighted F1 .770420 on 18,472 prefixes | Complete ordered `W_` and `COMPLETE` filters with expected counts. Sklearn reproduced the metrics. |
| Helpdesk predictive performance | Accuracy .796709 and weighted F1 .751614 on 4,983 prefixes | Official CSV and pinned XES agree on the fields used by the model. Sklearn reproduced the metrics. |
| Helpdesk full paired BE/AE | 3,986 scheduled prefixes. AE recall .999875 and BE recall .868038. Paired AE-minus-BE F1 −.094686. | Both models' full-log AE schedules and all nine paired metric outputs passed the audit. |
| Sepsis predictive performance | Accuracy .607055 and weighted F1 .575063 on all 4,479 prefixes | The published figures are .51 and .46. The comparison does not control for historical checkpoints or protocol differences. |
| Sepsis E3 and BE | Mean prefix TVD .157010. BE graph has 14 nodes and 16 directed edges | Complete on the local test prefix set. The graph represents model behavior. |
| AE workload | BPIC13-CP: 809,189,178 scheduled contexts. Sepsis: approximately 9.58 × 10^52 | The locked exhaustive procedure makes full execution infeasible at measured local resources. An incomplete run does not supply a full-log AE graph or paired XAI metrics. |
| Sepsis E1 workload | 15,000 of 2,425,371,457 variants persisted across two sessions | A rough extrapolation from the early prefix records gives 3.58 TB and 16.2 days. No full-log correlation is established. |

The [experimental results record](EXPERIMENTAL_RESULTS.md) gives artifact paths, denominators, exact values and limitations. Model fidelity, alignment to a known process model and human interpretability are separate claims. A baseline accuracy difference does not establish any of the three.

### Coverage by benchmark

All twelve logs have audited next-activity predictions. A workload count describes the planned population. Only a completed run earns a verification entry.

| Log | E1 | E2-FC | E3-PAPER | BE | Exhaustive AE and evaluation |
|---|---|---|---|---|---|
| BPIC12 | ≥2,440,580,925 variants, storage-limited | Pending | Running; local C-drive ledger | Pending | AE workload check pending. BE-only XAI variant IDs alone require ≥124.9 GB. |
| BPIC12_O | Verified | Verified | Verified | Verified | 113,657,644 contexts. At least 47.5 GB of context text, storage-limited. BE-only evaluation verified. |
| BPIC12_W | Verified, 1,334,973 variants | Pending | Verified | Running | BE workload check underway |
| BPIC12_WC | Verified | 77,590/184,720 persisted; RAM-floor pause | Verified | Verified | Approximately 5.633 × 10^19 scheduled contexts |
| BPIC13_CP | Verified | Verified | Verified | Verified | 809,189,178 contexts. At least 241 GB of context text, storage-limited. BE-only evaluation verified. |
| BPIC13 incidents | Verified | Verified | Verified | Verified | Approximately 1.595 × 10^37 scheduled contexts. BE-only evaluation running. |
| Helpdesk | Verified | Verified | Verified | Verified | Baseline and candidate AE and all nine paired outputs verified |
| Sepsis | 15,000 of 2,425,371,457 variants persisted | Verified | Verified | Verified | Approximately 9.578 × 10^52 scheduled contexts. BE-only XAI variant IDs alone require ≥120.4 GB. |
| Complex-Model | 15,755,268,423 variants scheduled | 23,809/215,550 persisted; RAM-floor pause | Verified | Verified | Approximately 4.058 × 10^20 scheduled contexts. BE-only XAI variant IDs alone require ≥808.3 GB. |
| Long-Dist-Dep | Verified | Verified | Verified | Verified | Baseline and candidate AE and all nine paired outputs verified |
| Looped-AND | Verified | Verified | Verified | Verified | Approximately 1.219 × 10^27 scheduled contexts |
| Sequence | Verified | Verified | Verified | Verified | Baseline and candidate AE and all nine paired outputs verified |

## Acceptance and handoff

| Requirement | Status | Evidence or remaining check |
|---|---|---|
| Independent Transformer and three attention methods | PASS | Unit tests and completed research runs on the fixture and BPIC13-CP |
| Independent BE and AE | PASS for implementation | Full fixture graph/matrix coverage and resumption tests. Real exhaustive coverage is listed separately below. |
| Predictive and XAI evaluation, integrated workflow | PASS for implementation and verified runs | Predictive evaluation on all twelve logs. All nine paired XAI outputs on the fixture, Helpdesk, Sequence and Long-Dist-Dep. Directed export with artifact receipts. |
| Reference and baseline boundaries | PASS | Read-only author repository. Sampling diagnostics are separate from primary schedules. |
| Environment and dependency recreation | PASS | CPU lock installed in a second uv Python 3.11.15 environment, tests and `pip check` verified |
| Data pipeline and twelve-log scope | PASS for the input gate | Twelve log variants have verified input provenance and counts. The author archive supplies the four synthetic XES files and reference BPMNs. Full pipeline execution remains tracked separately. |
| Tests and end-to-end checks | PASS | 78 tests in `artifacts/s0/round4-xai-derivation-suite.xml`. Dependency validation passed. Complete paired and BE-only fixture scopes, independent per-prefix XAI arithmetic audits, finite quota validation, four-head arithmetic, interrupted E1 recovery, trace-wise filtering, an induced-path count checked against enumeration, and corruption checks on study and explainer ledgers. |
| Full feasible experiments and comparison | PARTIAL | The coverage table tracks open independent runs. Archived CPU inference was replayed on twelve logs. Ten match the stored metrics, with unresolved discrepancies for Helpdesk and Sepsis. |
| Full exhaustive AE on Sepsis | BLOCKED for execution | A single prefix has 174 eligible positions. Adding ordinary local or cloud resources cannot make this schedule feasible. |
| Commands, configuration, seeds, checkpoints | PASS for reported runs | [Commands](COMMANDS.md), versioned configs, source hashes and sealed run receipts |
| Plan, progress, traceability and experimental record | PASS | Maintained in `docs/round4/` |
| Final technical report and Round 5 handoff | PARTIAL | This is a working report. Full acceptance and a final handoff still depend on unresolved coverage and provenance. |

Round 5 can use the checked fixture and Sequence as software regression baselines. Helpdesk provides a paired real-log reference with exact context and metric coverage. The author archive reconciles the printed Tables 2 and 3 values. Independent historical-run reproduction and additional feasible benchmark runs remain open. Any later approximation of AE or E1 must have a separate experiment ID and comparison design.

To continue, use [the recorded commands](COMMANDS.md) with the same prepared file, checkpoint, output path and source version for a partial run. The current experimental priority is to finish feasible studies on verified official logs and retain precise workload and provenance evidence for each study that cannot complete.
