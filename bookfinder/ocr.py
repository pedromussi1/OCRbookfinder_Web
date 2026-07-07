"""OCR: image path -> extracted text, with optional preprocessing."""

from __future__ import annotations

import re
import string

import cv2
import pytesseract

from .preprocess import PreprocessConfig, preprocess
from .tesseract_setup import configure_tesseract

configure_tesseract()

_OCR_CONFIG = r"--oem 3 --psm 6"


def extract_text(image_path: str, preprocess_config: PreprocessConfig | None = None) -> str:
    """Read text from an image file. ``preprocess_config`` controls the OpenCV pipeline."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    processed = preprocess(image, preprocess_config)
    text = pytesseract.image_to_string(processed, config=_OCR_CONFIG)
    return text.strip()


def normalize_query(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace, and join hyphenated line breaks.

    This is the search-query form of the OCR text (retained from the original app,
    plus hyphen-join so words split across lines aren't broken).
    """
    text = re.sub(r"-\s*\n\s*", "", text)                       # de-hyphenate line breaks
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    text = text.lower()
    return " ".join(text.split())
