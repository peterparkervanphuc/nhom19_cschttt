"""Verify a completed XAI evaluation against its input and checkpoint receipts."""

import argparse
from collections import Counter
import json
from itertools import combinations
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


def rank_correlation(left, right):
    """Pair-count tau-b, independent of the implementation's SciPy call."""
    if left is None or right is None:
        return None
    require(len(left) == len(right) and all(math.isfinite(x) for x in [*left, *right]),
            "Invalid XAI rank vectors")
    concordant = discordant = left_ties = right_ties = 0
    for i, j in combinations(range(len(left)), 2):
        a = (left[i] > left[j]) - (left[i] < left[j])
        b = (right[i] > right[j]) - (right[i] < right[j])
        concordant += a * b > 0
        discordant += a * b < 0
        left_ties += a == 0 and b != 0
        right_ties += b == 0 and a != 0
    non_ties = concordant + discordant
    denominator = math.sqrt((non_ties + left_ties) * (non_ties + right_ties))
    return (concordant - discordant) / denominator if denominator else None


def verify_record(row):
    """Recompute metrics from stored intermediates; does not rerun inference."""
    counts = row["completeness_counts"]
    tp, fp, fn = (counts[key] for key in ("tp", "fp", "fn"))
    require(all(type(value) is int and value >= 0 for value in (tp, fp, fn)), "Invalid XAI counts")
    edges = {tuple(edge) for edge in row["projected_edges"]}
    require(len(edges) == len(row["projected_edges"]), "Duplicate XAI projected edges")
    require(tp + fp == len({target for _, target in edges}), "XAI explained target count differs")
    rules = len({source for source, _ in edges})
    expected = {"completeness_precision": tp / (tp + fp) if tp + fp else None,
                "completeness_recall": tp / (tp + fn) if tp + fn else None,
                "completeness_f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
                "compactness_rules": rules, "compactness_rhs": len(edges) / rules if rules else None}
    for name in ("precision", "recall", "f1"):
        require(close_value(counts[name], expected["completeness_" + name]),
                "XAI completeness count arithmetic differs")
    for vector in (row["common_importance"], row["explanation_importance"]):
        require(vector is None or len(vector) == len(row["universe"]), "XAI importance support differs")
    expected["correctness"] = rank_correlation(row["common_importance"], row["explanation_importance"])
    groups = {"near": [], "far": []}
    for variant in row["variant_records"]:
        similarity, overlap = variant["similarity"], variant["jaccard"]
        require(0 <= similarity <= 1 and 0 <= overlap <= 1, "Invalid XAI variant inputs")
        score = 1 - abs(similarity - overlap)
        require(close_value(variant["score"], score), "XAI variant arithmetic differs")
        cohort = "near" if similarity >= .8 else "far"
        require(variant["cohort"] == cohort, "XAI variant cohort differs")
        require(not variant["both_empty"] or (not edges and overlap == 1), "XAI empty variant differs")
        groups[cohort].append(score)
    expected["continuity"] = statistics.mean(groups["near"]) if groups["near"] else None
    expected["contrastivity"] = statistics.mean(groups["far"]) if groups["far"] else None
    gate = row["consistency_gate"]
    similarity, features, overlap = (gate[key] for key in ("prediction_similarity", "feature_similarity", "jaccard"))
    require(all(value is None or math.isfinite(value) and -1 <= value <= 1
                for value in (similarity, features)) and 0 <= overlap <= 1, "Invalid XAI consistency inputs")
    eligible = similarity is not None and features is not None and similarity >= .8 and features >= .8
    require(gate["eligible"] == eligible, "XAI consistency eligibility differs")
    require(not gate["both_empty"] or (not edges and overlap == 1), "XAI empty consistency differs")
    expected["consistency"] = 1 - abs(similarity - overlap) if eligible else None
    require(set(row["values"]) == set(METRICS), "XAI record metrics differ")
    for name, value in expected.items():
        require(close_value(row["values"][name], value), f"XAI per-prefix arithmetic differs: {name}")


def verify_method(method, cohort):
    rows, aggregates = method["records"], method["summary"]
    require([(row["prefix_id"], row["case_id"]) for row in rows] == list(cohort.items()), "XAI cohort differs")
    require(set(aggregates) == set(METRICS), "Missing or unexpected XAI metrics")
    for row in rows:
        verify_record(row)
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
    selected_ids = set(sample)
    prefix_labels = {p["prefix_id"]: set(p["activities"]) for p in prepared["prefixes"]["test"]
                     if p["prefix_id"] in selected_ids}
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
        edges = {tuple(edge) for edge in read_sealed(base)["edges"]}
        candidate_edges = {tuple(edge) for edge in read_sealed(other)["edges"]}
        sources = {source for source, _ in edges}
        compact = {"rule_count": len(sources), "mean_rhs": len(edges) / len(sources) if sources else None}
        require(all(close_value(method["global_compactness"][key], value) for key, value in compact.items()),
                f"Global XAI compactness differs: {name}")
        for row in method["records"]:
            projected = sorted(edge for edge in edges if edge[0] in prefix_labels[row["prefix_id"]])
            require([list(edge) for edge in projected] == row["projected_edges"],
                    f"XAI projection differs from the baseline graph: {name}")
            changed = {edge for edge in candidate_edges if edge[0] in prefix_labels[row["prefix_id"]]}
            projected = set(projected)
            union = projected | changed
            overlap = len(projected & changed) / len(union) if union else 1.
            require(close_value(row["consistency_gate"]["jaccard"], overlap)
                    and row["consistency_gate"]["both_empty"] == (not union),
                    f"XAI consistency graph overlap differs: {name}")
        verify_method(method, cohort)
    if paired is not None:
        verify_intersections(paired, methods, cohort)
    return {"status": "verified", "mode": mode, "prefix_population": len(prefix_cases), "scheduled": len(cohort),
            "selected": result["selected"], "evaluation_sha256": file_hash(output),
            "auditor_sha256": file_hash(Path(__file__)),
            "metric_verification": "All nine outputs recomputed from stored per-prefix intermediates; no inference replay",
            "verified_method_records": sum(len(method["records"]) for method in methods.values()),
            "metrics": {name: method["summary"] for name, method in methods.items()}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--baseline-be", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.run, args.prepared, args.checkpoint, args.baseline_be)))
