"""Numerical records for E1 feature correlation, E2 parameters, E3 scores."""

from dataclasses import asdict
from pathlib import Path

import numpy as np

from ..artifacts import seal, write_json
from ..evaluate.metrics import cosine_similarity, jsd, summary, tau_b, tvd
from ..model.predictor import Predictor, Prediction
from ..model.training import TrainingConfig, train
from .perturbations import training_dfg, variants


def normalize_importance(values: np.ndarray) -> np.ndarray | None:
    total = float(values.sum())
    return values / total if total > 0 else None


def activity_attention(prediction: Prediction, activities, universe) -> tuple[np.ndarray, float]:
    mass = prediction.attention.sum(axis=(0, 1))
    totals = dict.fromkeys(universe, 0.)
    outside = 0.
    for label, contribution in zip(activities, mass):
        if label is None:
            continue
        if label in totals:
            totals[label] += float(contribution)
        else:
            outside += float(contribution)
    return np.array([totals[label] for label in universe]), outside


def e1_records(predictor: Predictor, prefix: dict, selections):
    baseline = predictor.predict(prefix["activities"])
    universe = sorted(set(prefix["activities"]))
    for variant in selections:
        prediction = predictor.predict(variant.activities)
        similarity = cosine_similarity(baseline.probabilities, prediction.probabilities)
        if similarity is None:
            raise ArithmeticError("Normalized prediction vectors have undefined cosine")
        scores, outside = activity_attention(prediction, variant.activities, universe)
        yield {**asdict(variant), "cosine_similarity": similarity,
                        "cosine_distance": 1 - similarity,
                        "probabilities": prediction.probabilities.tolist(),
                        "attention_mass": scores.tolist(), "outside_universe_mass": outside,
                        "eligible_near": similarity >= .8}


def e1_prefix(predictor: Predictor, prefix: dict, graph, starts) -> dict:
    universe = sorted(set(prefix["activities"]))
    state = e1_state(universe)
    records = list(e1_records(predictor, prefix, variants(prefix["activities"], prefix["prefix_id"], graph, starts)))
    for row in records:
        e1_accumulate(state, row)
    return {**e1_summary(prefix["prefix_id"], state), "variants": records}


def e1_state(universe):
    return {"universe": universe, "impact_sum": dict.fromkeys(universe, 0.0),
            "impact_count": dict.fromkeys(universe, 0), "mass_sum": [0.0] * len(universe),
            "near_count": 0, "completed_variants": 0}


def e1_accumulate(state, row):
    label = row["original_activity"]
    state["impact_sum"][label] += row["cosine_distance"]
    state["impact_count"][label] += 1
    state["completed_variants"] += 1
    if row["eligible_near"]:
        state["mass_sum"] = [a + b for a, b in zip(state["mass_sum"], row["attention_mass"], strict=True)]
        state["near_count"] += 1


def e1_summary(prefix_id, state):
    universe = state["universe"]
    common_raw = np.array([state["impact_sum"][label] / state["impact_count"][label] for label in universe])
    common = normalize_importance(common_raw)
    attention_raw = np.asarray(state["mass_sum"]) / max(1, state["near_count"])
    attention_normalized = normalize_importance(attention_raw)
    score = tau_b(common, attention_normalized) if common is not None and attention_normalized is not None else None
    return {"prefix_id": prefix_id, "universe": universe,
            "common_raw": common_raw.tolist(), "attention_raw": attention_raw.tolist(),
            "common": None if common is None else common.tolist(),
            "attention": None if attention_normalized is None else attention_normalized.tolist(),
            "tau_b": score, "null_reason": "undefined_importance_or_rank" if score is None else None,
            "expected_variants": state["completed_variants"], "completed_variants": state["completed_variants"],
            "near_count": state["near_count"]}


def e2_pair(baseline: Prediction, modified: Prediction) -> dict:
    if baseline.class_order != modified.class_order or not np.array_equal(baseline.valid, modified.valid):
        raise ValueError("E2 pair requires the same class order and valid support")
    if baseline.attention.shape != modified.attention.shape:
        raise ValueError("E2 attention shapes differ")
    valid = baseline.valid
    if not np.any(valid):
        raise ValueError("E2 requires a nonempty valid prefix")
    left = baseline.attention[:, valid, :][:, :, valid]
    right = modified.attention[:, valid, :][:, :, valid]
    flat_left, flat_right = left.ravel() / left.sum(), right.ravel() / right.sum()
    rows = []
    positions = np.flatnonzero(valid)
    for head in range(left.shape[0]):
        for index, position in enumerate(positions):
            rows.append({"head": head, "query_position": int(position),
                         "jsd": jsd(left[head, index], right[head, index]),
                         "left_mass": float(left[head, index].sum()),
                         "right_mass": float(right[head, index].sum())})
    raw_max, normalized_max = float(right.max()), float(flat_right.max())
    output_tvd = tvd(baseline.probabilities, modified.probabilities)
    return {"jsd": jsd(flat_left, flat_right), "prediction_tvd": output_tvd,
            "max_raw": raw_max, "max_l1": normalized_max,
            "raw_bin": attention_bin(raw_max), "l1_bin": attention_bin(normalized_max),
            "author_tvd_filter": output_tvd <= .1,
            "row_records": rows, "valid_rows": len(rows),
            "baseline_checkpoint": baseline.checkpoint_id, "modified_checkpoint": modified.checkpoint_id}


