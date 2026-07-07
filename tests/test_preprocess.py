"""Preprocessing produces a valid single-channel image for OCR."""

import numpy as np

from bookfinder.preprocess import PreprocessConfig, preprocess


def _fake_bgr(h=120, w=400):
    # A light page with a dark horizontal "text" band.
    img = np.full((h, w, 3), 240, dtype=np.uint8)
    img[50:70, 20:380] = 30
    return img


def test_full_pipeline_returns_2d_uint8():
    out = preprocess(_fake_bgr(), PreprocessConfig())
    assert out.ndim == 2                 # grayscale/binary
    assert out.dtype == np.uint8


def test_baseline_is_grayscale_only():
    img = _fake_bgr()
    out = preprocess(img, PreprocessConfig.baseline())
    assert out.ndim == 2
    # Grayscale-only keeps original dimensions (no upscale).
    assert out.shape == img.shape[:2]


def test_threshold_is_binary():
    out = preprocess(_fake_bgr(), PreprocessConfig())
    assert set(np.unique(out)).issubset({0, 255})
