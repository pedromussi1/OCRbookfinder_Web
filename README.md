<h1 align="center">OCR BookFinder Web</h1>

<p align="center">
  <a href="https://youtu.be/U1GcrE8YPWU"><img src="https://i.imgur.com/OTuB77Y.gif" alt="YouTube Demonstration" width="800"></a>
</p>

<p align="center">Upload a photo of a book (cover or page); the app OCRs the text, searches a book database, and <b>ranks</b> the candidates to identify the title.</p>

Identifying a book from an OCR'd cover is a small **retrieval** problem: the search API
returns ~10 candidates, and the real question is *which one is correct*. This project
treats that ranking step as a measurable experiment — and along the way fixes a ranking
bug in the original code.

---

## What changed from the original

The original app worked but had real defects. This rewrite addresses each and adds an
evaluation harness so the improvements are **measured, not asserted**:

| Original | Now |
|---|---|
| `max(books, key=lambda x: x.get('relevance', 0))` — Google Books has no `relevance` field, so this always returned the **first** hit | Pluggable rankers (fuzzy / semantic / hybrid) scored against the OCR text |
| Hardcoded `/usr/bin/tesseract` (Linux-only; crashed on Windows/macOS) | Cross-platform Tesseract discovery (PATH → known dirs → `TESSERACT_CMD`) |
| Grayscale-only preprocessing | Configurable OpenCV pipeline (upscale, denoise, Otsu threshold, deskew) |
| Single search backend, strict anonymous quota (429s) | Keyless **Open Library** default + optional Google Books, with on-disk response caching |
| `debug=True` in production, no upload validation | Debug off by default, file-type/size validation, unique upload names |
| No tests, unpinned deps | `pytest` suite + pinned `requirements.txt` |

## Pipeline

```
image ──▶ preprocess (OpenCV) ──▶ OCR (Tesseract) ──▶ search ──▶ rank ──▶ best match
```

Each stage lives in its own module under [`bookfinder/`](bookfinder/) so the experiment
can swap any stage independently.

**Two search modes, chosen automatically:**
- **Cover photo** → Open Library *metadata* search on the OCR'd title/author, then fuzzy /
  semantic / hybrid ranking.
- **Interior page photo** → when metadata search finds nothing, it falls back to Open
  Library *full-text* "search inside." Because that endpoint needs error-free tokens, the
  OCR text is split into many short overlapping windows; the correct book accumulates hits
  across them, and `AggregateRanker` sums a book's editions so it beats one-off quotation
  anthologies. All keyless — no API key or quota.

## The experiment

`eval.py` runs an **ablation ladder** over a labeled dataset and reports **Recall@1**,
**Recall@5**, and **MRR** (mean reciprocal rank of the correct book).

```bash
python eval.py                 # all rungs, Open Library backend
python eval.py --rungs baseline fuzzy
python eval.py --offline       # reproduce from cached search responses
```

### Results (synthetic demo covers, n=12)

Reproduce with `python data/make_demo_covers.py && python eval.py`:

| Rung | Recall@1 | Recall@5 | MRR |
|---|---|---|---|
| grayscale-only + search-engine order *(reproduces the original bug)* | 0.58 | 1.00 | 0.74 |
| full preprocess + search-engine order | 0.58 | 1.00 | 0.74 |
| full preprocess + **fuzzy rank** | **1.00** | 1.00 | **1.00** |
| full preprocess + semantic rank | 1.00 | 1.00 | 1.00 |
| full preprocess + hybrid rank | 1.00 | 1.00 | 1.00 |

**Reading the table:** the search engine's raw order returns the *exact* book first only
58% of the time — it often surfaces a sequel or edition first (e.g. *Dune Messiah* before
*Dune*). Any of the three rankers lifts Recall@1 to 100%. This is precisely what the
original `relevance` line failed to do. On clean synthetic covers fuzzy/semantic/hybrid
tie; they diverge on **real photos**, where noisy OCR breaks exact string matching and the
semantic embedding still recovers the title (see [DATASET.md](DATASET.md)).

> **On the dataset.** The committed set is *synthetic* clean covers — enough to prove the
> pipeline end-to-end against the live API. Preprocessing shows no gain here because the
> text is already clean; its benefit appears on **real photographed covers** (glare, skew,
> noise). See [DATASET.md](DATASET.md) to collect a real set and regenerate this table —
> that is where the preprocessing and semantic rungs earn their keep.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt  # core (baseline/preprocess/fuzzy + web app)
# optional, for the semantic/hybrid rungs (pulls in PyTorch):
pip install -r requirements-semantic.txt
```

Tesseract must be installed separately (`winget install tesseract`,
`brew install tesseract`, or `apt install tesseract-ocr`). The app finds it on PATH; set
`TESSERACT_CMD` to override.

## Run the app

```bash
python app.py                    # http://127.0.0.1:5000/
```

Choose the ranker via `BOOKFINDER_RANKER` (`fuzzy` default, or `semantic`/`hybrid`).

## Project layout

```
bookfinder/        reusable pipeline package
  preprocess.py    configurable OpenCV pipeline
  ocr.py           Tesseract wrapper + query normalization
  books_api.py     Open Library / Google Books backends with caching
  ranking.py       baseline / fuzzy / semantic / hybrid rankers
  pipeline.py      orchestration (BookFinder)
eval.py            ablation experiment (Recall@k, MRR)
data/              labels.csv + demo cover generator
tests/             pytest suite
app.py             Flask web app
```

## Tests

```bash
python -m pytest -q
```

## Known limitations

- Full-text page identification depends on the book being in Open Library's scanned
  full-text index; very obscure or unscanned books may not be found.
- Heavy OCR errors reduce the number of clean windows that match; more of the page in frame
  (more windows) makes identification more robust.
- Synthetic demo covers overstate the easy case; real-photo numbers will be lower and are
  the honest measure.
