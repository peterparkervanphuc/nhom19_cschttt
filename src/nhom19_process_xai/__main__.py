"""Reproducible command-line entry points for the research pipeline."""

import argparse
from dataclasses import fields
import json
from pathlib import Path

from .artifacts import read_sealed, seal, write_json
from .data.preparation import prepare_file
from .evaluate.metrics import predictive_metrics
from .model.predictor import Predictor
from .model.training import TrainingConfig, train
from .experiments.studies import run_study
from .explain.runner import run_explainers
from .evaluate.xai import run_evaluation
from .graphs.export import export_graph


def main(argv=None):
    parser = argparse.ArgumentParser(prog="nhom19_process_xai")
    subcommands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subcommands.add_parser("prepare")
    prepare_parser.add_argument("--config", type=Path, required=True)
    prepare_parser.add_argument("--output", type=Path, required=True)
    train_parser = subcommands.add_parser("train")
    train_parser.add_argument("--prepared", type=Path, required=True)
    train_parser.add_argument("--config", type=Path, required=True)
    train_parser.add_argument("--output", type=Path, required=True)
    train_parser.add_argument("--resume", action="store_true")
    prediction_parser = subcommands.add_parser("predict")
    prediction_parser.add_argument("--prepared", type=Path, required=True)
    prediction_parser.add_argument("--checkpoint", type=Path, required=True)
    prediction_parser.add_argument("--output", type=Path, required=True)
    experiment_parser = subcommands.add_parser("experiment")
    experiment_parser.add_argument("study", choices=["E1", "E2", "E3"])
    experiment_parser.add_argument("--prepared", type=Path, required=True)
    experiment_parser.add_argument("--checkpoint", type=Path, required=True)
    experiment_parser.add_argument("--output", type=Path, required=True)
    experiment_parser.add_argument("--profile")
    experiment_parser.add_argument("--streaming", action="store_true")
    experiment_parser.add_argument("--max-seconds", type=float, default=3600)
    experiment_parser.add_argument("--max-variants", type=int,
                                   help="Checkpoint streaming E1 after this many new variants")
    for command in ("explain", "evaluate"):
        command_parser = subcommands.add_parser(command)
        command_parser.add_argument("--prepared", type=Path, required=True)
        command_parser.add_argument("--checkpoint", type=Path, required=True)
        command_parser.add_argument("--output", type=Path, required=True)
        if command == "explain":
            command_parser.add_argument("--be-only", action="store_true",
                                        help="Export the BE result and count the AE workload without running AE")
            command_parser.add_argument("--max-seconds", type=float,
                                        help="Pause between BE prefixes or AE contexts; resume with the same output")
            command_parser.add_argument("--cache-policy", choices=["all", "baseline"], default="all",
                                        help="Persist all predictions or only unmasked baseline tensors")
        if command == "evaluate":
            command_parser.add_argument("--be-only", action="store_true", help="Evaluate BE without running AE")
            command_parser.add_argument("--baseline-be", type=Path, help="Reuse a verified BE graph with --be-only")
    graph_parser = subcommands.add_parser("graph")
    graph_parser.add_argument("--explanation", type=Path, required=True)
    graph_parser.add_argument("--output", type=Path, required=True)
    pilot_parser = subcommands.add_parser("pilot")
    pilot_parser.add_argument("--prepared", type=Path, required=True)
    pilot_parser.add_argument("--checkpoint", type=Path, required=True)
    pilot_parser.add_argument("--output", type=Path, required=True)
    pilot_parser.add_argument("--sample-size", type=int, default=12)
    pilot_parser.add_argument("--contexts-per-prefix", type=int, default=32)
    pilot_parser.add_argument("--max-seconds", type=float, default=120)
    pipeline_parser = subcommands.add_parser("pipeline")
    pipeline_parser.add_argument("--dataset-config", type=Path, required=True)
    pipeline_parser.add_argument("--training-config", type=Path, required=True)
    pipeline_parser.add_argument("--output", type=Path, required=True)
    pipeline_parser.add_argument("--streaming", action="store_true", help="Run E1–E3 with resumable SQLite ledgers")
    pipeline_parser.add_argument("--be-only", action="store_true",
                                 help="Evaluate BE and report the AE schedule without running AE")
    pipeline_parser.add_argument("--study-max-seconds", type=float,
                                 help="Wall time quota per streaming study session (default: 3600)")
    args = parser.parse_args(argv)
    if args.command == "pipeline":
        from .workflow import run_pipeline
        if args.study_max_seconds is not None and not args.streaming:
            parser.error("--study-max-seconds requires --streaming")
        result = run_pipeline(args.dataset_config, args.training_config, args.output,
                              streaming=args.streaming,
                              study_max_seconds=3600 if args.study_max_seconds is None else args.study_max_seconds,
                              be_only=args.be_only)
        print(json.dumps({"status": result["status"], "stages": len(result["completed"]),
                          "active_stage": result["active_stage"],
                          "evaluation_mode": result["identity"].get("evaluation_mode", "paired")}))
    elif args.command == "pilot":
        from .pilot import run_pilot
        result = run_pilot(read_sealed(args.prepared), args.checkpoint, args.output,
                           args.sample_size, args.contexts_per_prefix, max_seconds=args.max_seconds)
        print(json.dumps({key: result[key] for key in ("status", "primary_status", "stop_reason",
                                                      "completed_contexts", "observed_subset_expected_contexts")}))
    elif args.command == "graph":
        print(json.dumps(export_graph(args.explanation, args.output)))
    elif args.command == "prepare":
        config = json.loads(args.config.read_text(encoding="utf-8-sig"))
        data = prepare_file(config, args.config.parent, args.output)
        print(json.dumps(data["counts"]))
    elif args.command == "train":
        config = json.loads(args.config.read_text(encoding="utf-8-sig"))
        allowed = {field.name for field in fields(TrainingConfig)}
        if set(config) - allowed:
            raise ValueError("Unknown training configuration fields")
        result = train(read_sealed(args.prepared), args.output, TrainingConfig(**config), args.resume)
        print(json.dumps({"status": result["status"], "epochs": result["completed_epochs"]}))
    elif args.command == "explain":
        result = run_explainers(read_sealed(args.prepared), args.checkpoint, args.output,
                                be_only=args.be_only, max_seconds=args.max_seconds, cache_policy=args.cache_policy)
        print(json.dumps({"be_status": result["be_status"], "ae_status": result["status"],
                          "be_completed_prefixes": result["be_completed_prefixes"],
                          "be_expected_prefixes": result["be_expected_prefixes"],
                          "stop_reason": result["stop_reason"],
                          "ae_expected": result["expected"], "ae_completed": result["completed"],
                          "coverage": result["coverage"]}))
    elif args.command == "evaluate":
        result = run_evaluation(read_sealed(args.prepared), args.checkpoint, args.output,
                                be_only=args.be_only, baseline_be=args.baseline_be)
        print(json.dumps({"status": result["status"], "selected_seed": result["selected"]["seed"],
                          "paired_status": result["paired_status"]}))
    elif args.command == "experiment":
        if args.max_variants is not None and not (args.streaming and args.study == "E1"):
            parser.error("--max-variants applies to streaming E1")
        if args.streaming and args.study == "E1":
            from .experiments.e1_streaming import run_streaming_e1
            if args.profile is not None:
                parser.error("E1 uses the locked primary profile")
            result = run_streaming_e1(read_sealed(args.prepared), args.checkpoint, args.output,
                                      args.max_seconds, stop_after_variants=args.max_variants)
        elif args.streaming:
            from .experiments.streaming import run_streaming_study
            result = run_streaming_study(args.study, read_sealed(args.prepared), args.checkpoint,
                                        args.output, args.profile, args.max_seconds)
        else:
            result = run_study(args.study, read_sealed(args.prepared), args.checkpoint, args.output, args.profile)
        print(json.dumps({"study": args.study, "status": result["status"]}))
    elif args.command == "predict":
        if args.output.exists():
            raise FileExistsError("Prediction output already exists")
        prepared = read_sealed(args.prepared)
        predictor = Predictor(args.checkpoint, prepared)
        records = []
        for prefix in prepared["prefixes"]["test"]:
            prediction = predictor.predict(prefix["activities"])
            label = predictor.class_order[int(prediction.probabilities.argmax())]
            records.append({"prefix_id": prefix["prefix_id"], "case_id": prefix["case_id"],
                            "target": prefix["target"], "predicted": label,
                            "probabilities": prediction.probabilities.tolist()})
        metrics = predictive_metrics([row["target"] for row in records],
                                     [row["predicted"] for row in records])
        write_json(args.output, seal({"checkpoint_sha256": predictor.checkpoint_id,
                                     "identity": predictor.identity, "scope": prepared.get("scope"),
                                     "class_order": predictor.class_order, "records": records,
                                     "expected": len(prepared["prefixes"]["test"]),
                                     "completed": len(records), "metrics": metrics}))
        print(json.dumps({"accuracy": metrics["accuracy"], "n_total": metrics["n_total"]}))


if __name__ == "__main__":
    main()
