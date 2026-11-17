import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
import torch

from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.preparation import prepare_file
from nhom19_process_xai.evaluate.xai import METRICS, evaluate_prefix, paired_method_differences, run_evaluation, sample_prefixes, weight_distance
from nhom19_process_xai.model.predictor import Prediction
from nhom19_process_xai.model.training import TrainingConfig, train
from scripts.audit_xai_evaluation import audit


def test_six_properties_hand_fixture():
    prediction = Prediction(np.array([.8, .2]), np.ones((1, 2, 2))/2,
                            np.ones((1, 2, 2))/2, np.array([True, True]), "baseline", ("X", "Y"))
    prefix = {"prefix_id": "p", "case_id": "c", "activities": ["A", "B"]}
    features = {"universe": ["A", "B"], "common": [.7, .3], "variants": [
        {"variant_id": "v1", "activities": [None, "B"], "original_activity": "A", "cosine_similarity": .8},
        {"variant_id": "v2", "activities": [], "original_activity": "B", "cosine_similarity": .6}]}
    record = evaluate_prefix(prefix, prediction, features, {("A", "X"), ("B", "Y")},
                              prediction, features, {("A", "X")})
    assert record["values"] == pytest.approx({"correctness": -1., "completeness_precision": 1.,
                                 "completeness_recall": 1., "completeness_f1": 1.,
                                 "consistency": .5, "continuity": .7, "contrastivity": .4,
                                 "compactness_rules": 2, "compactness_rhs": 1.}, abs=1e-12, rel=0)
    assert record["variant_records"][0]["cohort"] == "near"


def test_raw_weight_distance_and_sample():
    baseline, candidate = torch.nn.Linear(2, 1, bias=False), torch.nn.Linear(2, 1, bias=False)
    with torch.no_grad():
        baseline.weight.copy_(torch.tensor([[-1., 0.]]))
        candidate.weight.copy_(torch.tensor([[1., 1.]]))
    assert weight_distance(baseline, candidate) == 1.5
    rows = [{"prefix_id": str(i)} for i in range(10)]
    assert len(sample_prefixes(rows)) == 8
    assert sample_prefixes(rows) == sample_prefixes(list(reversed(rows)))
    assert sample_prefixes([]) == []


def test_comparison_uses_valid_paired_intersection():
    def row(identifier, value):
        return {"prefix_id": identifier, "values": dict.fromkeys(METRICS, value)}
    methods = {"BE": {"records": [row("a", .2), row("b", None), row("c", .9)]},
               "AE": {"records": [row("c", None), row("b", .8), row("a", .5)]}}
    result = paired_method_differences(methods)["correctness"]
    assert result["paired_valid"] == 1
    assert result["excluded_unpaired_null"] == 2
    assert result["difference"]["mean"] == pytest.approx(.3)
    assert result["difference"]["sd"] is None
    assert result["BE_on_intersection"]["mean"] == .2
    methods["AE"]["records"].pop()
    with pytest.raises(ValueError, match="shared"):
        paired_method_differences(methods)


def test_co03_and_all_xai_outputs(tmp_path):
    config_path = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    prepare_file(json.loads(config_path.read_text()), config_path.parent, tmp_path / "prepared.json")
    data = read_sealed(tmp_path / "prepared.json")
    train(data, tmp_path / "base", TrainingConfig(epochs=1))
    result = run_evaluation(data, tmp_path / "base/checkpoint.pt", tmp_path / "eval")
    assert result["status"] == "completed"
    assert len(result["candidates"]) == 5
    assert result["selected"] == min(result["candidates"], key=lambda row: (-row["distance"], row["seed"]))
    assert len(result["sample_ids"]) == 2
    for method in ["BE", "AE"]:
        assert set(result["methods"][method]["summary"]) == set(METRICS)
        assert all(row["n_total"] == 2 for row in result["methods"][method]["summary"].values())
    assert read_sealed(tmp_path / "eval/evaluation.json")["status"] == "completed"
    checked = audit(tmp_path / "eval", tmp_path / "prepared.json", tmp_path / "base/checkpoint.pt", None)
    assert checked["status"] == "verified" and checked["verified_method_records"] == 4
    original = tmp_path / "eval/baseline-graphs/BE.json"
    be_result = run_evaluation(data, tmp_path / "base/checkpoint.pt", tmp_path / "be",
                               be_only=True, baseline_be=original)
    assert be_result["methods"] == {"BE": result["methods"]["BE"]}
    assert be_result["paired_status"] == "not_evaluated"
    assert be_result["paired_AE_minus_BE"] is None
    assert be_result["graph_runs"]["candidate-graphs"]["ae_completed"] == 0
    assert not (tmp_path / "be/candidate-graphs/AE.json").exists()
    checked = audit(tmp_path / "be", tmp_path / "prepared.json", tmp_path / "base/checkpoint.pt", original)
    assert checked["status"] == "verified" and checked["verified_method_records"] == 2
    with pytest.raises(ValueError, match="Graph identity or coverage mismatch"):
        run_evaluation(data, tmp_path / "base/checkpoint.pt", tmp_path / "wrong",
                       be_only=True, baseline_be=tmp_path / "be/candidate-graphs/BE.json")
    assert not (tmp_path / "wrong/candidates").exists()


def test_be_resource_pause_prevents_evaluation_publication(tmp_path):
    config_path = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    prepare_file(json.loads(config_path.read_text()), config_path.parent, tmp_path / "prepared.json")
    data = read_sealed(tmp_path / "prepared.json")
    checkpoint = tmp_path / "base/checkpoint.pt"
    train(data, checkpoint.parent, TrainingConfig(epochs=1))
    directory = tmp_path / "paused-eval"
    with patch("nhom19_process_xai.explain.runner.resource_snapshot",
               return_value={"disk_free_bytes": 0, "system_available_ram_bytes": 10**12}):
        with pytest.raises(RuntimeError, match="BE graph paused"):
            run_evaluation(data, checkpoint, directory, be_only=True)
    assert not (directory / "evaluation.json").exists()
    assert read_sealed(directory / "baseline-graphs/coverage.json")["be_status"] == "incomplete"
    assert not (directory / "candidate-graphs").exists()
    assert run_evaluation(data, checkpoint, directory, be_only=True)["status"] == "completed"
