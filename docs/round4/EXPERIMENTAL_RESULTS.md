# Round 4 experimental results

Software fixture integration is complete, including E1–E3, BE/AE and all nine XAI outputs. Seven real-log and four author-supplied synthetic-log baselines have executed on verified inputs. Full twelve-log reproduction remains incomplete. The primary schedule and diagnostic profiles are defined in Round 3 and Round 3.6. Every result below retains its own dataset, split, source and checkpoint identity.

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
| BPIC12 O | 7,763/7,763 | .8249324235 | .8191420842 | .7993637164 | 53.697025 |
| BPIC12 W | 47,280/47,280 | .8840351369 | .8821277496 | .8803739866 | 800.939466 |
| BPIC12 WC | 18,472/18,472 | .7770249616 | .7877327848 | .7704196948 | 184.164754 |
| Helpdesk | 4,983/4,983 | .8164058218 | .7967088100 | .7516142831 | 35.086813 |

Artifacts: artifacts/sepsis-v1/base and predictions.json; artifacts/bpic13-cp-v1/base and predictions.json. Raw acquisition and file/count checks are described in DATASET_PROVENANCE.md. No test targets were used for fitting or class-vocabulary construction.

BPIC13 incidents outputs use the same paths under `artifacts/bpic13-i-v1/`. Checkpoint SHA-256 and all target/prefix IDs were verified. Independent sklearn metrics agreed with the sealed record. Paper Table 2 gives precision/accuracy/F1 of .50/.69/.57 for BPIC13-I. The local weighted F1 gap is approximately +.0994 on the independent split, with historical checkpoint linkage still unknown.

BPIC12_O outputs use `artifacts/bpic12-o-v1/`. The CLI passed the expected input hash and count checks. It retained 31,244 out of 262,200 source events with prefix `O_`, removing 8,072 of 13,087 cases. The 7,763 prediction IDs and targets matched the prepared split exactly, and sklearn reproduced the metrics. Published precision/accuracy/F1 are .96/.93/.93. The local F1 difference is −.1306 on the independent split.

BPIC12_W outputs use `artifacts/bpic12-w-v1/`. A second XES scan reconstructed all 47,280 test prefix IDs and observed labels from the official raw archive and independent case split. It matched every prediction row, checked the checkpoint hash and reproduced the metrics with sklearn. The audit is in `prediction-audit.json`.

BPIC12_WC outputs use `artifacts/bpic12-wc-v1/`. The 18,472 prediction IDs, targets and checkpoint hash match the prepared data and baseline. Sklearn reproduced the reported metrics. Paper Table 2 gives precision/accuracy/F1 of .75/.78/.75. The local F1 difference is approximately +.0204 on the independent split.

Helpdesk outputs use `artifacts/helpdesk-v1/`. All 4,983 prediction IDs, targets, checkpoint hash and sklearn scores matched. Paper Table 2 gives .74/.79/.76, with a local weighted F1 difference of about −.0084. The XES input agrees event by event with the official data on model fields. The historical run linkage remains unverified. The independent E1 workload counter reports 390,254 variants for this split.

For descriptive context, the supplied paper's Table 2, printed page 30, reports weighted precision/accuracy/weighted F1 of (.49, .51, .46) for Sepsis and (.69, .83, .76) for BPIC13_CP. Against the printed values, local F1 differences are +.1151 and −.2382, respectively. Source implementation, split/seed, masking and other protocol decisions differ, so these differences are descriptive. The local table extract is retained in `artifacts/paper-table2-page30.txt`. [Paper](https://link.springer.com/article/10.1007/s44311-025-00018-4)

### Table 2 archive reconciliation

