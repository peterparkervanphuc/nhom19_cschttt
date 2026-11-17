"""Count the full E1 schedule without evaluating or storing variants."""

import argparse
from collections import Counter
from functools import lru_cache
from pathlib import Path

from nhom19_process_xai.artifacts import read_sealed, seal, write_json
from nhom19_process_xai.data.pipeline import file_hash
from nhom19_process_xai.experiments.perturbations import training_dfg


def count_schedule(prepared):
    graph, starts = training_dfg(prepared)
    nodes = sorted(graph)
    index = {label: position for position, label in enumerate(nodes)}
    successors = [tuple(index[target] for target in graph.successors(label) if target != label)
                  for label in nodes]
    prefixes = prepared["prefixes"]["test"]
    uses = Counter()
    adjustment = 0
    for prefix in prefixes:
        labels = prefix["activities"]
        adjustment += len(labels) + len(starts - {labels[0]})
        for previous, original, following in zip(labels, labels[1:], labels[2:]):
            if previous == following or previous not in index or following not in index:
                continue
            uses[previous, following] += 1
            if (original not in (previous, following) and graph.has_edge(previous, original)
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
    return {"prefix_count": len(prefixes), "boundary_and_identity_adjustment": adjustment,
            "pair_counts": pair_counts,
            "variant_count": adjustment + sum(row["uses"] * row["path_count"] for row in pair_counts)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, epilog="Counting can grow exponentially with activity count.")
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = count_schedule(read_sealed(args.prepared))
    result.update(scope="workload-count-only", prepared_sha256=file_hash(args.prepared),
                  counter_sha256=file_hash(Path(__file__)))
    write_json(args.output, seal(result))
    print(result["variant_count"])
