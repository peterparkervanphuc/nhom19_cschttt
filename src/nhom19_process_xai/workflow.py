"""Single-command execution with validated stage receipts for resume."""

import json
from pathlib import Path

from .artifacts import read_sealed, seal, write_json
from .data.pipeline import file_hash, fingerprint
from .model.predictor import Predictor
from .model.training import run_lock, source_hash


def _stage_files(name: str, artifact: Path, directory: Path) -> list[Path]:
    """Immutable outputs needed to interpret/replay a completed stage."""
    files = {artifact}
    if name == "train":
        files.add(directory / "base/run.json")
    elif name == "E2":
        for model_dir in (directory / "E2-models").iterdir():
            if model_dir.is_dir():
                files.update([model_dir / "checkpoint.pt", model_dir / "run.json"])
    elif name == "evaluate":
        files.update((directory / "evaluation").rglob("*.json"))
        files.update((directory / "evaluation").rglob("checkpoint.pt"))
    elif name.startswith("graph-"):
        manifest = read_sealed(artifact)
        for filename, digest in manifest["files"].items():
            path = artifact.parent / filename
            if Path(filename).name != filename or not path.is_file() or file_hash(path) != digest:
                raise ValueError("Graph file checksum mismatch")
            files.add(path)
    if any(not path.is_file() for path in files):
        raise ValueError(f"Missing required artifact for {name}")
    return sorted(files)


def _validate_publication(name: str, artifact: Path, directory: Path, config: dict, raw_hash: str) -> None:
    """Validate an orphaned atomic output against the persisted stage intent.

    Recovery is only allowed for the active stage, with unchanged input/source
    identity. Training resumes through its own checkpoint identity validation.
    """
    payload = read_sealed(artifact)
    if name == "prepare":
        if payload["config_sha256"] != fingerprint(config) or payload["raw_sha256"] != raw_hash:
            raise ValueError("Prepared publication identity mismatch")
        return
    prepared = read_sealed(directory / "prepared.json")
    predictor = Predictor(directory / "base/checkpoint.pt", prepared)
    if name.startswith("graph-"):
        method = name.removeprefix("graph-")
        source = directory / "evaluation/baseline-graphs" / f"{method}.json"
        if payload["method"] != method or payload["source_sha256"] != file_hash(source):
            raise ValueError("Graph publication identity mismatch")
        return
    if payload["identity"] != predictor.identity:
        raise ValueError(f"Stage publication identity mismatch: {name}")
    key = "checkpoint_sha256" if name == "predict" else "baseline_checkpoint"
    if payload[key] != predictor.checkpoint_id:
        raise ValueError(f"Stage checkpoint mismatch: {name}")
    expected = len(prepared["prefixes"]["test"])
    if name == "predict":
        if payload["expected"] != expected or payload["completed"] != expected or len(payload["records"]) != expected:
            raise ValueError("Incomplete prediction publication")
    elif payload["status"] != "completed":
        raise ValueError(f"Incomplete stage publication: {name}")
    elif name.startswith("E"):
        if payload["study"] != name or payload["completed_prefixes"] != expected:
            raise ValueError("Study publication coverage mismatch")
        if name == "E2":
            if payload["completed_pairs"] != 10 or len(payload["pairs"]) != 10:
                raise ValueError("Incomplete E2 publication")
            for pair in payload["pairs"]:
                path = directory / "E2-models" / f"{pair['arm']}-{pair['seed']}" / "checkpoint.pt"
                modified = Predictor(path, prepared)
                if any(row["modified_checkpoint"] != modified.checkpoint_id for row in pair["records"]):
                    raise ValueError("E2 model publication mismatch")
    elif name == "evaluate":
        for candidate in payload["candidates"]:
            path = directory / "evaluation/candidates" / str(candidate["seed"]) / "checkpoint.pt"
            if file_hash(path) != candidate["checkpoint_sha256"]:
                raise ValueError("Evaluation candidate checksum mismatch")
        for folder, checkpoint_id in [("baseline-graphs", predictor.checkpoint_id),
                                      ("candidate-graphs", payload["selected"]["checkpoint_sha256"])]:
            for method in ("BE", "AE"):
                graph = read_sealed(directory / "evaluation" / folder / f"{method}.json")
                if graph["status"] != "completed" or graph["identity"]["checkpoint"] != checkpoint_id:
                    raise ValueError("Evaluation graph publication mismatch")


