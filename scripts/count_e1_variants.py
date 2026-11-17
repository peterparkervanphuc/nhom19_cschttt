"""Count an E1 schedule or a lower bound without evaluating variants."""

import argparse
from collections import Counter
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import networkx as nx

from nhom19_process_xai.artifacts import read_sealed, seal, write_json
from nhom19_process_xai.data.pipeline import file_hash, iter_xes_traces, split_cases
from nhom19_process_xai.data.preparation import preprocess
from nhom19_process_xai.experiments.perturbations import training_dfg


def count_paths(graph, starts, prefixes, activity_limit=None):
    if activity_limit is not None and not 1 <= activity_limit < len(graph):
        raise ValueError("Activity limit must retain a nonempty proper subset of the DFG")
    def rank(label):
        degree = graph.in_degree(label) + graph.out_degree(label) - 2 * graph.has_edge(label, label)
        return -degree, label

    retained = sorted(graph, key=rank)[:activity_limit] if activity_limit is not None else sorted(graph)
    nodes = sorted(retained)
    index = {label: position for position, label in enumerate(nodes)}
    successors = [tuple(index[target] for target in graph.successors(label) if target != label and target in index)
                  for label in nodes]
    uses = Counter()
    adjustment = 0
    prefix_count = 0
    for labels in prefixes:
        prefix_count += 1
        adjustment += len(labels) + len(starts - {labels[0]})
        for previous, original, following in zip(labels, labels[1:], labels[2:]):
            if previous == following or previous not in index or following not in index:
                continue
            uses[previous, following] += 1
            if (original in index and original not in (previous, following) and graph.has_edge(previous, original)
                    and graph.has_edge(original, following)):
                adjustment -= 1
        if len(labels) > 1 and labels[-2] in graph:
            adjustment += len(set(graph.successors(labels[-2])) - {labels[-1]})

    pair_counts = []
    for destination in nodes:
        terminal = index[destination]

        @lru_cache(maxsize=None)
        def paths(current, visited):
            if current == terminal:
                return 1
            return sum(paths(target, visited | (1 << target)) for target in successors[current]
                       if not visited & (1 << target))

        for source in nodes:
            if uses[source, destination]:
                origin = index[source]
                pair_counts.append({"source": source, "destination": destination,
                                    "uses": uses[source, destination], "path_count": paths(origin, 1 << origin)})
        paths.cache_clear()
    total = adjustment + sum(row["uses"] * row["path_count"] for row in pair_counts)
    result = {"prefix_count": prefix_count, "boundary_and_identity_adjustment": adjustment,
              "pair_counts": pair_counts}
    if activity_limit is None:
        result["variant_count"] = total
    else:
        result.update(variant_count_lower_bound=total, full_activity_count=len(graph),
                      induced_activities=retained)
    return result


def count_schedule(prepared, activity_limit=None):
    graph, starts = training_dfg(prepared)
    return count_paths(graph, starts, (row["activities"] for row in prepared["prefixes"]["test"]), activity_limit)


def count_xes_lower_bound(config_path, activity_limit):
    raw_config = config_path.read_bytes()
    config = json.loads(raw_config)
    if config["format"] != "xes" or "split" in config or config.get("scope") != "verified_dataset":
        raise ValueError("XES lower bound requires a verified XES configuration with a seeded split")
    path = config_path.parent / config["path"]
    digest = file_hash(path)
    if digest != config["expected_sha256"]:
        raise ValueError("Raw XES checksum mismatch")
    cases = {}
    for trace in iter_xes_traces(path, config.get("naive_timezone")):
        events, _ = preprocess(trace, config.get("filters", []), config.get("lifecycle_classifier", False))
        if events:
            events.sort(key=lambda event: (event.timestamp, event.source_ordinal))
            cases[events[0].case_id] = [event.activity for event in events]
    if file_hash(path) != digest:
        raise ValueError("Raw XES changed during scan")
    counts = {"cases": len(cases), "events": sum(map(len, cases.values())),
              "activities": len({label for labels in cases.values() for label in labels})}
    if any(counts.get(key) != value for key, value in config.get("expected_counts", {}).items()):
        raise ValueError("Scanned XES counts differ from configuration")
    seed = config.get("seed", 42)
    split = split_cases(cases, seed)
    graph, starts = nx.DiGraph(), set()
    for case_id in split["train"]:
        labels = cases[case_id]
        starts.add(labels[0])
        graph.add_nodes_from(labels)
        graph.add_edges_from(zip(labels, labels[1:]))
    prefixes = (cases[case_id][:length] for case_id in split["test"] for length in range(1, len(cases[case_id])))
    result = count_paths(graph, starts, prefixes, activity_limit)
    result.update(raw_sha256=digest, dataset_config_sha256=sha256(raw_config).hexdigest(), split_seed=seed,
                  train_cases=len(split["train"]), test_cases=len(split["test"]))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, epilog="Counting can grow exponentially with activity count.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prepared", type=Path)
    source.add_argument("--xes-config", type=Path, help="Stream a verified XES using its dataset configuration")
    parser.add_argument("--induced-activities", type=int, help="Count only interior paths inside this many top-degree activities")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.xes_config is not None:
        if args.induced_activities is None:
            parser.error("--xes-config requires --induced-activities")
        result = count_xes_lower_bound(args.xes_config, args.induced_activities)
    else:
        result = count_schedule(read_sealed(args.prepared), args.induced_activities)
        result["prepared_sha256"] = file_hash(args.prepared)
    exact = args.induced_activities is None
    result.update(scope="workload-count-only" if exact else "workload-lower-bound-only",
                  counter_sha256=file_hash(Path(__file__)))
    write_json(args.output, seal(result))
    print(result["variant_count" if exact else "variant_count_lower_bound"])
