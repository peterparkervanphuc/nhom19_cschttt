import json
from pathlib import Path
import sqlite3

import pytest

from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.preparation import prepare_file
from nhom19_process_xai.experiments.streaming import run_streaming_study
from nhom19_process_xai.experiments.studies import run_study
from nhom19_process_xai.model.training import TrainingConfig, train


@pytest.mark.parametrize("name", ["E2", "E3"])
def test_streaming_resume_matches_in_memory_units(tmp_path, name):
    config = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    prepared = prepare_file(json.loads(config.read_text()), config.parent, tmp_path / "prepared.json")
    train(prepared, tmp_path / "base", TrainingConfig(epochs=1))
    checkpoint = tmp_path / "base/checkpoint.pt"
    output = tmp_path / "stream.json"
    first = run_streaming_study(name, prepared, checkpoint, output, stop_after_units=1)
    assert first["status"] == "incomplete"
    assert first["completed_units"] == 1
    assert not output.exists()
    complete = run_streaming_study(name, prepared, checkpoint, output)
    normal = run_study(name, prepared, checkpoint, tmp_path / "memory.json")
    assert complete["status"] == "completed"
    assert complete["completed_units"] == (30 if name == "E2" else 3)
    with sqlite3.connect(tmp_path / complete["records_database"]) as connection:
        rows = [json.loads(record[0])["payload"] for record in connection.execute("SELECT payload FROM records ORDER BY arm,seed,prefix_id")]
    expected = [row for pair in normal["pairs"] for row in pair["records"]] if name == "E2" else normal["records"]
    # Checkpoint files contain elapsed-time metadata, so independently trained
    # identical models have different file hashes. Compare numerical records.
    def numeric(row):
        return {key: value for key, value in row.items() if key not in {"modified_checkpoint", "baseline_checkpoint"}}
    assert sorted([numeric(row) for row in rows], key=lambda row: (row["prefix_id"], json.dumps(row, sort_keys=True))) == sorted(
        [numeric(json.loads(json.dumps(row))) for row in expected], key=lambda row: (row["prefix_id"], json.dumps(row, sort_keys=True)))
    assert read_sealed(output)["completed_units"] == len(rows)
