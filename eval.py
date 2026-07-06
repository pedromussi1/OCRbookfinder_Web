"""Retrieval experiment: measure each rung of the ranking ladder.

For every labeled image we run the pipeline, find the rank of the first candidate whose
title matches the ground-truth book, and aggregate Recall@1, Recall@5, and MRR.

Usage:
    python eval.py                      # run all rungs on data/labels.csv
    python eval.py --rungs baseline fuzzy
    python eval.py --offline            # use only cached Google Books responses

Each "rung" pairs a preprocessing config with a ranker, so the table shows the marginal
effect of (a) OpenCV preprocessing and (b) smarter ranking.
"""

from __future__ import annotations

import argparse
import csv
import os

from rapidfuzz import fuzz

from bookfinder.books_api import Candidate, make_client
from bookfinder.ocr import extract_text, normalize_query
from bookfinder.preprocess import PreprocessConfig
from bookfinder.ranking import RANKERS

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LABELS = os.path.join(HERE, "data", "labels.csv")
_TITLE_MATCH_THRESHOLD = 85  # fuzzy ratio above which a candidate counts as the right book

# The ablation ladder: (label, preprocessing, ranker-name).
RUNGS = {
    "baseline":       ("grayscale-only + search order",   PreprocessConfig.baseline(), "baseline"),
    "preprocess":     ("full preprocess + search order",  PreprocessConfig(),          "baseline"),
    "fuzzy":          ("full preprocess + fuzzy rank",     PreprocessConfig(),          "fuzzy"),
    "semantic":       ("full preprocess + semantic rank",  PreprocessConfig(),          "semantic"),
    "hybrid":         ("full preprocess + hybrid rank",    PreprocessConfig(),          "hybrid"),
}


def load_labels(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def is_correct(candidate: Candidate, gt_title: str) -> bool:
    """A candidate is correct if its title fuzzily matches the ground-truth title."""
    return fuzz.token_set_ratio(candidate.title.lower(), gt_title.lower()) >= _TITLE_MATCH_THRESHOLD


def rank_of_correct(candidates, gt_title: str) -> int | None:
    """1-indexed rank of the first correct candidate, or None if absent."""
    for i, sc in enumerate(candidates, start=1):
        if is_correct(sc.candidate, gt_title):
            return i
    return None


def run_rung(label: str, prep: PreprocessConfig, ranker_name: str, rows, client) -> dict:
    """Run one ablation rung over all labeled images and aggregate metrics."""
    ranker = RANKERS[ranker_name]()
    ranks: list[int | None] = []
    for row in rows:
        image_path = os.path.join(HERE, row["filename"])
        text = extract_text(image_path, prep)
        query = normalize_query(text)
        candidates = client.search(query)
        ranked = ranker.rank(query, candidates)
        ranks.append(rank_of_correct(ranked, row["title"]))

    n = len(rows)
    recall_at_1 = sum(1 for r in ranks if r == 1) / n
    recall_at_5 = sum(1 for r in ranks if r is not None and r <= 5) / n
    mrr = sum((1.0 / r) for r in ranks if r is not None) / n
    return {"rung": label, "recall@1": recall_at_1, "recall@5": recall_at_5, "mrr": mrr, "ranks": ranks}


def print_table(results: list[dict]) -> None:
    print(f"\n{'rung':<34}{'Recall@1':>10}{'Recall@5':>10}{'MRR':>8}")
    print("-" * 62)
    for r in results:
        print(f"{r['rung']:<34}{r['recall@1']:>10.2f}{r['recall@5']:>10.2f}{r['mrr']:>8.2f}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Book-retrieval ablation experiment.")
    parser.add_argument("--labels", default=DEFAULT_LABELS, help="path to labels.csv")
    parser.add_argument("--rungs", nargs="+", choices=list(RUNGS), default=list(RUNGS),
                        help="which ablation rungs to run")
    parser.add_argument("--provider", default="openlibrary", choices=["openlibrary", "google"],
                        help="book-search backend")
    parser.add_argument("--offline", action="store_true",
                        help="use only cached search responses")
    args = parser.parse_args()

    rows = load_labels(args.labels)
    client = make_client(args.provider, offline=args.offline)
    print(f"Evaluating {len(rows)} images across {len(args.rungs)} rung(s)...")

    results = []
    for key in args.rungs:
        desc, prep, ranker_name = RUNGS[key]
        results.append(run_rung(desc, prep, ranker_name, rows, client))

    print_table(results)


if __name__ == "__main__":
    main()
