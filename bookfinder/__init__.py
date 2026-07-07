"""OCRbookfinder: identify a book from a photo of its cover or a page.

Pipeline: image -> (OpenCV preprocess) -> OCR -> Google Books search -> rank candidates.

The ranking strategy is pluggable so the accompanying experiment (``eval.py``) can
measure each stage of the ladder: baseline -> fuzzy -> semantic -> hybrid.
"""

from .pipeline import BookFinder, PipelineConfig

__all__ = ["BookFinder", "PipelineConfig"]
