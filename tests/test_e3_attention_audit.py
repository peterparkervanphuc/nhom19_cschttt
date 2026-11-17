import json
from pathlib import Path
import sqlite3

import pytest

from nhom19_process_xai.artifacts import read_sealed, seal, write_json
from nhom19_process_xai.data.pipeline import file_hash
from nhom19_process_xai.data.preparation import prepare_file
from nhom19_process_xai.experiments.streaming import run_streaming_study
from nhom19_process_xai.explain.runner import run_explainers
from nhom19_process_xai.model.training import TrainingConfig, train
from scripts.audit_streamed_study import audit


def test_e3_audit_links_retained_attention_and_rejects_wrong_mass(tmp_path):
    config = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    prepared = prepare_file(json.loads(config.read_text()), config.parent, tmp_path / "prepared.json")
    checkpoint = tmp_path / "base/checkpoint.pt"
    train(prepared, checkpoint.parent, TrainingConfig(epochs=1))
    manifest_path = tmp_path / "E3.json"
    manifest = run_streaming_study("E3", prepared, checkpoint, manifest_path)
    run_explainers(prepared, checkpoint, tmp_path / "cache", be_only=True)
    cache = tmp_path / "cache/ledger.sqlite"
    result = audit(manifest_path, tmp_path / "prepared.json", checkpoint, baseline_cache=cache)
    assert result["baseline_attention_cache"]["prefixes"] == 3
    assert result["baseline_attention_cache"]["cache_sha256"] == file_hash(cache)
    assert result["baseline_attention_cache"]["occurrences"] == sum(
        len(p["activities"]) for p in prepared["prefixes"]["test"])
    ledger = tmp_path / manifest["records_database"]
    with sqlite3.connect(ledger) as db:
        arm, seed, prefix_id, raw = db.execute("SELECT * FROM records LIMIT 1").fetchone()
        row = json.loads(raw)["payload"]
        row["records"][0]["original_row_mass"][0][0] += .1
        db.execute("UPDATE records SET payload=? WHERE arm=? AND seed=? AND prefix_id=?",
                   (json.dumps(seal(row)), arm, seed, prefix_id))
    changed = read_sealed(manifest_path)
    changed["records_sha256"] = file_hash(ledger)
    write_json(manifest_path, seal(changed))
    with pytest.raises(ValueError, match="attention"):
        audit(manifest_path, tmp_path / "prepared.json", checkpoint, baseline_cache=cache)
