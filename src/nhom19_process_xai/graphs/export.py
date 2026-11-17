"""Export the exact directed graph without changing its semantics."""

from pathlib import Path
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.path import Path as DrawingPath
import networkx as nx

from ..artifacts import atomic_write, read_sealed, seal, write_json
from ..data.pipeline import file_hash


def export_graph(explanation_path: Path, output: Path) -> dict:
    """Publish the complete export directory in one non-overwriting rename."""
    output = output.resolve()
    if output.exists():
        raise FileExistsError("Graph export directory already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{output.name}-", dir=output.parent) as temporary:
        pending = Path(temporary) / "export"
        manifest = _write_graph(explanation_path, pending)
        pending.rename(output)
    return manifest


def _write_graph(explanation_path: Path, output: Path) -> dict:
    explanation = read_sealed(explanation_path)
    if explanation.get("status") != "completed":
        raise ValueError("Graph export requires a completed explanation")
    output.mkdir(parents=True, exist_ok=True)
    paths = [output / name for name in ("graph.json", "graph.graphml", "graph.svg", "manifest.json")]
    if any(path.exists() for path in paths):
        raise FileExistsError("Graph export artifacts already exist")
    edges = sorted({tuple(edge) for edge in explanation["edges"]})
    graph = nx.DiGraph()
    graph.add_nodes_from(sorted({node for edge in edges for node in edge}))
    graph.add_edges_from(edges)
    write_json(paths[0], seal({"method": explanation["method"], "identity": explanation["identity"],
                              "edges": edges, "scope": "global-test-prefix-graph",
                              "explanation_sha256": file_hash(explanation_path)}))
    atomic_write(paths[1], lambda path: nx.write_graphml(graph, path))
    circular = len(graph) > 6
    size = max(8, len(graph) * .67)
    figure, axes = plt.subplots(figsize=(size, size) if circular else (6, 4))
    if graph:
        positions = nx.circular_layout(graph) if circular else nx.spring_layout(graph, seed=404)
        nx.draw_networkx(graph, positions, ax=axes, node_color="#e5edf6", edge_color="#3b4b5c",
                         edgelist=[edge for edge in graph.edges if edge[0] != edge[1]],
                         arrows=True, arrowsize=16, node_size=2200, font_size=9,
                         connectionstyle="arc3,rad=0.08")
        # NetworkX's default self-loop can disappear beneath large fixed-size
        # nodes. Use an explicit outward curve and reserve plot margins.
        for node in nx.nodes_with_selfloops(graph):
            x, y = positions[node]
            if circular:
                # The circular layout places the nodes on a unit-radius ring.
                # Curve each self-loop away from the other nodes and edges.
                points = [(x + radial * x - lateral * y, y + radial * y + lateral * x)
                          for radial, lateral in [(0.07, -0.07), (0.38, -0.18),
                                                  (0.38, 0.18), (0.07, 0.07)]]
            else:
                points = [(x - .12, y + .10), (x - .55, y + .65),
                          (x + .55, y + .65), (x + .12, y + .10)]
            loop = FancyArrowPatch(path=DrawingPath(points,
                                                    [DrawingPath.MOVETO, DrawingPath.CURVE4,
                                                     DrawingPath.CURVE4, DrawingPath.CURVE4]),
                                   arrowstyle="-|>", mutation_scale=16, color="#3b4b5c",
                                   zorder=0, clip_on=False)
            axes.add_patch(loop)
        axes.margins(.25)
        if circular:
            axes.set_aspect("equal")
    else:
        axes.text(.5, .5, "No explanation edges", transform=axes.transAxes, ha="center")
    axes.set_title(explanation["method"] + " — activity relations")
    axes.set_axis_off()
    figure.tight_layout()
    atomic_write(paths[2], lambda path: figure.savefig(path, format="svg", bbox_inches="tight"))
    plt.close(figure)
    manifest = {"method": explanation["method"], "nodes": len(graph), "edges": len(edges),
                "source_sha256": file_hash(explanation_path),
                "files": {path.name: file_hash(path) for path in paths[:3]}}
    write_json(paths[3], seal(manifest))
    return manifest
