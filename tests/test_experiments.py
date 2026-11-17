import json
from pathlib import Path

import networkx as nx
import numpy as np
import pytest

from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.preparation import prepare_file
from nhom19_process_xai.experiments.perturbations import variants
from nhom19_process_xai.experiments.studies import attention_bin, attention_displacement, e2_pair, run_study
from nhom19_process_xai.model.predictor import Prediction
from nhom19_process_xai.model.training import TrainingConfig, train


def test_path_replacements_keep_original_attribution():
    graph = nx.DiGraph([("A", "C"), ("A", "B"), ("B", "C"), ("B", "D"), ("D", "C")])
    rows = [row for row in variants(["A", "X", "C"], "prefix", graph, {"A"}) if row.position == 1]
    assert {row.activities for row in rows} == {("A", None, "C"), ("A", "C"), ("A", "B", "C"), ("A", "B", "D", "C")}
    assert {row.original_activity for row in rows} == {"X"}
    assert len({row.variant_id for row in rows}) == 4


def test_max_bins_and_mass_accounting():
    assert [attention_bin(value) for value in [0, .25, .5, .75, 1]] == [0, 1, 2, 3, 3]
    original = np.array([[[.25, .75], [.60, .40]]])
    paper = np.array([[[.25, 0], [0, 0]]])
    author = np.array([[[1., 0], [0, 0]]])
    left = attention_displacement(original, paper, 1)
    right = attention_displacement(original, author, 1)
    assert left["half_l1"] == .875
    assert right["half_l1"] == 1.25
    assert left["support_removed_mass"] == 1.75
    assert right["net_mass_removed"] == 1
    assert left["row_renormalized_tvd"] == [.75]
    assert left["excluded_zero_rows"] == 1


def test_jsd_joint_matches_rows_and_rejects_wrong_pair():
    left = np.array([[[.9, .1], [.9, .1]], [[.1, .9], [.1, .9]]])
    right = left[::-1].copy()
    first = Prediction(np.array([.8, .2]), left, left, np.array([True, True]), "base", ("A", "B"))
    second = Prediction(np.array([.8, .2]), right, right, np.array([True, True]), "other", ("A", "B"))
    result = e2_pair(first, second)
    assert result["jsd"] == pytest.approx(np.mean([row["jsd"] for row in result["row_records"]]))
    assert result["jsd"] > 0
    assert result["prediction_tvd"] == 0
    assert result["max_l1"] == .225
    second.valid[1] = False
    with pytest.raises(ValueError, match="support"):
        e2_pair(first, second)


def test_three_studies_end_to_end_fixture(tmp_path):
    config_path = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    data_path = tmp_path / "prepared.json"
    prepare_file(json.loads(config_path.read_text()), config_path.parent, data_path)
    prepared = read_sealed(data_path)
    train(prepared, tmp_path / "base", TrainingConfig(epochs=1))
    checkpoint = tmp_path / "base/checkpoint.pt"
    for name in ["E1", "E2", "E3"]:
        output = tmp_path / f"{name}.json"
        result = run_study(name, prepared, checkpoint, output)
        assert read_sealed(output)["status"] == "completed"
        assert result["completed_prefixes"] == 3
        if name == "E2":
            assert result["completed_pairs"] == 10
            assert all(len(pair["records"]) == 3 for pair in result["pairs"])
        else:
            assert len(result["records"]) == 3