def attention_bin(value: float) -> int:
    if not np.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Maximum attention must be in [0,1]")
    return min(3, int(value * 4))


def attention_displacement(original: np.ndarray, modified: np.ndarray, position: int) -> dict:
    if original.shape != modified.shape or original.ndim != 3:
        raise ValueError("Attention tensors must align as [H,T,T]")
    before, after = original.sum(-1), modified.sum(-1)
    eligible = (before > 0) & (after > 0)
    row_tvd = [tvd(original[h, q] / before[h, q], modified[h, q] / after[h, q])
               for h, q in zip(*np.where(eligible))]
    query_mass = original[:, position, :].sum(-1)
    column_mass = original[:, :, position].sum(-1) - original[:, position, position]
    return {"half_l1": float(np.abs(original - modified).sum() / 2),
            "original_row_mass": before.tolist(), "modified_row_mass": after.tolist(),
            "query_removed_mass": query_mass.tolist(), "key_only_removed_mass": column_mass.tolist(),
            "support_removed_mass": float((query_mass + column_mass).sum()),
            "net_mass_removed": float(original.sum() - modified.sum()),
            "remaining_per_head": after.sum(-1).tolist(),
            "row_renormalized_tvd": row_tvd, "excluded_zero_rows": int((~eligible).sum())}


def e3_prefix(predictor: Predictor, prefix: dict, mode: str) -> dict:
    original = predictor.predict(prefix["activities"])
    records = []
    for position in range(len(prefix["activities"])):
        masked = list(prefix["activities"])
        masked[position] = None
        input_arm = predictor.predict(masked)
        score_arm = predictor.predict(prefix["activities"], (position,), mode)
        records.append({"position": position, "occurrence_id": prefix["occurrence_ids"][position],
                        "prediction_tvd_input_vs_score": tvd(input_arm.probabilities, score_arm.probabilities),
                        "prediction_tvd_input_vs_base": tvd(input_arm.probabilities, original.probabilities),
                        "prediction_tvd_score_vs_base": tvd(score_arm.probabilities, original.probabilities),
                        "input_probabilities": input_arm.probabilities.tolist(),
                        "score_probabilities": score_arm.probabilities.tolist(),
                        **attention_displacement(original.attention, score_arm.effective_attention, position)})
    return {"prefix_id": prefix["prefix_id"], "checkpoint": original.checkpoint_id,
            "class_order": original.class_order, "valid": original.valid.tolist(), "profile": mode,
            "base_probabilities": original.probabilities.tolist(), "records": records,
            "prediction_tvd": summary([row["prediction_tvd_input_vs_score"] for row in records]),
            "attention_half_l1": summary([row["half_l1"] for row in records])}


def run_study(name: str, prepared: dict, checkpoint: Path, output: Path,
              profile: str | None = None) -> dict:
    if output.exists():
        raise FileExistsError("Study output already exists")
    predictor = Predictor(checkpoint, prepared)
    prefixes = prepared["prefixes"]["test"]
    result = {"study": name, "identity": predictor.identity,
              "scope": prepared.get("scope"), "baseline_checkpoint": predictor.checkpoint_id,
              "expected_prefixes": len(prefixes)}
    if name == "E1":
        if profile is not None:
            raise ValueError("E1 currently supports the locked primary profile")
        graph, starts = training_dfg(prepared)
        rows = [e1_prefix(predictor, prefix, graph, starts) for prefix in prefixes]
        result.update(records=rows, tau_b=summary([row["tau_b"] for row in rows]))
    elif name == "E3":
        profile = profile or "E3-PAPER"
        if profile not in {"E3-PAPER", "E3-AUTHOR"}:
            raise ValueError("Unsupported E3 profile")
        rows = [e3_prefix(predictor, prefix, profile) for prefix in prefixes]
        result.update(profile=profile, records=rows,
                      prediction_tvd=summary([row["prediction_tvd"]["mean"] for row in rows]))
    elif name == "E2":
        profile = profile or "E2-FC"
        if profile not in {"E2-FC", "E2-AC", "E2-UNI"}:
            raise ValueError("Unsupported E2 profile")
        pairs = []
        for arm, seeds in [("BASE", range(2001, 2006)), (profile, range(2006, 2011))]:
            for seed in seeds:
                directory = output.parent / (output.stem + "-models") / f"{arm}-{seed}"
                config = TrainingConfig(**{**predictor.identity["training"], "seed": seed, "profile": arm})
                train(prepared, directory, config, resume=(directory / "checkpoint.pt").exists())
                modified = Predictor(directory / "checkpoint.pt", prepared)
                rows = [{"prefix_id": prefix["prefix_id"],
                         **e2_pair(predictor.predict(prefix["activities"]), modified.predict(prefix["activities"]))}
                        for prefix in prefixes]
                pairs.append({"arm": arm, "seed": seed, "records": rows,
                              "jsd": summary([row["jsd"] for row in rows]),
                              "tvd": summary([row["prediction_tvd"] for row in rows])})
        result.update(profile=profile, pairs=pairs, expected_pairs=10, completed_pairs=len(pairs))
    else:
        raise ValueError("Study must be E1, E2 or E3")
    result.update(status="completed", completed_prefixes=len(prefixes))
    write_json(output, seal(result))
    return result
