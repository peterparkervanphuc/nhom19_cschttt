"""Durable explainer execution and checkpoint-scoped inference reuse."""

from contextlib import closing
import io
import json
import math
from pathlib import Path
import sqlite3
import time

import numpy as np

from ..artifacts import read_sealed, seal, write_json
from ..data.pipeline import fingerprint
from ..graphs.relations import merge_prune
from ..model.predictor import Prediction, Predictor
from ..model.training import run_lock, source_hash
from ..resources import resource_snapshot
from .algorithms import ae_contexts, ae_matrices, relevant_activities


class CachedPredictor:
    """Bound to one database; the owner commits each BE prefix or AE context."""
    def __init__(self, predictor: Predictor, connection: sqlite3.Connection, policy: str = "all"):
        if policy not in {"all", "baseline"}:
            raise ValueError("Unknown cache policy")
        self.predictor = predictor
        self.connection = connection
        self.policy = policy
        self.class_order = predictor.class_order
        self.checkpoint_id = predictor.checkpoint_id
        self.hits = 0
        self.executions = 0
        connection.execute("CREATE TABLE IF NOT EXISTS inference (key TEXT PRIMARY KEY, payload BLOB, checksum TEXT)")

    def predict(self, activities, intervention_positions=(), mode="E3-PAPER"):
        if self.policy == "baseline" and (any(label is None for label in activities) or intervention_positions):
            result = self.predictor.predict(activities, intervention_positions, mode)
            self.executions += 1
            return result
        key = fingerprint([self.checkpoint_id, self.class_order, list(activities),
                           list(intervention_positions), mode, "cpu", "float32"])
        cached = self.connection.execute("SELECT payload, checksum FROM inference WHERE key=?", (key,)).fetchone()
        if cached is not None:
            import hashlib
            if hashlib.sha256(cached[0]).hexdigest() != cached[1]:
                raise ValueError("Inference cache checksum mismatch")
            with np.load(io.BytesIO(cached[0]), allow_pickle=False) as data:
                result = Prediction(data["probabilities"], data["attention"], data["effective"],
                                    data["valid"], self.checkpoint_id, self.class_order)
            self.hits += 1
            return result
        result = self.predictor.predict(activities, intervention_positions, mode)
        buffer = io.BytesIO()
        np.savez_compressed(buffer, probabilities=result.probabilities, attention=result.attention,
                            effective=result.effective_attention, valid=result.valid)
        import hashlib
        payload = buffer.getvalue()
        self.connection.execute("INSERT INTO inference VALUES (?,?,?)",
                                (key, payload, hashlib.sha256(payload).hexdigest()))
        self.executions += 1
        return result


