# Reproducible commands

Run from the independent project root in PowerShell. Use a fresh output directory for each code/config revision. Existing results are protected. Resume training within an unchanged identity with --resume. An interrupted process may leave writer.lock, which requires checking the recorded PID and process state before removing only that lock.

```powershell
& .venv/Scripts/python.exe -m pytest -q
& .venv/Scripts/python.exe -m nhom19_process_xai prepare --config configs/fixture/dataset.json --output artifacts/fixture/prepared.json
& .venv/Scripts/python.exe -m nhom19_process_xai train --prepared artifacts/fixture/prepared.json --config configs/fixture/training.json --output artifacts/fixture/base
& .venv/Scripts/python.exe -m nhom19_process_xai predict --prepared artifacts/fixture/prepared.json --checkpoint artifacts/fixture/base/checkpoint.pt --output artifacts/fixture/predictions.json
& .venv/Scripts/python.exe -m nhom19_process_xai experiment E1 --prepared artifacts/fixture/prepared.json --checkpoint artifacts/fixture/base/checkpoint.pt --output artifacts/fixture/E1.json
& .venv/Scripts/python.exe -m nhom19_process_xai experiment E2 --prepared artifacts/fixture/prepared.json --checkpoint artifacts/fixture/base/checkpoint.pt --output artifacts/fixture/E2.json
& .venv/Scripts/python.exe -m nhom19_process_xai experiment E3 --prepared artifacts/fixture/prepared.json --checkpoint artifacts/fixture/base/checkpoint.pt --output artifacts/fixture/E3.json
```

These commands executed successfully at the second implementation checkpoint. Adding --profile E2-AC or E2-UNI selects a distinct E2 diagnostic. E3 accepts --profile E3-AUTHOR. Use distinct output names. Diagnostic CLI executions are pending at this checkpoint. Artifacts from old code are retained with their recorded source hashes. An attempted training resume after source changes is rejected.

Environment recreation uses the existing uv installation to create a dedicated CPython3.11.15 venv and synchronize requirements-cpu.lock with --require-hashes and the official CPU wheel index. The exact approved interpreter path is in the Round 3.6 S0 document, and the actually used path is in artifacts/s0/environment.json. See PROGRESS.md for the commands used in this machine context.

