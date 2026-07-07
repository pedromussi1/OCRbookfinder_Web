"""Ranking logic, verified with fixture candidates (no network)."""

from bookfinder.books_api import Candidate
from bookfinder.ranking import BaselineRanker, FuzzyRanker


def _candidates():
    # Deliberately put the correct book LAST so a real ranker must reorder it up.
    return [
        Candidate("Cooking with Dune Sand", "", ["A. Nother"], "", "id1"),
        Candidate("Iliad Study Guide", "", ["Cliff"], "", "id2"),
        Candidate("Dune", "", ["Frank Herbert"], "", "id3"),
    ]


def test_baseline_preserves_google_order():
    ranked = BaselineRanker().rank("dune frank herbert", _candidates())
    assert [sc.candidate.volume_id for sc in ranked] == ["id1", "id2", "id3"]


def test_fuzzy_ranks_true_title_first():
    ranked = FuzzyRanker().rank("dune frank herbert atreides arrakis", _candidates())
    assert ranked[0].candidate.title == "Dune"
    # Scores must be sorted descending.
    scores = [sc.score for sc in ranked]
    assert scores == sorted(scores, reverse=True)


def test_empty_candidates_is_safe():
    assert FuzzyRanker().rank("anything", []) == []
