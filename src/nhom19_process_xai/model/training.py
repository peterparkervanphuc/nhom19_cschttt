"""Seeded CPU training with atomic epoch checkpoints and exact resume."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
import os
from pathlib import Path
import platform
import random
import time

import numpy as np
import torch
from torch import Tensor

from ..artifacts import atomic_write, write_json
from ..data.pipeline import file_hash, fingerprint
from .transformer import ModelConfig, ProcessTransformer


@dataclass(frozen=True)
class TrainingConfig:
    epochs: int = 10
    batch_size: int = 12
    learning_rate: float = .001
    seed: int = 1729
    profile: str = "BASE"
    num_threads: int = 1

    def __post_init__(self):
        if min(self.epochs, self.batch_size, self.num_threads) < 1:
            raise ValueError("epochs, batch_size and threads must be positive")
        if not np.isfinite(self.learning_rate) or self.learning_rate <= 0:
            raise ValueError("learning_rate must be finite and positive")


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed % 2**32)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def collate(records: list[dict]) -> tuple[Tensor, Tensor, Tensor]:
    if not records or any(not row["token_ids"] for row in records):
        raise ValueError("Training batches require nonempty prefixes")
    if any(row["target_id"] is None for row in records):
        raise ValueError("Unseen output classes cannot be training targets")
    length = max(len(row["token_ids"]) for row in records)
    tokens = torch.zeros(len(records), length, dtype=torch.int64)
    for index, row in enumerate(records):
        tokens[index, :len(row["token_ids"])] = torch.tensor(row["token_ids"], dtype=torch.int64)
    return tokens, tokens != 0, torch.tensor([row["target_id"] for row in records], dtype=torch.int64)


def source_hash() -> str:
    root = Path(__file__).parents[1]
    return fingerprint({str(path.relative_to(root)).replace("\\", "/"): file_hash(path)
                        for path in sorted(root.rglob("*.py"))})


@contextmanager
def run_lock(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "writer.lock"
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(descriptor, str(os.getpid()).encode("ascii"))
        os.close(descriptor)
        yield
    finally:
        path.unlink()


def checkpoint_rng() -> dict:
    state = np.random.get_state()
    return {"python": random.getstate(), "torch": torch.get_rng_state(),
            "numpy": [state[0], state[1].tolist(), state[2], state[3], state[4]]}


def restore_rng(state: dict) -> None:
    random.setstate(state["python"])
    torch.set_rng_state(state["torch"])
    name, array, index, has_gauss, cached = state["numpy"]
    np.random.set_state((name, np.asarray(array, dtype=np.uint32), index, has_gauss, cached))


def train(prepared: dict, directory: Path, config: TrainingConfig,
          resume: bool = False, stop_after_epoch: int | None = None) -> dict:
    """Train to the configured final epoch; an early stop is explicitly incomplete.

    Resume always starts at a fully published epoch, restoring optimizer,
    dropout RNG and sampler RNG. No test-target loss enters optimization.
    """
    torch.set_num_threads(config.num_threads)
    seed_everything(config.seed)
    train_records = prepared["prefixes"]["train"]
    if not train_records:
        raise ValueError("No training prefixes")
    vocab = prepared["vocabulary"]
    all_records = train_records + prepared["prefixes"]["test"]
    # The context bound uses log structure only, including room for DFG paths.
    max_length = max(len(row["token_ids"]) for row in all_records)
    positions = max_length + max(0, prepared["counts"]["activities"] - 3)
    model_config = ModelConfig(len(vocab["inputs"]) + 2, len(vocab["outputs"]),
                               max(1, positions), profile=config.profile)
    identity = {"schema_version": 1, "dataset_sha256": fingerprint(prepared),
                "processed_sha256": prepared["processed_sha256"],
                "split_sha256": prepared["split_sha256"], "vocabulary": vocab,
                "vocabulary_sha256": fingerprint(vocab), "model": asdict(model_config),
                "training": asdict(config), "source_sha256": source_hash(),
                "torch_version": str(torch.__version__), "python_version": platform.python_version(),
                "device": "cpu", "dtype": "float32"}
    checkpoint_path = directory / "checkpoint.pt"
    limit = config.epochs if stop_after_epoch is None else stop_after_epoch
    if not 1 <= limit <= config.epochs:
        raise ValueError("stop_after_epoch must lie within the configured training schedule")
    with run_lock(directory):
        model = ProcessTransformer(model_config)
        optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate,
                                     betas=(.9, .999), eps=1e-7, weight_decay=0)
        sampler = torch.Generator().manual_seed(config.seed)
        completed = 0
        history = []
        elapsed_before = 0.
        if resume:
            checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
            if checkpoint["identity"] != identity:
                raise ValueError("Resume identity differs in dataset, code, environment or configuration")
            model.load_state_dict(checkpoint["model_state"])
            optimizer.load_state_dict(checkpoint["optimizer_state"])
            restore_rng(checkpoint["rng"])
            sampler.set_state(checkpoint["sampler_rng"])
            completed, history = checkpoint["epoch"], checkpoint["history"]
            elapsed_before = checkpoint["elapsed_seconds"]
            if limit < completed:
                raise ValueError("Resume cannot move to an earlier epoch")
        elif checkpoint_path.exists() or (directory / "run.json").exists():
            raise FileExistsError("Existing training run requires explicit resume")
        started = time.perf_counter()
        for epoch in range(completed + 1, limit + 1):
            model.train()
            order = torch.randperm(len(train_records), generator=sampler).tolist()
            total_loss = 0.
            for start in range(0, len(order), config.batch_size):
                rows = [train_records[i] for i in order[start:start + config.batch_size]]
                tokens, valid, targets = collate(rows)
                optimizer.zero_grad(set_to_none=True)
                result = model(tokens, valid)
                loss = torch.nn.functional.cross_entropy(result.logits, targets)
                if not torch.isfinite(loss):
                    raise ArithmeticError("Training loss is non-finite")
                loss.backward()
                if any(parameter.grad is not None and not torch.isfinite(parameter.grad).all()
                       for parameter in model.parameters()):
                    raise ArithmeticError("Training gradients are non-finite")
                optimizer.step()
                total_loss += float(loss.detach()) * len(rows)
            history.append({"epoch": epoch, "loss": total_loss / len(train_records),
                            "n_samples": len(train_records)})
            checkpoint = {"identity": identity, "epoch": epoch, "history": history,
                          "model_state": model.state_dict(), "optimizer_state": optimizer.state_dict(),
                          "rng": checkpoint_rng(), "sampler_rng": sampler.get_state(),
                          "elapsed_seconds": elapsed_before + time.perf_counter() - started}
            atomic_write(checkpoint_path, lambda path: torch.save(checkpoint, path))
            completed = epoch
            write_json(directory / "run.json", {
                "identity": identity, "completed_epochs": completed, "expected_epochs": config.epochs,
                "status": "completed" if completed == config.epochs else "incomplete",
                "checkpoint_sha256": file_hash(checkpoint_path), "history": history,
                "elapsed_seconds": checkpoint["elapsed_seconds"]})
        # A crash after checkpoint publication but before the summary is recoverable.
        manifest = {"identity": identity, "completed_epochs": completed, "expected_epochs": config.epochs,
                    "status": "completed" if completed == config.epochs else "incomplete",
                    "checkpoint_sha256": file_hash(checkpoint_path), "history": history,
                    "elapsed_seconds": checkpoint["elapsed_seconds"]}
        write_json(directory / "run.json", manifest)
        return manifest
