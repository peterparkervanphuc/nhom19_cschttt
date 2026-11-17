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

BPIC13-CP follows the same prepare/train/predict commands with configs/datasets/bpic13-cp.json, data/processed/bpic13-cp-v1.json and artifacts/bpic13-cp-v1. Its streaming E2 command uses `experiment E2 --streaming ... --output artifacts/bpic13-cp-v1/E2-stream.json --max-seconds 600`. Diagnostic fixture runs use separate E2-AC.json, E2-UNI.json and E3-AUTHOR.json outputs under pipeline-fixture-v2. The actual completion status is in EXPERIMENTAL_RESULTS.md and the sealed manifests.

```powershell
& .venv/Scripts/python.exe scripts/render_round4_results.py --e1 artifacts/bpic13-cp-v1/E1.json --e2 artifacts/bpic13-cp-v1/E2-stream.json --e3 artifacts/bpic13-cp-v1/E3-stream.json --output artifacts/figures/bpic13-cp-v2
```

To build the full BE graph and count the exhaustive AE workload on the same prefixes, use `explain --be-only`. The command reports BE status and AE coverage separately. A subsequent `explain` with the same arguments and source version can reuse the BE results and begin AE.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai explain --prepared data/processed/sepsis-v1.json --checkpoint artifacts/sepsis-v1/base/checkpoint.pt --output artifacts/sepsis-v1/be-only-v1 --be-only
& .venv/Scripts/python.exe -m nhom19_process_xai graph --explanation artifacts/sepsis-v1/be-only-v1/BE.json --output artifacts/sepsis-v1/graphs/BE
```

Count the exact E1 schedule without creating variants using the diagnostic below. Counting can itself grow exponentially with the number of distinct activities. The Sepsis count took under two seconds on the local CPU and the BPIC13-CP count matched the 15,569 variants from its completed E1 run.

```powershell
& .venv/Scripts/python.exe scripts/count_e1_variants.py --prepared data/processed/sepsis-v1.json --output artifacts/sepsis-v1/E1-workload-counter.json
```

Run E1 with a wall time quota and an optional quota for new variants. Use the same output path, dataset, checkpoint and source to resume. The SQLite ledger and prefix accumulators advance together in transactions. An incomplete session publishes progress under the sibling `E1-stream-e1-run/` directory. The result JSON appears only after all scheduled prefixes complete. Use the original source commit or its snapshot if resuming after code changes.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai experiment E1 --streaming --prepared data/processed/sepsis-v1.json --checkpoint artifacts/sepsis-v1/base/checkpoint.pt --output artifacts/sepsis-v1/E1-stream.json --max-variants 5000 --max-seconds 60
```

BE can be evaluated independently where the exhaustive AE schedule cannot complete. The command keeps the five Co03 candidates and the same evaluation sample as paired mode. A provided baseline graph must match the checkpoint, dataset and full prefix set. The output contains BE rows and an explicit paired status of `not_evaluated`.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai evaluate --prepared data/processed/bpic13-cp-v1.json --checkpoint artifacts/bpic13-cp-v1/base/checkpoint.pt --be-only --baseline-be artifacts/bpic13-cp-v1/explain-v1/BE.json --output artifacts/bpic13-cp-v1/evaluation-be
```

Reopen a completed streaming run using the command below. It checks the dataset and checkpoint, the complete test cohort, the SQLite digest and each record seal, and reconstructs the summaries. For E1, pass the exact count artifact from `scripts/count_e1_variants.py`. E2 and E3 do not need `--workload`.

```powershell
& .venv/Scripts/python.exe scripts/audit_streamed_study.py --manifest artifacts/bpic13-cp-v1/E1-stream.json --prepared data/processed/bpic13-cp-v1.json --checkpoint artifacts/bpic13-cp-v1/base/checkpoint.pt --workload artifacts/bpic13-cp-v1/E1-workload-counter.json
```

For the author-supplied synthetic benchmarks, extract the exact XES members from the archive listed in [Dataset provenance](DATASET_PROVENANCE.md) to the paths expected by `configs/datasets/synthetic-*.json`. The prepare command checks the member bytes and dataset counts. Reopen a completed explainer run with the following auditor, which requires a closed SQLite ledger.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai prepare --config configs/datasets/synthetic-sequence.json --output data/processed/synthetic-sequence.json
& .venv/Scripts/python.exe scripts/audit_explainer_run.py --run artifacts/synthetic-sequence/explain --prepared data/processed/synthetic-sequence.json --checkpoint artifacts/synthetic-sequence/base/checkpoint.pt
```

To audit the BE graph and the planned AE schedule without claiming AE execution, use the `--be-only` flag on this auditor.

## Integrated streaming studies

Use the pipeline's streaming mode to persist E1–E3 units in SQLite. If a study stops at a quota or resource floor, `pipeline.json` names the active stage and its study progress receipt. Rerun with the same inputs, source, output directory and `--streaming` mode. The per-study time limit may be changed when resuming. It applies to E1–E3, with E2 checking between whole model training jobs. Predictive output and explanation evaluation retain their existing execution paths.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai pipeline --dataset-config configs/fixture/dataset.json --training-config configs/fixture/training.json --output artifacts/pipeline-streaming-fixture --streaming --study-max-seconds 600
```

Completed streaming stage receipts bind the ledger to the study manifest. The E2 receipt also includes all ten arm checkpoints and training manifests.

The paired Sequence evaluation used the command below. Its baseline graph directory was initialized from the closed standalone Sequence run by copying `BE.json`, `AE.json`, `coverage.json` and the fully checkpointed `ledger.sqlite` with hash checks. The evaluation also runs from a fresh output directory, generating its own baseline and candidate graphs. A fresh directory may take longer.

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai evaluate --prepared data/processed/synthetic-sequence.json --checkpoint artifacts/synthetic-sequence/base/checkpoint.pt --output artifacts/synthetic-sequence/evaluation-paired
```
