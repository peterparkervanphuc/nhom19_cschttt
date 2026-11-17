# Round 4 technical handoff

**Overall: PARTIALLY COMPLETE — the strict experimental reproduction gate has not passed.** This handoff preserves a working independent implementation and actual experiments; it does not claim full-paper reproduction or substitute smoke tests for the missing studies.

## Component status

| Component | Status | Actual evidence and remaining limitation |
|---|---|---|
| Data and preprocessing | PASS | Twelve verified log variants; source checksums, case splits, train-only vocabulary and prefix/target audits. Historical paper populations differ. |
| Transformer, training and inference | PASS | All twelve primary models trained for ten epochs and all test predictions audited. Four nine-dimensional heads follow locked D02; the author's constructor uses wider heads. |
| E1 Feature Correlation | ACCEPTABLE | Nine complete log experiments. BPIC12, Sepsis and Complex-Model remain incomplete/storage-limited. Numerical differences from the paper/archive are documented. |
| E2 Attention Parameter Manipulation | ACCEPTABLE | Eight complete primary 5+5 studies, plus a complete real Helpdesk AC diagnostic with 49,830 verified pairs. Full BPIC12 and other remaining schedules are not complete. |
| E3 Attention Score Masking | ACCEPTABLE | Eleven complete log studies. Full BPIC12 retains 10,690 of 73,742 prefixes. Per-occurrence TVD is audited; seven logs also reference retained baseline attention tensors directly. |
| BE | ACCEPTABLE | Eleven complete full-log graphs. Full BPIC12 is running from durable prefix checkpoints; at least 46,320 of 73,742 prefixes were persisted at 21:54 on 2026-11-17. |
| AE | ACCEPTABLE | Actual exhaustive baseline/candidate graphs and signed votes on Helpdesk, Sequence and Long-Dist-Dep, plus the fixture. Other full schedules are storage-limited or astronomically large. No capped pilot is presented as exhaustive AE. |
| Predictive and XAI evaluation | PASS for executed cohorts | Twelve predictive evaluations; full paired BE/AE metrics on three benchmarks; BE-only metrics on BPIC13-CP, BPIC12_O, BPIC13 incidents and Looped-AND. All nine outputs retain undefined values and denominators. |
| Main pipeline integration | PASS | Complete nine-stage Sequence run, independent graph/metric audits, exact agreement with standalone outputs and verified resume. Current software tests also exercise complete paired and BE-only fixture paths. |
| Software verification | PASS | 93 tests passed; dependency validation passed. Latest full-suite receipt: `artifacts/s0/round4-evaluation-cache-policy-suite.xml`. No broad rerun was needed after documentation/analysis-only changes. |
| Paper comparison and provenance | ACCEPTABLE | Direct inspection of Figures 3, 4 and 7, 63 numerical E1–E3 comparisons with exact source/member hashes, controlled Helpdesk FC/AC comparison, and Table 2/3 archive reconciliation. Identical historical conditions are not established. |
| Complete experimental reproduction | NEEDS FIX | Missing studies and protocol differences prevent a COMPLETE verdict. No essential software component is classified NOT IMPLEMENTED; missing experimental coverage remains mandatory work. |

## Read the results

- [Reproduction comparison](REPRODUCTION_COMPARISON.md): printed paper findings, author-archive references, independent numbers, absolute/relative differences and per-experiment reproduction assessment.
- [Experimental results](EXPERIMENTAL_RESULTS.md): complete measured results, sample sizes, nulls, BE/AE comparisons and limitations.
- [Technical report](TECHNICAL_REPORT.md): architecture, benchmark coverage and acceptance evidence.
- [Commands](COMMANDS.md): exact entry points, source-snapshot resumption, artifact audits and external C-drive locations.
- [Traceability](REQUIREMENTS_TRACEABILITY.md) and [dataset provenance](DATASET_PROVENANCE.md): C01–C12 and official input evidence.

The 63-row table is `artifacts/reproduction-comparison-v2/comparison.csv`, with a sealed JSON companion. Its numerical references are author supplementary CSV values, not invented plot coordinates or exact values printed in the paper. Correlation ratios and near-zero-reference percentages are omitted. Compatibility evidence is `artifacts/s0/reproduction-compatibility-final.json`; the legacy CP E1 bridge matched all 15,569 variants and 1,574 summaries with zero numeric difference.

The complete integrated real benchmark is Helpdesk; the complete single-command repeat is the author-supplied Sequence benchmark. These are actual research datasets, separate from the small software fixture. CPU replay of archived TensorFlow models is reference evidence, separate from independent implementation results.

## Preserve and resume

The independent environment is `.venv`, uv CPython 3.11.15 with PyTorch 2.6.0+cpu and the hash-locked dependencies. No global installation, cloud provisioning or original-source modification is required.

| Run | Source snapshot | Output / state |
|---|---|---|
| Full BPIC12 BE | `78d6619` | `artifacts/bpic12-v1/be-only-v1`; `--be-only --cache-policy baseline`; same checkpoint/data on resume |
| Full BPIC12 E2 | `f6d7c71` | Locator `artifacts/bpic12-v1/E2-location.json`; first modified BASE seed 2001 has completed ten epochs; the full 10-model study is incomplete |
| Full BPIC12 E3 | `f6d7c71` | Locator `artifacts/bpic12-v1/E3-location.json`; 10,690 prefix records retained |
| BPIC12_WC E2 | `9bf57f8` | `artifacts/bpic12-wc-v1/E2-stream.json`; 129,784/184,720 units retained |
| Complex-Model E2 | `f6d7c71` | `artifacts/synthetic-complex-model/E2-stream.json`; 141,987/215,550 units retained |
| BPIC12_W E2 | Use a documented fixed snapshot | Not yet executed; reuse its completed baseline checkpoint |

Set `PYTHONPATH` to the snapshot's `src` directory and restore it after the command, as shown in [Commands](COMMANDS.md). Check actual processes and writer locks before resuming. Completed outputs refuse overwrite. Keep active jobs and all atomic epoch/prefix checkpoints intact; the deadline does not turn an incomplete run into a complete one.

The full BPIC12 BE prefix records already prove an AE lower bound of at least 1.75755 × 10^39 contexts from a fixed 43,804-prefix snapshot. This is a lower bound, not a completed graph or exact full AE total. Other documented bounds include approximately 2.178 × 10^40 for BPIC12_W and 9.578 × 10^52 for Sepsis. Adding ordinary local hardware cannot complete those exhaustive schedules. An author-style cap would be a separately declared protocol, not silent fulfillment of the exhaustive primary method.

## Closing assessment

Actual experiments and evaluation demonstrate a usable, independently executable baseline on the completed cohorts. They do not establish full quantitative reproduction of the original research. E1 rank/cohort choices, E2 initializer/head-width differences, E3 masking semantics and historical split/checkpoint differences remain material. NaN is preserved, statistical significance is not inferred from descriptive differences, and model fidelity is kept separate from BPMN alignment and human interpretability.

**Round 4 remains PARTIALLY COMPLETE.** Remaining Round 4 experiments and reproduction discrepancies must remain visible before declaring it closed. No Round 5 improvements, academic report or slides were started. The sibling author repository remains read-only at `494b315a555e713bdd61f0edd7d033c31d5850bf`; unrelated user directories and prior outputs are preserved.
