import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from nhom19_process_xai.data.preparation import prepare_file
from nhom19_process_xai.model.training import TrainingConfig, run_lock, train


pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows lock recovery tool")
ROOT = Path(__file__).resolve().parents[1]


def recover(directory, *flags):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/recover_run_lock.py"), str(directory), *flags],
        capture_output=True, text=True, timeout=20,
    )


def test_recover_after_crash_and_resume_training(tmp_path):
    config_path = ROOT / "configs/fixture/dataset.json"
    prepared = prepare_file(json.loads(config_path.read_text()), config_path.parent, tmp_path / "prepared.json")
    config = TrainingConfig(epochs=2, batch_size=2)
    directory = tmp_path / "run"
    train(prepared, directory, config, stop_after_epoch=1)
    crash = subprocess.run(
        [sys.executable, "-c",
         "import os, sys; from pathlib import Path; "
         "from nhom19_process_xai.model.training import run_lock; "
         "lock = run_lock(Path(sys.argv[1])); lock.__enter__(); os._exit(17)", str(directory)],
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")}, timeout=30,
    )
    assert crash.returncode == 17
    marker = directory / "writer.lock"
    checkpoint = directory / "checkpoint.pt"
    checkpoint_before = checkpoint.read_bytes()

    with pytest.raises(FileExistsError):
        train(prepared, directory, config, resume=True)
    inspected = recover(directory)
    assert inspected.returncode == 0 and inspected.stdout.strip() == "writer.lock: stale"
    assert marker.exists()
    removed = recover(directory, "--remove")
    assert removed.returncode == 0, removed.stderr
    assert removed.stdout.strip() == "writer.lock: removed"
    assert not marker.exists() and checkpoint.read_bytes() == checkpoint_before
    missing = recover(directory, "--remove")
    assert missing.returncode == 0 and missing.stdout.strip() == "writer.lock: missing"
    assert train(prepared, directory, config, resume=True)["status"] == "completed"


def test_recovery_refuses_live_owner_and_invalid_marker(tmp_path):
    marker = tmp_path / "writer.lock"
    with run_lock(tmp_path):
        result = recover(tmp_path, "--remove")
        assert result.returncode == 1 and result.stdout.strip() == "writer.lock: active"
        assert marker.read_text() == str(os.getpid())

    marker.write_text("not a PID")
    result = recover(tmp_path, "--remove")
    assert result.returncode == 1 and "valid PID" in result.stderr
    assert marker.read_text() == "not a PID"