## Integrated execution and verified real-data commands

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai pipeline --dataset-config configs/fixture/dataset.json --training-config configs/fixture/training.json --output artifacts/pipeline-fixture-v2
& .venv/Scripts/python.exe -m nhom19_process_xai prepare --config configs/datasets/sepsis.json --output data/processed/sepsis-v1.json
& .venv/Scripts/python.exe -m nhom19_process_xai train --prepared data/processed/sepsis-v1.json --config configs/primary/training.json --output artifacts/sepsis-v1/base
& .venv/Scripts/python.exe -m nhom19_process_xai predict --prepared data/processed/sepsis-v1.json --checkpoint artifacts/sepsis-v1/base/checkpoint.pt --output artifacts/sepsis-v1/predictions.json
& .venv/Scripts/python.exe -m nhom19_process_xai pilot --prepared data/processed/sepsis-v1.json --checkpoint artifacts/sepsis-v1/base/checkpoint.pt --output artifacts/sepsis-v1/pilot-v1 --sample-size 12 --contexts-per-prefix 32 --max-seconds 120
& .venv/Scripts/python.exe -m nhom19_process_xai experiment E3 --streaming --prepared data/processed/sepsis-v1.json --checkpoint artifacts/sepsis-v1/base/checkpoint.pt --output artifacts/sepsis-v1/E3-stream.json --max-seconds 180
```

All paths above already hold results; use a new run name for a new execution. The original Sepsis training command used configs/fixture/training.json, whose values were copied unchanged to configs/primary/training.json for clear naming. A completed study refuses overwrite. An incomplete streaming study resumes from the same output name with identical source/data/checkpoint/profile. Quota checks happen between prefixes and whole training jobs, not inside them. Missing units retain incomplete status; no silent sampling occurs. Do not run the in-memory full `pipeline` on a large log before the work/resource gate, especially exhaustive AE.

The original E3 code snapshot is preserved under artifacts/source-snapshots/6adfd3e3f7f2e36238b4316e8839d42953fc2d074753fea953ff4dd16c2c5eda. To resume that exact run after subsequent code edits, scope PYTHONPATH to that snapshot for the command and restore the previous value afterward. Its manifest lists every package file checksum. This preserves the identity check instead of bypassing it.

Full BPIC12 E3 uses the local C drive because it has more free space than the project drive. Its authoritative manifest/progress paths and input digests are in `artifacts/bpic12-v1/E3-location.json`. The output is under `%LOCALAPPDATA%/nhom19_cschttt/round4/bpic12-v1/`, outside cloud-synchronized folders. Resume an incomplete run with the exact source snapshot below; a completed manifest refuses overwrite.

```powershell
& {
    $previousPath = $env:PYTHONPATH
    $largeRun = Join-Path $env:LOCALAPPDATA 'nhom19_cschttt/round4/bpic12-v1'
    try {
        $env:PYTHONPATH = (Resolve-Path artifacts/source-snapshots/f6d7c71/src).Path
        & .venv/Scripts/python.exe -m nhom19_process_xai experiment E3 --streaming --prepared data/processed/bpic12-v1.json --checkpoint artifacts/bpic12-v1/base/checkpoint.pt --output (Join-Path $largeRun 'E3-stream.json') --max-seconds 1800
    } finally {
        $env:PYTHONPATH = $previousPath
    }
}
```

After completion, run `scripts/audit_streamed_study.py` with that manifest, `data/processed/bpic12-v1.json` and `artifacts/bpic12-v1/base/checkpoint.pt`. Keep the SQLite database beside its manifest when auditing or resuming.

BPIC13-CP follows the same prepare/train/predict commands with configs/datasets/bpic13-cp.json, data/processed/bpic13-cp-v1.json and artifacts/bpic13-cp-v1. Its streaming E2 command uses `experiment E2 --streaming ... --output artifacts/bpic13-cp-v1/E2-stream.json --max-seconds 600`. Diagnostic fixture runs use separate E2-AC.json, E2-UNI.json and E3-AUTHOR.json outputs under pipeline-fixture-v2. The actual completion status is in EXPERIMENTAL_RESULTS.md and the sealed manifests.

```powershell
& .venv/Scripts/python.exe scripts/render_round4_results.py --e1 artifacts/bpic13-cp-v1/E1.json --e2 artifacts/bpic13-cp-v1/E2-stream.json --e3 artifacts/bpic13-cp-v1/E3-stream.json --output artifacts/figures/bpic13-cp-v2
```

To build the full BE graph and count the exhaustive AE workload on the same prefixes, use `explain --be-only`. The command reports BE status and AE coverage separately. A subsequent `explain` with the same arguments and source version can reuse the BE results and begin AE.

New explainer runs check the same 256 MiB available-RAM and 1 GiB free-disk floors as the streaming studies. Add `--max-seconds 1800` to `explain` for a finite wall-time session. Checks occur between new BE prefixes and AE contexts; one unit must fit, and preparation/checkpoint loading precedes the session timer. An unfinished BE run preserves sealed prefix records and writes `coverage.json` with `be_status=incomplete`; its AE total and coverage remain null until the relevant positions are known for every prefix. It publishes no partial `BE.json` or `AE.json`. Rerun the same command and source to resume, with an optionally different wall quota. Evaluation refuses to publish metrics while BE is incomplete. Older active runs retain their original snapshot behavior.

`explain --cache-policy baseline` stores complete unmasked baseline tensors and computes masked predictions without persisting them. This reduces disk use at the cost of more repeated forward executions. Every BE mask record and AE logical context/vote remains retained. The default `all` policy caches all predictions. The selected policy is part of the explainer identity and must stay unchanged on resume. Both policies produced identical fixture BE records, AE matrices and graphs, and identical relevance records on the measured 200-prefix Helpdesk cohort. Use `baseline` for the new full BPIC12 BE run to reserve disk for the primary studies. `evaluate` accepts the same option for its graph jobs and records it in the evaluation result; the nine fixture BE outputs match the full-cache paired run exactly.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai explain --prepared data/processed/sepsis-v1.json --checkpoint artifacts/sepsis-v1/base/checkpoint.pt --output artifacts/sepsis-v1/be-only-v1 --be-only
& .venv/Scripts/python.exe -m nhom19_process_xai graph --explanation artifacts/sepsis-v1/be-only-v1/BE.json --output artifacts/sepsis-v1/graphs/BE
```

