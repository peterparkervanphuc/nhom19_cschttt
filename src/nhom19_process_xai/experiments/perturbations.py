"""Training-log DFG perturbations with original occurrence attribution."""

from dataclasses import dataclass

import networkx as nx

from ..data.pipeline import fingerprint


@dataclass(frozen=True)
class Variant:
    variant_id: str
    position: int
    original_activity: str
    activities: tuple[str | None, ...]
    operation: str
    replacement: tuple[str, ...]


def training_dfg(prepared: dict) -> tuple[nx.DiGraph, set[str]]:
    cases = {}
    train_ids = set(prepared["split"]["train"])
    for event in prepared["events"]:
        if event["case_id"] in train_ids:
            cases.setdefault(event["case_id"], []).append(event)
    graph = nx.DiGraph()
    starts = set()
    for events in cases.values():
        events.sort(key=lambda event: (event["timestamp"], event["source_ordinal"]))
        labels = [event["activity"] for event in events]
        starts.add(labels[0])
        graph.add_nodes_from(labels)
        graph.add_edges_from(zip(labels, labels[1:]))
    return graph, starts


def _replacements(graph: nx.DiGraph, source: str, target: str):
    """Yield simple path interiors in tuple order without collecting paths."""
    if source == target or source not in graph or target not in graph:
        return
    reachable = nx.ancestors(graph, target)
    if source not in reachable:
        return
    successors = {node: sorted(set(graph.successors(node)) & reachable)
                  for node in reachable}
    visited = {source, target}

    def walk(node, interior):
        if graph.has_edge(node, target):
            yield interior
        for next_node in successors[node]:
            if next_node not in visited:
                visited.add(next_node)
                yield from walk(next_node, (*interior, next_node))
                visited.remove(next_node)

    yield from walk(source, ())


def variants(activities: tuple[str, ...] | list[str], prefix_id: str,
             graph: nx.DiGraph, starts: set[str]):
    labels = tuple(activities)
    for position, original in enumerate(labels):
        masked = labels[:position] + (None,) + labels[position + 1:]
        yield Variant(fingerprint([prefix_id, position, "mask"]), position, original,
                      masked, "mask", ())
        if position == 0:
            candidates = ((label,) for label in sorted(starts))
        elif position == len(labels) - 1:
            previous = labels[position - 1]
            candidates = ((label,) for label in sorted(graph.successors(previous))) if previous in graph else ()
        else:
            previous, following = labels[position - 1], labels[position + 1]
            candidates = _replacements(graph, previous, following)
        for replacement in candidates:
            if replacement == (original,):
                continue
            changed = labels[:position] + replacement + labels[position + 1:]
            yield Variant(fingerprint([prefix_id, position, "replace", replacement]),
                          position, original, changed, "replace", replacement)
