"""Full-text aggregation ranking and windowed search (no network)."""

from bookfinder.books_api import Candidate, OpenLibraryFullTextClient
from bookfinder.ranking import AggregateRanker


def test_aggregate_sums_editions_over_one_off_anthology():
    # The real book appears as 3 editions; an anthology appears once with a high score.
    cands = [
        Candidate("Famous First Lines", "", ["Anon"], "", "a1", relevance=200.0),
        Candidate("Dune", "", ["Frank Herbert"], "", "d1", relevance=130.0),
        Candidate("Dune", "", ["Frank Herbert"], "", "d2", relevance=120.0),
        Candidate("The Illustrated Dune", "", ["Frank Herbert"], "", "d3", relevance=110.0),
    ]
    ranked = AggregateRanker().rank("some prose", cands)
    # "dune" group (130+120) outweighs the 200-point anthology.
    assert ranked[0].candidate.title == "Dune"
    assert ranked[0].score == 250.0


def test_aggregate_picks_highest_scoring_representative():
    cands = [
        Candidate("Dune", "", ["Frank Herbert"], "", "d2", relevance=120.0),
        Candidate("Dune", "", ["Frank Herbert"], "", "d1", relevance=130.0),
    ]
    ranked = AggregateRanker().rank("prose", cands)
    assert ranked[0].candidate.volume_id == "d1"  # the higher-scoring edition represents


def test_fulltext_offline_missing_windows_return_empty():
    # Offline with an empty cache: windows are skipped, not raised — resilient by design.
    client = OpenLibraryFullTextClient(offline=True)
    assert client.search("one two three four five six seven eight") == []


def test_fulltext_request_failure_is_isolated(monkeypatch):
    # A failing/slow window request must not crash the whole batch.
    import requests

    client = OpenLibraryFullTextClient()

    def boom(window):
        raise requests.RequestException("network down")

    monkeypatch.setattr(client, "_fetch", boom)
    # All windows "fail" but search returns cleanly (empty), never raises.
    assert client.search("one two three four five six seven eight nine ten") == []
