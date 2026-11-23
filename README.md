# Explaining Transformer-Based Next Activity Prediction Using Attention Scores

Independent implementation of the ProcessTransformer process-prediction and explainability research pipeline. The project supports deterministic training, prefix-level prediction, attention studies, baseline/candidate explainers, explanation graph export, resumable streaming experiments, and artifact checksums.

## Requirements

- Python 3.11
- Windows, Linux, or macOS
- CPU or CUDA-compatible PyTorch installation

The project is designed for CPU execution. The pinned CPU dependencies are available in `requirements-cpu.lock`.

## Installation

Create and activate a virtual environment, then install the package and its dependencies:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip setuptools
.venv\Scripts\python -m pip install -e .
```

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
python -m pip install -e .
```

For the pinned CPU environment:

```bash
python -m pip install -r requirements-cpu.lock
```

## Quick Start

Run the project pipeline against the deterministic software fixture:

```bash
python -m nhom19_process_xai pipeline \
  --dataset-config configs/fixture/dataset.json \
  --training-config configs/fixture/training.json \
  --output artifacts/fixture-run
```

Use the resumable streaming pipeline with:

```bash
python -m nhom19_process_xai pipeline \
  --dataset-config configs/fixture/dataset.json \
  --training-config configs/primary/training.json \
  --output artifacts/fixture-streaming \
  --streaming \
  --study-max-seconds 3600
```

Generated artifacts are written beneath the selected output directory. The pipeline uses sealed JSON and checksums to validate stage identity and recover only from unchanged inputs.

## Command Overview

Prepare sealed prepared-data JSON:

```bash
python -m nhom19_process_xai prepare \
  --config configs/fixture/dataset.json \
  --output artifacts/prepared.json
```

Train a model:

```bash
python -m nhom19_process_xai train \
  --prepared artifacts/prepared.json \
  --config configs/fixture/training.json \
  --output artifacts/base
```

Predict test prefixes:

```bash
python -m nhom19_process_xai predict \
  --prepared artifacts/prepared.json \
  --checkpoint artifacts/base/checkpoint.pt \
  --output artifacts/predictions.json
```

Run an attention study:

```bash
python -m nhom19_process_xai experiment E1 \
  --prepared artifacts/prepared.json \
  --checkpoint artifacts/base/checkpoint.pt \
  --output artifacts/E1.json
```

Supported studies are `E1`, `E2`, and `E3`.

Run explainers or evaluation:

```bash
python -m nhom19_process_xai explain \
  --prepared artifacts/prepared.json \
  --checkpoint artifacts/base/checkpoint.pt \
  --output artifacts/explanation

python -m nhom19_process_xai evaluate \
  --prepared artifacts/prepared.json \
  --checkpoint artifacts/base/checkpoint.pt \
  --output artifacts/evaluation
```

Export explanation graphs:

```bash
python -m nhom19_process_xai graph \
  --explanation artifacts/evaluation/baseline-graphs/BE.json \
  --output artifacts/graphs/BE
```

Run a bounded pilot:

```bash
python -m nhom19_process_xai pilot \
  --prepared artifacts/prepared.json \
  --checkpoint artifacts/base/checkpoint.pt \
  --output artifacts/pilot \
  --sample-size 12 \
  --contexts-per-prefix 32 \
  --max-seconds 120
```

## Tests

Run the complete test suite:

```bash
python -m pytest
```

Run tests with coverage:

```bash
python -m pytest --cov=nhom19_process_xai --cov-report=term-missing
```

## Project Structure

```text
configs/    Dataset and training configurations
scripts/    Auditing, comparison, and result-generation utilities
src/        Installable Python package
tests/      Unit and integration tests
artifacts/  Generated local outputs (ignored by Git)
data/       Local datasets and generated data (ignored by Git)
docs/       Research documentation (ignored by Git)
reports/    Local reports and PDF/LaTeX output (ignored by Git)
```

## Dataset Configuration

Dataset definitions live in `configs/datasets/`. Real dataset entries reference local copies under `data/raw/` and include identity hashes and expected counts where applicable.

The fixture in `configs/fixture/dataset.json` uses `tests/fixtures/events.csv` and is sufficient for a reproducible local smoke test.

## Reproducibility

The implementation:

- Seeds Python, NumPy, and PyTorch.
- Uses deterministic algorithms during model training.
- Locks pipeline output directories while a stage is active.
- Writes JSON artifacts atomically.
- Seals JSON payloads with SHA-256 fingerprints.
- Validates stage receipts and artifact identities when resuming.
- Supports resumable SQLite-backed streaming studies.

## License

MIT License. See [`LICENSE`](LICENSE) for details.
