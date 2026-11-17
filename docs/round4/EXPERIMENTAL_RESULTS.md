# Round 4 experimental results

Software fixture integration is complete, including E1–E3, BE/AE and all nine XAI outputs. Six real-data baselines have executed on verified inputs. Full twelve-log reproduction remains incomplete. The primary schedule and diagnostic profiles are defined in Round3 and Round3.6. Every result below retains its own dataset, split, source and checkpoint identity.

| Component | Execution status | Evidence |
|---|---|---|
| E1 Feature Correlation | Fixture executed on 3 test prefixes | artifacts/fixture/E1.json, tau-b null for all 3 single-label universes |
| E2 Attention Parameter Manipulation | Fixture BASE vs 5 fresh BASE and 5 FC, all 10 epochs | artifacts/fixture/E2.json and E2-models/, 10 pairs × 3 prefixes |
| E3 Attention Score Masking | Fixture E3-PAPER executed | artifacts/fixture/E3.json, mean prefix TVD 0.21716457605361938 |
| BE | Full fixture global graph executed | artifacts/pipeline-fixture-v2/evaluation/baseline-graphs/BE.json |
| AE | Full fixture contexts/votes/matrices completed; interrupted resume verified | artifacts/pipeline-fixture-v2/evaluation/baseline-graphs/AE.json and ledger.sqlite |
| Predictive and XAI evaluation | Full fixture complete, five Co03 candidates and nine outputs | artifacts/pipeline-fixture-v2/evaluation/evaluation.json |

Published BPIC12 BE #rules 13.04 ± 2.03 and AE 6.32 ± 1.11 are comparison references, not locally generated measurements. Full paper provenance and exact Helpdesk/synthetic identities remain subject to dataset gates.

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
| BPIC12 WC | 18,472/18,472 | .7770249616 | .7877327848 | .7704196948 | 184.164754 |
| Helpdesk | 4,983/4,983 | .8164058218 | .7967088100 | .7516142831 | 35.086813 |

Artifacts: artifacts/sepsis-v1/base and predictions.json; artifacts/bpic13-cp-v1/base and predictions.json. Raw acquisition and file/count checks are described in DATASET_PROVENANCE.md. No test targets were used for fitting or class-vocabulary construction.

BPIC13 incidents outputs use the same paths under `artifacts/bpic13-i-v1/`. Checkpoint SHA-256 and all target/prefix IDs were verified. Independent sklearn metrics agreed with the sealed record. Paper Table 2 gives precision/accuracy/F1 of .50/.69/.57 for BPIC13-I. The local weighted F1 gap is approximately +.0994 on the independent split, with historical checkpoint linkage still unknown.

BPIC12_O outputs use `artifacts/bpic12-o-v1/`. The CLI passed the expected input hash and count checks. It retained 31,244 out of 262,200 source events with prefix `O_`, removing 8,072 of 13,087 cases. The 7,763 prediction IDs and targets matched the prepared split exactly, and sklearn reproduced the metrics. Published precision/accuracy/F1 are .96/.93/.93. The local F1 difference is −.1306 on the independent split.

BPIC12_WC outputs use `artifacts/bpic12-wc-v1/`. The 18,472 prediction IDs, targets and checkpoint hash match the prepared data and baseline. Sklearn reproduced the reported metrics. Paper Table 2 gives precision/accuracy/F1 of .75/.78/.75. The local F1 difference is approximately +.0204 on the independent split.

Helpdesk outputs use `artifacts/helpdesk-v1/`. All 4,983 prediction IDs, targets, checkpoint hash and sklearn scores matched. Paper Table 2 gives .74/.79/.76, with a local weighted F1 difference of about −.0084. The XES input agrees event by event with the official data on model fields. The historical run linkage remains unverified. The independent E1 workload counter reports 390,254 variants for this split.

