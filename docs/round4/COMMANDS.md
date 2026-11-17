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
