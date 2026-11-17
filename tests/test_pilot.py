import json
from pathlib import Path

import networkx as nx
import pytest

from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.preparation import prepare_file
from nhom19_process_xai.experiments.perturbations import variants
from nhom19_process_xai.model.training import TrainingConfig, train
from nhom19_process_xai.pilot import dfg_workload, run_pilot, select_pilot_prefixes


def test_workload_exact_and_censored_counts():
    graph = nx.DiGraph([("A", "B"), ("B", "C"), ("A", "C"), ("A", "D"), ("D", "C")])
    prefix = {"prefix_id": "one", "activities": ["A", "B", "C"]}
    actual = list(variants(prefix["activities"], "one", graph, {"A", "B"}))
    exact = dfg_workload([prefix], graph, {"A", "B"}, 10)
    assert exact["exact"]
    assert exact["total_variants_lower_bound"] == len(actual)
    censored = dfg_workload([prefix], graph, {"A", "B"}, 1)
    assert not censored["exact"]
    assert censored["total_variants_lower_bound"] <= len(actual)


def test_selection_and_pilot_are_explicitly_partial(tmp_path):
    config = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    prepared = prepare_file(json.loads(config.read_text()), config.parent, tmp_path / "prepared.json")
    sample = select_pilot_prefixes(prepared["prefixes"]["test"], 2)
    assert [len(row["activities"]) for row in sample] == [1, 2]
    assert sample == select_pilot_prefixes(list(reversed(prepared["prefixes"]["test"])), 2)
    train(prepared, tmp_path / "base", TrainingConfig(epochs=1))
    checkpoint = tmp_path / "base/checkpoint.pt"
    result = run_pilot(prepared, checkpoint, tmp_path / "pilot", sample_size=2,
                       contexts_per_prefix=1, minimum_ram_bytes=0, minimum_disk_bytes=0)
    assert result["status"] == "completed"
    assert result["primary_status"] == "incomplete"
    assert result["completed_contexts"] == 2
    assert result["observed_subset_coverage"] < 1
    assert result["full_population_expected_contexts"] is None
    assert read_sealed(tmp_path / "pilot/pilot.json")["sample_ids"] == [row["prefix_id"] for row in sample]
    assert not (tmp_path / "pilot/AE.json").exists()
    with pytest.raises(FileExistsError):
        run_pilot(prepared, checkpoint, tmp_path / "pilot")
    stopped = run_pilot(prepared, checkpoint, tmp_path / "stopped", minimum_disk_bytes=10**30)
    assert stopped["status"] == "incomplete"
    assert stopped["stop_reason"] == "disk_floor"
    assert stopped["forward_executions"] == 0
