import json
from pathlib import Path
import sqlite3

import pytest

from nhom19_process_xai.__main__ import main
from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.preparation import prepare_file
from nhom19_process_xai.explain.runner import run_explainers
from nhom19_process_xai.model.training import TrainingConfig, train


@pytest.fixture
def trained_fixture(tmp_path):
    config_path = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    prepare_file(json.loads(config_path.read_text()), config_path.parent, tmp_path / "prepared.json")
    data = read_sealed(tmp_path / "prepared.json")
    train(data, tmp_path / "base", TrainingConfig(epochs=1))
    return data, tmp_path / "base/checkpoint.pt"


def test_durable_ae_resume_and_cache_votes(trained_fixture, tmp_path):
    data, checkpoint = trained_fixture
    partial_dir = tmp_path / "partial"
    interrupted = run_explainers(data, checkpoint, partial_dir, stop_after_contexts=1)
    assert interrupted["status"] == "incomplete"
    assert interrupted["completed"] == 1
    assert not (partial_dir / "AE.json").exists()
    resumed = run_explainers(data, checkpoint, partial_dir)
    continuous_dir = tmp_path / "continuous"
    complete = run_explainers(data, checkpoint, continuous_dir)
    assert resumed["status"] == complete["status"] == "completed"
    assert resumed["completed"] == resumed["expected"]
    left, right = read_sealed(partial_dir / "AE.json"), read_sealed(continuous_dir / "AE.json")
    assert left["matrices"] == right["matrices"]
    assert left["edges"] == right["edges"]
    assert left["retained_votes"] == right["retained_votes"]
    assert complete["cache_hits_this_session"] > 0
    again = run_explainers(data, checkpoint, partial_dir)
    assert again["forward_executions_this_session"] == 0
    with sqlite3.connect(partial_dir / "ledger.sqlite") as db:
        assert db.execute("SELECT count(*) FROM contexts").fetchone()[0] == resumed["expected"]


def test_identity_mismatch_rejected(trained_fixture, tmp_path):
    data, checkpoint = trained_fixture
    directory = tmp_path / "run"
    run_explainers(data, checkpoint, directory, stop_after_contexts=1)
    with sqlite3.connect(directory / "ledger.sqlite") as db:
        db.execute("UPDATE metadata SET value='{}' WHERE key='identity'")
    with pytest.raises(ValueError, match="identity"):
        run_explainers(data, checkpoint, directory)


def test_be_only_cli_keeps_ae_pending_and_resumable(trained_fixture, tmp_path, capsys):
    data, checkpoint = trained_fixture
    directory = tmp_path / "be-only"
    main(["explain", "--prepared", str(tmp_path / "prepared.json"),
          "--checkpoint", str(checkpoint), "--output", str(directory), "--be-only"])
    status = json.loads(capsys.readouterr().out)
    assert status["be_status"] == "completed"
    assert status["ae_status"] == "incomplete"
    assert status["ae_expected"] > 0 and status["ae_completed"] == 0
    assert (directory / "BE.json").exists() and not (directory / "AE.json").exists()
    completed = run_explainers(data, checkpoint, directory)
    assert completed["completed"] == status["ae_expected"]
    assert completed["status"] == "completed"
