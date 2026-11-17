"""Compare selected Complex-Model and Looped-AND BPMN relations with BE."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from nhom19_process_xai.artifacts import read_sealed, seal, write_json
from nhom19_process_xai.data.pipeline import file_hash, fingerprint, iter_xes_traces, split_cases


ARCHIVE_SHA256 = "b1b88b2d7797fbe3369dccc5c4fe8d9a96af5d52293954279d4bab2f0bcc169e"
BPMN_ROOT = "Supplementary_Material/Synthetic_Event_Logs/generated_event_logs/"


def load_bpmn(archive, member):
    raw = archive.read(BPMN_ROOT + member)
    namespace = "{http://www.omg.org/spec/BPMN/20100524/MODEL}"
    process, = ET.fromstring(raw).findall(namespace + "process")
    tasks = {node.attrib["name"]: node.attrib["id"] for node in process.findall(namespace + "task")}
    types = {node.attrib["id"]: node.tag.removeprefix(namespace) for node in process if "id" in node.attrib}
    flows = {(node.attrib["sourceRef"], node.attrib["targetRef"]) for node in process.findall(namespace + "sequenceFlow")}
    return tasks, types, flows, {"member": BPMN_ROOT + member, "sha256": sha256(raw).hexdigest()}


def audit_inputs(project, tag, graph_folder):
    config_path = project / "configs/datasets" / f"{tag}.json"
    config = json.loads(config_path.read_bytes())
    raw_log = config_path.parent / config["path"]
    digest = file_hash(raw_log)
    if digest != config["expected_sha256"] or config.get("filters") or config.get("lifecycle_classifier"):
        raise ValueError("Expected the pinned activity-only XES without filters")
    cases = {}
    for trace in iter_xes_traces(raw_log, config.get("naive_timezone")):
        if trace:
            cases[trace[0].case_id] = [event.activity for event in sorted(trace, key=lambda e: (e.timestamp, e.source_ordinal))]
    if len(cases) != config["expected_counts"]["cases"] or file_hash(raw_log) != digest:
        raise ValueError("XES case count or digest differs from the configuration")
    split = split_cases(cases, config["seed"])
    folder = project / "artifacts" / tag
    run = json.loads((folder / "base/run.json").read_bytes())
    graph_dir = folder / "graphs" / graph_folder
    graph_path = graph_dir / "graph.json"
    graph, manifest = read_sealed(graph_path), read_sealed(graph_dir / "manifest.json")
    original = json.loads((folder / "explainer-audit.json").read_bytes())
    graph_digest = file_hash(graph_path)
    identity = run["identity"]
    ids = sorted(fingerprint([identity["processed_sha256"], identity["split_sha256"], case_id, length])
                 for case_id in split["test"] for length in range(1, len(cases[case_id])))
    if (graph["method"] != "BE" or original["status"] != "verified"
            or manifest["files"]["graph.json"] != graph_digest
            or manifest["source_sha256"] != graph["explanation_sha256"]
            or graph["explanation_sha256"] != original["be_sha256"]
            or run["checkpoint_sha256"] != graph["identity"]["checkpoint"]
            or identity["dataset_sha256"] != graph["identity"]["dataset"]
            or identity["split_sha256"] != fingerprint(split) or ids != graph["identity"]["prefix_ids"]):
        raise ValueError("BE evidence differs from the sealed graph or test population")
    metadata = {"raw_xes_sha256": digest, "be_graph_sha256": graph_digest, "checkpoint_sha256": run["checkpoint_sha256"],
                "test_split_sha256": identity["split_sha256"], "test_prefixes": len(ids)}
    return [cases[case_id] for case_id in split["test"]], set(map(tuple, graph["edges"])), metadata


def successor(flows, source):
    target, = [end for start, end in flows if start == source]
    return target


def pair_rows(traces, be_edges, pairs):
    direct = Counter((a, b) for labels in traces for a, b in zip(labels, labels[1:]))
    return [{"source": a, "target": b, "direct_test_count": direct[a, b], "in_be": (a, b) in be_edges}
            for a, b in pairs]


def loop_attempts(labels):
    if labels[0] != "A" or labels[-1] != "Z" or len(labels) <= 2 or (len(labels) - 2) % 4:
        raise ValueError("Expected the terminal activities and complete parallel iterations")
    interior = labels[1:-1]
    for i in range(0, len(interior), 4):
        block = interior[i:i + 4]
        if set(block) != set("IJMN") or block.index("I") >= block.index("J") or block.index("M") >= block.index("N"):
            raise ValueError("Trace violates parallel branch precedence")
    return len(interior) // 4


def audit_looped(project, archive):
    t, types, flows, artifact = load_bpmn(archive, "15_looped_AND/looped_AND.bpmn")
    entry = successor(flows, t["A"])
    split = successor(flows, entry)
    join = successor(flows, t["J"])
    exit_node = successor(flows, join)
    start, = [identifier for identifier, kind in types.items() if kind == "startEvent"]
    end, = [identifier for identifier, kind in types.items() if kind == "endEvent"]
    expected = {(start, t["A"]), (t["A"], entry), (entry, split), (split, t["I"]), (split, t["M"]),
                (t["I"], t["J"]), (t["M"], t["N"]), (t["J"], join), (t["N"], join), (join, exit_node),
                (exit_node, entry), (exit_node, t["Z"]), (t["Z"], end)}
    if flows != expected or [types[node] for node in (entry, split, join, exit_node)] != ["exclusiveGateway",
            "parallelGateway", "parallelGateway", "exclusiveGateway"]:
        raise ValueError("Archived Looped-AND gateway topology differs")
    traces, edges, evidence = audit_inputs(project, "synthetic-looped-and", "BE-v3")
    attempts = [loop_attempts(labels) for labels in traces]
    pairs = [("A", "I"), ("A", "M"), ("I", "J"), ("M", "N"), ("J", "Z"), ("N", "Z"),
             *[(a, a) for a in "IJMN"]]
    return {**evidence, "bpmn": artifact, "case_count": len(traces), "repeated_cases": sum(n > 1 for n in attempts),
            "iterations_min": min(attempts), "iterations_max": max(attempts), "relations": pair_rows(traces, edges, pairs)}


def audit_complex(project, archive):
    t, types, flows, artifact = load_bpmn(archive, "14_complex_models/complex_model_001/complex_model_001.bpmn")
    for label, branches in [("D", "EHP"), ("P", "QRS")]:
        start = successor(flows, t[label])
        if types[start] != "parallelGateway" or {end for a, end in flows if a == start} != {t[b] for b in branches}:
            raise ValueError(f"Archived Complex-Model split after {label} differs")
    traces, edges, evidence = audit_inputs(project, "synthetic-complex-model", "BE")
    pairs = [("A", "A"), ("A", "B"), ("B", "C"), ("A", "J"), *(("D", b) for b in "EHP"), *(
        ("P", b) for b in "QRS")]
    return {**evidence, "bpmn": artifact, "case_count": len(traces), "relations": pair_rows(traces, edges, pairs),
            "cases_with_P_before_each_nested_branch": {
                branch: sum("P" in row and branch in row and row.index("P") < row.index(branch) for row in traces)
                for branch in "QRS"}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if file_hash(args.archive) != ARCHIVE_SHA256:
        raise ValueError("Archive SHA-256 does not match the verified author supplement")
    project = Path(__file__).resolve().parents[1]
    with ZipFile(args.archive) as archive:
        evidence = {"looped_and": audit_looped(project, archive), "complex_model": audit_complex(project, archive)}
    write_json(args.output, seal({"status": "verified", "scope": "selected BPMN relations", **evidence}))
    print(json.dumps({"status": "verified", **{key: result["case_count"] for key, result in evidence.items()}}))
