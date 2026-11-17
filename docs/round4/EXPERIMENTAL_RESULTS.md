# Round 4 experimental results

Software fixture integration is complete, including E1–E3, BE/AE and all nine XAI outputs. All twelve independent predictive baselines have been trained and verified. Full twelve-log experimental coverage remains incomplete. The primary schedule and diagnostic profiles are defined in Round 3 and Round 3.6. Every result below retains its own dataset, split, source and checkpoint identity.

The strengthened XAI audit reconstructed the nine per-prefix metrics from stored intermediates on BPIC13-CP and BPIC12_O BE-only evaluations, the Helpdesk, Sequence and Long-Dist-Dep paired evaluations, and the integrated Sequence repeat: 29,131 method records in total, including the repeat. It also checked projections against the saved global graphs and candidate Jaccard overlaps. Independent pair counting reproduced Kendall tau-b with ties and undefined cases preserved. The six `evaluation-derivation-audit.json` receipts retain the auditor hash. This verifies recorded metric arithmetic and graph alignment; it does not replay each model inference.

| Component | Execution status | Evidence |
|---|---|---|
| E1 Feature Correlation | Fixture executed on 3 test prefixes | artifacts/fixture/E1.json, tau-b null for all 3 single-label universes |
| E2 Attention Parameter Manipulation | Fixture BASE vs 5 fresh BASE and 5 FC, all 10 epochs | artifacts/fixture/E2.json and E2-models/, 10 pairs × 3 prefixes |
| E3 Attention Score Masking | Fixture E3-PAPER executed | artifacts/fixture/E3.json, mean prefix TVD 0.21716457605361938 |
| BE | Full fixture global graph executed | artifacts/pipeline-fixture-v2/evaluation/baseline-graphs/BE.json |
| AE | Full fixture contexts/votes/matrices completed; interrupted resume verified | artifacts/pipeline-fixture-v2/evaluation/baseline-graphs/AE.json and ledger.sqlite |
| Predictive and XAI evaluation | Full fixture complete, five Co03 candidates and nine outputs | artifacts/pipeline-fixture-v2/evaluation/evaluation.json |

Published BPIC12 BE #rules 13.04 ± 2.03 and AE 6.32 ± 1.11 are comparison references. Their provenance is distinct from the local results below.

These fixture runs use fixed c1/c2/c3 train and c4/c5 test, CPU float32, baseline seed1729, batch12, lr.001 and10 epochs. Complete hashes and class order are inside sealed outputs and base/run.json. Fixture E2 pair means range from 1.332115489355604e-08 to 1.0309166561330458e-07 for JSD and from 0.09884713093439738 to 0.23245424032211304 for prediction TVD. These tiny inputs support integration checks only. E2-AC and E2-UNI CLI fixture runs also completed ten model comparisons each. E3-AUTHOR completed all three prefixes, mean prefix TVD=.2051203412. Outputs are separate under pipeline-fixture-v2.

The XAI fixture cohort is the same two prefixes for both methods. BE completeness(P/R/F1)=(1,.5,.5), consistency=.8374382802, continuity=.6691127479, rules=.5, RHS=3. AE completeness=(1,1,1), consistency=.7417424178, continuity=.4620500849, rules=1, RHS=2.5. Precision and RHS for BE have only1 valid observation; other non-null entries have2. Correctness and contrastivity are undefined for both, retained as null with reasons. Do not compare group means as though their denominators were identical: the output now also reports AE-minus-BE on each metric's valid paired intersection. No statistical significance test was performed.

## Real-data baselines

The runs use the verified official version 1 archives, activity-only labels, a case-level random 70/30 split with seed 42 and training seed 1729. They use CPU float32, 10 epochs, batch size 12 and Adam with learning rate .001. Each run uses an independently trained checkpoint.

| Log | Test prefixes completed/expected | Weighted precision | Accuracy/weighted recall | Weighted F1 | Training wall seconds |
|---|---:|---:|---:|---:|---:|
| Sepsis | 4,479/4,479 | .6445562480 | .6070551462 | .5750634064 | 88.211886 |
| BPIC13 closed problems | 1,574/1,574 | .4916116862 | .5654383736 | .5217793991 | 19.217390 |
| BPIC13 incidents | 17,402/17,402 | .7093138347 | .6971037812 | .6693827922 | 156.156451 |
| BPIC12 full | 73,742/73,742 | .8331685711 | .8297713650 | .8026122138 | 2,175.455447 |
| BPIC12 O | 7,763/7,763 | .8249324235 | .8191420842 | .7993637164 | 53.697025 |
| BPIC12 W | 47,280/47,280 | .8840351369 | .8821277496 | .8803739866 | 800.939466 |
| BPIC12 WC | 18,472/18,472 | .7770249616 | .7877327848 | .7704196948 | 184.164754 |
| Helpdesk | 4,983/4,983 | .8164058218 | .7967088100 | .7516142831 | 35.086813 |

Artifacts: artifacts/sepsis-v1/base and predictions.json; artifacts/bpic13-cp-v1/base and predictions.json. Raw acquisition and file/count checks are described in DATASET_PROVENANCE.md. No test targets were used for fitting or class-vocabulary construction.

BPIC13 incidents outputs use the same paths under `artifacts/bpic13-i-v1/`. Checkpoint SHA-256 and all target/prefix IDs were verified. Independent sklearn metrics agreed with the sealed record. Paper Table 2 gives precision/accuracy/F1 of .50/.69/.57 for BPIC13-I. The local weighted F1 gap is approximately +.0994 on the independent split, with historical checkpoint linkage still unknown.

Full BPIC12 completed ten epochs on the fixed seed-42 split. An independent scan of the raw XES recovered all 13,087 cases, 262,200 events and 24 labels. It rebuilt the 9,160/3,927 training/test split and verified every test prefix ID, target, class order, prediction argmax and probability normalization. Sklearn reproduced all four predictive aggregates. Evidence is in `artifacts/bpic12-v1/predictive-audit.json`.

BPIC12_O outputs use `artifacts/bpic12-o-v1/`. The CLI passed the expected input hash and count checks. It retained 31,244 out of 262,200 source events with prefix `O_`, removing 8,072 of 13,087 cases. The 7,763 prediction IDs and targets matched the prepared split exactly, and sklearn reproduced the metrics. Published precision/accuracy/F1 are .96/.93/.93. The local F1 difference is −.1306 on the independent split.

BPIC12_W outputs use `artifacts/bpic12-w-v1/`. A second XES scan reconstructed all 47,280 test prefix IDs and observed labels from the official raw archive and independent case split. It matched every prediction row, checked the checkpoint hash and reproduced the metrics with sklearn. The audit is in `prediction-audit.json`.

BPIC12_WC outputs use `artifacts/bpic12-wc-v1/`. The 18,472 prediction IDs, targets and checkpoint hash match the prepared data and baseline. Sklearn reproduced the reported metrics. Paper Table 2 gives precision/accuracy/F1 of .75/.78/.75. The local F1 difference is approximately +.0204 on the independent split.

Helpdesk outputs use `artifacts/helpdesk-v1/`. All 4,983 prediction IDs, targets, checkpoint hash and sklearn scores matched. Paper Table 2 gives .74/.79/.76, with a local weighted F1 difference of about −.0084. The XES input agrees event by event with the official data on model fields. The historical run linkage remains unverified. The independent E1 workload counter reports 390,254 variants for this split.

For descriptive context, the supplied paper's Table 2, printed page 30, reports weighted precision/accuracy/weighted F1 of (.49, .51, .46) for Sepsis and (.69, .83, .76) for BPIC13_CP. Against the printed values, local F1 differences are +.1151 and −.2382, respectively. Source implementation, split/seed, masking and other protocol decisions differ, so these differences are descriptive. The local table extract is retained in `artifacts/paper-table2-page30.txt`. [Paper](https://link.springer.com/article/10.1007/s44311-025-00018-4)

### Table 2 archive reconciliation

