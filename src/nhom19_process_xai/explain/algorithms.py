"""Independent BE and AE following D06–D08 of the locked contracts."""

import random

import numpy as np

from ..data.pipeline import fingerprint
from ..evaluate.metrics import cosine_similarity
from ..experiments.studies import activity_attention, normalize_importance
from ..graphs.relations import merge_prune


def be_masks(length: int, prefix_id: str) -> list[int]:
    if length < 1:
        raise ValueError("BE requires a nonempty prefix")
    population = (1 << length) - 1
    count = min(20, population)
    if count == population:
        return list(range(1, population + 1))
    rng = random.Random(int(fingerprint([505, prefix_id]), 16))
    sampled = set()
    while len(sampled) < count:
        mask = rng.getrandbits(length)
        if mask:
            sampled.add(mask)
    return sorted(sampled)


def relevant_activities(predictor, prefix: dict) -> dict:
    labels = prefix["activities"]
    universe = sorted(set(labels))
    original = predictor.predict(labels)
    scores = []
    records = []
    masks = be_masks(len(labels), prefix["prefix_id"])
    for mask in masks:
        modified = [None if mask & (1 << index) else label for index, label in enumerate(labels)]
        prediction = predictor.predict(modified)
        similarity = cosine_similarity(original.probabilities, prediction.probabilities)
        eligible = similarity is not None and similarity >= .8
        mass, _ = activity_attention(prediction, modified, universe)
        if eligible:
            scores.append(mass)
        records.append({"mask": str(mask), "similarity": similarity,
                        "eligible": eligible, "attention_mass": mass.tolist()})
    mean = np.mean(scores, axis=0) if scores else np.zeros(len(universe))
    importance = normalize_importance(mean)
    relevant = [] if importance is None else [label for label, score in zip(universe, importance) if score > .1]
    predictions = [label for label, score in zip(original.class_order, original.probabilities) if score > .1]
    return {"prefix_id": prefix["prefix_id"], "universe": universe,
            "raw_importance": mean.tolist(),
            "importance": None if importance is None else importance.tolist(),
            "relevant": relevant, "predictions": predictions,
            "reason": "no_positive_attention" if importance is None else None,
            "population_masks": str((1 << len(labels)) - 1), "selected_masks": len(masks),
            "records": records}


def backward(predictor, prefixes: list[dict]) -> dict:
    edges = set()
    contributions = []
    for prefix in sorted(prefixes, key=lambda item: item["prefix_id"]):
        relevance = relevant_activities(predictor, prefix)
        local = {(source, target) for source in relevance["relevant"] for target in relevance["predictions"]}
        before = edges | local
        edges, removed = merge_prune(edges, local)
        contributions.append({**relevance, "local_edges": sorted(local),
                              "merged_edges": sorted(before), "removed": removed,
                              "remaining_edges": sorted(edges)})
    return {"method": "BE", "edges": sorted(edges), "prefix_records": contributions,
            "expected_prefixes": len(prefixes), "completed_prefixes": len(contributions)}


def ae_contribution(probability: float, changed_probability: float, masked_mass: float,
                    visible_mass: float, changed_visible_mass: float) -> dict[str, float]:
    close = abs(changed_probability - probability) <= .05
    masked = probability * masked_mass * (-1 if close else 1)
    visible = (probability * changed_visible_mass if close else
               abs(visible_mass - changed_visible_mass) * abs(changed_probability - probability))
    return {"masked": masked, "visible": visible}


