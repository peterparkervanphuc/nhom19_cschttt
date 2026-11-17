import networkx as nx
import pytest

from nhom19_process_xai.artifacts import read_sealed, seal, write_json
from nhom19_process_xai.graphs.export import export_graph


def test_graphml_orientation_loop_and_dedup(tmp_path):
    source = tmp_path / "explanation.json"
    write_json(source, seal({"method": "AE", "status": "completed", "identity": {"checkpoint": "fixture"},
                             "edges": [["A", "B"], ["A", "A"], ["A", "B"]]}))
    output = tmp_path / "graph"
    result = export_graph(source, output)
    assert result["edges"] == 2
    graph = nx.read_graphml(output / "graph.graphml")
    assert graph.is_directed()
    assert set(graph.edges) == {("A", "B"), ("A", "A")}
    assert read_sealed(output / "graph.json")["edges"] == [["A", "A"], ["A", "B"]]
    assert "<svg" in (output / "graph.svg").read_text()
    with pytest.raises(FileExistsError):
        export_graph(source, output)


def test_failed_export_never_publishes_partial_directory(tmp_path, monkeypatch):
    import matplotlib.figure
    source = tmp_path / "source.json"
    write_json(source, seal({"method": "BE", "status": "completed", "identity": {}, "edges": []}))
    savefig = matplotlib.figure.Figure.savefig

    def fail(*args, **kwargs):
        raise OSError("simulated renderer error")

    monkeypatch.setattr(matplotlib.figure.Figure, "savefig", fail)
    with pytest.raises(OSError, match="simulated"):
        export_graph(source, tmp_path / "export")
    assert not (tmp_path / "export").exists()
    monkeypatch.setattr(matplotlib.figure.Figure, "savefig", savefig)
    assert export_graph(source, tmp_path / "export")["edges"] == 0
