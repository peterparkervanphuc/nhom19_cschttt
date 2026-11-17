"""Six XAI properties on fixed model graphs and explicitly paired cohorts."""

from collections import Counter
from pathlib import Path
import random

import numpy as np
import torch

from ..artifacts import read_sealed, seal, write_json
from ..data.pipeline import fingerprint
from ..experiments.perturbations import training_dfg
from ..experiments.studies import e1_prefix, normalize_importance
from ..explain.runner import run_explainers
from ..graphs.relations import project
from ..model.predictor import Predictor
from ..model.training import TrainingConfig, train
from .metrics import agreement, compactness, completeness, cosine_similarity, jaccard, summary, tau_b


METRICS = ("correctness", "completeness_precision", "completeness_recall", "completeness_f1",
           "consistency", "continuity", "contrastivity", "compactness_rules", "compactness_rhs")


def weight_distance(baseline, candidate) -> float:
    left, right = dict(baseline.named_parameters()), dict(candidate.named_parameters())
    if set(left) != set(right):
        raise ValueError("Co03 parameter names differ")
    total, count = 0., 0
    for name in sorted(left):
        if left[name].shape != right[name].shape or left[name].dtype != right[name].dtype:
            raise ValueError("Co03 parameter shapes or dtypes differ")
        if left[name].requires_grad != right[name].requires_grad:
            raise ValueError("Co03 training scopes differ")
        if left[name].requires_grad:
            total += float((left[name].detach().double() - right[name].detach().double()).abs().sum())
            count += left[name].numel()
    if count == 0:
        raise ValueError("Co03 has no trainable parameters")
    return total / count


def sample_prefixes(prefixes: list[dict]) -> list[dict]:
    ordered = sorted(prefixes, key=lambda row: row["prefix_id"])
    if not ordered:
        return []
    selected = random.Random(404).sample(ordered, max(1, int(.8 * len(ordered))))
    return sorted(selected, key=lambda row: row["prefix_id"])


def evaluate_prefix(prefix, base_prediction, base_features, base_edges,
                    other_prediction, other_features, other_edges):
    projected = project(base_edges, prefix["activities"])
    changed_graph = project(other_edges, prefix["activities"])
    targets = {label for label, probability in zip(base_prediction.class_order, base_prediction.probabilities)
               if probability > .1}
    explained = {target for _, target in projected}
    complete = completeness(targets, explained)
    compact = compactness(projected)
    effects = {label: [] for label in base_features["universe"]}
    continuity, contrastivity, variant_records = [], [], []
    for variant in base_features["variants"]:
        altered_edges = project(base_edges, [label for label in variant["activities"] if label is not None])
        similarity = variant["cosine_similarity"]
        overlap = jaccard(projected, altered_edges)
        effects[variant["original_activity"]].append(1 - overlap)
        score = agreement(similarity, overlap)
        (continuity if similarity >= .8 else contrastivity).append(score)
        variant_records.append({"variant_id": variant["variant_id"], "similarity": similarity,
                                "jaccard": overlap, "score": score,
                                "cohort": "near" if similarity >= .8 else "far",
                                "both_empty": not projected and not altered_edges})
    explanation_raw = np.array([np.mean(effects[label]) for label in base_features["universe"]])
    importance = normalize_importance(explanation_raw)
    common = base_features["common"]
    correctness = tau_b(common, importance) if common is not None and importance is not None else None
    similarity = cosine_similarity(base_prediction.probabilities, other_prediction.probabilities)
    other_common = other_features["common"]
    if base_features["universe"] != other_features["universe"]:
        raise ValueError("Co03 feature universes differ")
    feature_similarity = cosine_similarity(common, other_common) if common is not None and other_common is not None else None
    eligible = similarity is not None and feature_similarity is not None and similarity >= .8 and feature_similarity >= .8
    overlap = jaccard(projected, changed_graph)
    values = {"correctness": correctness,
              "completeness_precision": complete["precision"], "completeness_recall": complete["recall"],
              "completeness_f1": complete["f1"],
              "consistency": agreement(similarity, overlap) if eligible else None,
              "continuity": summary(continuity)["mean"], "contrastivity": summary(contrastivity)["mean"],
              "compactness_rules": compact["rule_count"], "compactness_rhs": compact["mean_rhs"]}
    reasons = {name: None for name in METRICS}
    if correctness is None:
        reasons["correctness"] = "undefined_importance_or_rank"
    for name in ("precision", "recall", "f1"):
        if complete[name] is None:
            reasons["completeness_" + name] = "zero_denominator"
    if not eligible:
        reasons["consistency"] = "pair_ineligible_or_zero_feature_norm"
    if not continuity:
        reasons["continuity"] = "no_near_variants"
    if not contrastivity:
        reasons["contrastivity"] = "no_far_variants"
    if compact["mean_rhs"] is None:
        reasons["compactness_rhs"] = "empty_rule_graph"
    return {"prefix_id": prefix["prefix_id"], "case_id": prefix["case_id"], "values": values,
            "null_reasons": reasons, "completeness_counts": complete,
            "universe": base_features["universe"], "common_importance": common,
            "explanation_importance": None if importance is None else importance.tolist(),
            "consistency_gate": {"prediction_similarity": similarity, "feature_similarity": feature_similarity,
                                 "jaccard": overlap, "eligible": eligible,
                                 "both_empty": not projected and not changed_graph},
            "variant_records": variant_records, "projected_edges": sorted(projected)}


