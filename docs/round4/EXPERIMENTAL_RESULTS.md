# Round 4 experimental results

Software fixture integration is complete, including E1–E3, BE/AE and all nine XAI outputs. Two official real-data baselines and bounded pilots have executed. Full twelve-log reproduction remains incomplete. The primary schedule and diagnostic profiles are defined in Round3 and Round3.6. Every result below retains its own dataset, split, source and checkpoint identity.

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

Both use the verified official version1 originals, activity-only labels, case-level random70/30 seed42 and train seed1729; CPU float32,10 epochs,batch12,Adam lr.001. These are independent splits and implementations, not recovered author checkpoints.

| Log | Test prefixes completed/expected | Weighted precision | Accuracy/weighted recall | Weighted F1 | Training wall seconds |
|---|---:|---:|---:|---:|---:|
| Sepsis | 4,479/4,479 | .6445562480 | .6070551462 | .5750634064 | 88.211886 |
| BPIC13 closed problems | 1,574/1,574 | .4916116862 | .5654383736 | .5217793991 | 19.217390 |

Artifacts: artifacts/sepsis-v1/base and predictions.json; artifacts/bpic13-cp-v1/base and predictions.json. Raw acquisition and file/count checks are described in DATASET_PROVENANCE.md. No test targets were used for fitting or class-vocabulary construction.

For descriptive context, the supplied paper's Table2, printed page30, reports precision/accuracy/F1=(.49,.51,.46) for Sepsis and (.69,.83,.76) for BPIC13_CP. Local F1 differences are +.1151 and −.2382, respectively. These are not controlled improvements/regressions or significance results: source implementation, split/seed, masking and other locked protocol decisions differ, and the historical training artifacts are unavailable. The BPIC13 gap needs investigation before making fidelity-to-paper claims. Local extraction is retained in artifacts/paper-table2-page30.txt; the successful extraction used installed fontTools and produced no parser warning. [Paper](https://link.springer.com/article/10.1007/s44311-025-00018-4)

## Workload gates and streaming runs

Sepsis diagnostic pilot selected12 prefixes at deterministic length quantiles, including the length184 maximum. It completed286 contexts,433 forwards and63 cache hits in7.557264s, with process-lifetime peak working set382,783,488 bytes. k sample min/median/p95/max=0/5/89.3/174. This is deliberately stratified, not a representative estimate of the full k distribution. One observed prefix requires 2^175 contexts (about4.789×10^52); that alone is a lower bound for full-log AE. Exhaustive AE primary is computationally infeasible under the locked protocol. No global AE graph or primary nine-metric summary is exported from this pilot.

BPIC13-CP diagnostic pilot has k sample max26 and expected contexts134,219,012 across just12 selected prefixes. Its bounded run took2.019184s. Full-log expected contexts remain unknown. Do not extrapolate a complete graph or a full-runtime estimate from the first numeric subsets of the mostly-masked arm.

Sepsis E1's bounded DFG path counter found at least204,539 variants in the12 sampled prefixes and hit the per-neighbor path-count cap. This is a censored workload count, not an E1 measurement or an exhaustive upper bound. Full E1 requires streaming/checkpointing at variant level before a large run.

| Log and study | Completed units | Measured result | Evidence under `artifacts/` |
|---|---:|---|---|
| Sepsis E3-PAPER | 4,479/4,479 prefixes | Mean prefix TVD .157010, SD .174390 | `sepsis-v1/E3-stream.json` |
| BPIC13-CP E1 | 1,574/1,574 prefixes, 15,569 variants | Mean tau-b .245327, SD .940071, 856 valid and 718 undefined | `bpic13-cp-v1/E1.json` |
| BPIC13-CP E2-FC | 15,740/15,740 paired prefix records | Seed mean JSD .007405–.024901 for BASE and .00482464–.00482480 for FC. Seed mean prediction TVD .048891–.082763 for BASE and .050001–.095071 for FC | `bpic13-cp-v1/E2-stream.json` |
| BPIC13-CP E3-PAPER | 1,574/1,574 prefixes | Mean prefix TVD .222190, SD .178234 | `bpic13-cp-v1/E3-stream.json` |
| BPIC13-CP BE | 1,574/1,574 prefixes | Global graph with 3 nodes and 5 directed edges | `bpic13-cp-v1/graphs/BE/manifest.json` |
| BPIC13-CP AE | 1/809,189,178 contexts | Incomplete. The BE pass established the exact workload over all test prefixes | `bpic13-cp-v1/explain-v1/coverage.json` |

Sepsis E3 stopped at 1,199 prefixes after its first 180-second quota. The second session resumed from the exact source snapshot, preserving prior units. Total wall time across these sessions was 608.32 seconds. BPIC13-CP E2 used five fresh BASE and five frozen-constant seeds, with 10 epochs each. Figure files in `artifacts/figures/bpic13-cp-v2/` show the E1 distribution, the descriptive E2 scatter and the E3 distribution. Its CSV preserves the ten exact seed means when markers overlap.

No author-runtime execution, historical split equivalence, BPMN alignment or user study has been established. Model fidelity, process-model structural agreement and human interpretability remain separate claims. Missing results and undefined metrics are not zeros.
