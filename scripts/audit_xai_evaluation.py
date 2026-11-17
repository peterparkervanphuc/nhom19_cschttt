"""Verify a completed XAI evaluation against its input and checkpoint receipts."""

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import random
import statistics

from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.pipeline import file_hash, fingerprint
from nhom19_process_xai.evaluate.xai import METRICS
from nhom19_process_xai.model.predictor import Predictor


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close_value(actual, expected):
    if expected is None or actual is None:
        return actual is expected
    return math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-13)


def verify_summary(actual, values):
    values = list(values)
    valid = [value for value in values if value is not None]
    expected = {"mean": statistics.mean(valid) if valid else None,
                "sd": statistics.stdev(valid) if len(valid) > 1 else None,
                "n_valid": len(valid), "n_total": len(values),
                "coverage": len(valid) / len(values) if values else None}
    require(all(key in actual and close_value(actual[key], value) for key, value in expected.items()),
            "XAI aggregate differs from recorded per-prefix values")


def verify_method(method, cohort):
    rows, aggregates = method["records"], method["summary"]
    require([(row["prefix_id"], row["case_id"]) for row in rows] == list(cohort.items()), "XAI cohort differs")
    require(set(aggregates) == set(METRICS), "Missing or unexpected XAI metrics")
    for metric, aggregate in aggregates.items():
        verify_summary(aggregate, (row["values"][metric] for row in rows))
        reasons = Counter(row["null_reasons"][metric] for row in rows if row["values"][metric] is None)
        require(None not in reasons and aggregate["null_reasons"] == reasons,
                f"XAI null-reason counts differ: {metric}")
        require(all((row["null_reasons"][metric] is None) == (row["values"][metric] is not None) for row in rows),
                f"XAI metric null reasons are inconsistent: {metric}")


def verify_intersections(paired, methods, cohort):
    require(set(paired) == set(METRICS), "Missing or unexpected paired metrics")
    for metric, comparison in paired.items():
        rows = []
        for prefix_id, be, ae in zip(cohort, methods["BE"]["records"], methods["AE"]["records"], strict=True):
            left, right = be["values"][metric], ae["values"][metric]
            if left is not None and right is not None:
                rows.append({"prefix_id": prefix_id, "BE": left, "AE": right, "AE_minus_BE": right - left})
        require(rows == comparison["pairs"] and comparison["paired_valid"] == len(rows)
                and comparison["scheduled"] == len(cohort)
                and comparison["excluded_unpaired_null"] == len(cohort) - len(rows),
                f"XAI paired intersection differs: {metric}")
        for summary, column in (("BE_on_intersection", "BE"), ("AE_on_intersection", "AE"),
                                ("difference", "AE_minus_BE")):
            verify_summary(comparison[summary], (row[column] for row in rows))


def audit(directory, prepared_path, checkpoint, baseline_be):
    prepared = read_sealed(prepared_path)
    baseline = Predictor(checkpoint, prepared)
    prefix_cases = {p["prefix_id"]: p["case_id"] for p in prepared["prefixes"]["test"]}
    sample = sorted(random.Random(404).sample(sorted(prefix_cases), max(1, int(.8 * len(prefix_cases)))))
    cohort = {key: prefix_cases[key] for key in sample}
    left = {name: p.detach().reshape(-1).tolist() for name, p in baseline.model.named_parameters() if p.requires_grad}
    candidates = []
    for seed in range(3001, 3006):
        model_path = directory / "candidates" / str(seed) / "checkpoint.pt"
        candidate = Predictor(model_path, prepared)
        require(candidate.identity["training"] == {**baseline.identity["training"], "seed": seed},
                f"Unexpected Co03 training configuration: {seed}")
        right = {name: p.detach().reshape(-1).tolist() for name, p in candidate.model.named_parameters() if p.requires_grad}
        require(left.keys() == right.keys(), f"Co03 parameter sets differ: {seed}")
        distance = math.fsum(abs(a - b) for name in left for a, b in zip(left[name], right[name], strict=True))
        candidates.append((seed, candidate.checkpoint_id, distance / sum(map(len, left.values()))))
    del prepared

    output = directory / "evaluation.json"
    result = read_sealed(output)
    require(result["status"] == "completed" and result["identity"] == baseline.identity
            and result["baseline_checkpoint"] == baseline.checkpoint_id and result["sample_seed"] == 404
            and result["sample_ids"] == sample and result["sample_hash"] == fingerprint(sample)
            and result["population"] == len(prefix_cases), "Evaluation identity or sample differs")
    for measured, (seed, digest, distance) in zip(result["candidates"], candidates, strict=True):
        require(measured["seed"] == seed and measured["checkpoint_sha256"] == digest
                and close_value(measured["distance"], distance), f"Co03 candidate identity or distance differs: {seed}")
    ordered = sorted(result["candidates"], key=lambda row: (-row["distance"], row["seed"]))
    require(result["selected"] == ordered[0], "Co03 selected checkpoint differs")

    mode, methods = result["evaluation_mode"], result["methods"]
    paired = result["paired_AE_minus_BE"]
    require((mode, result["paired_status"], set(methods), paired is None) in
            [("be-only", "not_evaluated", {"BE"}, True), ("paired", "completed", {"BE", "AE"}, False)],
            "Evaluation mode, method set or paired reporting differs")
    require(set(result["graph_receipts"]) == set(methods) and (baseline_be is None or mode == "be-only"),
            "Evaluation graph receipts do not match the methods")
    for name, method in methods.items():
        base = baseline_be or (directory / "baseline-graphs" / f"{name}.json")
        other = directory / "candidate-graphs" / f"{name}.json"
        receipt = result["graph_receipts"][name]
        require(receipt == {"baseline_graph_sha256": file_hash(base), "candidate_graph_sha256": file_hash(other)},
                f"Evaluation graph digest differs: {name}")
        verify_method(method, cohort)
    if paired is not None:
        verify_intersections(paired, methods, cohort)
    return {"status": "verified", "mode": mode, "prefix_population": len(prefix_cases), "scheduled": len(cohort),
            "selected": result["selected"], "evaluation_sha256": file_hash(output),
            "metrics": {name: method["summary"] for name, method in methods.items()}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--baseline-be", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.run, args.prepared, args.checkpoint, args.baseline_be)))
