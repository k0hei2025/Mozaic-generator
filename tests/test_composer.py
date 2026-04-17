"""Tests for composer module."""

import numpy as np
from PIL import Image

from mozaik.color_matcher import ColorMatcher
from mozaik.composer import compose_mosaic
from mozaik.grid import compute_grid
from mozaik.tile_loader import Tile


def _make_tiles(n: int = 20) -> list[Tile]:
    rng = np.random.RandomState(0)
    tiles = []
    for i in range(n):
        c = tuple(rng.randint(0, 256, size=3).tolist())
        img = Image.new("RGB", (40, 40), c)
        tiles.append(Tile(image=img, color=np.array(c, dtype=np.float64), path=f"t{i}.png"))
    return tiles


def test_output_dimensions():
    target = Image.new("RGB", (200, 200))
    tiles = _make_tiles()
    cells, grid_dims = compute_grid(target, tile_size=(40, 40))
    matcher = ColorMatcher(tiles, k=5)
    result = compose_mosaic(cells, grid_dims, (40, 40), matcher, show_progress=False)
    assert result.size == (200, 200)


def test_enlargement():
    target = Image.new("RGB", (80, 80))
    tiles = _make_tiles()
    cells, grid_dims = compute_grid(target, tile_size=(40, 40))
    matcher = ColorMatcher(tiles, k=5)
    result = compose_mosaic(
        cells, grid_dims, (40, 40), matcher, enlargement=2, show_progress=False
    )
    # 2 cols * 80 = 160, 2 rows * 80 = 160
    assert result.size == (160, 160)


def test_blend_produces_valid_image():
    target = Image.new("RGB", (80, 80), (100, 100, 100))
    tiles = _make_tiles()
    cells, grid_dims = compute_grid(target, tile_size=(40, 40))
    matcher = ColorMatcher(tiles, k=5)
    result = compose_mosaic(
        cells, grid_dims, (40, 40), matcher, blend_alpha=0.3, show_progress=False
    )
    arr = np.asarray(result)
    assert arr.min() >= 0 and arr.max() <= 255


def test_no_reuse():
    target = Image.new("RGB", (80, 80))
    tiles = _make_tiles(20)
    cells, grid_dims = compute_grid(target, tile_size=(40, 40))
    matcher = ColorMatcher(tiles, k=5)
    # 4 cells, 20 tiles — should work without reuse
    result = compose_mosaic(
        cells, grid_dims, (40, 40), matcher, allow_reuse=False, show_progress=False
    )
    assert result.size == (80, 80)