def run_explainers(prepared: dict, checkpoint: Path, directory: Path,
                   stop_after_contexts: int | None = None, *, be_only: bool = False,
                   max_seconds: float | None = None, cache_policy: str = "all") -> dict:
    if cache_policy not in {"all", "baseline"}:
        raise ValueError("Unknown cache policy")
    if be_only and stop_after_contexts is not None:
        raise ValueError("A BE-only run cannot set an AE context quota")
    if stop_after_contexts is not None and stop_after_contexts < 1:
        raise ValueError("Context stop must be positive")
    if max_seconds is not None and (not math.isfinite(max_seconds) or max_seconds <= 0):
        raise ValueError("Explainer wall time quota must be finite and positive")
    predictor = Predictor(checkpoint, prepared)
    prefixes = sorted(prepared["prefixes"]["test"], key=lambda prefix: prefix["prefix_id"])
    identity = {"checkpoint": predictor.checkpoint_id, "dataset": fingerprint(prepared),
                "source": source_hash(), "prefix_ids": [prefix["prefix_id"] for prefix in prefixes],
                "class_order": predictor.class_order, "be_profile": "BE-P1", "ae_profile": "D07-D08",
                "cache_policy": cache_policy}
    identity = json.loads(json.dumps(identity))
    with run_lock(directory), closing(sqlite3.connect(directory / "ledger.sqlite")) as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
        old = connection.execute("SELECT value FROM metadata WHERE key='identity'").fetchone()
        if old is not None and json.loads(old[0]) != identity:
            raise ValueError("Explainer resume identity mismatch")
        if old is None:
            connection.execute("INSERT INTO metadata VALUES ('identity',?)", (json.dumps(identity),))
        connection.execute("CREATE TABLE IF NOT EXISTS contexts (prefix_id TEXT, scenario TEXT, subset TEXT, payload TEXT, PRIMARY KEY(prefix_id,scenario,subset))")
        connection.commit()
        cached = CachedPredictor(predictor, connection, cache_policy)
        started = time.perf_counter()
        cpu_started = time.process_time()
        before = resource_snapshot(directory)
        observed = before

        def quota():
            nonlocal observed
            if max_seconds is not None and time.perf_counter() - started >= max_seconds:
                return "wall_time_quota"
            observed = resource_snapshot(directory)
            if observed["disk_free_bytes"] < 1024**3:
                return "disk_floor"
            available = observed["system_available_ram_bytes"]
            if available is not None and available < 256 * 1024**2:
                return "available_ram_floor"
            return None

        be_path = directory / "BE.json"
        if be_path.exists():
            be = read_sealed(be_path)
            if be["identity"] != identity:
                raise ValueError("BE artifact identity mismatch")
        else:
            edges = set()
            records = []
            prefix_dir = directory / "be-prefixes"
            for prefix in prefixes:
                record_path = prefix_dir / (prefix["prefix_id"] + ".json")
                if record_path.exists():
                    relevance = read_sealed(record_path)
                else:
                    stop = quota()
                    if stop:
                        coverage = {"identity": identity, "status": "incomplete", "be_status": "incomplete",
                                    "mode": "be-only" if be_only else "be-and-ae",
                                    "be_expected_prefixes": len(prefixes), "be_completed_prefixes": len(records),
                                    "expected": None, "completed": 0, "pending": None, "coverage": None,
                                    "stop_reason": stop, "max_seconds": max_seconds,
                                    "before": before, "resource_at_last_check": observed,
                                    "wall_seconds_this_session": time.perf_counter() - started,
                                    "cpu_seconds_this_session": time.process_time() - cpu_started}
                        write_json(directory / "coverage.json", seal(coverage))
                        return coverage
                    relevance = relevant_activities(cached, prefix)
                    connection.commit()
                    write_json(record_path, seal(relevance))
                local = {(source, target) for source in relevance["relevant"] for target in relevance["predictions"]}
                snapshot = edges | local
                edges, removed = merge_prune(edges, local)
                records.append({**relevance, "local_edges": sorted(local),
                                "merged_edges": sorted(snapshot), "removed": removed,
                                "remaining_edges": sorted(edges)})
            be = {"identity": identity, "method": "BE", "status": "completed", "edges": sorted(edges),
                  "prefix_records": records, "expected_prefixes": len(prefixes), "completed_prefixes": len(records)}
            write_json(be_path, seal(be))
        relevance_by_id = {record["prefix_id"]: record for record in be["prefix_records"]}
        expected_by_prefix = {}
        for prefix in prefixes:
            relevant = set(relevance_by_id[prefix["prefix_id"]]["relevant"])
            k = sum(label in relevant for label in prefix["activities"])
            expected_by_prefix[prefix["prefix_id"]] = {"k": k, "expected": 2 * (1 << k)}
        expected = sum(row["expected"] for row in expected_by_prefix.values())
        def is_completed(prefix_id, scenario, subset):
            return connection.execute("SELECT 1 FROM contexts WHERE prefix_id=? AND scenario=? AND subset=?",
                                      (prefix_id, scenario, subset)).fetchone() is not None
        added = 0
        stop = None
        for prefix in (() if be_only else prefixes):
            contexts = iter(ae_contexts(cached, prefix, relevance_by_id[prefix["prefix_id"]], is_completed))
            while True:
                stop = quota()
                if stop:
                    break
                try:
                    context = next(contexts)
                except StopIteration:
                    break
                connection.execute("INSERT INTO contexts VALUES (?,?,?,?)",
                                    (context["prefix_id"], context["scenario"], context["subset"],
                                     json.dumps(seal(context), allow_nan=False)))
                connection.commit()
                added += 1
                if stop_after_contexts is not None and added >= stop_after_contexts:
                    break
            if stop or stop_after_contexts is not None and added >= stop_after_contexts:
                break
        completed = connection.execute("SELECT COUNT(*) FROM contexts").fetchone()[0]
        status = "completed" if completed == expected else "incomplete"
        coverage = {"identity": identity, "status": status, "expected": expected, "completed": completed,
                    "be_status": be["status"], "mode": "be-only" if be_only else "be-and-ae",
                    "be_expected_prefixes": len(prefixes), "be_completed_prefixes": len(be["prefix_records"]),
                    "stop_reason": stop, "max_seconds": max_seconds,
                    "before": before, "resource_at_last_check": observed,
                    "pending": expected - completed, "coverage": completed / expected if expected else None,
                    "per_prefix": expected_by_prefix, "cache_hits_this_session": cached.hits,
                    "forward_executions_this_session": cached.executions,
                    "cache_entries": connection.execute("SELECT COUNT(*) FROM inference").fetchone()[0],
                    "wall_seconds_this_session": time.perf_counter() - started,
                    "cpu_seconds_this_session": time.process_time() - cpu_started}
        if status == "completed" and not be_only:
            def records():
                for prefix in prefixes:
                    for scenario in ("most", "few"):
                        cursor = connection.execute("SELECT payload FROM contexts WHERE prefix_id=? AND scenario=? ORDER BY length(subset), subset",
                                                    (prefix["prefix_id"], scenario))
                        for (payload,) in cursor:
                            envelope = json.loads(payload)
                            if fingerprint(envelope["payload"]) != envelope["sha256"]:
                                raise ValueError("AE context checksum mismatch")
                            yield envelope["payload"]
            sources = sorted({label for prefix in prefixes for label in prefix["activities"]})
            ae = ae_matrices(records(), list(predictor.class_order), sources)
            ae.update(identity=identity, status=status, expected_contexts=expected, coverage=coverage)
            write_json(directory / "AE.json", seal(ae))
        write_json(directory / "coverage.json", seal(coverage))
        return coverage