Count the exact E1 schedule without creating variants using the diagnostic below. Counting can itself grow exponentially with the number of distinct activities. The Sepsis count took under two seconds on the local CPU and the BPIC13-CP count matched the 15,569 variants from its completed E1 run.

```powershell
& .venv/Scripts/python.exe scripts/count_e1_variants.py --prepared data/processed/sepsis-v1.json --output artifacts/sepsis-v1/E1-workload-counter.json
```

Recompute the full BPIC12 E1 storage gate directly from the pinned XES without loading the large prepared JSON. The result counts all masks and boundary replacements and restricts interior paths to the 14 highest-degree activities. The receipt stores a lower bound separately from the exact count required for a completed-run audit.

```powershell
& .venv/Scripts/python.exe scripts/count_e1_variants.py --xes-config configs/datasets/bpic12.json --induced-activities 14 --output artifacts/bpic12-v1/E1-workload-lower-bound-v2.json
```

Add `--xai-baseline-run` with the completed baseline `run.json` to restrict the bound to the seed-404 XAI cohort. The command checks the adjacent checkpoint and case-split hashes and reports the minimum number of bytes occupied by the variant IDs for one method.

```powershell
& .venv/Scripts/python.exe scripts/count_e1_variants.py --xes-config configs/datasets/bpic12.json --induced-activities 14 --xai-baseline-run artifacts/bpic12-v1/base/run.json --output artifacts/bpic12-v1/xai-evaluation-workload-v2.json
```

Run E1 with a wall time quota and an optional quota for new variants. Use the same output path, dataset, checkpoint and source to resume. The SQLite ledger and prefix accumulators advance together in transactions. An incomplete session publishes progress under the sibling `E1-stream-e1-run/` directory. The result JSON appears only after all scheduled prefixes complete. Use the original source commit or its snapshot if resuming after code changes.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai experiment E1 --streaming --prepared data/processed/sepsis-v1.json --checkpoint artifacts/sepsis-v1/base/checkpoint.pt --output artifacts/sepsis-v1/E1-stream.json --max-variants 5000 --max-seconds 60
```

BE can be evaluated independently where the exhaustive AE schedule cannot complete. The command keeps the five Co03 candidates and the same evaluation sample as paired mode. A provided baseline graph must match the checkpoint, dataset and full prefix set. The output contains BE rows and an explicit paired status of `not_evaluated`.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai evaluate --prepared data/processed/bpic13-cp-v1.json --checkpoint artifacts/bpic13-cp-v1/base/checkpoint.pt --be-only --baseline-be artifacts/bpic13-cp-v1/explain-v1/BE.json --output artifacts/bpic13-cp-v1/evaluation-be
```

Audit a completed evaluation against its candidate checkpoints, graph digests and deterministic cohort. The auditor recomputes model distances, graph projections, candidate graph overlaps, all nine per-prefix outputs from their stored intermediates and the aggregate summaries. Tau-b uses independent pair counting. It checks variant agreement scores, near/far membership, consistency eligibility and null handling without replaying model inference. For paired results it also reconstructs each valid intersection and its descriptive differences. Pass `--baseline-be` if the BE-only run reused a standalone baseline graph.

```powershell
& .venv/Scripts/python.exe scripts/audit_xai_evaluation.py --run artifacts/bpic12-o-v1/evaluation-be --prepared data/processed/bpic12-o-v1.json --checkpoint artifacts/bpic12-o-v1/base/checkpoint.pt --baseline-be artifacts/bpic12-o-v1/be-only-v1/BE.json
& .venv/Scripts/python.exe scripts/audit_xai_evaluation.py --run artifacts/synthetic-long-dist-dep/evaluation-paired --prepared data/processed/synthetic-long-dist-dep.json --checkpoint artifacts/synthetic-long-dist-dep/base/checkpoint.pt
```

