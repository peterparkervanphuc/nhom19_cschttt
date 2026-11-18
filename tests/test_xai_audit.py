from copy import deepcopy

import pytest

from nhom19_process_xai.evaluate.metrics import summary
from nhom19_process_xai.evaluate.xai import METRICS
from scripts.audit_xai_evaluation import verify_method


def hand_method():
    row = {
        "prefix_id": "p", "case_id": "c", "universe": ["A", "B", "C"],
        "common_importance": [.5, .3, .2], "explanation_importance": [.2, .3, .5],
        "projected_edges": [["A", "X"], ["A", "Y"], ["B", "Y"]],
        "completeness_counts": {"tp": 1, "fp": 1, "fn": 2,
                                "precision": .5, "recall": 1 / 3, "f1": .4},
        "consistency_gate": {"prediction_similarity": .9, "feature_similarity": .8,
                             "jaccard": .5, "eligible": True, "both_empty": False},
        "variant_records": [
            {"variant_id": "a", "similarity": .8, "jaccard": .5,
             "score": .7, "cohort": "near", "both_empty": False},
            {"variant_id": "b", "similarity": .6, "jaccard": 0.,
             "score": .4, "cohort": "far", "both_empty": False}],
        "values": {"correctness": -1., "completeness_precision": .5,
                   "completeness_recall": 1 / 3, "completeness_f1": .4,
                   "consistency": .6, "continuity": .7, "contrastivity": .4,
                   "compactness_rules": 2, "compactness_rhs": 1.5},
        "null_reasons": dict.fromkeys(METRICS),
    }
    return summarize(row)


def summarize(row):
    return {"records": [row], "summary": {
        name: {**summary([value]), "null_reasons": {} if value is not None else
               {row["null_reasons"][name]: 1}}
        for name, value in row["values"].items()}}


def test_xai_audit_accepts_hand_arithmetic_and_ties():
    method = hand_method()
    verify_method(method, {"p": "c"})
    row = deepcopy(method["records"][0])
    row["common_importance"] = [1., 1., 2.]
    row["explanation_importance"] = [1., 2., 2.]
    row["values"]["correctness"] = .5
    verify_method(summarize(row), {"p": "c"})
    row["common_importance"] = [1., 1., 1.]
    row["values"]["correctness"] = None
    row["null_reasons"]["correctness"] = "undefined_importance_or_rank"
    verify_method(summarize(row), {"p": "c"})


@pytest.mark.parametrize("metric", METRICS)
def test_xai_audit_rejects_self_consistent_wrong_metric(metric):
    row = hand_method()["records"][0]
    row["values"][metric] += .01
    # Recompute the aggregate too: checking only aggregate consistency misses this.
    with pytest.raises(ValueError, match="arithmetic"):
        verify_method(summarize(row), {"p": "c"})


def test_xai_audit_rejects_wrong_variant_cohort():
    method = hand_method()
    method["records"][0]["variant_records"][0]["cohort"] = "far"
    with pytest.raises(ValueError, match="cohort"):
        verify_method(method, {"p": "c"})


def test_xai_audit_accepts_empty_graph_and_undefined_metrics():
    row = hand_method()["records"][0]
    row.update(projected_edges=[], common_importance=None, explanation_importance=None,
               completeness_counts={"tp": 0, "fp": 0, "fn": 0,
                                    "precision": None, "recall": None, "f1": None},
               variant_records=[{"variant_id": "a", "similarity": .6, "jaccard": 1.,
                                 "score": .6, "cohort": "far", "both_empty": True}],
               consistency_gate={"prediction_similarity": .9, "feature_similarity": None,
                                 "jaccard": 1., "eligible": False, "both_empty": True})
    row["values"] = dict.fromkeys(METRICS)
    row["values"].update(contrastivity=.6, compactness_rules=0)
    row["null_reasons"] = {name: "undefined" if value is None else None
                           for name, value in row["values"].items()}
    verify_method(summarize(row), {"p": "c"})


@pytest.mark.parametrize("field", ["score", "eligible"])
def test_xai_audit_rejects_corrupted_intermediate(field):
    method = hand_method()
    row = method["records"][0]
    if field == "score":
        row["variant_records"][0]["score"] = .8
    else:
        row["consistency_gate"]["eligible"] = False
    with pytest.raises(ValueError):
        verify_method(method, {"p": "c"})
