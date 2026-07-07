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

    def identify(self, image_path: str) -> BookResult:
        raw_text = extract_text(image_path, self.config.preprocess)
        query = normalize_query(raw_text)
        candidates = self.client.search(query)
        ranked = self.ranker.rank(query, candidates)
        return BookResult(raw_text=raw_text, query=query, ranked=ranked)
