"""Single-command execution with validated stage receipts for resume."""

import json
import math
from pathlib import Path

from .artifacts import read_sealed, seal, write_json
from .data.pipeline import file_hash, fingerprint
from .model.predictor import Predictor
from .model.training import run_lock, source_hash


def _study_directory(name: str, directory: Path) -> Path:
    return directory / ("E1-e1-run" if name == "E1" else f"{name}-run")


def _stage_files(name: str, artifact: Path, directory: Path, streaming: bool) -> list[Path]:
    """Immutable outputs needed to interpret/replay a completed stage."""
    files = {artifact}
    if name == "train":
        files.add(directory / "base/run.json")
    if streaming and name in {"E1", "E2", "E3"}:
        files.add(_study_directory(name, directory) / "records.sqlite")
    if name == "E2":
        models = _study_directory(name, directory) / "models" if streaming else directory / "E2-models"
        for model_dir in models.iterdir():
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


def _validate_streamed_study(name: str, payload: dict, directory: Path, prepared: dict, predictor: Predictor) -> None:
    identity = payload["identity"]
    prefix_ids = [row["prefix_id"] for row in prepared["prefixes"]["test"]]
    expected = len(prefix_ids)
    if (payload["status"] != "completed" or payload["study"] != name or identity["study"] != name
            or identity["dataset"] != predictor.identity["dataset_sha256"]
            or identity["checkpoint"] != predictor.checkpoint_id
            or identity["source"] != source_hash()
            or sorted(identity["prefix_ids"]) != sorted(prefix_ids)
            or payload["baseline_checkpoint"] != predictor.checkpoint_id
            or payload["completed_prefixes"] != expected or payload["expected_prefixes"] != expected):
        raise ValueError(f"Streamed study publication mismatch: {name}")
    ledger = _study_directory(name, directory) / "records.sqlite"
    if Path(payload["records_database"]) != ledger.relative_to(directory) or file_hash(ledger) != payload["records_sha256"]:
        raise ValueError(f"Streamed study ledger checksum mismatch: {name}")
    if name == "E1":
        records = payload["records"]
        if sorted(row["prefix_id"] for row in records) != sorted(prefix_ids):
            raise ValueError("Incomplete E1 prefix records")
        return
    arms = ([("BASE", seed) for seed in range(2001, 2006)] + [("E2-FC", seed) for seed in range(2006, 2011)]
            if name == "E2" else [("E3-PAPER", None)])
    if (payload["profile"] != ("E2-FC" if name == "E2" else "E3-PAPER")
            or [(pair["arm"], pair["seed"]) for pair in payload["pairs"]] != arms
            or payload["completed_units"] != expected * len(arms)
            or payload["expected_units"] != payload["completed_units"]
            or any(pair["completed_prefixes"] != expected for pair in payload["pairs"])):
        raise ValueError(f"Incomplete streamed study schedule: {name}")
    if name == "E2":
        for pair in payload["pairs"]:
            model = ledger.parent / "models" / f"{pair['arm']}-{pair['seed']}" / "checkpoint.pt"
            if file_hash(model) != pair["checkpoint_sha256"]:
                raise ValueError("Streamed E2 checkpoint checksum mismatch")


def _validate_publication(name: str, artifact: Path, directory: Path, config: dict,
                          raw_hash: str, streaming: bool, methods: tuple[str, ...]) -> None:
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
    if streaming and name in {"E1", "E2", "E3"}:
        _validate_streamed_study(name, payload, directory, prepared, predictor)
        return
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
        be_only = methods == ("BE",)
        if (payload["evaluation_mode"] != ("be-only" if be_only else "paired")
                or payload["paired_status"] != ("not_evaluated" if be_only else "completed")
                or set(payload["methods"]) != set(methods)):
            raise ValueError("Evaluation publication mode mismatch")
        for candidate in payload["candidates"]:
            path = directory / "evaluation/candidates" / str(candidate["seed"]) / "checkpoint.pt"
            if file_hash(path) != candidate["checkpoint_sha256"]:
                raise ValueError("Evaluation candidate checksum mismatch")
        for folder, checkpoint_id in [("baseline-graphs", predictor.checkpoint_id),
                                      ("candidate-graphs", payload["selected"]["checkpoint_sha256"])]:
            for method in methods:
                graph = read_sealed(directory / "evaluation" / folder / f"{method}.json")
                if graph["status"] != "completed" or graph["identity"]["checkpoint"] != checkpoint_id:
                    raise ValueError("Evaluation graph publication mismatch")


def run_pipeline(dataset_config: Path, training_config: Path, directory: Path, *,
                 streaming: bool = False, study_max_seconds: float = 3600,
                 be_only: bool = False) -> dict:
    from .__main__ import main
    if not math.isfinite(study_max_seconds) or study_max_seconds <= 0:
        raise ValueError("Study wall time quota must be finite and positive")
    dataset_config, training_config = dataset_config.resolve(), training_config.resolve()
    directory = directory.resolve()
    config = json.loads(dataset_config.read_text(encoding="utf-8-sig"))
    raw_hash = file_hash((dataset_config.parent / config["path"]).resolve())
    identity = {"dataset_config": file_hash(dataset_config), "training_config": file_hash(training_config),
                "raw_data": raw_hash, "source": source_hash(), "schema_version": 2}
    if streaming:
        identity["streaming_studies"] = True
    if be_only:
        identity["evaluation_mode"] = "be-only"
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
        command = ["experiment", name, *prediction_args, "--output", str(output)]
        if streaming:
            command.extend(["--streaming", "--max-seconds", str(study_max_seconds)])
        stages.append((name, command, output))
    evaluate = ["evaluate", *prediction_args, "--output", str(directory / "evaluation")]
    methods = ("BE",) if be_only else ("BE", "AE")
    if be_only:
        evaluate.append("--be-only")
    stages.append(("evaluate", evaluate, directory / "evaluation/evaluation.json"))
    for method in methods:
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
            progress.pop("study_progress", None)
            write_json(progress_path, seal(progress))
            if name == "train" and artifact.exists():
                command.append("--resume")
            if name == "train" or not artifact.exists():
                main(command)
            if streaming and name in {"E1", "E2", "E3"} and not artifact.exists():
                study_progress = _study_directory(name, directory) / "progress.json"
                if read_sealed(study_progress)["status"] != "incomplete":
                    raise ValueError(f"Missing publication for streamed study: {name}")
                progress["study_progress"] = str(study_progress.relative_to(directory))
                write_json(progress_path, seal(progress))
                return progress
            if name != "train":
                _validate_publication(name, artifact, directory, config, raw_hash, streaming, methods)
            files = _stage_files(name, artifact, directory, streaming)
            progress["completed"][name] = {"artifact": str(artifact.relative_to(directory)),
                                            "sha256": file_hash(artifact), "command": command,
                                            "files": {str(path.relative_to(directory)): file_hash(path) for path in files}}
            write_json(progress_path, seal(progress))
        progress.update(status="completed", active_stage=None)
        write_json(progress_path, seal(progress))
        return progress
