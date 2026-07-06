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
from dataclasses import asdict, dataclass

import requests

_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
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

    @property
    def text_blob(self) -> str:
        """Title + subtitle + authors — the fields a cover/title query should match."""
        return " ".join(filter(None, [self.title, self.subtitle, " ".join(self.authors)]))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Candidate":
        return cls(**d)


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
        with open(path, "w", encoding="utf-8") as fh:
            json.dump([c.to_dict() for c in candidates], fh)
        return candidates

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


PROVIDERS: dict[str, type[SearchClient]] = {
    "openlibrary": OpenLibraryClient,
    "google": GoogleBooksClient,
}


def make_client(provider: str = "openlibrary", **kwargs) -> SearchClient:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider {provider!r}; choose from {sorted(PROVIDERS)}")
    return PROVIDERS[provider](**kwargs)
