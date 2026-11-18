"""FP64 primitives and per-sample metrics from the locked S3/S6 contracts."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

import numpy as np
from scipy.stats import kendalltau


def aligned_vectors(left, right) -> tuple[np.ndarray, np.ndarray]:
    left, right = np.asarray(left, dtype=np.float64), np.asarray(right, dtype=np.float64)
    if left.ndim != 1 or left.shape != right.shape or not left.size:
        raise ValueError("Vectors must have matching nonempty one-dimensional support")
    if not np.isfinite(left).all() or not np.isfinite(right).all():
        raise ValueError("Vectors must be finite")
    return left, right


def probabilities(left, right) -> tuple[np.ndarray, np.ndarray]:
    left, right = aligned_vectors(left, right)
    for vector in (left, right):
        if np.any(vector < 0) or abs(float(vector.sum()) - 1) > 1e-6:
            raise ValueError("Probability vector must be nonnegative with unit sum")
    return left, right


def cosine_similarity(left, right) -> float | None:
    left, right = aligned_vectors(left, right)
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator == 0:
        return None
    score = float(left @ right / denominator)
    if abs(score) > 1 + 1e-12:
        raise ArithmeticError("Cosine exceeds its numerical bound")
    return min(1., max(-1., score))


def tvd(left, right) -> float:
    left, right = probabilities(left, right)
    return float(np.abs(left - right).sum() / 2)


def jsd(left, right) -> float:
    left, right = probabilities(left, right)
    midpoint = (left + right) / 2
    result = 0.
    for vector in (left, right):
        positive = vector > 0
        result += float(np.sum(vector[positive] * np.log(vector[positive] / midpoint[positive]))) / 2
    if result < -1e-12 or result > np.log(2) + 1e-6:
        raise ArithmeticError("JSD exceeds its numerical bound")
    return max(0., result)


def tau_b(left, right) -> float | None:
    left, right = aligned_vectors(left, right)
    if len(left) < 2:
        return None
    statistic = float(kendalltau(left, right, variant="b").statistic)
    return statistic if np.isfinite(statistic) else None


def jaccard(left: set[tuple[str, str]], right: set[tuple[str, str]]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.


def completeness(targets: set[str], explained: set[str]) -> dict[str, float | int | None]:
    tp, fp, fn = len(targets & explained), len(explained - targets), len(targets - explained)
    return {"tp": tp, "fp": fp, "fn": fn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
            "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None}


def compactness(edges: set[tuple[str, str]]) -> dict[str, float | int | None]:
    antecedents = {source for source, _ in edges}
    return {"rule_count": len(antecedents),
            "mean_rhs": len(edges) / len(antecedents) if antecedents else None}


def agreement(similarity: float, rule_jaccard: float) -> float:
    if not 0 <= similarity <= 1 or not 0 <= rule_jaccard <= 1:
        raise ValueError("Agreement inputs must be in [0,1]")
    return 1 - abs(similarity - rule_jaccard)


def summary(values: Iterable[float | None]) -> dict[str, float | int | None]:
    values = list(values)
    valid = [value for value in values if value is not None and not np.isnan(value)]
    if not all(np.isfinite(value) for value in valid):
        raise ValueError("Infinite metric values cannot be aggregated")
    return {"mean": float(np.mean(valid)) if valid else None,
            "sd": float(np.std(valid, ddof=1)) if len(valid) > 1 else None,
            "n_valid": len(valid), "n_total": len(values),
            "coverage": len(valid) / len(values) if values else None}


def predictive_metrics(truth: list[str], predicted: list[str]) -> dict:
    if len(truth) != len(predicted):
        raise ValueError("Every true label must have exactly one prediction")
    if not truth:
        return {"accuracy": None, "precision": None, "recall": None, "f1": None,
                "n_total": 0, "classes": {}}
    support = Counter(truth)
    per_class = {}
    for label in sorted(set(truth) | set(predicted)):
        tp = sum(t == label and p == label for t, p in zip(truth, predicted))
        fp = sum(t != label and p == label for t, p in zip(truth, predicted))
        fn = sum(t == label and p != label for t, p in zip(truth, predicted))
        per_class[label] = {"support": support[label],
                            "precision": tp / (tp + fp) if tp + fp else 0.,
                            "recall": tp / (tp + fn) if tp + fn else 0.,
                            "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.,
                            "zero_precision_denominator": tp + fp == 0,
                            "zero_recall_denominator": tp + fn == 0}
    result = {metric: sum(row[metric] * row["support"] for row in per_class.values()) / len(truth)
              for metric in ("precision", "recall", "f1")}
    result.update(accuracy=sum(t == p for t, p in zip(truth, predicted)) / len(truth),
                  n_total=len(truth), classes=per_class)
    return result
