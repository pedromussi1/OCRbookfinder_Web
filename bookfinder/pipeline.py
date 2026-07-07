"""End-to-end pipeline: image -> preprocess -> OCR -> Google Books -> ranked candidates."""

from __future__ import annotations

from dataclasses import dataclass, field

from .books_api import Candidate, SearchClient, make_client
from .ocr import extract_text, normalize_query
from .preprocess import PreprocessConfig
from .ranking import BaseRanker, RANKERS, ScoredCandidate


@dataclass
class PipelineConfig:
    """Selects the preprocessing and ranking used for a run.

    ``ranker`` may be a ranker name ('baseline'|'fuzzy'|'semantic'|'hybrid') or an
    instance. ``preprocess`` defaults to the full OpenCV pipeline.
    """

    preprocess: PreprocessConfig = field(default_factory=PreprocessConfig)
    ranker: str | BaseRanker = "fuzzy"
    provider: str = "openlibrary"   # keyless default; 'google' needs GOOGLE_BOOKS_API_KEY
    offline: bool = False
    max_results: int = 10
    # When metadata search finds nothing (e.g. a photo of an interior page rather than a
    # cover), fall back to full-text "search inside" + edition aggregation.
    fulltext_fallback: bool = True


@dataclass
class BookResult:
    """The pipeline's output for one image."""

    raw_text: str
    query: str
    ranked: list[ScoredCandidate]

    @property
    def best(self) -> Candidate | None:
        return self.ranked[0].candidate if self.ranked else None

    def summary(self) -> str:
        """Human-readable one-liner for the top match (used by the web app)."""
        if not self.best:
            return "No matches found."
        authors = ", ".join(self.best.authors) if self.best.authors else "Unknown author"
        return f"{self.best.title}, Authors: {authors}"


def _resolve_ranker(ranker: str | BaseRanker) -> BaseRanker:
    if isinstance(ranker, BaseRanker):
        return ranker
    if ranker not in RANKERS:
        raise ValueError(f"Unknown ranker {ranker!r}; choose from {sorted(RANKERS)}")
    return RANKERS[ranker]()


class BookFinder:
    """Reusable pipeline object; construct once, call ``identify`` per image."""

    def __init__(self, config: PipelineConfig | None = None, client: SearchClient | None = None):
        self.config = config or PipelineConfig()
        self.ranker = _resolve_ranker(self.config.ranker)
        self.client = client or make_client(
            self.config.provider, offline=self.config.offline, max_results=self.config.max_results
        )
        # Built lazily on first fallback so the common (cover) path pays nothing.
        self._fulltext_client: SearchClient | None = None

    def _fulltext(self) -> SearchClient:
        if self._fulltext_client is None:
            self._fulltext_client = make_client(
                "openlibrary_fulltext", offline=self.config.offline,
                max_results=self.config.max_results,
            )
        return self._fulltext_client

    # A cover OCRs to a few words (title + author); an interior page OCRs to a long
    # paragraph. Past this many words we treat it as a page and skip the (futile, ~1s)
    # metadata search, going straight to full-text.
    _PAGE_WORD_THRESHOLD = 20

    def identify(self, image_path: str) -> BookResult:
        raw_text = extract_text(image_path, self.config.preprocess)
        query = normalize_query(raw_text)

        looks_like_page = len(query.split()) > self._PAGE_WORD_THRESHOLD

        # Covers: metadata (title/author) search. Skip it for obvious pages to save a round-trip.
        candidates = [] if looks_like_page else self.client.search(query)
        if candidates:
            ranked = self.ranker.rank(query, candidates)
        elif self.config.fulltext_fallback:
            # A page (or a cover with no metadata hit): full-text search + edition
            # aggregation so the real book beats one-off quotation anthologies.
            fulltext = self._fulltext().search(query)
            ranked = _resolve_ranker("aggregate").rank(query, fulltext)
        else:
            ranked = []
        return BookResult(raw_text=raw_text, query=query, ranked=ranked)
