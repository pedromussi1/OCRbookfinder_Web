# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-07-07

### Added
- Redesigned web UI: responsive, dark-mode-aware layout with drag-and-drop upload, image
  preview, a loading state during search, and a cleaner results page.
- `Dockerfile` (+ `.dockerignore`) for containerized hosting (Hugging Face Spaces / any
  Docker host); installs Tesseract and serves via gunicorn on port 7860.
- `BOOKFINDER_CACHE_DIR` environment override for the response cache (writable path when hosted).

### Changed
- The upload directory is now ensured at import time so the app works under gunicorn.

## [2.1.0] - 2026-07-06

### Added
- **Interior-page identification** via Open Library full-text "search inside", used
  automatically when metadata search finds no cover match. The OCR text is split into short
  overlapping windows (robust to OCR errors, which otherwise zero a full-text query), and a
  new `AggregateRanker` sums a book's editions/window-hits so the real book outranks
  quotation anthologies. Keyless — no API key or quota.
- `openlibrary_fulltext` search provider and `aggregate` ranker.

### Fixed
- Regression from 2.0.0: photos of interior book pages returned "No matches found" because
  the default metadata backend only matches titles/authors. Page photos now resolve again
  (verified on Dune, The Iliad, and The Art of War pages).

## [2.0.0] - 2026-07-06

Complete rewrite: from a ~70-line single-file script into a reusable pipeline plus a
measured retrieval experiment.

### Added
- `bookfinder/` pipeline package: preprocess (OpenCV) → OCR (Tesseract) → search → rank.
- Pluggable rankers: `baseline`, `fuzzy` (RapidFuzz), `semantic` (sentence-transformers),
  and `hybrid`.
- `eval.py` ablation harness reporting **Recall@1 / Recall@5 / MRR**.
- Keyless **Open Library** search backend (plus optional Google Books) with on-disk caching.
- Configurable OpenCV preprocessing (upscale, denoise, Otsu threshold, deskew).
- `pytest` suite (9 tests), pinned `requirements.txt` (+ optional `requirements-semantic.txt`).
- `DATASET.md` collection guide and a synthetic demo-cover generator.

### Fixed
- **Broken ranking**: `max(books, key=lambda x: x.get('relevance', 0))` referenced a field
  that does not exist, so it always returned the search engine's first hit. Real ranking now
  lifts exact-match Recall@1 from ~58% to 100% on the demo set.
- Hardcoded Linux Tesseract path (`/usr/bin/tesseract`) → cross-platform discovery.
- `debug=True` in production; added upload type/size validation and unique filenames.

### Changed
- README rewritten around the experiment, with an honest results table and documented
  limitations (interior-page images, synthetic demo covers).

[2.2.0]: https://github.com/pedromussi1/OCRbookfinder_Web/releases/tag/v2.2.0
[2.1.0]: https://github.com/pedromussi1/OCRbookfinder_Web/releases/tag/v2.1.0
[2.0.0]: https://github.com/pedromussi1/OCRbookfinder_Web/releases/tag/v2.0.0
