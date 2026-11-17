"""Explicitly bounded diagnostic pilot, never a substitute for primary coverage."""

from contextlib import closing
from datetime import datetime, timezone
from itertools import islice
from pathlib import Path
import sqlite3
import time

import networkx as nx
import numpy as np

from .artifacts import read_sealed, seal, write_json
from .data.pipeline import fingerprint
from .experiments.perturbations import training_dfg
from .explain.algorithms import ae_contexts, relevant_activities
from .explain.runner import CachedPredictor
from .model.predictor import Predictor
from .model.training import run_lock, source_hash
from .resources import resource_snapshot


def select_pilot_prefixes(prefixes: list[dict], count: int) -> list[dict]:
    """Deterministic length quantiles including extremes; deliberately not random."""
    if count < 1:
        raise ValueError("Pilot sample size must be positive")
    ordered = sorted(prefixes, key=lambda row: (len(row["activities"]), row["prefix_id"]))
    count = min(count, len(ordered))
    if count < 2:
        return ordered[:count]
    return [ordered[i * (len(ordered) - 1) // (count - 1)] for i in range(count)]


def dfg_workload(prefixes: list[dict], graph: nx.DiGraph, starts: set[str], cap: int) -> dict:
    """Count path-based variants without materializing exponential path sets.

    Once a neighbor pair exceeds cap its count is a lower bound. This diagnostic
    does not feed truncated variants into E1 or change its primary definition.
    """
    if cap < 1:
        raise ValueError("Path counting cap must be positive")
    pairs = {}
    rows = []
    for prefix in prefixes:
        labels = prefix["activities"]
        total, exact = len(labels), True  # one PAD variant per occurrence
        for index, original in enumerate(labels):
            if index == 0:
                total += len(starts - {original})
            elif index == len(labels) - 1:
                successors = set(graph.successors(labels[index - 1])) if labels[index - 1] in graph else set()
                total += len(successors - {original})
            else:
                previous, following = labels[index - 1], labels[index + 1]
                if previous == following or previous not in graph or following not in graph:
                    continue
                key = (previous, following)
                if key not in pairs:
                    count = sum(1 for _ in islice(nx.all_simple_paths(graph, *key), cap + 1))
                    pairs[key] = {"count": count, "exact": count <= cap}
                row = pairs[key]
                # The identity path is simple only when its three nodes differ.
                identity_exists = original not in key and graph.has_edge(previous, original) and graph.has_edge(original, following)
                total += max(0, row["count"] - int(identity_exists))
                exact = exact and row["exact"]
        rows.append({"prefix_id": prefix["prefix_id"], "variants_lower_bound": total, "exact": exact})
    return {"path_count_cap": cap, "prefixes": rows,
            "total_variants_lower_bound": sum(row["variants_lower_bound"] for row in rows),
            "exact": all(row["exact"] for row in rows),
            "neighbor_pairs": [{"source": key[0], "target": key[1], **row} for key, row in sorted(pairs.items())]}


def run_pilot(prepared: dict, checkpoint: Path, directory: Path, sample_size: int = 12,
              contexts_per_prefix: int = 32, path_count_cap: int = 1000,
              max_seconds: float = 120, minimum_ram_bytes: int = 256 * 1024**2,
              minimum_disk_bytes: int = 1024**3) -> dict:
    if contexts_per_prefix < 1 or max_seconds <= 0:
        raise ValueError("Pilot quotas must be positive")
    predictor = Predictor(checkpoint, prepared)
    selected = select_pilot_prefixes(prepared["prefixes"]["test"], sample_size)
    with run_lock(directory):
        if any(path.name != "writer.lock" for path in directory.iterdir()):
            raise FileExistsError("Pilot requires a fresh output directory")
        started, cpu_started = time.perf_counter(), time.process_time()
        before = resource_snapshot(directory)
        result = {"schema_version": 1, "status": "incomplete", "primary_status": "incomplete",
                  "scope": "diagnostic-length-stratified-pilot", "dataset_scope": prepared.get("scope"),
                  "started_utc": datetime.now(timezone.utc).isoformat(),
                  "identity": {"dataset": fingerprint(prepared), "checkpoint": predictor.checkpoint_id,
                               "source": source_hash(), "class_order": predictor.class_order},
                  "selection": "equally spaced indices in (prefix length, prefix ID) order, including extremes",
                  "population": len(prepared["prefixes"]["test"]),
                  "sample_ids": [row["prefix_id"] for row in selected],
                  "quotas": {"contexts_per_prefix": contexts_per_prefix, "path_count_cap": path_count_cap,
                             "max_seconds": max_seconds, "minimum_ram_bytes": minimum_ram_bytes,
                             "minimum_disk_bytes": minimum_disk_bytes},
                  "before": before, "prefixes": [], "stop_reason": None}
        write_json(directory / "pilot.json", seal(result))

        def stop_reason():
            snapshot = resource_snapshot(directory)
            if time.perf_counter() - started >= max_seconds:
                return "wall_time_quota"
            if snapshot["disk_free_bytes"] < minimum_disk_bytes:
                return "disk_floor"
            ram = snapshot["system_available_ram_bytes"]
            if ram is not None and ram < minimum_ram_bytes:
                return "available_ram_floor"
            return None

        with closing(sqlite3.connect(directory / "cache.sqlite")) as connection:
            cached = CachedPredictor(predictor, connection)
            for prefix in selected:
                result["stop_reason"] = stop_reason()
                if result["stop_reason"]:
                    break
                relevance = relevant_activities(cached, prefix)
                k = sum(label in relevance["relevant"] for label in prefix["activities"])
                expected = 2 * (1 << k)
                ae_start = time.perf_counter()
                executions_before, hits_before = cached.executions, cached.hits
                completed, votes, bytes_written = 0, 0, 0
                for context in islice(ae_contexts(cached, prefix, relevance), contexts_per_prefix):
                    path = directory / "contexts" / prefix["prefix_id"] / f"{context['scenario']}-{context['subset']}.json"
                    write_json(path, seal(context))
                    completed += 1
                    votes += len(context["votes"])
                    bytes_written += path.stat().st_size
                    result["stop_reason"] = stop_reason()
                    if result["stop_reason"]:
                        break
                duration = time.perf_counter() - ae_start
                row = {"prefix_id": prefix["prefix_id"], "length": len(prefix["activities"]),
                       "relevance": relevance, "k": k, "expected_contexts": expected,
                       "completed_contexts": completed, "pending_contexts": expected - completed,
                       "coverage": completed / expected, "retained_votes": votes,
                       "ae_wall_seconds": duration, "ae_contexts_per_second": completed / duration,
                       "ae_forward_executions": cached.executions - executions_before,
                       "ae_cache_hits": cached.hits - hits_before, "context_bytes": bytes_written,
                       "resources": resource_snapshot(directory)}
                result["prefixes"].append(row)
                write_json(directory / "pilot.json", seal(result))
                if result["stop_reason"]:
                    break
            result.update(cache_hits=cached.hits, forward_executions=cached.executions,
                          cache_entries=connection.execute("SELECT count(*) FROM inference").fetchone()[0])
        # Counts only; no expensive E1 model forwards and no capped E1 metric.
        if result["stop_reason"] is None:
            graph, starts = training_dfg(prepared)
            result["E1_workload"] = dfg_workload(selected, graph, starts, path_count_cap)
        ks = [row["k"] for row in result["prefixes"]]
        expected = sum(row["expected_contexts"] for row in result["prefixes"])
        completed = sum(row["completed_contexts"] for row in result["prefixes"])
        result.update(status="completed" if len(ks) == len(selected) and result["stop_reason"] is None else "incomplete",
                      completed_sample_prefixes=len(ks), expected_sample_prefixes=len(selected),
                      observed_subset_expected_contexts=expected, completed_contexts=completed,
                      observed_subset_coverage=completed / expected if expected else None,
                      full_population_expected_contexts=None,
                      full_population_lower_bound_contexts=expected,
                      k_distribution_sample=None if not ks else {"min": min(ks), "median": float(np.median(ks)),
                                                                 "p95": float(np.percentile(ks, 95)), "max": max(ks)},
                      wall_seconds=time.perf_counter() - started, cpu_seconds=time.process_time() - cpu_started,
                      after=resource_snapshot(directory), ended_utc=datetime.now(timezone.utc).isoformat())
        write_json(directory / "pilot.json", seal(result))
        return result