def paired_method_differences(methods: dict) -> dict:
    """Descriptive AE-minus-BE only, on each metric's valid paired intersection."""
    indexed = {method: {row["prefix_id"]: row for row in methods[method]["records"]}
               for method in ("BE", "AE")}
    if any(len(indexed[method]) != len(methods[method]["records"]) for method in indexed):
        raise ValueError("Duplicate prefix IDs in method comparison")
    if indexed["BE"].keys() != indexed["AE"].keys():
        raise ValueError("Method comparison requires a shared scheduled cohort")
    result = {}
    for metric in METRICS:
        pairs = []
        for prefix_id in sorted(indexed["BE"]):
            be, ae = (indexed[method][prefix_id]["values"][metric] for method in ("BE", "AE"))
            if be is not None and ae is not None:
                pairs.append({"prefix_id": prefix_id, "BE": be, "AE": ae, "AE_minus_BE": ae - be})
        result[metric] = {"interpretation": "descriptive; no significance test", "pairs": pairs,
                          "scheduled": len(indexed["BE"]), "paired_valid": len(pairs),
                          "excluded_unpaired_null": len(indexed["BE"]) - len(pairs),
                          "difference": summary([row["AE_minus_BE"] for row in pairs]),
                          "BE_on_intersection": summary([row["BE"] for row in pairs]),
                          "AE_on_intersection": summary([row["AE"] for row in pairs])}
    return result


def run_evaluation(prepared: dict, checkpoint: Path, directory: Path) -> dict:
    output = directory / "evaluation.json"
    if output.exists():
        raise FileExistsError("Evaluation output already exists")
    baseline = Predictor(checkpoint, prepared)
    if baseline.identity["model"]["profile"] != "BASE":
        raise ValueError("XAI primary evaluation requires the baseline architecture")
    candidates = []
    for seed in range(3001, 3006):
        candidate_dir = directory / "candidates" / str(seed)
        config = TrainingConfig(**{**baseline.identity["training"], "seed": seed, "profile": "BASE"})
        train(prepared, candidate_dir, config, resume=(candidate_dir / "checkpoint.pt").exists())
        candidate = Predictor(candidate_dir / "checkpoint.pt", prepared)
        candidates.append({"seed": seed, "distance": weight_distance(baseline.model, candidate.model),
                           "checkpoint_sha256": candidate.checkpoint_id})
    selected = min(candidates, key=lambda row: (-row["distance"], row["seed"]))
    selected_path = directory / "candidates" / str(selected["seed"]) / "checkpoint.pt"
    other = Predictor(selected_path, prepared)
    for model_path, folder in [(checkpoint, "baseline-graphs"), (selected_path, "candidate-graphs")]:
        status = run_explainers(prepared, model_path, directory / folder)
        if status["status"] != "completed":
            raise ValueError("Evaluation requires completed global explainer graphs")
    cohort = sample_prefixes(prepared["prefixes"]["test"])
    graph, starts = training_dfg(prepared)
    paired = []
    for prefix in cohort:
        paired.append((prefix, baseline.predict(prefix["activities"]), e1_prefix(baseline, prefix, graph, starts),
                       other.predict(prefix["activities"]), e1_prefix(other, prefix, graph, starts)))
    methods = {}
    for method in ("BE", "AE"):
        base_artifact = read_sealed(directory / "baseline-graphs" / f"{method}.json")
        other_artifact = read_sealed(directory / "candidate-graphs" / f"{method}.json")
        base_edges = {tuple(edge) for edge in base_artifact["edges"]}
        other_edges = {tuple(edge) for edge in other_artifact["edges"]}
        rows = [evaluate_prefix(prefix, p, features, base_edges, q, other_features, other_edges)
                for prefix, p, features, q, other_features in paired]
        aggregates = {}
        for metric in METRICS:
            aggregates[metric] = {**summary([row["values"][metric] for row in rows]),
                                  "null_reasons": dict(Counter(row["null_reasons"][metric] for row in rows
                                                               if row["values"][metric] is None))}
        methods[method] = {"records": rows, "summary": aggregates, "global_compactness": compactness(base_edges)}
    result = {"status": "completed", "scope": prepared.get("scope"), "identity": baseline.identity,
              "baseline_checkpoint": baseline.checkpoint_id, "candidates": candidates, "selected": selected,
              "sample_seed": 404, "sample_ids": [prefix["prefix_id"] for prefix in cohort],
              "sample_hash": fingerprint([prefix["prefix_id"] for prefix in cohort]),
              "population": len(prepared["prefixes"]["test"]), "methods": methods,
              "paired_AE_minus_BE": paired_method_differences(methods)}
    write_json(output, seal(result))
    return result
