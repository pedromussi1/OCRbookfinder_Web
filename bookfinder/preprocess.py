"""OpenCV preprocessing for OCR.

The original app did grayscale only. This adds an optional, configurable pipeline
(upscale -> denoise -> threshold -> deskew) so the experiment can measure how much
each step improves recognition. Every step is toggleable via ``PreprocessConfig``.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class PreprocessConfig:
    """Toggles for each preprocessing step. Defaults = the full pipeline."""

    grayscale: bool = True
    upscale: bool = True          # upscale small images so Tesseract has enough pixels
    denoise: bool = True          # bilateral filter: smooth noise, keep edges
    threshold: bool = True        # Otsu binarization
    deskew: bool = True           # rotate to straighten text lines
    min_width: int = 1000         # target min width when upscaling

    @classmethod
    def baseline(cls) -> "PreprocessConfig":
        """Grayscale only — matches the original app, for the baseline ablation rung."""
        return cls(grayscale=True, upscale=False, denoise=False, threshold=False, deskew=False)


def _upscale(image: np.ndarray, min_width: int) -> np.ndarray:
    h, w = image.shape[:2]
    if w >= min_width:
        return image
    scale = min_width / float(w)
    return cv2.resize(image, (min_width, int(h * scale)), interpolation=cv2.INTER_CUBIC)


def _deskew(gray: np.ndarray) -> np.ndarray:
    """Estimate skew from the dark (text) pixels and rotate to correct it."""
    inverted = cv2.bitwise_not(gray)
    coords = np.column_stack(np.where(inverted > 0))
    if coords.shape[0] < 50:  # too few ink pixels to trust an angle
        return gray
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    if abs(angle) < 0.5:      # ignore trivial skew
        return gray
    h, w = gray.shape[:2]
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(
        gray, matrix, (w, h), flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )


def preprocess(image: np.ndarray, config: PreprocessConfig | None = None) -> np.ndarray:
    """Apply the configured pipeline to a BGR image, returning the processed image."""
    config = config or PreprocessConfig()
    out = image
    if config.upscale:
        out = _upscale(out, config.min_width)
    if config.grayscale:
        out = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
    if config.denoise:
        out = cv2.bilateralFilter(out, d=9, sigmaColor=75, sigmaSpace=75)
    if config.threshold:
        # Otsu needs single-channel input; guarantee grayscale first.
        if out.ndim == 3:
            out = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        _, out = cv2.threshold(out, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if config.deskew:
        if out.ndim == 3:
            out = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        out = _deskew(out)
    return out
