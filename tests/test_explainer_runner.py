import json
from pathlib import Path
import sqlite3
from unittest.mock import patch

import pytest

from nhom19_process_xai.__main__ import main
from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.pipeline import file_hash, fingerprint
from nhom19_process_xai.data.preparation import prepare_file
from nhom19_process_xai.explain.runner import CachedPredictor, run_explainers
from nhom19_process_xai.model.predictor import Predictor
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


@pytest.mark.parametrize("floor", ["disk_free_bytes", "system_available_ram_bytes"])
def test_be_resource_pause_resumes_exact_graph(trained_fixture, tmp_path, floor):
    data, checkpoint = trained_fixture
    ample = {"disk_free_bytes": 10**12, "system_available_ram_bytes": 10**12}
    scarce = {**ample, floor: 0}
    directory = tmp_path / "partial-be"
    with patch("nhom19_process_xai.explain.runner.resource_snapshot", side_effect=[ample, ample, scarce]):
        paused = run_explainers(data, checkpoint, directory)
    assert paused["be_status"] == "incomplete" and paused["be_completed_prefixes"] == 1
    assert paused["expected"] is None and paused["pending"] is None and paused["coverage"] is None
    assert not (directory / "BE.json").exists() and not (directory / "AE.json").exists()
    assert not (directory / "writer.lock").exists()
    assert len(list((directory / "be-prefixes").glob("*.json"))) == 1
    assert read_sealed(directory / "coverage.json")["stop_reason"] == (
        "disk_floor" if floor == "disk_free_bytes" else "available_ram_floor")
    resumed = run_explainers(data, checkpoint, directory)
    complete = run_explainers(data, checkpoint, tmp_path / "continuous-be")
    assert resumed["status"] == complete["status"] == "completed"
    for method in ("BE", "AE"):
        left = read_sealed(directory / f"{method}.json")
        right = read_sealed(tmp_path / "continuous-be" / f"{method}.json")
        assert left["edges"] == right["edges"]
        if method == "BE":
            assert left["prefix_records"] == right["prefix_records"]
        else:
            assert left["matrices"] == right["matrices"]


def test_explainer_wall_quota_keeps_be_unpublished(trained_fixture, tmp_path):
    data, checkpoint = trained_fixture
    paused = run_explainers(data, checkpoint, tmp_path / "wall", max_seconds=1e-20)
    assert paused["be_status"] == "incomplete" and paused["be_completed_prefixes"] == 0
    assert paused["stop_reason"] == "wall_time_quota"
    assert not (tmp_path / "wall/BE.json").exists()


@pytest.mark.parametrize("quota", [float("nan"), float("inf"), -1.])
def test_explainer_rejects_invalid_wall_quota(tmp_path, quota):
    with pytest.raises(ValueError, match="quota"):
        run_explainers({}, tmp_path / "missing.pt", tmp_path / "invalid", max_seconds=quota)


def test_ae_resource_pause_preserves_completed_be(trained_fixture, tmp_path):
    data, checkpoint = trained_fixture
    directory = tmp_path / "ae-resource"
    run_explainers(data, checkpoint, directory, be_only=True)
    original = (directory / "BE.json").read_bytes()
    ample = {"disk_free_bytes": 10**12, "system_available_ram_bytes": 10**12}
    with patch("nhom19_process_xai.explain.runner.resource_snapshot",
               side_effect=[ample, {**ample, "disk_free_bytes": 0}]):
        paused = run_explainers(data, checkpoint, directory)
    assert paused["be_status"] == "completed" and paused["status"] == "incomplete"
    assert paused["completed"] == 0 and paused["expected"] > 0
    assert paused["stop_reason"] == "disk_floor"
    assert (directory / "BE.json").read_bytes() == original
    assert not (directory / "AE.json").exists()
    assert run_explainers(data, checkpoint, directory)["status"] == "completed"


def test_explainer_cli_accepts_resumable_wall_quota(trained_fixture, tmp_path, capsys):
    _, checkpoint = trained_fixture
    args = ["explain", "--prepared", str(tmp_path / "prepared.json"), "--checkpoint", str(checkpoint),
            "--output", str(tmp_path / "cli-wall"), "--be-only"]
    main([*args, "--max-seconds", "1e-20"])
    paused = json.loads(capsys.readouterr().out)
    assert paused["be_status"] == "incomplete" and paused["ae_expected"] is None
    assert paused["be_completed_prefixes"] == 0 and paused["stop_reason"] == "wall_time_quota"
    main(args)
    assert json.loads(capsys.readouterr().out)["be_status"] == "completed"


def test_cache_writes_share_owner_transaction(trained_fixture, tmp_path):
    data, checkpoint = trained_fixture
    path = tmp_path / "batched-cache.sqlite"
    with sqlite3.connect(path) as owner:
        owner.execute("PRAGMA journal_mode=WAL")
        cache = CachedPredictor(Predictor(checkpoint, data), owner)
        owner.commit()
        labels = data["prefixes"]["test"][0]["activities"]
        cache.predict(labels)
        cache.predict([None] * len(labels))
        assert owner.in_transaction
        with sqlite3.connect(path) as observer:
            assert observer.execute("SELECT count(*) FROM inference").fetchone()[0] == 0
        owner.commit()
        with sqlite3.connect(path) as observer:
            assert observer.execute("SELECT count(*) FROM inference").fetchone()[0] == 2


def test_be_cache_is_durable_before_prefix_publication(trained_fixture, tmp_path, monkeypatch):
    from nhom19_process_xai.explain import runner
    data, checkpoint = trained_fixture
    original_write = runner.write_json
    classes = sorted(data["vocabulary"]["outputs"], key=data["vocabulary"]["outputs"].get)
    prefixes = {row["prefix_id"]: row for row in data["prefixes"]["test"]}
    checked = []

    def checked_write(path, envelope):
        if path.parent.name == "be-prefixes":
            identifier = envelope["payload"]["prefix_id"]
            key = fingerprint([file_hash(checkpoint), classes, prefixes[identifier]["activities"],
                               [], "E3-PAPER", "cpu", "float32"])
            with sqlite3.connect(path.parent.parent / "ledger.sqlite") as observer:
                assert observer.execute("SELECT 1 FROM inference WHERE key=?", (key,)).fetchone() == (1,)
            checked.append(identifier)
        original_write(path, envelope)

    monkeypatch.setattr(runner, "write_json", checked_write)
    run_explainers(data, checkpoint, tmp_path / "publication", be_only=True)
    assert set(checked) == prefixes.keys()
