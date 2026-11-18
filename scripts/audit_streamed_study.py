"""Reopen an E1/E2/E3 result and check it against its full scheduled cohort."""

import argparse
from contextlib import closing
import hashlib
import io
import json
from math import floor, fsum, isclose
from pathlib import Path
import sqlite3
from statistics import median

import numpy as np
from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.pipeline import file_hash, fingerprint
from nhom19_process_xai.evaluate.metrics import summary
from nhom19_process_xai.experiments.e1_streaming import decode
from nhom19_process_xai.experiments.studies import e1_accumulate, e1_state, e1_summary


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit_e1(db, manifest, prefixes, workload):
    summaries = {row["prefix_id"]: row for row in manifest["records"]}
    require(len(summaries) == len(manifest["records"]) and summaries.keys() == prefixes.keys(),
            "E1 summaries differ from the prepared test cohort")
    counts = dict(db.execute("SELECT prefix_id,COUNT(*) FROM variants GROUP BY prefix_id"))
    require(counts == {key: row["completed_variants"] for key, row in summaries.items()},
            "E1 variant counts differ from the manifest")
    total = sum(counts.values())
    require(total == manifest["completed_variants"] == workload, "E1 total differs from the exact schedule")
    for prefix_id, count in counts.items():
        stored = db.execute("SELECT complete,payload FROM prefixes WHERE prefix_id=?", (prefix_id,)).fetchone()
        require(stored is not None and stored[0] == 1 and decode(stored[1]) == summaries[prefix_id],
                f"E1 stored prefix summary differs: {prefix_id}")
        require(count == summaries[prefix_id]["expected_variants"], "E1 prefix expected count differs")
    current, next_ordinal, state = None, 0, None
    for prefix_id, ordinal, payload in db.execute(
            "SELECT prefix_id,ordinal,payload FROM variants ORDER BY prefix_id,ordinal"):
        if current != prefix_id:
            if current is not None:
                require(e1_summary(current, state) == summaries[current], "E1 reconstructed summary differs")
            current, next_ordinal = prefix_id, 0
            state = e1_state(sorted(set(prefixes[prefix_id])))
        require(ordinal == next_ordinal, "E1 ordinal gap")
        row = decode(payload)
        position = row["position"]
        original = prefixes[prefix_id]
        require(0 <= position < len(original) and original[position] == row["original_activity"],
                "E1 affected occurrence differs from the prepared prefix")
        if row["operation"] == "mask":
            expected = original[:position] + [None] + original[position + 1:]
        else:
            require(row["operation"] == "replace", "Unknown E1 variant operation")
            expected = original[:position] + row["replacement"] + original[position + 1:]
        require(row["activities"] == expected, "E1 variant does not match the recorded operation")
        e1_accumulate(state, row)
        next_ordinal += 1
    if current is not None:
        require(e1_summary(current, state) == summaries[current], "E1 reconstructed summary differs")
    require(manifest["tau_b"] == summary([row["tau_b"] for row in manifest["records"]]),
            "E1 aggregate differs from the prefix summaries")
    return total


def audit_masked_positions(row, occurrence_ids):
    records = row["records"]
    require([(record["position"], record["occurrence_id"]) for record in records] == list(enumerate(occurrence_ids)),
            "E3 masking does not cover each prepared occurrence exactly once")
    values = []
    for record in records:
        stored = record["prediction_tvd_input_vs_score"]
        paired = zip(record["input_probabilities"], record["score_probabilities"], strict=True)
        recomputed = fsum(abs(left - right) for left, right in paired) / 2
        require(0 <= stored <= 1 and isclose(stored, recomputed, rel_tol=0, abs_tol=1e-12),
                "E3 occurrence TVD differs from the recorded prediction vectors")
        values.append(stored)
    require(row["prediction_tvd"] == summary(values), "E3 prefix TVD summary differs from its occurrences")
    return values