Reopen a completed streaming run using the command below. It checks the dataset and checkpoint, the complete test cohort, the SQLite digest and each record seal, and reconstructs the summaries. For E1, pass the exact count artifact from `scripts/count_e1_variants.py`. E2 and E3 do not need `--workload`. The E2 receipt also recomputes the raw and L1-normalized maximum-attention bins and the TVD filter on each record, reporting counts separately by arm. The E3 receipt checks every prepared occurrence, recomputes TVD from both stored probability vectors and reports the occurrence-weighted summary separately.

```powershell
& .venv/Scripts/python.exe scripts/audit_streamed_study.py --manifest artifacts/bpic13-cp-v1/E1-stream.json --prepared data/processed/bpic13-cp-v1.json --checkpoint artifacts/bpic13-cp-v1/base/checkpoint.pt --workload artifacts/bpic13-cp-v1/E1-workload-counter.json
```

For the verified BPIC12_W E1 and Sepsis E2 runs, use these read-only replays against the completed manifests.

```powershell
& .venv/Scripts/python.exe scripts/audit_streamed_study.py --manifest artifacts/bpic12-w-v1/E1-stream.json --prepared data/processed/bpic12-w-v1.json --checkpoint artifacts/bpic12-w-v1/base/checkpoint.pt --workload artifacts/bpic12-w-v1/E1-workload-counter.json
& .venv/Scripts/python.exe scripts/audit_streamed_study.py --manifest artifacts/sepsis-v1/E2-stream.json --prepared data/processed/sepsis-v1.json --checkpoint artifacts/sepsis-v1/base/checkpoint.pt
```

For E3-PAPER, add `--baseline-cache` pointing to a closed BE inference ledger for the same checkpoint and full cohort. This links each E3 prefix to its retained baseline probability and attention tensor, verifies the cache checksum and recomputes every attention displacement and row-normalized TVD. It does not execute model inference or duplicate the tensors. Preserve the referenced cache with the E3 result and its audit receipt.

```powershell
& .venv/Scripts/python.exe scripts/audit_streamed_study.py --manifest artifacts/bpic13-cp-v1/E3-stream.json --prepared data/processed/bpic13-cp-v1.json --checkpoint artifacts/bpic13-cp-v1/base/checkpoint.pt --baseline-cache artifacts/bpic13-cp-v1/explain-v1/ledger.sqlite
```

For the author-supplied synthetic benchmarks, extract the exact XES members from the archive listed in [Dataset provenance](DATASET_PROVENANCE.md) to the paths expected by `configs/datasets/synthetic-*.json`. The prepare command checks the member bytes and dataset counts. Reopen a completed explainer run with the following auditor, which requires a closed SQLite ledger.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai prepare --config configs/datasets/synthetic-sequence.json --output data/processed/synthetic-sequence.json
& .venv/Scripts/python.exe scripts/audit_explainer_run.py --run artifacts/synthetic-sequence/explain --prepared data/processed/synthetic-sequence.json --checkpoint artifacts/synthetic-sequence/base/checkpoint.pt
```

Use `--be-only` on the auditor to verify the BE graph and the planned AE schedule without running AE. Both modes report a lower bound on the bytes of context text. Full mode also checks that every selected target has exactly one vote occurrence for each prefix position in each context.

## Integrated streaming studies

Use the pipeline's streaming mode to persist E1–E3 units in SQLite. If a study stops at a quota or resource floor, `pipeline.json` names the active stage and its study progress receipt. Rerun with the same inputs, source, output directory and `--streaming` mode. The per-study time limit may be changed when resuming. It applies to E1–E3, with E2 checking between whole model training jobs. Predictive output and explanation evaluation retain their existing execution paths.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai pipeline --dataset-config configs/fixture/dataset.json --training-config configs/fixture/training.json --output artifacts/pipeline-streaming-fixture --streaming --study-max-seconds 600
```

Completed streaming stage receipts bind the ledger to the study manifest. The E2 receipt also includes all ten arm checkpoints and training manifests.

The complete Sequence log uses its verified dataset configuration and the primary training settings. This run was started with package snapshot `9bf57f8`. Use the same source snapshot, configuration and output directory on resume.

