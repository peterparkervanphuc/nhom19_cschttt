from pathlib import Path
import runpy

from nhom19_process_xai.graphs.relations import merge_prune


def test_audit_distinguishes_removed_edges_from_lost_paths():
    script = Path(__file__).resolve().parents[1] / "scripts/audit_explainer_run.py"
    check = runpy.run_path(str(script))["unreachable_removed_edges"]
    triangle = {(u, v) for u in "ABC" for v in "ABC" if u != v}
    remaining, removed = merge_prune(set(), triangle)
    assert check(remaining, removed) == sorted(triangle)

    edges = {("A", "B"), ("B", "C"), ("A", "C")}
    remaining, removed = merge_prune(set(), edges)
    assert [(edge["source"], edge["target"]) for edge in removed] == [("A", "C")]
    assert not check(remaining, removed)
