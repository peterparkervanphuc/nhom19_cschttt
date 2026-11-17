import math

import numpy as np
import pytest

from nhom19_process_xai.evaluate.metrics import (
    agreement, compactness, completeness, cosine_similarity, jaccard,
    jsd, predictive_metrics, summary, tau_b, tvd,
)
from nhom19_process_xai.graphs.relations import merge_prune, project


def test_divergence_hand_values_and_support():
    assert jsd([1, 0], [0, 1]) == pytest.approx(math.log(2), abs=1e-12)
    assert tvd([1, 0], [0, 1]) == 1
    assert jsd([.2, .8], [.2, .8]) == 0
    assert tvd([.8, .2], [.6, .4]) == pytest.approx(.2, abs=1e-12)
    with pytest.raises(ValueError):
        jsd([0, 0], [0, 0])
    with pytest.raises(ValueError):
        tvd([1, 0], [1])
    with pytest.raises(ValueError):
        jsd([np.nan, 0], [1, 0])


def test_cosine_and_ranks():
    assert cosine_similarity([1, 0], [.8, .6]) == .8
    assert cosine_similarity([0, 0], [1, 0]) is None
    assert tau_b([1, 1, 2], [1, 2, 3]) == pytest.approx(2 / math.sqrt(6))
    assert tau_b([1, 1], [1, 2]) is None
    assert tau_b([1, 2, 3], [3, 2, 1]) == -1


def test_fidelity_and_compactness():
    result = completeness({"A", "B"}, {"B", "C", "D"})
    assert result["precision"] == 1/3
    assert result["recall"] == .5
    assert result["f1"] == .4
    assert completeness(set(), set())["f1"] is None
    assert compactness({("A", "A"), ("A", "B"), ("B", "C")}) == {"rule_count": 2, "mean_rhs": 1.5}
    assert compactness(set()) == {"rule_count": 0, "mean_rhs": None}
    assert jaccard(set(), set()) == 1
    assert jaccard({("A", "B")}, {("B", "A")}) == 0
    assert agreement(.9, .5) == .6


def test_prediction_unseen_output_and_summary():
    result = predictive_metrics(["A", "B", "D"], ["A", "A", "B"])
    assert result["accuracy"] == 1/3
    assert result["precision"] == 1/6
    assert result["recall"] == 1/3
    assert result["f1"] == pytest.approx(2/9)
    aggregate = summary([.2, .4, None])
    assert aggregate["sd"] == pytest.approx(math.sqrt(.02))
    assert aggregate["coverage"] == 2/3
    assert summary([])["coverage"] is None
    assert summary([0])["sd"] is None


def test_pruning_simultaneous_and_orientation():
    edges = {("A", "A"), ("A", "B"), ("B", "C"), ("A", "C"), ("A", "D"), ("D", "C")}
    remaining, removed = merge_prune(set(), edges)
    assert remaining == edges - {("A", "C")}
    assert removed == [{"source": "A", "target": "C", "witnesses": ["B", "D"]}]
    complete = {(a, b) for a in "ABC" for b in "ABC" if a != b}
    assert merge_prune(set(), complete)[0] == set()
    assert merge_prune(set(), set()) == (set(), [])
    assert project(edges, ["B"]) == {("B", "C")}
