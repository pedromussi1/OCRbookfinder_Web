"""Ranking strategies for ordering Google Books candidates against OCR text.

This is the ablation ladder from the experiment:

  * ``BaselineRanker``  -- Google's own order (reproduces the original app's behavior,
                           whose ``max(..., key=lambda x: x.get('relevance', 0))`` bug
                           always returned the first hit).
  * ``FuzzyRanker``     -- RapidFuzz token-set ratio between the OCR text and each
                           candidate's title/author blob.
  * ``SemanticRanker``  -- cosine similarity of sentence-transformer embeddings.
  * ``HybridRanker``    -- weighted blend of fuzzy + semantic.

Each ranker implements ``score(query, candidates) -> List[float]`` (aligned to the
input order); the shared ``rank`` then sorts. Scoring in place keeps the hybrid blend
straightforward — no index bookkeeping.
"""

from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz

from .books_api import Candidate


@dataclass
class ScoredCandidate:
    candidate: Candidate
    score: float


def _normalize(scores: list[float]) -> list[float]:
    """Min-max scale to [0, 1]; flat inputs map to all-zeros."""
    if not scores:
        return []
    lo, hi = min(scores), max(scores)
    if hi - lo < 1e-9:
        return [0.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


class BaseRanker:
    """Sort candidates by ``score`` (best first). Subclasses implement ``score``."""

    name = "base"

    def score(self, query: str, candidates: list[Candidate]) -> list[float]:
        raise NotImplementedError

    def rank(self, query: str, candidates: list[Candidate]) -> list[ScoredCandidate]:
        scores = self.score(query, candidates)
        scored = [ScoredCandidate(c, s) for c, s in zip(candidates, scores)]
        scored.sort(key=lambda sc: sc.score, reverse=True)
        return scored


class BaselineRanker(BaseRanker):
    """Keep Google Books' own ordering. Mirrors the original (buggy) 'first hit' behavior."""

    name = "baseline"

    def score(self, query: str, candidates: list[Candidate]) -> list[float]:
        n = len(candidates)
        return [float(n - i) for i in range(n)]  # descending -> preserves incoming order


class FuzzyRanker(BaseRanker):
    """Rank by fuzzy string similarity of the OCR text to each candidate's title blob."""

    name = "fuzzy"

    def score(self, query: str, candidates: list[Candidate]) -> list[float]:
        return [float(fuzz.token_set_ratio(query, c.text_blob)) for c in candidates]


class SemanticRanker(BaseRanker):
    """Rank by cosine similarity of sentence-transformer embeddings.

    The model is loaded lazily so the rest of the package (and the web app) work
    without torch/sentence-transformers installed until this rung is actually used.
    """

    name = "semantic"

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # lazy, heavy import

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def score(self, query: str, candidates: list[Candidate]) -> list[float]:
        if not candidates:
            return []
        from sentence_transformers import util

        model = self._get_model()
        blobs = [c.text_blob for c in candidates]
        q_emb = model.encode(query, convert_to_tensor=True, normalize_embeddings=True)
        c_emb = model.encode(blobs, convert_to_tensor=True, normalize_embeddings=True)
        sims = util.cos_sim(q_emb, c_emb)[0]
        return [float(sims[i]) for i in range(len(candidates))]


class HybridRanker(BaseRanker):
    """Weighted blend of min-max-normalized fuzzy and semantic scores."""

    name = "hybrid"

    def __init__(self, fuzzy_weight: float = 0.5, model_name: str = "all-MiniLM-L6-v2"):
        self.fuzzy_weight = fuzzy_weight
        self._fuzzy = FuzzyRanker()
        self._semantic = SemanticRanker(model_name)

    def score(self, query: str, candidates: list[Candidate]) -> list[float]:
        if not candidates:
            return []
        fuzzy = _normalize(self._fuzzy.score(query, candidates))
        semantic = _normalize(self._semantic.score(query, candidates))
        w = self.fuzzy_weight
        return [w * f + (1 - w) * s for f, s in zip(fuzzy, semantic)]


RANKERS: dict[str, type[BaseRanker]] = {
    "baseline": BaselineRanker,
    "fuzzy": FuzzyRanker,
    "semantic": SemanticRanker,
    "hybrid": HybridRanker,
}
