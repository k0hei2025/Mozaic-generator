"""Shared image helpers."""

from __future__ import annotations

import numpy as np
from PIL import Image

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}


def load_image(path: str) -> Image.Image:
    """Open an image file and convert to RGB."""
    return Image.open(path).convert("RGB")


def resize_and_crop(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Center-crop *img* to the target aspect ratio, then resize to *size*.

    This avoids distortion — the image is first cropped to match the target
    aspect ratio, then scaled down (or up) to the exact pixel dimensions.
    """
    target_w, target_h = size
    target_ratio = target_w / target_h

    src_w, src_h = img.size
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        # Source is wider — crop sides
        new_w = int(target_ratio * src_h)
        offset = (src_w - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, src_h))
    elif src_ratio < target_ratio:
        # Source is taller — crop top/bottom
        new_h = int(src_w / target_ratio)
        offset = (src_h - new_h) // 2
        img = img.crop((0, offset, src_w, offset + new_h))

    return img.resize(size, Image.LANCZOS)


def average_color(img: Image.Image) -> np.ndarray:
    """Return the mean (R, G, B) of *img* as a float64 array of shape (3,)."""
    arr = np.asarray(img, dtype=np.float64)
    return arr.mean(axis=(0, 1))


def blend_tile(tile: Image.Image, target_color: np.ndarray, alpha: float = 0.3) -> Image.Image:
    """Blend *tile* toward *target_color* by *alpha* (0 = pure tile, 1 = solid color)."""
    arr = np.asarray(tile, dtype=np.float64)
    blended = arr * (1 - alpha) + target_color * alpha
    return Image.fromarray(blended.clip(0, 255).astype(np.uint8))
