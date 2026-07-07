# Building a real evaluation dataset

The committed dataset (`data/labels.csv` → `data/demo_covers/`) is **synthetic**: clean
rendered covers that prove the pipeline works but make OCR trivially easy. The honest
measurement — where preprocessing and semantic ranking actually earn their keep — comes
from **real photographed covers**. This guide is how to build that set.

## What to photograph

- **Book/manga covers**, not interior pages. This tool identifies a book from its
  **title + author** text; metadata search cannot match a page of prose (see below).
- Aim for **60–100 covers** across genres/publishers.
- Deliberately include the hard cases the preprocessing pipeline targets:
  - angled / skewed shots
  - glare and uneven lighting
  - low resolution / far away
  - stylized title fonts

## Labeling

Add one row per image to `data/labels.csv`:

```csv
filename,title,author,type,notes
data/photos/dune_01.jpg,Dune,Frank Herbert,cover,angled + glare
```

- `filename` is relative to the repo root.
- `title` is the ground truth used for scoring (a candidate counts as correct when its
  title fuzzily matches this, threshold in `eval.py`).
- `author` and `notes` are for your reference; `type` is `cover` or `page`.

## Regenerate the results

```bash
python eval.py                 # runs every rung, caches search responses
python eval.py --offline       # deterministic re-run from cache
```

Paste the printed table into the README. On real photos you should see:

- **preprocess** rung > **baseline** rung (OpenCV cleanup helps noisy OCR), and
- **fuzzy/semantic/hybrid** > **search-engine order** (ranking fixes wrong-first-hit).

## Covers vs. interior pages

The tool handles **both**, via two search modes chosen automatically:

- **Cover photos** → metadata search on the OCR'd title/author (the ablation experiment
  above measures this path).
- **Interior prose pages** (like the 5 images originally shipped under `static/uploads/` —
  Dune, The Iliad, Art of War) → full-text "search inside" with windowed queries + edition
  aggregation (see the README). These are identified correctly but are not part of the
  metadata-retrieval ablation, since they exercise a different backend.

If you collect a page-photo set, label it the same way (ground-truth `title`); `type=page`
distinguishes it from covers.
