import json
from pathlib import Path
import sqlite3
from contextlib import closing

import networkx as nx
import pytest

from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.preparation import prepare_file
from nhom19_process_xai.experiments.e1_streaming import decode, run_streaming_e1
from nhom19_process_xai.experiments.perturbations import _replacements, variants
from nhom19_process_xai.experiments.studies import run_study
from nhom19_process_xai.model.training import TrainingConfig, train
from scripts.count_e1_variants import count_paths


def test_lazy_replacements_agree_with_sorted_simple_paths():
    graph = nx.DiGraph([("A", "D"), ("A", "B"), ("B", "B"), ("B", "D"),
                        ("B", "C"), ("C", "A"), ("C", "D"), ("X", "A")])
    for source in graph:
        for target in graph:
            if source != target:
                expected = sorted(tuple(path[1:-1]) for path in nx.all_simple_paths(graph, source, target))
                assert list(_replacements(graph, source, target)) == expected
    assert list(_replacements(graph, "A", "A")) == []


def test_induced_schedule_retains_boundary_variants_and_excludes_identity():
    graph = nx.DiGraph([("A", "B"), ("B", "D"), ("A", "C"), ("C", "D"),
                        ("A", "D"), ("D", "A"), ("C", "C")])
    starts = {"A", "C"}
    prefixes = [("A", "B", "D"), ("A", "C", "D"), ("C", "B", "D"), ("D", "A")]
    full = [(labels, variant) for labels in prefixes for variant in variants(labels, "fixture", graph, starts)]
    retained = {"A", "B", "D"}
    expected = sum(variant.operation == "mask" or variant.position in (0, len(labels) - 1)
                   or {labels[variant.position - 1], *variant.replacement, labels[variant.position + 1]} <= retained
                   for labels, variant in full)

    exact = count_paths(graph, starts, iter(prefixes))
    bound = count_paths(graph, starts, iter(prefixes), 3)

    assert exact["variant_count"] == len(full)
    assert set(bound["induced_activities"]) == retained
    assert "variant_count" not in bound
    assert bound["variant_count_lower_bound"] == expected < exact["variant_count"]


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
