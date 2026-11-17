import json
from pathlib import Path
import sqlite3
from contextlib import closing

import networkx as nx
import pytest

from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.preparation import prepare_file
from nhom19_process_xai.experiments.e1_streaming import decode, run_streaming_e1
from nhom19_process_xai.experiments.perturbations import _replacements
from nhom19_process_xai.experiments.studies import run_study
from nhom19_process_xai.model.training import TrainingConfig, train


def test_lazy_replacements_agree_with_sorted_simple_paths():
    graph = nx.DiGraph([("A", "D"), ("A", "B"), ("B", "B"), ("B", "D"),
                        ("B", "C"), ("C", "A"), ("C", "D"), ("X", "A")])
    for source in graph:
        for target in graph:
            if source != target:
                expected = sorted(tuple(path[1:-1]) for path in nx.all_simple_paths(graph, source, target))
                assert list(_replacements(graph, source, target)) == expected
    assert list(_replacements(graph, "A", "A")) == []


def test_variant_checkpoint_resumes_mid_prefix(tmp_path):
    config = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    prepared = prepare_file(json.loads(config.read_text()), config.parent, tmp_path / "prepared.json")
    train(prepared, tmp_path / "base", TrainingConfig(epochs=1))
    checkpoint = tmp_path / "base/checkpoint.pt"
    output = tmp_path / "stream.json"
    first = run_streaming_e1(prepared, checkpoint, output, 60, stop_after_variants=1)
    assert (first["status"], first["completed_prefixes"], first["completed_variants"]) == ("incomplete", 0, 1)
    assert not output.exists()
    assert read_sealed(tmp_path / "stream-e1-run/progress.json")["completed_variants"] == 1
    resumed = run_streaming_e1(prepared, checkpoint, output, 60)
    reference = run_study("E1", prepared, checkpoint, tmp_path / "in-memory.json")
    assert resumed["status"] == "completed"
    assert resumed["tau_b"] == reference["tau_b"]
    assert resumed["new_variants"] == resumed["completed_variants"] - 1
    with closing(sqlite3.connect(tmp_path / resumed["records_database"])) as db:
        for row in reference["records"]:
            serialized = db.execute("SELECT payload FROM variants WHERE prefix_id=? ORDER BY ordinal",
                                    (row["prefix_id"],))
            assert [decode(payload) for (payload,) in serialized] == json.loads(json.dumps(row["variants"]))
    assert resumed["records"] == sorted(
        [{key: value for key, value in row.items() if key != "variants"} for row in reference["records"]],
        key=lambda row: row["prefix_id"])
    with pytest.raises(FileExistsError):
        run_streaming_e1(prepared, checkpoint, output, 60)
