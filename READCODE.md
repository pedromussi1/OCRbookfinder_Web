# Code Breakdown

OCR BookFinder identifies a book from a photo of its **cover** or an interior **page**. The
logic lives in the `bookfinder/` package; `app.py` is a thin Flask layer, and `eval.py` is a
measured retrieval experiment.

## Pipeline

```
image ─▶ preprocess (OpenCV) ─▶ OCR (Tesseract) ─▶ search ─▶ rank ─▶ best match
```

## `bookfinder/preprocess.py`
A configurable OpenCV pipeline (upscale → denoise → Otsu threshold → deskew), each step
toggleable via `PreprocessConfig`, so the experiment can measure each step's effect. The
`baseline()` config is grayscale-only (the original behavior).

## `bookfinder/ocr.py`
Runs Tesseract (`--oem 3 --psm 6`) on the preprocessed image and normalizes the text into a
search query. Tesseract is located cross-platform (PATH → common install dirs → `TESSERACT_CMD`).

## `bookfinder/books_api.py`
Search backends returning a common `Candidate` list, with on-disk caching:
- **`OpenLibraryClient`** — keyless metadata (title/author) search, the default for covers.
- **`OpenLibraryFullTextClient`** — full-text "search inside" for interior pages. Because
  that endpoint needs error-free tokens, the OCR text is split into short overlapping
  windows queried concurrently.
- **`GoogleBooksClient`** — optional (needs `GOOGLE_BOOKS_API_KEY`).

## `bookfinder/ranking.py`
Orders candidates against the OCR text: `baseline` (search-engine order), `fuzzy` (RapidFuzz),
`semantic` (sentence-transformers), `hybrid`, and `aggregate` (sums a book's editions/window
hits for the full-text page path). This is what fixed the original `relevance` bug.

## `bookfinder/pipeline.py`
`BookFinder.identify()` ties it together: preprocess → OCR → metadata search (covers), and
for a long, page-like query it falls back to full-text search + edition aggregation.

## `app.py` and `eval.py`
`app.py` handles the upload and renders the match. `eval.py` runs the ablation ladder over a
labeled set and reports **Recall@1/@5 + MRR** — the project's measured result.
