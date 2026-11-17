# Round 4 experimental reproduction comparison

**Overall status: PARTIALLY COMPLETE. Successful reproduction of the complete published experiment matrix has not been established.** Actual independent runs exist; implementation and smoke-test success are separate from reproduction success.

## Reference and reuse discipline

The supplied paper was checked directly on printed pages 16, 18 and 21, including Figures 3, 4 and 7. Its plots do not print all exact numerical summaries. The numerical references below therefore come from the author-linked supplementary CSVs, with that distinction preserved. All 96 preliminary-study CSVs and their stored quantiles were previously reconciled. The source archive SHA-256 is `b1b88b2d7797fbe3369dccc5c4fe8d9a96af5d52293954279d4bab2f0bcc169e`. [Paper](https://doi.org/10.1007/s44311-025-00018-4)

Existing independent results retain dataset, checkpoint and source identities. The E2/E3 metric functions, Transformer, prediction, training, explainer and numerical-metric code were compared with their retained source snapshots. The old BPIC13-CP E1 output was separately checked against the current generator and accumulator: all 15,569 variants and all 1,574 rank summaries match, with zero numeric difference. The compatibility evidence is `artifacts/s0/reproduction-compatibility-final.json` and `artifacts/bpic13-cp-v1/e1-current-compatibility.json`. Runner revisions and preprocessing versions remain identified separately; compatibility does not imply identical historical paper conditions.

## Direct comparison with the paper's findings

| Experiment | Metric | Paper Result | Our Result | Difference | Reproduction Status |
|---|---|---|---|---|---|
| E1 · Figure 3 | Median Kendall tau | Most logs slightly above .5; BPIC12, BPIC12-WC and Sepsis closer to zero, p.16 | Nine complete log studies. BPIC12-WC median 1.0 among 13,370 valid prefixes; Sequence .361111 among 3,000 | The low-correlation BPIC12-WC pattern is absent. Exact printed per-log medians are unavailable | **Partially reproduced**; the published pattern is not recovered consistently |
| E2 · Figure 4 | Mean JSD versus prediction TVD for 5+5 models | Ten model points per log; discussion associates low prediction variation with low attention variation, pp.16–18 | Eight complete 5+5 studies. Helpdesk BASE means: JSD .026803, TVD .040435; FC: .078434, .043597 | Quantitative comparison with the archived points is below. Independent FC initialization differs from the archived named uniform arm | **Partially reproduced**; numerical equivalence is not established |
| E2 · Figure 5 | Maximum-attention bins | Most observations in the two outer bins, pp.18–19 | Raw and L1-normalized maxima are recorded separately. For ordinary four-head attention, max after full L1 normalization is at most 1/(4n) | The high normalized bins cannot occur under the printed normalized definition. Raw source bins use a different quantity and a TVD filter | **Not reproduced under the printed normalized definition**; paper-level ambiguity remains |
| E3 · Figure 7 | Per-occurrence prediction TVD between input and attention masking | Histograms concentrated near zero; text describes almost identical predictions for most logs, p.21 | Eleven complete log studies. Helpdesk occurrence median .129620; Sequence .00000645; LDD .000238 | The near-zero pattern appears on some cohorts, while Helpdesk shows materially larger differences | **Partially reproduced**; masking and population differences prevent an exact replication claim |

These are observations about model behavior. They establish neither universal Transformer/LLM interpretability nor human interpretability. The paper's use of the word significant is not treated as a statistical test for the independent results.

## Numerical comparison: complete real Helpdesk experiment

All seven rows use actual completed independent runs on the full Helpdesk test population. E1 excludes undefined correlations; E3 uses individual masking occurrences, matching the statistic family of Figure 7 rather than substituting the equal-prefix mean. JSD uses natural logarithms; TVD is on normalized class probabilities.

**† References are computed from the author's supplementary CSVs; they are not exact values transcribed from labels in the paper.** E2 values average the five archived model points in each named arm. Different historical cohorts, architecture and manipulation settings make the differences descriptive.

The Difference column gives signed Δ = ours − reference, absolute |Δ|, and relative Δ/reference. Relative changes of correlations and references with magnitude at most 1e−6 are omitted as misleading; this affects reporting only.

| Experiment | Metric | Paper Result† | Our Result | Difference: Δ / \|Δ\| / relative | Reproduction Status |
|---|---|---:|---:|---|---|
| E1 | Median tau-b | .639763 | 1.000000 | +.360237 / .360237 / n/a | Partial; magnitude not matched |
| E2 · BASE | Five-model mean JSD | .344049 | .026803 | −.317247 / .317247 / −92.21% | Partial; historical conditions differ |
| E2 · BASE | Five-model mean TVD | .131620 | .040435 | −.091185 / .091185 / −69.28% | Partial; historical conditions differ |
| E2 · FC versus archived uniform | Five-model mean JSD | .0000000717 | .078434 | +.078434 / .078434 / n/a | Partial; initialization differs |
| E2 · FC versus archived uniform | Five-model mean TVD | .097284 | .043597 | −.053687 / .053687 / −55.19% | Partial; initialization differs |
| E3 | Occurrence-weighted mean TVD | .129804 | .205587 | +.075784 / .075784 / +58.38% | Partial; masking/cohort differ |
| E3 | Occurrence-weighted median TVD | .056731 | .129620 | +.072889 / .072889 / +128.48% | Partial; masking/cohort differ |

The complete cross-log comparison currently has **63 metric rows**: nine E1 medians, 32 E2 arm/metric summaries and 22 E3 occurrence summaries. `artifacts/reproduction-comparison-v2/comparison.csv` and `comparison.json` preserve the exact numbers, denominators, source/member hashes, signed and absolute differences, relative differences and missing studies. Recompute with:

```powershell
& .venv/Scripts/python.exe scripts/compare_prestudy_results.py --output artifacts/reproduction-comparison-new
```

## Conditions limiting reproduction

- The independent case-level 70/30 split uses seed 42 and train-only vocabularies. Historical sample populations differ; the author pre-study sampler also samples unique sequences with replacement and a cap. E1 rank universes and perturbation sets differ, affecting ties, undefined correlations and medians.
- Locked D02 uses four nine-dimensional heads at embedding width 36. The pinned author constructor uses 36 dimensions per head. The independent primary schedule uses the paper appendix's 10 epochs and batch 12; recovered historical training configurations include other settings. Exact historical-run equivalence is not claimed.
- E1 uses the documented distance/closeness convention and exhaustive finite simple DFG paths. The source's cosine naming/direction and variant limits differ. These differences can alter feature rankings.
- E2-FC freezes constant .01 kernels and zero biases. The author's named uniform branch passes `train_attention=False`; the pinned constructor retains its initializer. A full real-data E2-AC diagnostic is running with the same independent dimensions. Its five verified BASE checkpoints were reused without retraining; its output is separate from the primary FC experiment.
- E3-PAPER zeros query/key entries after softmax. The pinned author masking operates before softmax, with separately tested Keras behavior on fully masked rows. The same TVD units do not remove this manipulation difference.
- CPU/GPU execution, unrecovered historical seeds and checkpoint/population differences remain possible contributors. Their individual causal effects have not been isolated.

## Completion gate

Real experiments, complete BE/AE graphs and real evaluation outputs exist on the documented cohorts. Nine E1, eight E2 and eleven E3 primary log studies are complete at this snapshot. The full twelve-log matrix is unfinished, and several exhaustive schedules exceed measured local storage or computational feasibility. BE/AE Table 3 comparisons and their different denominators are in [Experimental results](EXPERIMENTAL_RESULTS.md).

**Round 4 remains PARTIALLY COMPLETE.** No row above establishes successful numerical reproduction under identical historical conditions. The remaining execution/provenance gaps must stay visible; partial runs and verified software are not substitutes for the missing experiments.
