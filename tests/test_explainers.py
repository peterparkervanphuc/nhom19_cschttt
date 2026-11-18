import numpy as np
import pytest

from nhom19_process_xai.explain.algorithms import ae_contribution, ae_contexts, ae_matrices, be_masks
from nhom19_process_xai.model.predictor import Prediction


def test_be_sampling_repeats_and_long_prefixes():
    assert be_masks(2, "same") == [1, 2, 3]
    left = be_masks(100, "same")
    assert left == be_masks(100, "same")
    assert len(left) == len(set(left)) == 20
    assert max(left) > 2**64


def test_four_branches_and_repeated_mass_fixture():
    near = ae_contribution(.8, .76, .15, .45, .30)
    far = ae_contribution(.8, .60, .15, .45, .30)
    assert near == {"masked": -.12, "visible": .24}
    assert far["masked"] == .12
    assert far["visible"] == pytest.approx(.03)
    assert sum(far.values()) == pytest.approx(.15)
    assert ae_contribution(.8, .76, 0, 0, 0) == {"masked": 0, "visible": 0}


def context(scenario, scores):
    return {"scenario": scenario, "votes": [{"target": "T", "source": source, "score": score}
                                            for source, score in scores.items()]}


def test_signed_normalization_cancellation_threshold_or():
    result = ae_matrices([context("most", {"A": 1., "B": -.9})], ["T"], ["A", "B"])
    assert result["edges"] == [("A", "T")]
    assert result["matrices"]["most"]["normalized"][0] == pytest.approx([10, -9])
    canceled = ae_matrices([context("most", {"A": 1., "B": -1.})], ["T"], ["A", "B"])
    assert canceled["edges"] == []
    assert canceled["matrices"]["most"]["suppressed_row_reasons"] == ["cancellation"]
    result = ae_matrices([context("most", {"A": 1., "B": 9.}),
                          context("few", {"A": 9., "B": 1.})], ["T"], ["A", "B"])
    assert result["matrices"]["most"]["adjacency"] == [[False, True]]
    assert result["edges"] == [("A", "T"), ("B", "T")]


def test_occurrence_subsets_and_zero_relevant_positions():
    class FixedPredictor:
        def predict(self, labels):
            valid = np.array([label is not None for label in labels])
            mass = np.array([.15, .40, .45]) * valid
            matrix = np.tile(mass / mass.sum() if mass.sum() else mass, (3, 1))
            matrix[~valid] = 0
            return Prediction(np.array([.8, .2]), matrix[None], matrix[None], valid, "fixture", ("T", "U"))
    prefix = {"prefix_id": "p", "activities": ["A", "B", "A"], "occurrence_ids": [10, 11, 12]}
    rows = list(ae_contexts(FixedPredictor(), prefix, {"relevant": ["A"], "predictions": ["T"]}))
    assert len(rows) == 8
    assert len({(row["scenario"], row["subset"]) for row in rows}) == 8
    mixed = next(row for row in rows if row["scenario"] == "few" and row["subset"] == "1")
    assert mixed["masked_positions"] == [0]
    a_votes = [vote for vote in mixed["votes"] if vote["source"] == "A"]
    assert {tuple(vote["occurrence_ids"]) for vote in a_votes} == {(10,), (12,)}
    assert len(list(ae_contexts(FixedPredictor(), prefix, {"relevant": [], "predictions": []}))) == 2
