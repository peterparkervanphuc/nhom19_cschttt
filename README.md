# nhom19_cschttt
Research and reproduction of Käppel et al. (2025) on attention-based explainability for transformer-based next-activity prediction, including paper analysis, experimental implementation, graph-based explanations, critical evaluation, and presentation materials.

The independent Python package is `nhom19_process_xai` under `src/`. It implements ProcessTransformer, training and prediction, the three attention experiments, BE, exhaustive AE, explanation evaluation and directed graph export. It has no runtime dependency on the author's repository, which remains a separate read-only reference.

Round 4 is in progress. All twelve predictive baselines are verified; completed explanation studies and resource-limited schedules are listed separately in the [technical report](docs/round4/TECHNICAL_REPORT.md). The available results do not establish exact reproduction of every historical paper run.

Use the existing project environment from the repository root in PowerShell:

```powershell
& .venv/Scripts/python.exe -m nhom19_process_xai --help
& .venv/Scripts/python.exe -m pytest -q
```

The [reproducible commands](docs/round4/COMMANDS.md) cover preparation, individual components, the complete fixture pipeline, streaming studies, resumption and independent artifact audits. Environment recreation uses Python 3.11.15 and the hashed `requirements-cpu.lock`; the setup commands and cold-recreation evidence are in the [progress log](docs/round4/PROGRESS.md). Use a fresh output directory for a new run. Large-log execution requires a workload check, especially for exhaustive AE.

- [Execution plan](docs/round4/EXECUTION_PLAN.md): scope, acceptance criteria and remaining work.
- [Research traceability](docs/round4/REQUIREMENTS_TRACEABILITY.md): C01–C12 specifications, implementation and verification.
- [Dataset provenance](docs/round4/DATASET_PROVENANCE.md): official inputs, checksums, filters and reuse terms.
- [Experimental results](docs/round4/EXPERIMENTAL_RESULTS.md): measured values, denominators, reference comparisons and limitations.

Raw data, prepared logs, checkpoints and run artifacts stay under ignored `data/` and `artifacts/` directories. Dataset acquisition and local artifact receipts are documented separately from versioned source and configuration.
