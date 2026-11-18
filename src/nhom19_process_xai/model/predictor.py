"""Identity-checked checkpoint inference shared by experiments and explainers."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from ..data.pipeline import file_hash, fingerprint
from .transformer import ModelConfig, ProcessTransformer


@dataclass(frozen=True)
class Prediction:
    probabilities: np.ndarray
    attention: np.ndarray
    effective_attention: np.ndarray
    valid: np.ndarray
    checkpoint_id: str
    class_order: tuple[str, ...]


class Predictor:
    def __init__(self, checkpoint_path: Path, prepared: dict):
        self.checkpoint_id = file_hash(checkpoint_path)
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
        self.identity = checkpoint["identity"]
        if self.identity["dataset_sha256"] != fingerprint(prepared):
            raise ValueError("Checkpoint and prepared dataset differ")
        if checkpoint["epoch"] != self.identity["training"]["epochs"]:
            raise ValueError("Incomplete checkpoint cannot serve as final inference model")
        self.model = ProcessTransformer(ModelConfig(**self.identity["model"]))
        self.model.load_state_dict(checkpoint["model_state"])
        self.model.eval()
        self.inputs = self.identity["vocabulary"]["inputs"]
        outputs = self.identity["vocabulary"]["outputs"]
        self.class_order = tuple(sorted(outputs, key=outputs.get))
        torch.set_num_threads(self.identity["training"]["num_threads"])

    def predict(self, activities: tuple[str | None, ...] | list[str | None],
                intervention_positions: tuple[int, ...] = (), mode: str = "E3-PAPER") -> Prediction:
        # None denotes PAD. A literal string '[PAD]' remains an activity label.
        labels = list(activities) if activities else [None]
        ids = torch.tensor([[0 if label is None else self.inputs.get(label, 1) for label in labels]],
                           dtype=torch.int64)
        valid = torch.tensor([[label is not None for label in labels]], dtype=torch.bool)
        intervention = torch.zeros_like(valid)
        for position in intervention_positions:
            if not 0 <= position < len(labels) or not valid[0, position]:
                raise ValueError("Intervention position must identify a valid original occurrence")
            intervention[0, position] = True
        with torch.inference_mode():
            result = self.model(ids, valid, intervention=intervention, mode=mode)
        return Prediction(result.probabilities[0].double().numpy(),
                          result.attention_raw[0].double().numpy(),
                          result.attention_effective[0].double().numpy(),
                          valid[0].numpy(), self.checkpoint_id, self.class_order)
