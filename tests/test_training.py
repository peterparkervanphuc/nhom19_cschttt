import json
from pathlib import Path

import numpy as np
import pytest
import torch

from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.preparation import prepare_file
from nhom19_process_xai.model.predictor import Predictor
from nhom19_process_xai.model.training import TrainingConfig, collate, train


@pytest.fixture
def prepared(tmp_path):
    config_path = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    config = json.loads(config_path.read_text())
    output = tmp_path / "prepared.json"
    value = prepare_file(config, config_path.parent, output)
    assert read_sealed(output) == json.loads(json.dumps(value))
    return read_sealed(output)


def test_exact_epoch_resume(prepared, tmp_path):
    config = TrainingConfig(epochs=3, batch_size=2)
    continuous = tmp_path / "continuous"
    resumed = tmp_path / "resumed"
    train(prepared, continuous, config)
    first = train(prepared, resumed, config, stop_after_epoch=1)
    assert first["status"] == "incomplete"
    with pytest.raises(ValueError, match="Incomplete"):
        Predictor(resumed / "checkpoint.pt", prepared)
    result = train(prepared, resumed, config, resume=True)
    left = torch.load(continuous / "checkpoint.pt", weights_only=True)
    right = torch.load(resumed / "checkpoint.pt", weights_only=True)
    assert result["status"] == "completed"
    assert left["history"] == right["history"]
    for key in left["model_state"]:
        assert torch.equal(left["model_state"][key], right["model_state"][key]), key
    predictor = Predictor(resumed / "checkpoint.pt", prepared)
    actual = predictor.predict(["A", "A"])
    np.testing.assert_allclose(actual.probabilities.sum(), 1, atol=1e-6)
    assert actual.attention.shape == (4, 2, 2)
    assert np.all(predictor.predict([None, None]).attention == 0)
    assert np.isfinite(predictor.predict([]).probabilities).all()
    assert predictor.predict(["D"]).valid.tolist() == [True]
    with pytest.raises(ValueError, match="Resume identity"):
        train(prepared, resumed, TrainingConfig(epochs=4, batch_size=2), resume=True)
    with pytest.raises(FileExistsError):
        train(prepared, resumed, config)


def test_preparation_identity_rejects_tampering(prepared, tmp_path):
    directory = tmp_path / "model"
    train(prepared, directory, TrainingConfig(epochs=1))
    prepared["split"]["train"].reverse()
    with pytest.raises(ValueError, match="dataset differ"):
        Predictor(directory / "checkpoint.pt", prepared)


def test_collate_contract(prepared):
    ids, valid, labels = collate(prepared["prefixes"]["train"])
    assert ids.tolist() == [[2, 0], [2, 2], [2, 0], [3, 0], [3, 2]]
    assert valid.tolist() == [[True, False], [True, True], [True, False], [True, False], [True, True]]
    assert labels.tolist() == [0, 1, 2, 0, 2]
    with pytest.raises(ValueError, match="Unseen"):
        collate(prepared["prefixes"]["test"])