All 36 printed values match the author archive's `precision_weighted`, `accuracy` and `f1_weighted` fields after rounding to two decimals. The exact member names, member SHA-256 and unrounded numbers are in `data/raw/author-supplement/table2-reconciliation.json`. The matching files are under `Supplementary_Material/Trained_Models/`: `training_<log>_GPU/metrics.json` for the eight real-log rows and `training_{complex_model,long_dist_dep,looped_and,sequence}/metrics.json` for the four synthetic rows. The log directory names for BPIC13 are `bpic13_closed_problems` and `bpic13_incidents`. Both Helpdesk variants in the archive give the same rounded row, so the printed precision does not identify a unique run. [Author archive](https://drive.google.com/file/d/1p-mbznaXoYI0ofqlzKGPzJ1FVcAX0Pg4/view)

The BPIC13_CP GPU metrics are .691829892 weighted precision, .831763122 accuracy and .755370477 weighted F1. The archived run configuration records 5 epochs, batch size 50, learning rate .001 and GPU index 0. Its `result.csv` contains one newline and no prediction rows. Aggregate agreement with Table 2 verifies the values. The checkpoint-to-prediction linkage remains open.

### BPIC13_CP target alignment

The archived GPU configuration selects `test_pref.xes`. The pinned sampler writes the observed history to `test_pref.xes` and the next event starts `test_suf.xes`. The pinned evaluation calls `extract_traces_and_ypred_from_xes`, which returns `(trace[:-1], trace[-1])` from the configured file. With that configuration, it predicts the last event of each archived prefix using the preceding events. The independent evaluation predicts the first suffix event using the full prefix. [Pinned sampler](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/ml/core/sample_creator.py#L26-L37) · [Pinned trace utility](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/processtransformer/util/trace_util.py#L11-L28) · [Pinned evaluation](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/main.py#L141-L176)

Every one of the 1,486 archived prefix and suffix pairs was reconstructed from `test.xes` and its sample IDs. Using the code's last-prefix-event label makes 447 model inputs empty before padding. The label counts shift from 800 Accepted, 465 Completed, 216 Queued and 5 Unmatched with the first suffix event to 1,236 Accepted, 18 Completed, 227 Queued and 5 Unmatched with the last prefix event. An always-Accepted predictor on the last-prefix labels reproduces all ten archived metrics within `1e-15`, including the three shown in Table 2. On the correct next-event labels of those same archived samples, its accuracy is .538358 and weighted F1 is .376804. This reconstruction checks the published aggregates without executing the archived checkpoint. The source hashes, supports and exact metrics are in `data/raw/author-supplement/bpic13-cp-target-audit.json`.

All twelve archived Table 2 configurations point to `test_pref.xes`. All twelve prefix files parse, and multiplying their row counts by the archived accuracies gives an integer within floating-point tolerance in every case. All prefix IDs and sequences align with the indexed `test.xes` cases for eleven logs. The BPIC12_WC archived `test.xes` is truncated before its closing log tag, while both prefix and suffix XES files parse and share all 18,923 sample IDs. This evidence is compatible with the configured evaluation populations. The comparison does not recover the models' row-level predictions. The local independent BPIC12_WC run uses the verified 4TU file and its own filters. Exact archive members, counts and the XML error are in `data/raw/author-supplement/table2-target-population-audit.json` and `bpic12-wc-archive-test-parse-audit.json` in the same directory.

A separate diagnostic checked the effect of target alignment with a fixed independent checkpoint. All official cases and activity sequences matched the union of the archived train and test files. The independent model used that split and the archived 5-epoch, batch-50 schedule. On the same 1,486 prefix IDs, scoring the next event after the full prefix gave weighted precision .517888, accuracy .539704 and weighted F1 .503921. Scoring the last prefix event from the shortened prefix gave .757282, .595559 and .660913, respectively. Sklearn reproduced both sets of scores. The input/target shift changes the task, and the comparison uses the independent model under both conventions. The primary independent split and evaluation are unchanged. [Diagnostic output](../../artifacts/bpic13-cp-v1/archive-split-diagnostic/target-comparison.json)

## Workload gates and streaming runs

Sepsis diagnostic pilot selected12 prefixes at deterministic length quantiles, including the length184 maximum. It completed286 contexts,433 forwards and63 cache hits in7.557264s, with process-lifetime peak working set382,783,488 bytes. k sample min/median/p95/max=0/5/89.3/174. This is deliberately stratified, not a representative estimate of the full k distribution. One observed prefix requires 2^175 contexts (about4.789×10^52); that alone is a lower bound for full-log AE. Exhaustive AE primary is computationally infeasible under the locked protocol. No global AE graph or primary nine-metric summary is exported from this pilot.

The BPIC13-CP pilot observed max k of 26 and 134,219,012 expected contexts across 12 selected prefixes. Its bounded run took 2.019184 seconds. The subsequent full BE pass established the full-log count of 809,189,178. The pilot's first numeric subsets of the mostly-masked arm cannot estimate a complete graph or full runtime.

Sepsis E1's bounded DFG path counter found at least 204,539 variants in the 12 sampled prefixes. Extending the capped count to all 4,479 test prefixes gave a lower bound of 44,724,588 variants, with 81 neighbor pairs censored. An exact count using memoized visited subsets for simple directed paths gave **2,425,371,457** scheduled variants after adding masks and boundary replacements and excluding identity paths. The count is recorded under `artifacts/sepsis-v1/E1-workload-counter.json`.

Streaming E1 completed two Sepsis sessions on this unchanged schedule: 10,000 variants followed by 5,000 new variants. The ledger occupies 22,151,168 bytes and contains two completed prefixes. The second session took 2.891 seconds. A linear projection from this early section is about 3.58 TB and 16.2 days at the measured wall rate. Prefix lengths, model cost, storage overhead and hardware contention vary, so this is only an order-of-magnitude estimate. Source and checkpoint identity and the quota stop are recorded in `artifacts/sepsis-v1/E1-stream-e1-run/progress.json`; estimates are in the sibling `workload-estimate.json`. No full-log Sepsis E1 correlation is available.

BPIC13-CP streaming E1 stopped after 17 variants and then completed all 15,569 variants on 1,574 prefixes. Every ordered variant record matched the original full E1 run. The compared importance vectors and tau-b scores also matched exactly. The completed manifest is `artifacts/bpic13-cp-v1/E1-stream.json`.

| Log and study | Completed units | Measured result | Evidence under `artifacts/` |
|---|---:|---|---|
| Sepsis E3-PAPER | 4,479/4,479 prefixes | Mean prefix TVD .157010, SD .174390 | `sepsis-v1/E3-stream.json` |
| Sepsis BE | 4,479/4,479 prefixes | Global graph with 14 nodes and 16 directed edges | `sepsis-v1/graphs/BE-v2/manifest.json` |
| Sepsis AE | 0 of approximately 9.5781 × 10^52 contexts | Exact full-set schedule computed from complete BE, with k min/median/p95/max 0/5/29.1/174 | `sepsis-v1/be-only-v1/coverage.json` |
| BPIC13-CP E1 | 1,574/1,574 prefixes, 15,569 variants | Mean tau-b .245327, SD .940071, 856 valid and 718 undefined | `bpic13-cp-v1/E1.json` |
| BPIC13-CP E2-FC | 15,740/15,740 paired prefix records | Seed mean JSD .007405–.024901 for BASE and .00482464–.00482480 for FC. Seed mean prediction TVD .048891–.082763 for BASE and .050001–.095071 for FC | `bpic13-cp-v1/E2-stream.json` |
| BPIC13-CP E3-PAPER | 1,574/1,574 prefixes | Mean prefix TVD .222190, SD .178234 | `bpic13-cp-v1/E3-stream.json` |
| BPIC13-CP BE | 1,574/1,574 prefixes | Global graph with 3 nodes and 5 directed edges | `bpic13-cp-v1/graphs/BE/manifest.json` |
| BPIC13-CP AE | 1/809,189,178 contexts | Incomplete. The BE pass established the exact workload over all test prefixes | `bpic13-cp-v1/explain-v1/coverage.json` |
| BPIC13 incidents E1 | 17,402/17,402 prefixes, 304,355 variants | Mean tau-b .699499, SD .644450, 12,498 valid and 4,904 undefined | `bpic13-i-v1/E1-stream.json` |
| BPIC13 incidents E3 | 17,402/17,402 prefixes | Mean prefix TVD .152617, SD .158701 | `bpic13-i-v1/E3-stream.json` |
| BPIC12_O E1 | 7,763/7,763 prefixes, 67,722 variants | Mean tau-b .712442, SD .370154, 6,197 valid and 1,566 undefined | `bpic12-o-v1/E1-stream.json` |
| BPIC12_O E2-FC | 77,630/77,630 paired prefix records | Seed mean JSD .002668–.003713 for BASE and .00163521–.00163549 for FC. Seed mean prediction TVD .025136–.055303 for BASE and .026869–.039663 for FC | `bpic12-o-v1/E2-stream.json` |
| BPIC12_O E3-PAPER | 7,763/7,763 prefixes | Mean prefix TVD .384329, SD .309039. All records passed the streamed-study audit | `bpic12-o-v1/E3-stream.json` |
| BPIC12_O BE | 7,763/7,763 prefixes | Global graph with 7 nodes and 12 directed edges | `bpic12-o-v1/graphs/BE/manifest.json` |
| BPIC12_O AE | 0/113,657,644 contexts | Exact workload established from the full BE pass | `bpic12-o-v1/be-only-v1/coverage.json` |
| BPIC12_WC E1 | 18,472/18,472 prefixes, 280,907 variants | Mean tau-b .780294, SD .377938, 13,370 valid and 5,102 undefined | `bpic12-wc-v1/E1-stream.json` |
| Helpdesk E1 | 4,983/4,983 prefixes, 390,254 variants | Mean tau-b .903136, SD .236441, 3,497 valid and 1,486 undefined | `helpdesk-v1/E1-stream.json` |
| Helpdesk E3 | 4,983/4,983 prefixes | Mean prefix TVD .310606, SD .227002 | `helpdesk-v1/E3-stream.json` |

BPIC13 incidents E1 stopped after 236,445 variants at the 240-second session limit. The saved source from commit `e67565b` was used to resume. The second session added 67,910 variants in 57.25 seconds. The final ledger SHA-256, checkpoint SHA-256, per-prefix SQLite row counts and exact schedule count agree with the manifest.

BPIC13 incidents E3 completed 9,915 prefixes before its first 300-second quota, then 7,487 more in 282.28 seconds. The auditor verified every sealed prefix unit and reconstructed the reported summary. BPIC12_O graph edge membership matched the GraphML export and the SVG was visually checked.

The completed BPIC12_WC E1 and Helpdesk E3 results passed the streamed-study audit, including prepared and checkpoint hashes, full cohort membership, every SQLite record seal and reconstructed summaries. The independent exact schedule count also matched all BPIC12_WC E1 variants.

BPIC12_O E2 resumed under the identical source snapshot after a quota stop at 54,341 records. The second session added 23,289 records in 326.53 seconds. The auditor verified all ten arms and model checkpoints. Helpdesk E1 passed the same artifact audit and matched its independently computed variant count.

Sepsis E3 stopped at 1,199 prefixes after its first 180-second quota. The second session resumed from the exact source snapshot, preserving prior units. Total wall time across these sessions was 608.32 seconds. BPIC13-CP E2 used five fresh BASE and five frozen-constant seeds, with 10 epochs each. Figure files in `artifacts/figures/bpic13-cp-v2/` show the E1 distribution, the descriptive E2 scatter and the E3 distribution. Its CSV preserves the ten exact seed means when markers overlap.

The BPIC13-CP discrepancy was also probed against author commit `494b315a555e713bdd61f0edd7d033c31d5850bf`. `processtransformer/ml/prepare/splitter.py` lines 34–39 and 111–119 shuffle case IDs in log order and take the first floor(0.7 × N) cases for training. Applying that procedure with seed 42 to the acquired log yields the same 447 test cases as the independent sorted-ID protocol. Only 129 of those cases occur in the test XES recovered from the author archive. A separate diagnostic kept the local split, architecture, Adam settings and training seed, and used 5 epochs and batch 50. Accuracy was .559720 and weighted F1 was .517447 on all 1,574 prefixes (`artifacts/bpic13-cp-v1/source-schedule/predictions.json`). Both evaluation population and target alignment differ from the archive.

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

Among eligible consistency pairs, 0/1,207 had both projected graphs empty. The same count was 0/10,736 near and 0/1,737 far variant pairs. Global BE compactness was three rules with mean RHS 1.666667. The per-prefix mean F1 is based on per-prefix scores. The sealed output, graph receipt hashes, cohort membership, eligibility and null reasons are under `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json`.

### Table 3 archive reconciliation

Recomputed all 216 AE/BE mean and sample-SD pairs from the archived CSVs across twelve logs and nine outputs. Every pair matches the supplied QA-corrected evidence matrix after rounding to two decimals. Missing values stay missing, including sample SD when only one finite observation exists. The audit records each CSV path and hash, source column, workbook row and hash, row count, finite count, zero count and both aggregates in `data/raw/author-supplement/table3-reconciliation.json`. [Author archive](https://drive.google.com/file/d/1p-mbznaXoYI0ofqlzKGPzJ1FVcAX0Pg4/view)

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

The raw and normalized summaries place the same pairs in different bins. The archive contains rendered maximum-attention plots, while the exact generating records for the paper's Figure 5 remain unverified. The independent counts are in each log directory's `E2-bin-audit.json`.

### Sequence BPMN comparison

The archived `longer_sequence.bpmn` contains 12 tasks and no gateways. The diagnostic maps each BPMN name `X` to the XES activity label `Activity X` and takes the 11 direct task-to-task sequence flows. After excluding the start and end events, those flows match the complete observed activity sequence in both independent splits. BE shares 10 edges with the reference, adds 3 and misses 1 (Jaccard .714286). AE shares all 11 and adds 34 (Jaccard .244444). The edge lists and exact source hashes are in `artifacts/synthetic-sequence/bpmn-structure.json`. This checks agreement with the reference sequence. An explainer edge can also encode an earlier activity's contribution to a later prediction. Human interpretability remains untested.

The four Sequence and Long-Dist-Dep SVGs were rendered in Chromium and visually inspected. Node labels and arrowheads are visible. The 45-edge and 35-edge AE layouts have intersecting arcs, so use GraphML or canonical edge JSON for exact edge inspection. Screenshots are in `artifacts/graph-qa/`.

### Sequence paired explanation evaluation

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

The author's Complex-Model qualitative case names the relation between activity sets `{K,P,F,D}` and `{S,R,Q}`. All seven labels appear in the archived BPMN. The independent BE graph has `K → Q`, `K → R` and `K → S` between the named sets. The archive text specifies a group relation. The check records which independent pairwise edges connect those sets, without assuming a complete Cartesian product or running a BPMN conformance analysis. Source member `Detailed_Results/14_complex_models/complex_model_001/complex_model_001-visual_001/ground_truth_relations.txt`. [Author archive](https://drive.google.com/file/d/1p-mbznaXoYI0ofqlzKGPzJ1FVcAX0Pg4/view)

Both BE SVGs were rendered and inspected. The original Looped-AND drawing had overlapping nodes. The revised circular layout and loop curves show the five nodes and all four self-loop arrowheads. `artifacts/synthetic-looped-and/graphs/BE-v3/` has identical canonical graph JSON and GraphML hashes to the original export. The checked screenshot is `artifacts/graph-qa/synthetic-looped-and-BE-v3.png`.