All 36 printed values match the author archive's `precision_weighted`, `accuracy` and `f1_weighted` fields after rounding to two decimals. The exact member names, member SHA-256 and unrounded numbers are in `data/raw/author-supplement/table2-reconciliation.json`. The matching files are under `Supplementary_Material/Trained_Models/`: `training_<log>_GPU/metrics.json` for the eight real-log rows and `training_{complex_model,long_dist_dep,looped_and,sequence}/metrics.json` for the four synthetic rows. The log directory names for BPIC13 are `bpic13_closed_problems` and `bpic13_incidents`. Both Helpdesk variants in the archive give the same rounded row, so the printed precision does not identify a unique run. [Author archive](https://drive.google.com/file/d/1p-mbznaXoYI0ofqlzKGPzJ1FVcAX0Pg4/view)

The BPIC13_CP GPU metrics are .691829892 weighted precision, .831763122 accuracy and .755370477 weighted F1. The archived run configuration records 5 epochs, batch size 50, learning rate .001 and GPU index 0. Its `result.csv` contains one newline and no prediction rows. The separate CPU checkpoint replay below establishes the aggregate linkage.

### BPIC13_CP target alignment

The archived GPU configuration selects `test_pref.xes`. The pinned sampler writes the observed history to `test_pref.xes` and the next event starts `test_suf.xes`. The pinned evaluation calls `extract_traces_and_ypred_from_xes`, which returns `(trace[:-1], trace[-1])` from the configured file. With that configuration, it predicts the last event of each archived prefix using the preceding events. The independent evaluation predicts the first suffix event using the full prefix. [Pinned sampler](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/ml/core/sample_creator.py#L26-L37) · [Pinned trace utility](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/util/trace_util.py#L11-L28) · [Pinned evaluation](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/main.py#L141-L176)

Every one of the 1,486 archived prefix and suffix pairs was reconstructed from `test.xes` and its sample IDs. Using the code's last-prefix-event label makes 447 model inputs empty before padding. The label counts shift from 800 Accepted, 465 Completed, 216 Queued and 5 Unmatched with the first suffix event to 1,236 Accepted, 18 Completed, 227 Queued and 5 Unmatched with the last prefix event. An always-Accepted predictor on the last-prefix labels reproduces all ten archived metrics within `1e-15`, including the three shown in Table 2. On the correct next-event labels of those same archived samples, its accuracy is .538358 and weighted F1 is .376804. This reconstruction checks the published aggregates without executing the archived checkpoint. The source hashes, supports and exact metrics are in `data/raw/author-supplement/bpic13-cp-target-audit.json`.

The subsequent CPU replay loaded the actual archived TensorFlow SavedModel with its archived vocabulary and 35-token prepadding. It predicted Accepted for all 1,486 samples under both input conventions. All ten stored aggregates matched to within `1e-12` when the last prefix event was the target. Passing the full prefix and using the first suffix event instead gave precision .289829, accuracy .538358 and weighted F1 .376804. The result binds the archived model files, input archive, runtime versions and prediction counts in `artifacts/author-runtime/bpic13-cp-saved-model-audit-v2.json`. This verifies archived CPU inference on this cohort.

### CPU replay of all twelve Table 2 checkpoints

The isolated Python 3.7.12, TensorFlow 2.6.5 and Keras 2.6.0 runtime executed all twelve archived SavedModels. The replay verified the configured prefix-file path and exact population. For seven logs, the next-event target came from the suffix trace with the same sample ID. For the other five, the replay checked each `Case_i_j` prefix against the archived `test.xes` case at position `i` and took the label at index `j`. In the table, each pair is accuracy and weighted F1. The agreement column checks all ten archived aggregates to tolerance `1e-12`.

| Log | Archived prefixes | Archive | Last-prefix target replay | Next-event target replay | Stored aggregates |
|---|---:|---:|---:|---:|---|
| BPIC12 | 75,104 | .834070 / .801503 | .834070 / .801503 | .815616 / .778804 | 10 match |
| BPIC12_O | 7,681 | .927614 / .931827 | .927614 / .931827 | .825283 / .798047 | 10 match |
| BPIC12_W | 48,335 | .868584 / .870400 | .868584 / .870400 | .895935 / .895250 | 10 match |
| BPIC12_WC | 18,923 | .781113 / .752978 | .781113 / .752978 | .789674 / .772148 | 10 match |
| BPIC13_CP | 1,486 | .831763 / .755370 | .831763 / .755370 | .538358 / .376804 | 10 match |
| BPIC13-I | 17,580 | .687770 / .569349 | .687770 / .569349 | .674801 / .591128 | 10 match |
| Helpdesk | 5,025 | .786269 / .756574 | .787861 / .758117 | .798806 / .753561 | Mismatch |
| Sepsis | 4,154 | .513722 / .461106 | .396004 / .304944 | .336302 / .257073 | Mismatch |
| Complex-Model | 21,462 | .566862 / .506150 | .566862 / .506150 | .566862 / .506570 | 10 match |
| Long-Dist-Dep | 1,944 | .920267 / .894287 | .920267 / .894287 | 1.000000 / 1.000000 | 10 match |
| Looped-AND | 10,941 | .648295 / .642137 | .648295 / .642137 | .639704 / .615844 | 10 match |
| Sequence | 3,300 | 1.000000 / 1.000000 | 1.000000 / 1.000000 | 1.000000 / 1.000000 | 10 match |

The Helpdesk and Sepsis differences persisted when loading with `tf.keras.models.load_model(compile=False)` and calling the model with `training=False`. Within each of those logs, the Keras and serving-signature routes agree on both sets of metrics and predicted-class counts. The cause of their discrepancy from the stored aggregates remains unresolved. The next-event replay uses the archived checkpoints and archived sample populations. Exact member paths, checkpoint hashes, counts, loader receipts and metrics are under `artifacts/author-runtime/table2-replays/`. The consolidated comparison is `artifacts/author-runtime/table2-replay-comparison.json`.

A third CPU replay used the pinned author's `Transformer` as a Keras custom object and followed `Model.predict` with NumPy argmax. It reproduced both sets of metrics and predicted-class counts from the serving-signature replay for BPIC13-CP, Helpdesk and Sepsis. BPIC13-CP still matched the archive exactly. Helpdesk made 3,959 correct last-prefix predictions versus 3,951 implied by the archive. Sepsis made 1,645 versus 2,134. Even allowing each predicted class to map independently to its most frequent true class raises Sepsis to at most 1,707 correct on this cohort. A fixed relabeling of the CPU predictions therefore cannot account for the Sepsis discrepancy. The Sepsis replay had nine last-prefix top-two logit gaps at or below .001, and Helpdesk had zero at or below .01. These counts describe the CPU logits. The historical GPU logit values and run linkage remain unknown. Receipts are the three `*-keras-predict.json` files. [Pinned loading code](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/train_model.py#L91-L100) · [Pinned evaluation code](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/main.py#L139-L185)

All 5,025 archived Helpdesk and 4,154 archived Sepsis prefix traces already have nondecreasing timestamps. Stable time sorting changes no activity sequence or target. Timestamp ties involve distinct labels in two Helpdesk prefixes and 2,892 Sepsis prefixes, so a procedure that explicitly breaks ties could still change Sepsis inputs. Inspection of the pinned PM4Py 2.6.0 wheel shows it appends events in file order and defaults timestamp sorting to false in both default XES readers. The wheel hash, archive member paths and trace counts are recorded in `artifacts/author-runtime/table2-order-audit.json`. [PM4Py 2.6.0 wheel](https://pypi.org/project/pm4py/2.6.0/#files)

All twelve archived Table 2 configurations point to `test_pref.xes`. All twelve prefix files parse, and multiplying their row counts by the archived accuracies gives an integer within floating-point tolerance in every case. All prefix IDs and sequences align with the indexed `test.xes` cases for eleven logs. The BPIC12_WC archived `test.xes` is truncated before its closing log tag, while both prefix and suffix XES files parse and share all 18,923 sample IDs. This evidence is compatible with the configured evaluation populations. The comparison does not recover the models' row-level predictions. The local independent BPIC12_WC run uses the verified 4TU file and its own filters. Exact archive members, counts and the XML error are in `data/raw/author-supplement/table2-target-population-audit.json` and `bpic12-wc-archive-test-parse-audit.json` in the same directory.

A separate diagnostic checked the effect of target alignment with a fixed independent checkpoint. All official cases and activity sequences matched the union of the archived train and test files. The independent model used that split and the archived 5-epoch, batch-50 schedule. On the same 1,486 prefix IDs, scoring the next event after the full prefix gave weighted precision .517888, accuracy .539704 and weighted F1 .503921. Scoring the last prefix event from the shortened prefix gave .757282, .595559 and .660913, respectively. Sklearn reproduced both sets of scores. The input/target shift changes the task, and the comparison uses the independent model under both conventions. The primary independent split and evaluation are unchanged. [Diagnostic output](../../artifacts/bpic13-cp-v1/archive-split-diagnostic/target-comparison.json)

## Workload gates and streaming runs

Sepsis diagnostic pilot selected12 prefixes at deterministic length quantiles, including the length184 maximum. It completed286 contexts,433 forwards and63 cache hits in7.557264s, with process-lifetime peak working set382,783,488 bytes. k sample min/median/p95/max=0/5/89.3/174. This is deliberately stratified, not a representative estimate of the full k distribution. One observed prefix requires 2^175 contexts (about4.789×10^52); that alone is a lower bound for full-log AE. Exhaustive AE primary is computationally infeasible under the locked protocol. No global AE graph or primary nine-metric summary is exported from this pilot.

The BPIC13-CP pilot observed max k of 26 and 134,219,012 expected contexts across 12 selected prefixes. Its bounded run took 2.019184 seconds. The subsequent full BE pass established the full-log count of 809,189,178. The pilot's first numeric subsets of the mostly-masked arm cannot estimate a complete graph or full runtime.

Sepsis E1's bounded DFG path counter found at least 204,539 variants in the 12 sampled prefixes. Extending the capped count to all 4,479 test prefixes gave a lower bound of 44,724,588 variants, with 81 neighbor pairs censored. An exact count using memoized visited subsets for simple directed paths gave **2,425,371,457** scheduled variants after adding masks and boundary replacements and excluding identity paths. The count is recorded under `artifacts/sepsis-v1/E1-workload-counter.json`.

Streaming E1 completed two Sepsis sessions on this unchanged schedule: 10,000 variants followed by 5,000 new variants. The ledger occupies 22,151,168 bytes and contains two completed prefixes. The second session took 2.891 seconds. A linear projection from this early section is about 3.58 TB and 16.2 days at the measured wall rate. Prefix lengths, model cost, storage overhead and hardware contention vary, so this is only an order-of-magnitude estimate. Source and checkpoint identity and the quota stop are recorded in `artifacts/sepsis-v1/E1-stream-e1-run/progress.json`; estimates are in the sibling `workload-estimate.json`. No full-log Sepsis E1 correlation is available.

Full BPIC12 E1 has a verified lower bound of **2,440,580,925 variants** on 73,742 prefixes. The raw-XES scan rebuilt the fixed seed-42 split and training DFG. It counted every mask and boundary replacement, then retained only interior simple paths in the subgraph induced by the 14 highest-degree activities, excluding self-loops when ranking degree and breaking ties by label. Each retained neighbor-pair path count was weighted by its number of eligible occurrences in the test prefix set, with identity replacements removed. The schedule requires over 312 GB of logical text even if each persisted row contained only its 64-byte prefix ID and 64-byte record seal. The available project drive had under 44 GB free. The counter was a resource gate and yielded no E1 correlations. The activity subset and per-pair evidence are in `artifacts/bpic12-v1/E1-workload-lower-bound.json`.

The [replay command](COMMANDS.md) generated `artifacts/bpic12-v1/E1-workload-lower-bound-v2.json` directly from the same raw log. It reproduced all 67 pair-use and path counts, the boundary and identity adjustment and the total lower bound. The exact-count path also reproduced the BPIC12_O count of 67,722 with identical pair evidence.

BPIC12_W E1 completed its exact schedule of **1,334,973 variants** across 47,280 prefixes. The first session persisted 100,000 variants and finished 3,253 prefixes in 100.80 seconds. Resuming the same ledger with its original source and checkpoint added 1,234,973 variants in 1,185.77 seconds. The mean Kendall tau-b was .107094 with SD .800406 across 35,019 valid prefixes. The remaining 12,261 were undefined. The ledger audit reproduced the metrics, matched every variant to its affected position and checked the independently counted schedule. See `artifacts/bpic12-w-v1/E1-stream.json` and `artifacts/bpic12-w-v1/e1-record-audit.json`.

Exhaustive AE on BPIC12_O and BPIC13_CP is also storage-limited. From the verified BE records, the lower bound counts the 64-byte prefix ID in both the SQLite row and its JSON payload, the 64-byte payload checksum, and the occurrence ID characters stored once per prefix position per selected target. Each position is recorded on either the masked or visible side on every context. Multiplying by the exact per-prefix context counts gives at least **47,502,862,092 bytes** for BPIC12_O and **240,980,201,722 bytes** for BPIC13_CP before other payload fields, SQLite overhead and the inference cache. Both local drives had less than 42 GB free. Each log folder contains `ae-storage-bound.json`. The same computation on the completed Helpdesk baseline gives a 23,011,036-byte bound, below its observed 490,749,952-byte ledger size.

Even a BE-only XAI evaluation retains a 64-character ID for every perturbation on its fixed seed-404 cohort. The same induced-path bound, applied to that cohort, puts each of the following outputs beyond the available local disk space before any other field is counted.

| Log | Scheduled XAI prefixes | Minimum variants | Minimum ID bytes per method |
|---|---:|---:|---:|
| BPIC12 | 58,993 | 1,951,732,985 | 124,910,911,040 |
| Sepsis | 3,583 | 1,880,973,581 | 120,382,309,184 |
| Complex-Model | 17,244 | 12,630,132,171 | 808,328,458,944 |

The three sampled-prefix hashes match a separate reconstruction from the saved predictive cohorts. BPIC12_O served as a control: its sampled IDs match the completed evaluation and the bound equals its actual 54,573 variant records. Each log folder contains `xai-evaluation-workload-v2.json`. These counts establish a limit for the published per-variant output and yield no XAI metrics for the three storage-limited evaluations.

BPIC13-CP streaming E1 stopped after 17 variants and then completed all 15,569 variants on 1,574 prefixes. Every ordered variant record matched the original full E1 run. The compared importance vectors and tau-b scores also matched exactly. The completed manifest is `artifacts/bpic13-cp-v1/E1-stream.json`.

| Log and study | Completed units | Measured result | Evidence under `artifacts/` |
|---|---:|---|---|
| Sepsis E3-PAPER | 4,479/4,479 prefixes | Mean prefix TVD .157010, SD .174390 | `sepsis-v1/E3-stream.json` |
| Sepsis E2-FC | 44,790/44,790 model–prefix pairs | Mean JSD across each seed's cohort ranged .026494–.037467 for BASE and .02068012–.02068065 for FC. Mean TVD ranged .109344–.141047 and .119721–.169451, respectively. | `sepsis-v1/E2-stream.json` |
| Sepsis BE | 4,479/4,479 prefixes | Global graph with 14 nodes and 16 directed edges | `sepsis-v1/graphs/BE-v2/manifest.json` |
| Sepsis AE | 0 of approximately 9.5781 × 10^52 contexts | Exact full-set schedule computed from complete BE, with k min/median/p95/max 0/5/29.1/174 | `sepsis-v1/be-only-v1/coverage.json` |
| BPIC13-CP E1 | 1,574/1,574 prefixes, 15,569 variants | Mean tau-b .245327, SD .940071, 856 valid and 718 undefined | `bpic13-cp-v1/E1.json` |
| BPIC13-CP E2-FC | 15,740/15,740 paired prefix records | Seed mean JSD .007405–.024901 for BASE and .00482464–.00482480 for FC. Seed mean prediction TVD .048891–.082763 for BASE and .050001–.095071 for FC | `bpic13-cp-v1/E2-stream.json` |
| BPIC13-CP E3-PAPER | 1,574/1,574 prefixes | Mean prefix TVD .222190, SD .178234 | `bpic13-cp-v1/E3-stream.json` |
| BPIC13-CP BE | 1,574/1,574 prefixes | Global graph with 3 nodes and 5 directed edges | `bpic13-cp-v1/graphs/BE/manifest.json` |
| BPIC13-CP AE | 1/809,189,178 contexts | Incomplete. The BE pass established the exact workload over all test prefixes | `bpic13-cp-v1/explain-v1/coverage.json` |
| BPIC13 incidents E1 | 17,402/17,402 prefixes, 304,355 variants | Mean tau-b .699499, SD .644450, 12,498 valid and 4,904 undefined | `bpic13-i-v1/E1-stream.json` |
| BPIC13 incidents E2-FC | 174,020/174,020 model–prefix pairs | Mean JSD across the five BASE seeds ranged .169220–.215760 and mean TVD .052379–.057158. The five FC seeds ranged .21339337–.21339381 for mean JSD and .085113–.104775 for mean TVD. | `bpic13-i-v1/E2-stream.json` |
| BPIC13 incidents E3 | 17,402/17,402 prefixes | Mean prefix TVD .152617, SD .158701 | `bpic13-i-v1/E3-stream.json` |
| BPIC13 incidents BE | 17,402/17,402 prefixes | Six directed edges. The independent graph audit rebuilt a schedule of 15,950,735,951,275,900,776,544,602,750,118,088,858 AE contexts with a maximum of 121 eligible positions. | `bpic13-i-v1/be-only-v1/graph-audit.json` |
| BPIC12_O E1 | 7,763/7,763 prefixes, 67,722 variants | Mean tau-b .712442, SD .370154, 6,197 valid and 1,566 undefined | `bpic12-o-v1/E1-stream.json` |
| BPIC12_O E2-FC | 77,630/77,630 paired prefix records | Seed mean JSD .002668–.003713 for BASE and .00163521–.00163549 for FC. Seed mean prediction TVD .025136–.055303 for BASE and .026869–.039663 for FC | `bpic12-o-v1/E2-stream.json` |
| BPIC12_O E3-PAPER | 7,763/7,763 prefixes | Mean prefix TVD .384329, SD .309039. All records passed the streamed-study audit | `bpic12-o-v1/E3-stream.json` |
| BPIC12_WC E3-PAPER | 18,472/18,472 prefixes | Mean prefix TVD .111464, SD .179748. All records passed the streamed-study audit | `bpic12-wc-v1/E3-stream.json` |
| BPIC12_W E3-PAPER | 47,280/47,280 prefixes | Mean prefix TVD .087629, SD .183354. The audit also verified all 774,557 masked occurrences | `bpic12-w-v1/E3-stream.json` |
| BPIC12_WC BE | 18,472/18,472 prefixes | 13 directed edges. Run time 496.78 seconds and 115,562 model forwards | `bpic12-wc-v1/be-audit.json` |
| BPIC12_WC AE | 0 of 56,330,420,007,228,581,540 contexts | Full BE replay verified this exact schedule. The largest prefix has 64 eligible positions. Exhaustive execution is infeasible on the available hardware. | `bpic12-wc-v1/be-only-v1/coverage.json` |
| BPIC12_O BE | 7,763/7,763 prefixes | Global graph with 7 nodes and 12 directed edges | `bpic12-o-v1/graphs/BE/manifest.json` |
| BPIC12_O AE | 0/113,657,644 contexts | Exact workload established from the full BE pass | `bpic12-o-v1/be-only-v1/coverage.json` |
| BPIC12_WC E1 | 18,472/18,472 prefixes, 280,907 variants | Mean tau-b .780294, SD .377938, 13,370 valid and 5,102 undefined | `bpic12-wc-v1/E1-stream.json` |
| Helpdesk E1 | 4,983/4,983 prefixes, 390,254 variants | Mean tau-b .903136, SD .236441, 3,497 valid and 1,486 undefined | `helpdesk-v1/E1-stream.json` |
| Helpdesk E2-FC | 49,830/49,830 paired records | Mean JSD across each model's cohort ranged .022445–.029539 for BASE and .078434–.078435 for FC. Mean prediction TVD ranged .026770–.072433 and .027586–.056758, respectively. | `helpdesk-v1/E2-stream.json` |
| Helpdesk E3 | 4,983/4,983 prefixes | Mean prefix TVD .310606, SD .227002 | `helpdesk-v1/E3-stream.json` |

BPIC13 incidents E1 stopped after 236,445 variants at the 240-second session limit. The saved source from commit `e67565b` was used to resume. The second session added 67,910 variants in 57.25 seconds. The final ledger SHA-256, checkpoint SHA-256, per-prefix SQLite row counts and exact schedule count agree with the manifest.

BPIC13 incidents E3 completed 9,915 prefixes before its first 300-second quota, then 7,487 more in 282.28 seconds. The auditor verified every sealed prefix unit and reconstructed the reported summary. BPIC12_O graph edge membership matched the GraphML export and the SVG was visually checked.

BPIC13 incidents E2 completed across three sessions. A wall-time stop preserved 93,307 pairs, a RAM-floor stop added 24,251, and the final session added 56,462. The independent audit verified all ten modified checkpoints, each arm's exact test cohort, every record checksum and all aggregates and attention bins. The reported results are descriptive. See `artifacts/bpic13-i-v1/e2-record-audit.json`.

The BPIC13 incidents BE export has three nodes and six directed edges, including three self-loops. All six arrowheads and the three activity labels are visible in `artifacts/graph-qa/bpic13-i-BE.png`. The GraphML, graph JSON and SVG hashes match the export receipt. The three verified BPIC12_O studies were also plotted and visually checked. The plots and exact ten-seed E2 CSV are under `artifacts/figures/bpic12-o-v1/`.

The completed BPIC12_WC E1 and Helpdesk E3 results passed the streamed-study audit, including prepared and checkpoint hashes, full cohort membership, every SQLite record seal and reconstructed summaries. The independent exact schedule count also matched all BPIC12_WC E1 variants.

BPIC12_O E2 resumed under the identical source snapshot after a quota stop at 54,341 records. The second session added 23,289 records in 326.53 seconds. The auditor verified all ten arms and model checkpoints. Helpdesk E1 passed the same artifact audit and matched its independently computed variant count.

Sepsis E3 stopped at 1,199 prefixes after its first 180-second quota. The second session resumed from the exact source snapshot, preserving prior units. Total wall time across these sessions was 608.32 seconds. BPIC13-CP E2 used five fresh BASE and five frozen-constant seeds, with 10 epochs each. Figure files in `artifacts/figures/bpic13-cp-v2/` show the E1 distribution, the descriptive E2 scatter and the E3 distribution. Its CSV preserves the ten exact seed means when markers overlap.

Sepsis E2 completed in 966.89 seconds. Its ledger audit verified all ten model checkpoints, the entire cohort for every arm and seed, and the recomputed maximum-attention bins and TVD filters. Frozen-constant comparisons had lower attention JSD across all ten seed means and overlapping prediction TVD ranges with BASE. These are descriptive results for the independent models. See `artifacts/sepsis-v1/e2-record-audit.json`.

BPIC12_WC E3 completed 7,185, 8,394 and 2,893 new records across three sessions. The first session stopped at the available-RAM floor and the second at its wall-time quota. The final session used the identical source snapshot and completed all remaining units. The independent ledger audit verified coverage and aggregation from the 18,472 records in `artifacts/bpic12-wc-v1/e3-record-audit.json`.

BPIC12_W E3 completed 28,007, 11,186 and 8,087 prefixes across three sessions, preserving the same source, dataset and checkpoint. Total recorded run time was 3,362.57 seconds. The final audit verified all prefixes, matched each intervention to its prepared occurrence ID and recomputed every TVD from its two stored prediction vectors. The occurrence-weighted mean is .022465 and median .003584, compared with the primary equal-prefix mean of .087629. Evidence is in `artifacts/bpic12-w-v1/e3-record-audit.json`.

The BPIC13-CP discrepancy was also probed against author commit `494b315a555e713bdd61f0edd7d033c31d5850bf`. `processtransformer/ml/prepare/splitter.py` lines 34–39 and 111–119 shuffle case IDs in log order and take the first floor(0.7 × N) cases for training. Applying that procedure with seed 42 to the acquired log yields the same 447 test cases as the independent sorted-ID protocol. Only 129 of those cases occur in the test XES recovered from the author archive. A separate diagnostic kept the local split, architecture, Adam settings and training seed, and used 5 epochs and batch 50. Accuracy was .559720 and weighted F1 was .517447 on all 1,574 prefixes (`artifacts/bpic13-cp-v1/source-schedule/predictions.json`). Both evaluation population and target alignment differ from the archive.

## Helpdesk paired explanation evaluation

The official-data Helpdesk run completed E1–E3 and the full paired BE–AE evaluation. E2 stopped at the available-RAM floor after 40,492 records. The second session reused the same source and checkpoints and completed the final 9,338 records. All ten arm cohorts and their SQLite receipts were verified. The E1–E3 plots and ten-seed CSV are in `artifacts/figures/helpdesk-v1/`.

The baseline and chosen candidate were both explained on all 4,983 test prefixes. The Co03 schedule selected seed 3001, with weight distance .219357, from five verified candidate checkpoints. The graph audit replayed 107,602 baseline and 138,990 candidate AE contexts and regenerated both AE matrices from the sealed votes. The baseline BE and AE graphs contain 19 and 18 directed edges. Both SVGs were rendered and visually inspected. The separate metric cohort contains 3,986 prefixes selected with seed 404, with results paired on each output's valid intersection.

| Metric | Valid pairs | BE mean | AE mean | AE − BE |
|---|---:|---:|---:|---:|
| Correctness | 2,784 | .840080 | −.137458 | −.977538 |
| Completeness precision | 3,986 | .481276 | .313421 | −.167855 |
| Completeness recall | 3,986 | .868038 | .999875 | .131836 |
| Completeness F1 | 3,986 | .561468 | .466782 | −.094686 |
| Consistency | 3,958 | .640121 | .611902 | −.028219 |
| Continuity | 2,874 | .594932 | .645188 | .050256 |
| Contrastivity | 3,981 | .668752 | .538978 | −.129774 |
| Compactness rules | 3,986 | 2.217260 | 2.213748 | −.003512 |
| Compactness RHS | 3,986 | 2.339641 | 4.386436 | 2.046795 |

On this cohort, AE's recall is higher and BE's precision and F1 are higher. The published Helpdesk rows also favor BE on precision and F1, but give AE a lower recall (.25 versus .30) and a positive correctness mean (.73 versus .91). Those archived aggregates have different populations and settings, including 100 weighted completeness rows per method and 390/396 valid correctness records for AE. The paired differences above are descriptive and use the independent baseline, split and locked metric definitions. Evidence includes the two graph audit receipts and `artifacts/helpdesk-v1/evaluation-paired/evaluation-audit.json`.

## BPIC13-CP BE explanation evaluation

The BE-only evaluation completed all 1,259 scheduled metric prefixes (floor of 80% of 1,574, seed 404). Both graphs were built on the full test prefix set, using prefix activities and model predictions. None of the observed next-event targets entered BE rule construction. The run reused the baseline graph after validating its checksum, dataset, checkpoint and coverage. From five candidates, the largest trainable-weight distance was .189723 for seed 3005. The selected candidate's BE graph also completed the full test prefix set. The run left 809,086,778 candidate AE contexts pending and reports no paired AE–BE statistics.

| BE metric | Independent mean | Sample SD | Valid / scheduled | Published BE mean ± SD |
|---|---:|---:|---:|---:|
| Correctness | −.093826 | .979988 | 643 / 1,259 | .75 ± .18 |
| Completeness precision | .863384 | .235893 | 1,259 / 1,259 | .74 ± .23 |
| Completeness recall | .742123 | .198694 | 1,259 / 1,259 | .46 ± .11 |
| Completeness F1 | .777019 | .177182 | 1,259 / 1,259 | .50 ± .14 |
| Consistency | .988437 | .022998 | 1,207 / 1,259 | .59 ± .18 |
| Continuity | .608514 | .404096 | 1,259 / 1,259 | .49 ± .13 |
| Contrastivity | .614959 | .263102 | 779 / 1,259 | .05 ± .20 |
| Compactness rules | 1.585385 | .573370 | 1,259 / 1,259 | 2.16 ± .53 |
| Compactness RHS | 1.737490 | .256072 | 1,259 / 1,259 | .60 ± .20 |

The published BE column comes from the supplied QA-corrected evidence matrix, sheet “Bảng 3,” BPIC13_CP rows 8, 20, 32, 44, 56, 68, 80, 92 and 104, which reference printed page 34. The correctness mean has opposite signs in the two evaluations. The independent contrastivity mean excludes 480 undefined prefixes from its scheduled 1,259. The pinned author file `processtransformer/xai/metrics/contrastivity_co05.py` (lines 74, 95–107) defaults to cosine distance .25 and returns zero when no eligible variant survives. The independent protocol uses cosine similarity below .8 and leaves an empty far group undefined. The archived denominators and observed zero values are documented below. [Paper](https://link.springer.com/article/10.1007/s44311-025-00018-4)

The pinned author Co01 implementation computes cosine distances between vectors of consequent-activity counts for its explanation-side importance. Its shared importance function uses the first 20 artificial variants and initializes a score for every input-vocabulary entry. The locked independent Co01 instead averages `1 − Jaccard` on directed-edge projections over all shared E1 variants and ranks the activities present in the prefix. Both report Kendall correlation, but their inputs differ. That source-level difference is one reason the archived and independent correctness means are descriptive comparisons. Its contribution to the observed sign differences has not been isolated. [Pinned Co01 calculation](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/xai/metrics/correctness_co01.py#L96-L123) · [Pinned importance function](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/xai/metrics/feature_importance.py#L66-L137)

Among eligible BPIC13-CP consistency pairs, 0/1,207 had both projected graphs empty. The same count was 0/10,736 near and 0/1,737 far variant pairs. Global BE compactness was three rules with mean RHS 1.666667. The per-prefix mean F1 is based on per-prefix scores. The sealed output, graph receipt hashes, cohort membership, eligibility and null reasons are under `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json`.

### BPIC12_O BE-only evaluation

The independent run evaluated BE on the fixed seed-404 sample of 6,210 of 7,763 test prefixes. The audit recomputed all five Co03 model distances and verified the selection of seed 3001, distance .210044. The baseline and candidate BE graphs cover all 7,763 prefixes, with 12 and 13 directed edges respectively. Their recorded AE schedules remain unexecuted. The candidate alone would require at least 77,629,668,696 bytes of context text. See `artifacts/bpic12-o-v1/evaluation-be/evaluation-audit.json` and `candidate-graph-audit.json` in the same directory.

| Metric | Independent BE mean ± sample SD | Valid / scheduled | Table 3 BE mean ± sample SD |
|---|---:|---:|---:|
| Correctness | .300379 ± .537334 | 4,989 / 6,210 | .48 ± .22 |
| Completeness precision | .258248 ± .183438 | 6,210 / 6,210 | .11 ± .03 |
| Completeness recall | .724316 ± .396750 | 6,210 / 6,210 | .18 ± .03 |
| Completeness F1 | .358011 ± .218308 | 6,210 / 6,210 | .13 ± .02 |
| Consistency | .352596 ± .079037 | 4,073 / 6,210 | .65 ± .07 |
| Continuity | .718998 ± .147671 | 4,988 / 6,210 | .95 ± .07 |
| Contrastivity | .503752 ± .196505 | 6,210 / 6,210 | .07 ± .18 |
| Compactness, rules | 2.930435 ± 1.289098 | 6,210 / 6,210 | 4.61 ± .55 |
| Compactness, mean RHS size | 2.089581 ± .180565 | 6,210 / 6,210 | 2.56 ± .06 |

The archived completeness means use 100 weighted rows per method. The 400 archived correctness rows have 265 valid values for BE, and consistency uses 125 values. The differences in cohort, checkpoint and metric procedures limit the comparison to descriptive values. The independent run has no AE evaluation or paired differences.

### BPIC13 incidents BE-only evaluation

The completed run uses 13,921 prefixes sampled with seed 404 from all 17,402 test prefixes. Co03 selected seed 3004 with trainable-weight distance .283060 among five candidates. The baseline and candidate BE graphs both cover the full test set and each has six edges. The XAI auditor verified checkpoint hashes, all five distances, the sampled IDs, graph projections and overlaps, the nine per-prefix metric derivations, nulls and aggregate summaries. The selected candidate graph passed its separate graph and exhaustive-AE workload audit. Receipts are `artifacts/bpic13-i-v1/evaluation-be/evaluation-audit.json` and `candidate-audit.json`.

| Metric | Independent BE mean ± sample SD | Valid / scheduled | Table 3 BE mean ± sample SD |
|---|---:|---:|---:|
| Correctness | .247242 ± .931498 | 9,387 / 13,921 | NaN |
| Completeness precision | .733999 ± .303686 | 13,921 / 13,921 | .35 ± .05 |
| Completeness recall | .987680 ± .080022 | 13,921 / 13,921 | .26 ± .04 |
| Completeness F1 | .799195 ± .226498 | 13,921 / 13,921 | .29 ± .04 |
| Consistency | .837638 ± .108410 | 13,551 / 13,921 | .01 ± .02 |
| Continuity | .786360 ± .295812 | 13,921 / 13,921 | .19 ± .24 |
| Contrastivity | .589046 ± .198655 | 13,049 / 13,921 | .04 ± .18 |
| Compactness, rules | 1.869262 ± .641481 | 13,921 / 13,921 | 1.38 ± .49 |
| Compactness, mean RHS size | 2.246785 ± .475583 | 13,921 / 13,921 | .19 ± .24 |

The archived correctness output has zero finite values among 400 rows; NaN remains undefined. Archived completeness uses 100 weighted rows, consistency has 178 values, and continuity, contrastivity and compactness each have 400. These populations, metric procedures and checkpoints differ from the independent run. The table supplies descriptive comparisons and establishes neither improvement nor statistical significance. The candidate's exhaustive AE schedule is approximately 1.595 × 10^37 contexts, with a maximum of 121 eligible positions. AE metrics and paired method differences remain unevaluated.

### Table 3 archive reconciliation

Recomputed all 216 AE/BE mean and sample-SD pairs from the archived CSVs across twelve logs and nine outputs. Every pair matches the supplied QA-corrected evidence matrix after rounding to two decimals. Missing values stay missing, including sample SD when only one finite observation exists. The audit records each CSV path and hash, source column, workbook row and hash, row count, finite count, zero count and both aggregates in `data/raw/author-supplement/table3-reconciliation.json`. [Author archive](https://drive.google.com/file/d/1p-mbznaXoYI0ofqlzKGPzJ1FVcAX0Pg4/view)

The paper's text says AE consistently has higher completeness precision. The reconciled rounded Table 3 means favor AE on eight logs and BE on four. The latter are BPIC12 (.20 BE, .18 AE), Helpdesk (.54, .50), LDD (.30, .10) and Sequence (.32, .11). This contradicts the universal wording in the text. These are comparisons of descriptive means. The archived aggregates do not establish statistical significance. See `artifacts/author-runtime/table3-precision-claims-audit.json`. [Paper](https://link.springer.com/article/10.1007/s44311-025-00018-4)

| Table 3 output | Archived CSV | Column used |
|---|---|---|
| Correctness | `correctness_co01.csv` | `kendalltau-corr` |
| Completeness precision/recall/F1 | `completeness_co02_combined.csv` | `precision_weighted`, `recall_weighted`, `f_weighted` |
| Consistency | `consistency_co03_complete.csv` | `relaxed_consistency` |
| Continuity | `continuity_co04.csv` | `threshold_less_sim` |
| Contrastivity | `contrastivity_co05.csv` | `diff_sim` |
| Compactness | `compactness_co07.csv` | `num_rules`, `avg_right_side_length` |

For BPIC13_CP, the contrastivity CSV contains 400 rows per method. In each, exactly 373 rows have no eligible variants and record a score of zero. The published means include these rows. The 27 retained nonzero rows are the rest of each file. Completeness has 100 weighted rows per method, while correctness has 125/398 finite AE values and 397/398 finite BE values. These denominators are established for the archived results. The independent protocol reports per-prefix completeness and treats no eligible contrastivity variants as undefined. Comparisons use descriptive context and keep the two aggregation rules distinct.

Author-runtime parity and prediction-to-checkpoint linkage remain unverified.

## Author-supplied synthetic benchmarks

All four independent baselines used the same primary CPU training schedule as the real-log baselines. The prediction audit matched every case ID, prefix ID, observed target and checkpoint hash and reproduced weighted metrics using sklearn. Sequence and Long-Dist-Dep each reach perfect held-out accuracy on this split. Sequence has one activity sequence across all 1,000 cases. The 3,300 prefixes therefore come from repeated sequences and do not test generalization to new variants. [Dataset provenance](DATASET_PROVENANCE.md)

| Log | Test prefixes | Weighted precision | Accuracy | Weighted F1 | Training wall seconds |
|---|---:|---:|---:|---:|---:|
| Sequence | 3,300 | 1.000000 | 1.000000 | 1.000000 | 19.83 |
| Long-Dist-Dep | 1,957 | 1.000000 | 1.000000 | 1.000000 | 11.16 |
| Complex-Model | 21,555 | .590404 | .594897 | .556404 | 191.97 |
| Looped-AND | 10,873 | .743368 | .655753 | .607638 | 143.52 |

| Log | E1 variants and mean tau-b | E2 paired prefix records and seed mean JSD | E3 mean prefix TVD | BE edges | AE contexts and edges |
|---|---|---|---|---:|---|
| Sequence | 19,800 variants, .450363 over 3,000/3,300 valid prefixes | 33,000, BASE .004178–.008270 and FC .00474030–.00474037 | .086950 on 3,300 prefixes | 13 | 137,344/137,344, 45 edges |
| Long-Dist-Dep | 9,356 variants, .814777 over 1,657/1,957 valid prefixes | 19,570, BASE .00013762–.00037796 and FC .00010379–.00010382 | .141284 on 1,957 prefixes | 11 | 67,290/67,290, 35 edges |

The tables use `artifacts/synthetic-{sequence,long-dist-dep,complex-model,looped-and}/`. Sequence E2 resumed from 32,336 records, adding the final 664. All six E1–E3 manifests for Sequence and Long-Dist-Dep passed the streamed-study audit. For both baselines, `explainer-audit.json` records hashes of the BE/AE artifacts and ledger. The audit replayed BE merges and pruning and checked every AE subset key, intervention mask, vote occurrence and checksum before regenerating the aggregate matrices and graph from the stored votes.

The measured E1–E3 plots for both logs are in `artifacts/figures/synthetic-sequence/` and `artifacts/figures/synthetic-long-dist-dep/`. The PNGs were visually checked. Each plot folder contains SVGs, a ten-seed E2 CSV and source-hash manifest. Very small Sequence E2 TVDs plot close to the horizontal zero line. The CSV retains all ten exact values.

### E2 maximum-attention diagnostic

The pinned author code takes the raw modified attention maximum before L1 normalization, computes JSD after normalization, and retains a record for the author's bin plot only when prediction TVD ≤ .1. The independent E2 stores both maxima and the filter flag on every pair. The bins below follow the author's edges at .25, .50 and .75, with 1 in the top bin. [Pinned source](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/xai/metrics/attn_uniform_weights.py#L89-L119)

| Log | Raw maximum, all pairs | L1-normalized maximum, all pairs | Raw maximum, TVD ≤ .1 |
|---|---|---|---|
| Sequence | 13,500 / 12,000 / 3,900 / 3,600 | 30,000 / 3,000 / 0 / 0 | 13,500 / 12,000 / 3,900 / 3,600 |
| Long-Dist-Dep | 7,422 / 6,148 / 3,000 / 3,000 | 16,570 / 3,000 / 0 / 0 | 7,422 / 6,148 / 3,000 / 3,000 |
| BPIC12_O | 14,991 / 29,309 / 18,255 / 15,075 | 62,580 / 15,050 / 0 / 0 | 11,035 / 26,428 / 17,143 / 15,061 |
| Helpdesk | 1,995 / 9,192 / 7,443 / 31,200 | 36,090 / 13,740 / 0 / 0 | 1,420 / 8,877 / 7,045 / 30,046 |
| Looped-AND | 89,665 / 9,765 / 4,650 / 4,650 | 104,080 / 4,650 / 0 / 0 | 80,801 / 9,515 / 3,519 / 4,185 |

The raw and normalized summaries place the same pairs in different bins. The archived violin input audit below checks the author's binned rows. The independent counts are in each log's `E2-bin-audit.json` or `e2-record-audit.json`.

For Helpdesk, a second pass over the 49,830 verified E2 records recomputed the bins and TVD filter. Within the filtered cohort, 23,214 BASE and 6,832 frozen-constant records are in the highest raw bin. No record reaches that bin after L1 normalization. The receipt includes separate counts for both arms and the hash of the audited ledger.

### Archived preliminary-study results

The pinned supplement contains 96 CSVs for E1–E3 across twelve logs. The auditor checked their hashes and recomputed the stored quantiles. It found 15,391 finite Kendall correlations among 15,521 E1 rows, five `seed` and five `uniform` E2 model summary rows per log, and 397,068 occurrence-level E3 TVDs. The author's `violins()` reads each `attn_uniform_weights_attn.csv` directly. Every stored raw maximum maps to its recorded bin. From low to high, the pooled counts are **37,280 / 600 / 154 / 43,507**, with 99.08% in the extremes. The CSVs contain the retained JSD values and raw maxima. They omit pair-level TVD and model identity, so filter membership and model-specific counts cannot be recalculated from them. The combined Figure 5 SVG is absent from the supplement. [Paper Figure 5](https://link.springer.com/article/10.1007/s44311-025-00018-4#Fig5) · [Pinned plotting source](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/xai/metrics/run_exp/replot_nn_exps.py#L144-L176)

Archived E1 median tau is .639763 for Helpdesk, .680000 for Looped-AND and .677296 for Sequence. The archived E2 mean prediction TVD across the five `seed` models is .00002087 on Sequence and .00013651 on Long-Dist-Dep. The independent studies also found small mean prediction changes for these two logs. The pinned study runner builds a distinct-sequence pool and samples indices with replacement, with an upper limit of 2,000 draws. The archived CSVs omit the sampled prefix IDs. The independent protocol preserves every scheduled test-prefix ID and uses a frozen-constant arm, so differences between the two sets of statistics remain descriptive. The archive receipt is `artifacts/author-runtime/prestudy-archive-audit.json`. [Pinned sampling source](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/xai/metrics/run_through_nn_metrics.py#L118-L130)

For E3, the archive records one TVD per masked occurrence. The independent primary summary weights prefixes equally. A separate audit matched every audited masking position to its prepared occurrence ID and recomputed each TVD from the two stored prediction vectors. Pooling these TVDs gives the same unit of aggregation as the archive, while the cohort and masking differences remain. The separate values are in each log's `e3-occurrence-audit.json`. [Pinned E3 aggregation](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/xai/metrics/attn_masking.py#L32-L58)

| Log | Independent masked occurrences | Independent pooled median TVD | Archived masked occurrences | Archived pooled median TVD |
|---|---:|---:|---:|---:|
| Helpdesk | 12,547 | .129620 | 2,918 | .056731 |
| BPIC12_O | 31,039 | .071677 | 6,376 | .003090 |
| BPIC12_W | 774,557 | .003584 | 81,777 | .006551 |
| BPIC12_WC | 143,848 | .011058 | 39,060 | .001788 |
| BPIC13_CP | 6,243 | .055525 | 5,955 | .003920 |
| BPIC13 incidents | 146,211 | .017057 | 41,902 | .003688 |
| Sepsis | 60,338 | .022247 | 45,126 | .006061 |
| Complex-Model | 196,047 | .016654 | 29,575 | .003593 |
| Sequence | 19,800 | .00000645 | 61 | .0000286 |
| Long-Dist-Dep | 7,399 | .000238 | 53 | .001476 |
| Looped-AND | 164,829 | .009520 | 52,825 | .000089 |

All eleven independent rows above passed occurrence-ID alignment and per-occurrence TVD recomputation, followed by exact reconstruction of the stored prefix summaries. The occurrence-weighted distributions supplement the primary equal-prefix summaries. The archived values describe different sampled cohorts and the source masking implementation.

Seven logs also passed direct comparison with the full baseline attention tensors already retained in their closed BE caches: BPIC13-CP, BPIC12_O, Helpdesk, Sepsis, Sequence, Long-Dist-Dep and Looped-AND. Across 34,929 prefixes and 302,195 masking occurrences, the auditor reconstructed all recorded attention displacement fields, including the row-normalized TVDs, from those tensors. These `e3-attention-reference-audit.json` receipts add explicit baseline-tensor references and cache hashes without duplicating arrays or rerunning inference. This additional check remains pending for the other logs.

The completed BPIC13 incidents E1–E3 figures are in `artifacts/figures/bpic13-i-v1/`. All seven PNG, SVG and CSV digests and the three source-manifest digests match the sealed figure manifest. The three PNGs were visually inspected: axes, units and titles are readable, E1 identifies its 12,498 valid correlations out of 17,402 prefixes, and E3 identifies equal-prefix weighting. The E2 seed points are descriptive; overlapping markers do not establish statistical significance. The companion CSV preserves all ten exact seed values.

### Sequence BPMN comparison

The archived `longer_sequence.bpmn` contains 12 tasks and no gateways. The diagnostic maps each BPMN name `X` to the XES activity label `Activity X` and takes the 11 direct task-to-task sequence flows. After excluding the start and end events, those flows match the complete observed activity sequence in both independent splits. BE shares 10 edges with the reference, adds 3 and misses 1 (Jaccard .714286). AE shares all 11 and adds 34 (Jaccard .244444). The edge lists and exact source hashes are in `artifacts/synthetic-sequence/bpmn-structure.json`. This checks agreement with the reference sequence. An explainer edge can also encode an earlier activity's contribution to a later prediction. Human interpretability remains untested.

The four Sequence and Long-Dist-Dep SVGs were rendered in Chromium and visually inspected. Node labels and arrowheads are visible. The 45-edge and 35-edge AE layouts have intersecting arcs, so use GraphML or canonical edge JSON for exact edge inspection. Screenshots are in `artifacts/graph-qa/`.

### Sequence paired explanation evaluation

The complete Sequence benchmark was repeated through the single `pipeline --streaming` entry point with package snapshot `9bf57f8`. All nine stages completed. The repeat reproduced the prepared bytes, all 3,300 prediction rows, E1 records, E2/E3 summaries and all per-prefix BE/AE metrics and paired differences from the standalone benchmark. Both graph ledgers passed the independent context and matrix audit, with 137,344 baseline and 111,848 candidate contexts. Every recorded stage-file digest matched, including the 6,619 evaluation files and both SQLite ledgers. A repeated pipeline invocation verified its receipts and returned completed. The new SVGs were rendered and visually checked, with intersecting arcs in the dense AE graph. Evidence is under `artifacts/pipeline-synthetic-sequence/`, including `completion-audit.json`, `evaluation-audit.json` and the two graph audit receipts.

All nine outputs were computed for both methods on the same scheduled 2,640 prefixes, sampled with seed 404 from the full test population of 3,300. The selected Co03 candidate was seed 3005 with trainable-weight distance .207027 among five candidates. Baseline and candidate both used the full 3,300-prefix set for building global graphs, with all 137,344 and 111,848 AE contexts respectively. The evaluation reused a checked copy of the baseline ledger. Replaying it reproduced the matrices and edges, with new session telemetry. The audit verified both graph receipts, all candidate checkpoints and distances, sampled IDs, null reasons, per-method aggregates and valid paired intersections. Evidence is in `artifacts/synthetic-sequence/evaluation-paired/` with `evaluation.json`, `evaluation-audit.txt` and `candidate-audit.json`.

| Metric | AE mean ± SD (valid) | BE mean ± SD (valid) | Mean AE − BE (paired valid) |
|---|---:|---:|---:|
| Correctness | −.774227 ± .134631 (2,392) | .049301 ± .369469 (2,158) | −.799047 (2,158) |
| Completeness precision | .111637 ± .013629 (2,640) | .185818 ± .128661 (2,640) | −.074182 (2,640) |
| Completeness recall | 1.000000 ± .000000 (2,640) | .906061 ± .291800 (2,640) | .093939 (2,640) |
| Completeness F1 | .200579 ± .022155 (2,640) | .295173 ± .169606 (2,640) | −.094594 (2,640) |
| Consistency | .966199 ± .019801 (1,944) | .560626 ± .263475 (1,944) | .405572 (1,944) |
| Continuity | .784384 ± .130907 (2,392) | .805111 ± .115979 (2,392) | −.020727 (2,392) |
| Contrastivity | .198419 ± .204070 (2,640) | .254989 ± .207372 (2,640) | −.056569 (2,640) |
| Compactness rules | 6.007576 ± 3.190185 (2,640) | 6.007576 ± 3.190185 (2,640) | .000000 (2,640) |
| Compactness RHS | 5.828341 ± 1.245948 (2,640) | 1.205007 ± .108382 (2,640) | 4.623334 (2,640) |

Table 3's Sequence completeness F1 is .10 AE and .15 BE, each from one weighted aggregate row per method. Other archived Sequence outputs have at most 12 values per method. The independent measures are computed per prefix, with repeated activity sequences and the locked independent model, graph and split. The directions agree for completeness F1 and differ for consistency. The descriptive paired estimates give no significance or human interpretability result.

### Long-Dist-Dep paired evaluation and BPMN branch relations

The same paired protocol scheduled 1,565 of the 1,957 test prefixes. Seed 3003 had the greatest distance (.190390) among the five candidates. The baseline and candidate both completed full BE and AE, with 67,290 and 70,224 AE contexts respectively. Replayed baseline matrices, candidate context coverage, checkpoint receipts and every metric's valid intersection passed the audits in `artifacts/synthetic-long-dist-dep/evaluation-paired/`.

| Metric | AE mean ± SD (valid) | BE mean ± SD (valid) | Mean AE − BE (paired valid) |
|---|---:|---:|---:|
| Correctness | −.067322 ± .617188 (1,322) | −.409638 ± .464575 (1,322) | .342316 (1,322) |
| Completeness precision | .144409 ± .045285 (1,565) | .225119 ± .148779 (1,565) | −.080710 (1,565) |
| Completeness recall | 1.000000 ± .000000 (1,565) | .844728 ± .362279 (1,565) | .155272 (1,565) |
| Completeness F1 | .249826 ± .064405 (1,565) | .343773 ± .197638 (1,565) | −.093947 (1,565) |
| Consistency | .920365 ± .101513 (1,209) | .290109 ± .177200 (1,209) | .630256 (1,209) |
| Continuity | .604513 ± .274281 (1,565) | .558685 ± .294891 (1,565) | .045828 (1,565) |
| Contrastivity | .351526 ± .199944 (1,565) | .344284 ± .148823 (1,565) | .007242 (1,565) |
| Compactness rules | 3.765495 ± 1.901160 (1,565) | 3.765495 ± 1.901160 (1,565) | .000000 (1,565) |
| Compactness RHS | 5.056966 ± .573565 (1,565) | 1.319013 ± .263617 (1,565) | 3.737954 (1,565) |

The BPMN's parallel-gateway paths imply two selected long-range branch relations, `A → D` and `B → E`. All 157 held-out traces ending with a branch activity follow these two relations, with 74 `A … D` and 83 `B … E`. The other 143 held-out traces end at `Z`. AE contains both selected edges and BE contains neither. Neither method contains the cross-branch pairs `A → E` and `B → D`. The diagnostic checks these selected relations and retains the event counts and graph/BPMN hashes in `artifacts/synthetic-long-dist-dep/bpmn-long-range.json`.

### Complex-Model and Looped-AND workload gates

| Log | Audited BE prefixes and global edges | Exact E1 variants | Exact AE contexts | Largest AE eligibility size |
|---|---|---:|---:|---:|
| Complex-Model | 21,555 prefixes, 26 edges | 15,755,268,423 | 405,840,441,072,787,719,568 | 64 |
| Looped-AND | 10,873 prefixes, 10 edges | 734,926 | 1,219,192,350,409,752,944,173,595,276 | 88 |

The BE-only runs took 937.51 seconds and 729.06 seconds, respectively. The audit reopened both graph artifacts, replayed merge/pruning on the complete cohorts and rebuilt the planned AE schedules. Both schedules have zero executed AE contexts. Exhaustive AE is infeasible locally for these two logs. The Complex-Model E1 count exceeds the Sepsis workload by more than sixfold. The Looped-AND E1 schedule is small enough for a bounded streaming run. Evidence is in each log folder's `explainer-audit.json`, `explain/coverage.json` and `E1-workload-counter.json`.

Looped-AND E1 completed all 734,926 variants on 10,873 test prefixes after resuming from 298,414 variants at the first wall-time quota. Mean Kendall tau-b was .762740 with SD .213582 across 10,408 valid prefixes. The remaining 465 correlations were undefined. The auditor reopened the complete ledger, checked every variant and summary, and matched the independent workload counter. Evidence is in `artifacts/synthetic-looped-and/E1-stream.json` and `artifacts/synthetic-looped-and/e1-record-audit.json`.

Looped-AND E2-FC completed all 108,730 model–prefix pairs. The first session ran 1,800.34 seconds and persisted 90,056 rows. The second resumed the same ledger and added 18,674 rows in 304.70 seconds. Across five BASE seeds, mean JSD ranged .00065410–.00115739 and mean prediction TVD ranged .033617–.050431. The five frozen-constant comparisons had mean JSD .00064209–.00064241 and mean prediction TVD .027979–.062216. The audit verified all ten checkpoints, prefix membership, checksums, aggregates and attention bins. See `artifacts/synthetic-looped-and/e2-record-audit.json`.

Looped-AND E3-PAPER completed all 10,873 test prefixes in 672.84 seconds. The mean prefix prediction TVD was .078025 with SD .115340. The independent audit checked the exact prepared cohort, checkpoint and every SQLite record seal, then recomputed the summary. See `artifacts/synthetic-looped-and/E3-stream.json` and `artifacts/synthetic-looped-and/e3-record-audit.json`.

Complex-Model E3-PAPER completed all 21,555 test prefixes, with mean prediction TVD .135959 and SD .240711. The first session stopped at the RAM floor after 1,803 prefixes. Resuming with the same source and checkpoint added the remaining 19,752, for 608.21 seconds of total run time. The ledger audit verified every record and reproduced the summary. See `artifacts/synthetic-complex-model/E3-stream.json` and `artifacts/synthetic-complex-model/e3-record-audit.json`.

The author's Complex-Model qualitative case names the relation between activity sets `{K,P,F,D}` and `{S,R,Q}`. All seven labels appear in the archived BPMN. The independent BE graph has `K → Q`, `K → R` and `K → S` between the named sets. The archive text specifies a group relation. The check records which independent pairwise edges connect those sets, without assuming a complete Cartesian product or running a BPMN conformance analysis. Source member `Detailed_Results/14_complex_models/complex_model_001/complex_model_001-visual_001/ground_truth_relations.txt`. [Author archive](https://drive.google.com/file/d/1p-mbznaXoYI0ofqlzKGPzJ1FVcAX0Pg4/view)

The archived BPMN has parallel splits after `D` and `P`. On the 1,500 independent Complex-Model test cases, the first events after `D` were `E`, `H` and `P` in 511, 480 and 509 cases respectively. Each case placed `P` before all three nested branches `Q`, `R` and `S`. The independent BE graph retained `A → B` and `B → C` and omitted all six of these selected split edges. The author's qualitative comparison reports both explanation graphs recovering the split after `D`. The independent BE also has a self-loop `A → A`, with zero direct `A → A` pairs in the test cohort. This comparison concerns selected process relations and separate trained models. [Paper Figure 12](https://link.springer.com/article/10.1007/s44311-025-00018-4#Fig12) · [Paper Figure 13](https://link.springer.com/article/10.1007/s44311-025-00018-4#Fig13)

On Looped-AND, all 465 independent test cases follow the BPMN's `A`, parallel loop, `Z` structure. Every iteration has `I` before `J` and `M` before `N`, with the two branches interleaved. There are 464 cases with two or more iterations. BE retains both within-branch edges and omits the selected exits `J → Z` and `N → Z`, which occur directly 244 and 221 times. Its four self-loops on `I`, `J`, `M` and `N` do not occur as direct pairs. Repeated activities across iterations remain possible. The [replay command](COMMANDS.md) checks the BPMN topology, exact test cohort, verified BE graph and observed counts. See `artifacts/bpmn-complex-looped-audit.json`. [Paper Figure 15](https://link.springer.com/article/10.1007/s44311-025-00018-4#Fig15)

Both BE SVGs were rendered and inspected. The original Looped-AND drawing had overlapping nodes. The revised circular layout and loop curves show the five nodes and all four self-loop arrowheads. `artifacts/synthetic-looped-and/graphs/BE-v3/` has identical canonical graph JSON and GraphML hashes to the original export. The checked screenshot is `artifacts/graph-qa/synthetic-looped-and-BE-v3.png`.
