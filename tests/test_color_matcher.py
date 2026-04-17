"""Tests for color_matcher module."""

import numpy as np
from PIL import Image

from mozaik.color_matcher import ColorMatcher
from mozaik.tile_loader import Tile


def _make_tiles(colors: list[tuple[int, int, int]]) -> list[Tile]:
    """Create minimal Tile objects with solid-color images."""
    tiles = []
    for i, c in enumerate(colors):
        img = Image.new("RGB", (10, 10), c)
        tiles.append(Tile(image=img, color=np.array(c, dtype=np.float64), path=f"tile_{i}.png"))
    return tiles


def test_exact_match():
    tiles = _make_tiles([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    matcher = ColorMatcher(tiles, k=1)
    result = matcher.match(np.array([255.0, 0.0, 0.0]))
    assert np.allclose(result.color, [255, 0, 0])


def test_nearest_match():
    tiles = _make_tiles([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    matcher = ColorMatcher(tiles, k=1)
    # Should match green
    result = matcher.match(np.array([10.0, 240.0, 10.0]))
    assert np.allclose(result.color, [0, 255, 0])


def test_k_larger_than_tiles():
    tiles = _make_tiles([(100, 100, 100)])
    matcher = ColorMatcher(tiles, k=40)
    result = matcher.match(np.array([50.0, 50.0, 50.0]))
    assert result is not None


def test_no_reuse_mode():
    colors = [(i * 25, i * 25, i * 25) for i in range(10)]
    tiles = _make_tiles(colors)
    matcher = ColorMatcher(tiles, k=5)

    used_paths = set()
    for _ in range(10):
        result = matcher.match(np.array([125.0, 125.0, 125.0]), allow_reuse=False)
        used_paths.add(result.path)

    # All 10 tiles should have been used
    assert len(used_paths) == 10


def test_reset_clears_usage():
    tiles = _make_tiles([(128, 128, 128)])
    matcher = ColorMatcher(tiles, k=1)
    matcher.match(np.array([128.0, 128.0, 128.0]), allow_reuse=False)
    matcher.reset()
    # Should work again after reset
    result = matcher.match(np.array([128.0, 128.0, 128.0]), allow_reuse=False)
    assert result is not None
