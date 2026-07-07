"""Eval metric helpers: correctness matching and rank-of-correct."""

from bookfinder.books_api import Candidate
from bookfinder.ranking import ScoredCandidate
from eval import is_correct, rank_of_correct


def test_is_correct_fuzzy_title_match():
    assert is_correct(Candidate("Dune", "", ["Frank Herbert"], "", "x"), "Dune")
    assert is_correct(Candidate("Dune (Deluxe Edition)", "", [], "", "x"), "Dune")
    assert not is_correct(Candidate("The Iliad", "", [], "", "x"), "Dune")


def test_rank_of_correct_finds_position():
    ranked = [
        ScoredCandidate(Candidate("Wrong One", "", [], "", "a"), 0.9),
        ScoredCandidate(Candidate("Dune", "", [], "", "b"), 0.8),
    ]
    assert rank_of_correct(ranked, "Dune") == 2


def test_rank_of_correct_absent_returns_none():
    ranked = [ScoredCandidate(Candidate("Wrong", "", [], "", "a"), 0.9)]
    assert rank_of_correct(ranked, "Dune") is None