def audit_e2_e3(db, ledger, manifest, prefixes, checkpoint):
    study, profile = manifest["study"], manifest["profile"]
    schedule = (([("BASE", seed) for seed in range(2001, 2006)]
                + [(profile, seed) for seed in range(2006, 2011)]) if study == "E2" else [(profile, None)])
    require([(row["arm"], row["seed"]) for row in manifest["pairs"]] == schedule,
            "Arms or seeds differ from the fixed schedule")
    count = 0
    bins = {}
    position_tvd = []
    for arm in manifest["pairs"]:
        if study == "E2":
            trained = ledger.parent / "models" / f'{arm["arm"]}-{arm["seed"]}' / "checkpoint.pt"
            require(file_hash(trained) == arm["checkpoint_sha256"], "E2 trained checkpoint checksum mismatch")
            arm_bins = bins.setdefault(arm["arm"], {
                "raw_all": [0] * 4, "l1_all": [0] * 4, "raw_tvd_at_most_point_one": [0] * 4,
            })
        ids, primary, secondary = set(), [], []
        for prefix_id, raw in db.execute(
                "SELECT prefix_id,payload FROM records WHERE arm=? AND seed=? ORDER BY prefix_id",
                (arm["arm"], str(arm["seed"]))):
            row = decode(raw)
            require(row["prefix_id"] == prefix_id and prefix_id in prefixes, "Study prefix mismatch")
            ids.add(prefix_id)
            if study == "E2":
                require(row["baseline_checkpoint"] == checkpoint and
                        row["modified_checkpoint"] == arm["checkpoint_sha256"], "E2 checkpoint mismatch")
                raw_max, l1_max = row["max_raw"], row["max_l1"]
                require(0 <= raw_max <= 1 and 0 <= l1_max <= 1, "E2 attention maximum outside [0,1]")
                raw_bin, l1_bin = min(3, floor(4 * raw_max)), min(3, floor(4 * l1_max))
                passes_filter = row["prediction_tvd"] <= .1
                require((raw_bin, l1_bin, passes_filter) ==
                        (row["raw_bin"], row["l1_bin"], row["author_tvd_filter"]),
                        f"E2 attention bin or TVD filter mismatch: {prefix_id}")
                arm_bins["raw_all"][raw_bin] += 1
                arm_bins["l1_all"][l1_bin] += 1
                if passes_filter:
                    arm_bins["raw_tvd_at_most_point_one"][raw_bin] += 1
                primary.append(row["jsd"])
                secondary.append(row["prediction_tvd"])
            else:
                require(row["checkpoint"] == checkpoint and row["profile"] == profile,
                        "E3 checkpoint or profile mismatch")
                position_tvd.extend(audit_masked_positions(row, prefixes[prefix_id]))
                primary.append(row["prediction_tvd"]["mean"])
            count += 1
        require(ids == prefixes.keys() and arm["completed_prefixes"] == len(ids), "Study cohort incomplete")
        if study == "E2":
            require(arm["jsd"] == summary(primary) and arm["tvd"] == summary(secondary),
                    "E2 summary does not match sealed values")
        else:
            require(arm["prediction_tvd"] == summary(primary), "E3 summary does not match sealed values")
    ledger_count = db.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    require(count == ledger_count == manifest["completed_units"] == manifest["expected_units"],
            "Study unit totals disagree")
    details = {"attention_bins_by_arm": bins} if study == "E2" else {
        "occurrence_weighted_prediction_tvd": {**summary(position_tvd),
                                               "median": median(position_tvd) if position_tvd else None}}
    return count, details