```powershell
& {
    $previousPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = (Resolve-Path artifacts/source-snapshots/9bf57f8/src).Path
        & .venv/Scripts/python.exe -m nhom19_process_xai pipeline --dataset-config configs/datasets/synthetic-sequence.json --training-config configs/primary/training.json --output artifacts/pipeline-synthetic-sequence --streaming --study-max-seconds 1800
    } finally {
        $env:PYTHONPATH = $previousPath
    }
}
```

For a dataset whose exhaustive AE schedule exceeds available resources, append `--be-only` and use a distinct output directory. The pipeline still runs E1–E3, evaluates BE and records the AE schedules. Its completion receipt identifies the BE-only scope, and the evaluation reports paired results as unevaluated. The default mode runs both explainers and the paired evaluation.

## Synthetic BPMN comparison

To compare the verified Complex-Model and Looped-AND BE outputs against selected relations in the supplement BPMNs, run the structural audit. It checks the original XES digests, the independent test split and the audited BE export before counting transitions.

```powershell
& .venv/Scripts/python.exe scripts/audit_synthetic_structure.py --archive data/raw/author-supplement/Supplementary_Material.zip --output artifacts/bpmn-complex-looped-audit.json
```

## Archived Table 2 checkpoint replay

The reference-only CPU environment is under `artifacts/author-runtime/`. Its Conda explicit package list, pip freeze, installation report and wheel digest receipt preserve the separate runtime identity. The CPython 3.7 Windows TensorFlow wheel was fetched from PyPI in bounded ranges after the original pip transfer stalled. The verified SHA-256 is `4828c436e1b26e5bb21e650c05aa33a5705af27b3a1f52bc2af6c6a1e2ae5721`. The independent Python 3.11 environment and original repository are outside this replay's execution path. [Micromamba Windows installation](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html) · [TensorFlow 2.6.5 files](https://pypi.org/project/tensorflow/2.6.5/#files)

```powershell
$runtime = Join-Path (Get-Location).Path 'artifacts/author-runtime'
$env:CUDA_VISIBLE_DEVICES = '-1'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONPATH = $null
& "$runtime/Library/bin/micromamba.exe" --no-rc run -r "$runtime/mamba-root" --prefix "$runtime/python37" python scripts/audit_author_saved_model.py --archive data/raw/author-supplement/Supplementary_Material.zip --output artifacts/author-runtime/bpic13-cp-saved-model-audit-repeat.json
```

The command defaults to BPIC13-CP. Pass `--run` with the archived model name suffix, such as `bpic12_o_GPU`, and use a distinct output path for each replay. The default serving signature checks the archived last-prefix target and the first-suffix target on the same samples. For Helpdesk and Sepsis the additional `--loader keras` diagnostic called the Keras model with training disabled.

Verify the archived preliminary-study CSVs separately from model inference. This reads the pinned ZIP, recomputes the stored quantiles over all twelve logs and checks the E2 bin of every archived row against its stored maximum attention.

```powershell
& .venv/Scripts/python.exe scripts/audit_author_prestudy.py --archive data/raw/author-supplement/Supplementary_Material.zip --output artifacts/author-runtime/prestudy-archive-audit.json
```

The isolated `keras-predict` diagnostic uses the author's pinned `Transformer` class as a Keras custom object, then calls `Model.predict` and NumPy argmax as the pinned evaluation source does. Set `$authorRoot` to the path of the author checkout. The diagnostic checks its Git revision and tracked status before importing it.

```powershell
& "$runtime/Library/bin/micromamba.exe" --no-rc run -r "$runtime/mamba-root" --prefix "$runtime/python37" python scripts/audit_author_saved_model.py --archive data/raw/author-supplement/Supplementary_Material.zip --run sepsis_GPU --loader keras-predict --author-root $authorRoot --output artifacts/author-runtime/table2-replays/sepsis_GPU-keras-predict-repeat.json
```

The paired Sequence evaluation used the command below. Its baseline graph directory was initialized from the closed standalone Sequence run by copying `BE.json`, `AE.json`, `coverage.json` and the fully checkpointed `ledger.sqlite` with hash checks. The evaluation also runs from a fresh output directory, generating its own baseline and candidate graphs. A fresh directory may take longer.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai evaluate --prepared data/processed/synthetic-sequence.json --checkpoint artifacts/synthetic-sequence/base/checkpoint.pt --output artifacts/synthetic-sequence/evaluation-paired
```
