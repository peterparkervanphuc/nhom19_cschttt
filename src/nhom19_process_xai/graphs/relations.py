from __future__ import annotations

Edge = tuple[str, str]


def project(edges: set[Edge], activities: list[str] | tuple[str, ...]) -> set[Edge]:
    sources = set(activities)
    return {(source, target) for source, target in edges if source in sources}


def merge_prune(global_edges: set[Edge], local_edges: set[Edge]) -> tuple[set[Edge], list[dict]]:
    """One simultaneous pass over the merged snapshot, preserving self-loops."""
    snapshot = global_edges | local_edges
    nodes = {node for edge in snapshot for node in edge}
    removed = []
    for source, target in sorted(snapshot):
        witnesses = sorted(node for node in nodes - {source, target}
                           if (source, node) in snapshot and (node, target) in snapshot)
        if source != target and witnesses:
            removed.append({"source": source, "target": target, "witnesses": witnesses})
    remaining = snapshot - {(row["source"], row["target"]) for row in removed}
    return remaining, removed
