import json
from pathlib import Path

import pytest

from nhom19_process_xai import __main__ as cli
from nhom19_process_xai.experiments import e1_streaming
from nhom19_process_xai.workflow import run_pipeline


@pytest.mark.parametrize("stage", ["prepare", "E2", "evaluate", "graph-AE"])
def test_recover_after_stage_publication_and_verify_children(tmp_path, monkeypatch, stage):
    dataset = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    training = tmp_path / "training.json"
    training.write_text(json.dumps({"epochs": 1}), encoding="utf-8")
    output = tmp_path / "pipeline"
    original_main = cli.main

    def interrupted(command):
        original_main(command)
        name = command[1] if command[0] == "experiment" else command[0]
        if command[0] == "graph":
            name += "-" + Path(command[command.index("--output") + 1]).name
        if name == stage:
            raise RuntimeError("simulated interruption after publication, before receipt")

    monkeypatch.setattr(cli, "main", interrupted)
    with pytest.raises(RuntimeError, match="simulated interruption"):
        run_pipeline(dataset, training, output)
    monkeypatch.setattr(cli, "main", original_main)
    result = run_pipeline(dataset, training, output)
    assert result["status"] == "completed"
    assert len(result["completed"]) == 9
    assert run_pipeline(dataset, training, output) == result
    (output / "graphs/AE/graph.graphml").write_text("damaged", encoding="utf-8")
    with pytest.raises(ValueError, match="receipt|checksum"):
        run_pipeline(dataset, training, output)


def test_streaming_pipeline_resumes_and_checks_ledger_receipts(tmp_path, monkeypatch):
    dataset = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    training = tmp_path / "training.json"
    training.write_text(json.dumps({"epochs": 1}), encoding="utf-8")
    output = tmp_path / "pipeline"
    original_run = e1_streaming.run_streaming_e1

    def checkpoint_e1(prepared, checkpoint, destination, max_seconds, *, stop_after_variants=None):
        return original_run(prepared, checkpoint, destination, max_seconds, stop_after_variants=1)

    monkeypatch.setattr(e1_streaming, "run_streaming_e1", checkpoint_e1)
    partial = run_pipeline(dataset, training, output, streaming=True)
    assert partial["status"] == "incomplete"
    assert partial["active_stage"] == "E1"
    assert list(partial["completed"]) == ["prepare", "train", "predict"]
    assert not (output / "E1.json").exists()

    monkeypatch.setattr(e1_streaming, "run_streaming_e1", original_run)
    original_main = cli.main

    def interrupt_after_e2_publication(command):
        original_main(command)
        if command[:2] == ["experiment", "E2"]:
            raise RuntimeError("simulated interrupted E2 publication")

    monkeypatch.setattr(cli, "main", interrupt_after_e2_publication)
    with pytest.raises(RuntimeError, match="interrupted E2 publication"):
        run_pipeline(dataset, training, output, streaming=True)
    monkeypatch.setattr(cli, "main", original_main)
    complete = run_pipeline(dataset, training, output, streaming=True)
    assert complete["status"] == "completed"
    for ledger in ("E1-e1-run/records.sqlite", "E2-run/records.sqlite", "E3-run/records.sqlite"):
        stage = ledger[:2]
        assert str(Path(ledger)) in complete["completed"][stage]["files"]
    assert str(Path("E2-run/models/BASE-2001/checkpoint.pt")) in complete["completed"]["E2"]["files"]
    with (output / "E3-run/records.sqlite").open("ab") as database:
        database.write(b"corruption")
    with pytest.raises(ValueError, match="Stage receipt invalid: E3"):
        run_pipeline(dataset, training, output, streaming=True)
