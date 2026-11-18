"""Verify a completed BE graph, its AE schedule, and any completed AE output."""

import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.pipeline import file_hash, fingerprint
from nhom19_process_xai.explain.algorithms import ae_matrices
from nhom19_process_xai.graphs.relations import merge_prune


def require(condition, message):
    if not condition:
        raise ValueError(message)


def context_rows(db, prefixes, relevant_positions, targets_by_prefix):
    for prefix_id, prefix in prefixes.items():
        positions = relevant_positions[prefix_id]
        prefix_positions = set(range(len(prefix["activities"])))
        targets = targets_by_prefix[prefix_id]
        limit = 1 << len(positions)
        for scenario in ("most", "few"):
            rows = db.execute(
                "SELECT subset, payload FROM contexts WHERE prefix_id=? AND scenario=? "
                "ORDER BY length(subset), subset",
                (prefix_id, scenario),
            )
            count = 0
            for subset, raw in rows:
                envelope = json.loads(raw)
                context = envelope["payload"]
                require(fingerprint(context) == envelope["sha256"], "AE row checksum mismatch")
                require(subset == str(count) and count < limit
                        and (context["prefix_id"], context["scenario"], context["subset"], context["k"])
                        == (prefix_id, scenario, subset, len(positions)), "AE context key mismatch")
                chosen = {position for bit, position in enumerate(positions) if count & (1 << bit)}
                if scenario == "most":
                    chosen = prefix_positions - chosen
                require(context["masked_positions"] == sorted(chosen), "AE intervention differs from subset")
                seen = {target: set() for target in targets}
                vote_groups = set()
                for vote in context["votes"]:
                    indices = vote["positions"]
                    target, side = vote["target"], vote["side"]
                    index_set = set(indices)
                    group = (target, vote["source"], side)
                    require(target in targets and group not in vote_groups and indices
                            and len(index_set) == len(indices) and index_set <= prefix_positions
                            and seen[target].isdisjoint(index_set)
                            and all(prefix["activities"][index] == vote["source"] for index in indices)
                            and vote["occurrence_ids"] == [prefix["occurrence_ids"][index] for index in indices]
                            and side in {"masked", "visible"}
                            and all((index in chosen) == (side == "masked") for index in indices),
                            "AE vote occurrence does not match the recorded intervention")
                    seen[target].update(index_set)
                    vote_groups.add(group)
                require(all(indices == prefix_positions for indices in seen.values()),
                        "AE votes do not cover all occurrences for every selected target")
                yield context
                count += 1
            require(count == limit, "AE subset schedule incomplete")