def run_pipeline(dataset_config: Path, training_config: Path, directory: Path) -> dict:
    from .__main__ import main
    dataset_config, training_config = dataset_config.resolve(), training_config.resolve()
    directory = directory.resolve()
    config = json.loads(dataset_config.read_text(encoding="utf-8-sig"))
    raw_hash = file_hash((dataset_config.parent / config["path"]).resolve())
    identity = {"dataset_config": file_hash(dataset_config), "training_config": file_hash(training_config),
                "raw_data": raw_hash, "source": source_hash(), "schema_version": 2}
    progress_path = directory / "pipeline.json"
    prepared = directory / "prepared.json"
    checkpoint = directory / "base/checkpoint.pt"
    prediction_args = ["--prepared", str(prepared), "--checkpoint", str(checkpoint)]
    stages = [
        ("prepare", ["prepare", "--config", str(dataset_config), "--output", str(prepared)], prepared),
        ("train", ["train", "--prepared", str(prepared), "--config", str(training_config), "--output", str(directory / "base")], checkpoint),
        ("predict", ["predict", *prediction_args, "--output", str(directory / "predictions.json")], directory / "predictions.json"),
    ]
    for name in ("E1", "E2", "E3"):
        output = directory / f"{name}.json"
        stages.append((name, ["experiment", name, *prediction_args, "--output", str(output)], output))
    stages.append(("evaluate", ["evaluate", *prediction_args, "--output", str(directory / "evaluation")],
                   directory / "evaluation/evaluation.json"))
    for method in ("BE", "AE"):
        folder = directory / "graphs" / method
        stages.append(("graph-" + method, ["graph", "--explanation", str(directory / "evaluation/baseline-graphs" / f"{method}.json"),
                                           "--output", str(folder)], folder / "manifest.json"))
    with run_lock(directory):
        if progress_path.exists():
            progress = read_sealed(progress_path)
            if progress["identity"] != identity:
                raise ValueError("Pipeline resume identity differs")
        else:
            if any(path.name != "writer.lock" for path in directory.iterdir()):
                raise FileExistsError("New pipeline requires an empty output directory")
            progress = {"identity": identity, "status": "incomplete", "completed": {}}
        for name, command, artifact in stages:
            receipt = progress["completed"].get(name)
            if receipt is not None:
                for relative, digest in receipt["files"].items():
                    path = directory / relative
                    if not path.is_file() or file_hash(path) != digest:
                        raise ValueError(f"Stage receipt invalid: {name}, {relative}")
                continue
            previous_active = progress.get("active_stage")
            if artifact.exists() and previous_active != name:
                raise FileExistsError(f"Unowned stage output: {name}")
            progress["active_stage"] = name
            progress["status"] = "incomplete"
            write_json(progress_path, seal(progress))
            if name == "train" and artifact.exists():
                command.append("--resume")
            if name == "train" or not artifact.exists():
                main(command)
            if name != "train":
                _validate_publication(name, artifact, directory, config, raw_hash)
            files = _stage_files(name, artifact, directory)
            progress["completed"][name] = {"artifact": str(artifact.relative_to(directory)),
                                            "sha256": file_hash(artifact), "command": command,
                                            "files": {str(path.relative_to(directory)): file_hash(path) for path in files}}
            write_json(progress_path, seal(progress))
        progress.update(status="completed", active_stage=None)
        write_json(progress_path, seal(progress))
        return progress
