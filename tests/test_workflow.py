import json
from pathlib import Path

import pytest

from nhom19_process_xai import __main__ as cli
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