For descriptive context, the supplied paper's Table2, printed page30, reports precision/accuracy/F1=(.49,.51,.46) for Sepsis and (.69,.83,.76) for BPIC13_CP. Local F1 differences are +.1151 and −.2382, respectively. These are not controlled improvements/regressions or significance results: source implementation, split/seed, masking and other locked protocol decisions differ, and the historical training artifacts are unavailable. The BPIC13 gap needs investigation before making fidelity-to-paper claims. Local extraction is retained in artifacts/paper-table2-page30.txt; the successful extraction used installed fontTools and produced no parser warning. [Paper](https://link.springer.com/article/10.1007/s44311-025-00018-4)

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
| BPIC12_O BE | 7,763/7,763 prefixes | Global graph with 7 nodes and 12 directed edges | `bpic12-o-v1/graphs/BE/manifest.json` |
| BPIC12_O AE | 0/113,657,644 contexts | Exact workload established from the full BE pass | `bpic12-o-v1/be-only-v1/coverage.json` |

BPIC13 incidents E1 stopped after 236,445 variants at the 240-second session limit. The saved source from commit `e67565b` was used to resume. The second session added 67,910 variants in 57.25 seconds. The final ledger SHA-256, checkpoint SHA-256, per-prefix SQLite row counts and exact schedule count agree with the manifest.

BPIC13 incidents E3 completed 9,915 prefixes before its first 300-second quota, then 7,487 more in 282.28 seconds. The auditor verified every sealed prefix unit and reconstructed the reported summary. BPIC12_O graph edge membership matched the GraphML export and the SVG was visually checked.

Sepsis E3 stopped at 1,199 prefixes after its first 180-second quota. The second session resumed from the exact source snapshot, preserving prior units. Total wall time across these sessions was 608.32 seconds. BPIC13-CP E2 used five fresh BASE and five frozen-constant seeds, with 10 epochs each. Figure files in `artifacts/figures/bpic13-cp-v2/` show the E1 distribution, the descriptive E2 scatter and the E3 distribution. Its CSV preserves the ten exact seed means when markers overlap.

The BPIC13-CP discrepancy was probed against author commit `494b315a555e713bdd61f0edd7d033c31d5850bf`. `processtransformer/ml/prepare/splitter.py` lines 34–39 and 111–119 shuffle case IDs in log order and take the first floor(0.7 × N) cases for training. Applying that procedure with seed 42 to the acquired log yields the same 447 test cases as the independent sorted-ID protocol. The pinned `experiments/training/exp_bpic13_closed_problems.json` specifies 5 epochs and batch 50. A separate diagnostic kept the local dataset split, architecture, Adam settings and training seed, and adopted that schedule. Accuracy was .559720 and weighted F1 was .517447 on all 1,574 prefixes (`artifacts/bpic13-cp-v1/source-schedule/predictions.json`). This schedule alone does not close the gap to Table 2. The author's historical run configuration and checkpoint linkage remain unresolved.

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

The published BE column comes from the supplied QA-corrected evidence matrix, sheet “Bảng 3,” BPIC13_CP rows 8, 20, 32, 44, 56, 68, 80, 92 and 104, which reference printed page 34. Comparison is descriptive. The correctness direction differs, and the independent contrastivity mean has 480 undefined prefixes. The pinned author file `processtransformer/xai/metrics/contrastivity_co05.py` (lines 74, 95–107) defaults to cosine distance .25 and returns zero when no eligible variant survives. The independent protocol uses cosine similarity below .8 and leaves an empty far group undefined. That difference can affect the mean; the historical settings and denominators used to generate Table 3 remain unverified. [Paper](https://link.springer.com/article/10.1007/s44311-025-00018-4)

Among eligible consistency pairs, 0/1,207 had both projected graphs empty. The same count was 0/10,736 near and 0/1,737 far variant pairs. Global BE compactness was three rules with mean RHS 1.666667. The per-prefix mean F1 is based on per-prefix scores. The sealed output, graph receipt hashes, cohort membership, eligibility and null reasons are under `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json`.

Author-runtime parity, historical run linkage, BPMN alignment and human evaluation remain unverified. Model fidelity and structural agreement remain separate claims.
