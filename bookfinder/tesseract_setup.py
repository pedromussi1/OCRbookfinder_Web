"""Locate the Tesseract binary cross-platform.

The original app hardcoded ``/usr/bin/tesseract`` (Linux only), which crashes on
Windows/macOS. This finds Tesseract on PATH first, then falls back to the common
install locations, and lets an env var override everything.
"""

from __future__ import annotations

import os
import shutil

import pytesseract

# Common install locations to probe when Tesseract is not on PATH.
_FALLBACK_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "/usr/bin/tesseract",
    "/usr/local/bin/tesseract",
    "/opt/homebrew/bin/tesseract",
]


def configure_tesseract() -> str:
    """Point pytesseract at a real Tesseract binary and return its path.

    Resolution order: ``TESSERACT_CMD`` env var -> PATH -> known install dirs.
    Raises FileNotFoundError with an actionable message if none are found.
    """
    override = os.environ.get("TESSERACT_CMD")
    if override and os.path.exists(override):
        pytesseract.pytesseract.tesseract_cmd = override
        return override

    on_path = shutil.which("tesseract")
    if on_path:
        pytesseract.pytesseract.tesseract_cmd = on_path
        return on_path

    for candidate in _FALLBACK_PATHS:
        if os.path.exists(candidate):
            pytesseract.pytesseract.tesseract_cmd = candidate
            return candidate

    raise FileNotFoundError(
        "Tesseract not found. Install it (https://github.com/tesseract-ocr/tesseract), "
        "add it to PATH, or set the TESSERACT_CMD environment variable to its full path."
    )
