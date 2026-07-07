"""Book-search backends with on-disk caching.

Two interchangeable providers, both returning a common ``Candidate`` list:

  * ``OpenLibraryClient`` -- openlibrary.org, keyless and generous; the default.
  * ``GoogleBooksClient`` -- Google Books; richer descriptions but a strict anonymous
                             per-IP quota (429s). Set ``GOOGLE_BOOKS_API_KEY`` to lift it.

Caching (keyed by provider + query) makes the experiment reproducible and keeps us well
under rate limits on re-runs. Set ``offline=True`` to serve only from cache.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass

import requests

# Cache location; override with BOOKFINDER_CACHE_DIR (e.g. a writable /tmp path when hosted).
_CACHE_DIR = os.environ.get("BOOKFINDER_CACHE_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "cache"
)
# Search APIs reject/ignore very long queries; a distinctive prefix is enough.
_MAX_QUERY_CHARS = 300


@dataclass
class Candidate:
    """A normalized book-search result, provider-agnostic."""

    title: str
    subtitle: str
    authors: list[str]
    description: str
    volume_id: str
    relevance: float = 0.0  # backend's own score (used by full-text aggregation)

    @property
    def text_blob(self) -> str:
        """Title + subtitle + authors — the fields a cover/title query should match."""
        return " ".join(filter(None, [self.title, self.subtitle, " ".join(self.authors)]))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Candidate":
        # Tolerate cache files written before a field existed / was removed.
        fields = {"title", "subtitle", "authors", "description", "volume_id", "relevance"}
        return cls(**{k: v for k, v in d.items() if k in fields})


class SearchClient:
    """Base client: handles caching + offline mode. Subclasses implement ``_fetch``."""

    provider = "base"

    def __init__(self, cache_dir: str = _CACHE_DIR, offline: bool = False, max_results: int = 10):
        self.cache_dir = cache_dir
        self.offline = offline
        self.max_results = max_results
        os.makedirs(self.cache_dir, exist_ok=True)

    def _cache_path(self, query: str) -> str:
        raw = f"{self.provider}:{self.max_results}:{query}"
        key = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return os.path.join(self.cache_dir, f"{self.provider}_{key}.json")

    def search(self, query: str) -> list[Candidate]:
        query = query[:_MAX_QUERY_CHARS].strip()
        if not query:
            return []

        path = self._cache_path(query)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                return [Candidate.from_dict(d) for d in json.load(fh)]

        if self.offline:
            raise LookupError(f"Cache miss in offline mode for query: {query!r}")

        candidates = self._fetch(query)
        self._write_cache(path, candidates)
        return candidates

    def _write_cache(self, path: str, candidates: list[Candidate]) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)  # survive runtime /tmp cleanup
        with open(path, "w", encoding="utf-8") as fh:
            json.dump([c.to_dict() for c in candidates], fh)

    def _fetch(self, query: str) -> list[Candidate]:
        raise NotImplementedError


class OpenLibraryClient(SearchClient):
    """openlibrary.org search — keyless, no strict per-IP quota."""

    provider = "openlibrary"
    _URL = "https://openlibrary.org/search.json"

    def _fetch(self, query: str) -> list[Candidate]:
        params = {
            "q": query,
            "limit": self.max_results,
            "fields": "title,subtitle,author_name,key,first_sentence",
        }
        response = requests.get(self._URL, params=params, timeout=20)
        response.raise_for_status()
        docs = response.json().get("docs", [])
        out = []
        for doc in docs:
            first = doc.get("first_sentence")
            description = first[0] if isinstance(first, list) and first else (first or "")
            out.append(
                Candidate(
                    title=doc.get("title", ""),
                    subtitle=doc.get("subtitle", ""),
                    authors=doc.get("author_name", []) or [],
                    description=description,
                    volume_id=doc.get("key", ""),
                )
            )
        return out


class GoogleBooksClient(SearchClient):
    """Google Books search — richer data, strict anonymous quota (set an API key)."""

    provider = "google"
    _URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")

    def _fetch(self, query: str, retries: int = 4) -> list[Candidate]:
        params = {"q": query, "maxResults": self.max_results}
        if self.api_key:
            params["key"] = self.api_key
        delay = 2.0
        items = []
        for attempt in range(retries):
            response = requests.get(self._URL, params=params, timeout=15)
            if response.status_code == 429 and attempt < retries - 1:
                time.sleep(delay)
                delay *= 2  # exponential backoff: 2s, 4s, 8s
                continue
            response.raise_for_status()
            items = response.json().get("items", [])
            break
        out = []
        for item in items:
            info = item.get("volumeInfo", {})
            out.append(
                Candidate(
                    title=info.get("title", ""),
                    subtitle=info.get("subtitle", ""),
                    authors=info.get("authors", []),
                    description=info.get("description", ""),
                    volume_id=item.get("id", ""),
                )
            )
        return out


class OpenLibraryFullTextClient(SearchClient):
    """openlibrary.org "search inside" — full-text search over scanned books.

    Unlike metadata search, this matches the *contents* of books, so a photo of an interior
    prose page can be traced back to its book. Keyless.

    The endpoint does strict AND/phrase matching, so a single OCR error in a long query
    zeroes the results. To stay robust, we split the OCR text into many short overlapping
    windows and search each: error-free windows still match, and the correct book
    accumulates across them. Pair with the AggregateRanker, which sums a book's editions
    (and window hits) to outweigh one-off quotation anthologies.
    """

    provider = "openlibrary_fulltext"
    _URL = "https://openlibrary.org/search/inside.json"

    _WINDOW_SIZE = 6        # words per search window
    _WINDOW_STRIDE = 4      # overlap step between windows
    _MAX_WINDOWS = 15       # cap API calls per identification
    _MAX_WORDS = 120        # only scan this far into the page
    _CONCURRENCY = 8        # window queries to run in parallel (they are independent I/O)

    def search(self, query: str) -> list[Candidate]:
        """Windowed full-text search: many short queries, run concurrently."""
        words = query.split()
        if not words:
            return []

        windows: list[str] = []
        end = min(len(words), self._MAX_WORDS)
        i = 0
        while i + self._WINDOW_SIZE <= end and len(windows) < self._MAX_WINDOWS:
            windows.append(" ".join(words[i:i + self._WINDOW_SIZE]))
            i += self._WINDOW_STRIDE
        if not windows:  # text shorter than one window
            windows = [" ".join(words)]

        # The window queries are independent network calls, so fan them out; this turns
        # ~15 sequential requests (10+ seconds) into a couple of concurrent batches.
        out: list[Candidate] = []
        with ThreadPoolExecutor(max_workers=min(self._CONCURRENCY, len(windows))) as pool:
            for result in pool.map(self._search_window, windows):
                out.extend(result)
        return out

    def _search_window(self, window: str) -> list[Candidate]:
        """Search one window, with per-window caching. Skips (not fails) on offline miss."""
        path = self._cache_path(window)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                return [Candidate.from_dict(d) for d in json.load(fh)]
        if self.offline:
            return []  # resilient: a partial cache still yields an aggregate answer
        candidates = self._fetch(window)
        self._write_cache(path, candidates)
        return candidates

    def _fetch(self, window: str) -> list[Candidate]:
        response = requests.get(self._URL, params={"q": window}, timeout=30)
        response.raise_for_status()
        hits = response.json().get("hits", {}).get("hits", [])
        out = []
        for hit in hits[: max(self.max_results, 20)]:
            fields = hit.get("fields", {})
            title = (fields.get("meta_title") or [""])[0]
            authors = fields.get("meta_creatorSorter") or []
            identifier = (fields.get("identifier") or [""])[0]
            highlight = hit.get("highlight", {}).get("text", [])
            snippet = highlight[0] if highlight else ""
            out.append(
                Candidate(
                    title=title,
                    subtitle="",
                    authors=list(authors),
                    description=snippet,
                    volume_id=identifier,
                    relevance=float(hit.get("_score", 0.0)),
                )
            )
        return out


PROVIDERS: dict[str, type[SearchClient]] = {
    "openlibrary": OpenLibraryClient,
    "openlibrary_fulltext": OpenLibraryFullTextClient,
    "google": GoogleBooksClient,
}


def make_client(provider: str = "openlibrary", **kwargs) -> SearchClient:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider {provider!r}; choose from {sorted(PROVIDERS)}")
    return PROVIDERS[provider](**kwargs)