def ae_contexts(predictor, prefix: dict, relevance: dict, is_completed=None):
    """Yield each logical context, retaining repeated occurrence identities.

    Contexts with identical model inputs remain independent votes. The caller
    can persist these records and reuse forward computations via a keyed cache.
    """
    labels = prefix["activities"]
    original = predictor.predict(labels)
    universe = sorted(set(labels))
    relevant_positions = [index for index, label in enumerate(labels) if label in relevance["relevant"]]
    original_mass = original.attention.sum(axis=(0, 1))
    original_mass = original_mass / original_mass.sum() if original_mass.sum() > 0 else original_mass
    target_indices = [index for index, label in enumerate(original.class_order) if label in relevance["predictions"]]
    for scenario in ("most", "few"):
        for subset in range(1 << len(relevant_positions)):
            if is_completed is not None and is_completed(prefix["prefix_id"], scenario, str(subset)):
                continue
            chosen = {position for bit, position in enumerate(relevant_positions) if subset & (1 << bit)}
            masked = {index for index in range(len(labels)) if (index not in chosen if scenario == "most" else index in chosen)}
            variant = [None if index in masked else label for index, label in enumerate(labels)]
            prediction = predictor.predict(variant)
            new_mass = prediction.attention.sum(axis=(0, 1))
            new_mass = new_mass / new_mass.sum() if new_mass.sum() > 0 else new_mass
            votes = []
            for target_index in target_indices:
                for label in universe:
                    positions = [index for index, activity in enumerate(labels) if activity == label]
                    masked_positions = [index for index in positions if index in masked]
                    visible_positions = [index for index in positions if index not in masked]
                    contributions = ae_contribution(float(original.probabilities[target_index]),
                                                    float(prediction.probabilities[target_index]),
                                                    float(original_mass[masked_positions].sum()),
                                                    float(original_mass[visible_positions].sum()),
                                                    float(new_mass[visible_positions].sum()))
                    for side, indices in [("masked", masked_positions), ("visible", visible_positions)]:
                        if indices:
                            votes.append({"target": original.class_order[target_index], "source": label,
                                          "side": side, "positions": indices,
                                          "occurrence_ids": [prefix["occurrence_ids"][i] for i in indices],
                                          "score": contributions[side]})
            yield {"prefix_id": prefix["prefix_id"], "scenario": scenario, "subset": str(subset),
                   "k": len(relevant_positions), "masked_positions": sorted(masked),
                   "probabilities": prediction.probabilities.tolist(), "votes": votes}


def ae_matrices(contexts, targets: list[str], sources: list[str]) -> dict:
    """Aggregate signed evidence across all prefixes before per-scenario OR."""
    matrices = {scenario: np.zeros((len(targets), len(sources)), dtype=np.float64)
                for scenario in ("most", "few")}
    positive = {scenario: np.zeros_like(matrix) for scenario, matrix in matrices.items()}
    negative = {scenario: np.zeros_like(matrix) for scenario, matrix in matrices.items()}
    row_index = {target: index for index, target in enumerate(targets)}
    col_index = {source: index for index, source in enumerate(sources)}
    context_count = 0
    vote_count = 0
    for context in contexts:
        scenario = context["scenario"]
        for vote in context["votes"]:
            coordinate = (row_index[vote["target"]], col_index[vote["source"]])
            score = vote["score"]
            if not np.isfinite(score):
                raise ArithmeticError("Non-finite AE vote")
            matrices[scenario][coordinate] += score
            (positive if score >= 0 else negative)[scenario][coordinate] += score
            vote_count += 1
        context_count += 1
    edges = set()
    records = {}
    for scenario, matrix in matrices.items():
        normalized = np.zeros_like(matrix)
        totals = matrix.sum(1)
        reasons = []
        for row, total in enumerate(totals):
            if total > 1e-12:
                normalized[row] = matrix[row] / total
                reasons.append(None)
            elif np.any(positive[scenario][row]) and np.any(negative[scenario][row]):
                reasons.append("cancellation" if total >= 0 else "nonpositive")
            else:
                reasons.append("zero" if total == 0 else "nonpositive")
        boolean = normalized > .1
        for row, column in zip(*np.where(boolean)):
            edges.add((sources[column], targets[row]))
        records[scenario] = {"raw": matrix.tolist(), "positive": positive[scenario].tolist(),
                             "negative": negative[scenario].tolist(), "row_totals": totals.tolist(),
                             "normalized": normalized.tolist(), "adjacency": boolean.tolist(),
                             "suppressed_row_reasons": reasons}
    return {"method": "AE", "targets": targets, "sources": sources, "edges": sorted(edges),
            "matrices": records, "completed_contexts": context_count, "retained_votes": vote_count}