def audit(directory, prepared_path, checkpoint_path, *, be_only=False):
    ledger = directory / "ledger.sqlite"
    wal = ledger.with_suffix(".sqlite-wal")
    require(not (directory / "writer.lock").exists() and (not wal.exists() or wal.stat().st_size == 0),
            "Audit requires a closed and checkpointed ledger")
    prepared = read_sealed(prepared_path)
    prefixes = {row["prefix_id"]: row for row in sorted(
        prepared["prefixes"]["test"], key=lambda row: row["prefix_id"])}
    be = read_sealed(directory / "BE.json")
    coverage = read_sealed(directory / "coverage.json")
    identity = coverage["identity"]
    require(be["identity"] == identity
            and identity["dataset"] == fingerprint(prepared)
            and identity["checkpoint"] == file_hash(checkpoint_path)
            and identity["prefix_ids"] == list(prefixes), "Explainer identity mismatch")
    del prepared
    # Early coverage receipts omit mode and keep BE status only in the sealed BE file.
    be_status = coverage.get("be_status", be["status"] if "mode" not in coverage else None)
    require(be["method"] == "BE" and be["status"] == be_status == "completed"
            and be["completed_prefixes"] == be["expected_prefixes"] == len(prefixes)
            and [row["prefix_id"] for row in be["prefix_records"]] == list(prefixes),
            "BE cohort mismatch")
    positions = {}
    targets_by_prefix = {}
    edges = set()
    classes = set(identity["class_order"])
    text_bytes_floor = 0
    for record in be["prefix_records"]:
        prefix_id = record["prefix_id"]
        prefix = prefixes[prefix_id]
        relevant = set(record["relevant"])
        targets = set(record["predictions"])
        require(targets <= classes and len(prefix["occurrence_ids"]) == len(prefix["activities"]),
                "BE targets or prepared occurrence IDs are invalid")
        targets_by_prefix[prefix_id] = targets
        local = {(source, target) for source in relevant for target in record["predictions"]}
        require(set(map(tuple, record["local_edges"])) == local
                and set(map(tuple, record["merged_edges"])) == edges | local, "BE local merge mismatch")
        edges, removed = merge_prune(edges, local)
        require(record["removed"] == json.loads(json.dumps(removed))
                and set(map(tuple, record["remaining_edges"])) == edges, "BE pruning mismatch")
        positions[prefix_id] = [i for i, label in enumerate(prefix["activities"]) if label in relevant]
        occurrence_bytes = sum(len(json.dumps(value)) - 2 for value in prefix["occurrence_ids"])
        # Prefix IDs are stored in the row and payload. The payload seal adds 64 hex digits.
        bytes_per_context = 2 * len(prefix_id) + 64 + len(targets) * occurrence_bytes
        text_bytes_floor += (2 << len(positions[prefix_id])) * bytes_per_context
    require(set(map(tuple, be["edges"])) == edges, "BE output edge mismatch")
    schedule = {key: {"k": len(pos), "expected": 2 << len(pos)} for key, pos in positions.items()}
    expected = sum(row["expected"] for row in schedule.values())
    require(schedule == coverage["per_prefix"] and expected == coverage["expected"],
            "AE per-prefix schedule mismatch")
    if be_only:
        return {"status": "verified", "scope": "BE graph and AE schedule", "prefixes": len(prefixes),
                "be_edges": len(edges), "be_sha256": file_hash(directory / "BE.json"),
                "ae_scheduled_contexts": expected, "ae_max_positions": max(map(len, positions.values()), default=0),
                "ae_context_text_bytes_floor": text_bytes_floor}
    require(coverage["status"] == "completed", "Complete AE is required")
    require(ledger.stat().st_size >= text_bytes_floor, "AE ledger is smaller than the context text floor")
    ae = read_sealed(directory / "AE.json")
    require(ae["method"] == "AE" and ae["identity"] == identity and ae["coverage"] == coverage
            and ae["status"] == "completed", "AE output differs from coverage receipt")
    sources = sorted({label for prefix in prefixes.values() for label in prefix["activities"]})
    with closing(sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)) as db:
        require(json.loads(db.execute("SELECT value FROM metadata WHERE key='identity'").fetchone()[0])
                == identity, "AE ledger identity mismatch")
        regenerated = ae_matrices(context_rows(db, prefixes, positions, targets_by_prefix),
                                  identity["class_order"], sources)
        require(expected == db.execute("SELECT COUNT(*) FROM contexts").fetchone()[0]
                == ae["expected_contexts"] == regenerated["completed_contexts"]
                == coverage["expected"] == coverage["completed"]
                and coverage["pending"] == 0, "AE total schedule mismatch")
    require(json.loads(json.dumps(regenerated)) == {key: ae[key] for key in regenerated},
            "AE matrices or graphs differ from the sealed votes")
    return {"status": "verified", "prefixes": len(prefixes), "contexts": expected,
            "be_edges": len(edges), "ae_edges": len(ae["edges"]),
            "be_sha256": file_hash(directory / "BE.json"), "ae_sha256": file_hash(directory / "AE.json"),
            "ledger_sha256": file_hash(ledger), "ae_context_text_bytes_floor": text_bytes_floor}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--be-only", action="store_true", help="Audit BE and the scheduled AE workload")
    args = parser.parse_args()
    print(json.dumps(audit(args.run, args.prepared, args.checkpoint, be_only=args.be_only)))
