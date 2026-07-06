"""Render a small SYNTHETIC cover dataset so `eval.py` runs out of the box.

These are clean, generated title/author covers -- enough to prove the end-to-end
pipeline (OCR -> search -> rank -> correct book) against the live search API. They are
NOT a substitute for real photographed covers: the preprocessing ablation only shows
meaningful gains on real photos (glare, skew, noise). See DATASET.md to collect those.

Run:  python data/make_demo_covers.py   (writes data/demo_covers/*.png + updates labels)
"""

from __future__ import annotations

import csv
import os
import textwrap

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "demo_covers")
LABELS = os.path.join(HERE, "labels.csv")

# (title, author) -- chosen so some titles are ambiguous (e.g. "Dune" vs "Dune Messiah")
# so ranking has something to do beyond the search engine's own first hit.
BOOKS = [
    ("Dune", "Frank Herbert"),
    ("The Iliad", "Homer"),
    ("The Art of War", "Sun Tzu"),
    ("1984", "George Orwell"),
    ("Dracula", "Bram Stoker"),
    ("Frankenstein", "Mary Shelley"),
    ("The Hobbit", "J. R. R. Tolkien"),
    ("Moby Dick", "Herman Melville"),
    ("Pride and Prejudice", "Jane Austen"),
    ("Crime and Punishment", "Fyodor Dostoevsky"),
    ("Brave New World", "Aldous Huxley"),
    ("The Odyssey", "Homer"),
]


def render_cover(title: str, author: str, w: int = 700, h: int = 1000) -> np.ndarray:
    img = np.full((h, w, 3), 245, dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    y = 240
    for line in textwrap.wrap(title, width=14):
        size = cv2.getTextSize(line, font, 1.8, 4)[0]
        cv2.putText(img, line, ((w - size[0]) // 2, y), font, 1.8, (20, 20, 20), 4, cv2.LINE_AA)
        y += 90
    y += 60
    for line in textwrap.wrap(author, width=20):
        size = cv2.getTextSize(line, font, 1.1, 3)[0]
        cv2.putText(img, line, ((w - size[0]) // 2, y), font, 1.1, (60, 60, 60), 3, cv2.LINE_AA)
        y += 60
    return img


def slug(title: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in title.lower()).strip("_")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = [["filename", "title", "author", "type", "notes"]]
    for title, author in BOOKS:
        base = f"{slug(title)}.png"
        cv2.imwrite(os.path.join(OUT_DIR, base), render_cover(title, author))
        rows.append([f"data/demo_covers/{base}", title, author, "cover", "synthetic demo cover"])
    with open(LABELS, "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerows(rows)
    print(f"Wrote {len(BOOKS)} covers to {OUT_DIR} and updated {LABELS}")


if __name__ == "__main__":
    main()