def audit_attention_cache(db, cache_path, manifest, activities):
    """Link retained baseline tensors to E3-PAPER's complete masking records."""
    require(manifest["study"] == "E3" and manifest["profile"] == "E3-PAPER",
            "Baseline attention audit requires E3-PAPER")
    wal = cache_path.with_suffix(".sqlite-wal")
    require(not (cache_path.parent / "writer.lock").exists()
            and (not wal.exists() or wal.stat().st_size == 0), "Baseline attention cache is still open")
    digest = file_hash(cache_path)
    count = occurrences = 0
    with closing(sqlite3.connect(cache_path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)) as cache:
        identity = json.loads(cache.execute("SELECT value FROM metadata WHERE key='identity'").fetchone()[0])
        require(identity["dataset"] == manifest["identity"]["dataset"]
                and identity["checkpoint"] == manifest["baseline_checkpoint"]
                and set(identity["prefix_ids"]) == activities.keys(), "Baseline attention cache identity differs")
        for prefix_id, raw in db.execute("SELECT prefix_id,payload FROM records ORDER BY prefix_id"):
            row = decode(raw)
            require(list(identity["class_order"]) == row["class_order"], "Baseline attention classes differ")
            key = fingerprint([identity["checkpoint"], identity["class_order"], activities[prefix_id],
                               [], "E3-PAPER", "cpu", "float32"])
            saved = cache.execute("SELECT payload,checksum FROM inference WHERE key=?", (key,)).fetchone()
            require(saved is not None and hashlib.sha256(saved[0]).hexdigest() == saved[1],
                    "Baseline attention tensor missing or checksum differs")
            with np.load(io.BytesIO(saved[0]), allow_pickle=False) as arrays:
                original, probabilities = arrays["attention"], arrays["probabilities"]
                require(np.array_equal(arrays["valid"], row["valid"])
                        and np.array_equal(probabilities, row["base_probabilities"]),
                        "Baseline attention cache prediction or mask differs")
            length = len(activities[prefix_id])
            require(original.ndim == 3 and original.shape[1:] == (length, length)
                    and np.isfinite(original).all() and (original >= 0).all(), "Invalid baseline attention tensor")
            for record in row["records"]:
                position = record["position"]
                modified = original.copy()
                modified[:, position, :] = 0
                modified[:, :, position] = 0
                before, after = original.sum(-1), modified.sum(-1)
                eligible = (before > 0) & (after > 0)
                normalized = []
                for h, q in zip(*np.where(eligible)):
                    normalized.append(float(np.abs(original[h, q] / before[h, q]
                                                   - modified[h, q] / after[h, q]).sum() / 2))
                query = original[:, position, :].sum(-1)
                column = original[:, :, position].sum(-1) - original[:, position, position]
                expected = {"original_row_mass": before, "modified_row_mass": after,
                            "query_removed_mass": query, "key_only_removed_mass": column,
                            "support_removed_mass": (query + column).sum(),
                            "net_mass_removed": original.sum() - modified.sum(),
                            "remaining_per_head": after.sum(-1),
                            "half_l1": np.abs(original - modified).sum() / 2,
                            "row_renormalized_tvd": normalized,
                            "excluded_zero_rows": int((~eligible).sum())}
                for field, value in expected.items():
                    actual, expected_value = np.asarray(record[field]), np.asarray(value)
                    require(actual.shape == expected_value.shape
                            and np.allclose(actual, expected_value, rtol=0, atol=1e-12),
                            f"E3 attention displacement differs from retained tensor: {field}")
                occurrences += 1
            count += 1
    require(count == len(activities) and file_hash(cache_path) == digest, "Baseline attention coverage or digest differs")
    return {"prefixes": count, "occurrences": occurrences, "cache_sha256": digest,
            "cache_path": str(cache_path.resolve()), "cache_source_sha256": identity["source"],
            "retention": "Full baseline tensors retained in the referenced closed cache; no inference replay"}


def audit(manifest_path, prepared_path, checkpoint_path, workload_path=None, baseline_cache=None):
    manifest = read_sealed(manifest_path)
    require(baseline_cache is None or manifest["study"] == "E3" and manifest.get("profile") == "E3-PAPER",
            "Baseline attention audit requires E3-PAPER")
    prepared = read_sealed(prepared_path)
    study = manifest["study"]
    require(study in {"E1", "E2", "E3"} and manifest["status"] == "completed",
            "An audit requires a completed E1, E2 or E3 manifest")
    identity = manifest["identity"]
    checkpoint = file_hash(checkpoint_path)
    field = "occurrence_ids" if study == "E3" else "activities"
    prefixes = {row["prefix_id"]: list(row[field]) for row in prepared["prefixes"]["test"]}
    activities = ({row["prefix_id"]: list(row["activities"]) for row in prepared["prefixes"]["test"]}
                  if baseline_cache is not None else None)
    require(identity["study"] == study and identity["dataset"] == fingerprint(prepared)
            and identity["checkpoint"] == checkpoint == manifest["baseline_checkpoint"]
            and set(identity["prefix_ids"]) == prefixes.keys()
            and len(identity["prefix_ids"]) == len(prefixes)
            and manifest["completed_prefixes"] == manifest["expected_prefixes"] == len(prefixes),
            "Prepared data, checkpoint or test membership differs from the manifest")
    del prepared
    ledger = manifest_path.parent / manifest["records_database"]
    require(file_hash(ledger) == manifest["records_sha256"], "Ledger SHA-256 mismatch")
    with closing(sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        details = {}
        if study == "E1":
            require(workload_path is not None, "E1 needs an independently generated exact schedule count")
            workload = read_sealed(workload_path)
            require(workload["prepared_sha256"] == file_hash(prepared_path), "E1 workload input differs")
            units = audit_e1(db, manifest, prefixes, workload["variant_count"])
        else:
            units, details = audit_e2_e3(db, ledger, manifest, prefixes, checkpoint)
        if baseline_cache is not None:
            details["baseline_attention_cache"] = audit_attention_cache(db, baseline_cache, manifest, activities)
    return {"status": "verified", "study": study, "prefixes": len(prefixes), "units": units,
            "manifest_sha256": file_hash(manifest_path), "records_sha256": manifest["records_sha256"],
            "auditor_sha256": file_hash(Path(__file__)), **details}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--workload", type=Path)
    parser.add_argument("--baseline-cache", type=Path, help="Closed BE inference cache retaining the same baseline attention")
    args = parser.parse_args()
    print(json.dumps(audit(args.manifest, args.prepared, args.checkpoint, args.workload, args.baseline_cache)))
