"""Tests for grid module."""

import numpy as np
from PIL import Image

from mozaik.grid import compute_grid


def test_grid_dimensions():
    img = Image.new("RGB", (200, 100), (128, 128, 128))
    cells, (cols, rows) = compute_grid(img, tile_size=(40, 40))
    assert cols == 5
    assert rows == 2
    assert len(cells) == 10


def test_grid_cell_boxes_are_non_overlapping():
    img = Image.new("RGB", (120, 80))
    cells, _ = compute_grid(img, tile_size=(40, 40))
    boxes = [c.box for c in cells]
    # No two boxes should overlap
    for i, b1 in enumerate(boxes):
        for b2 in boxes[i + 1:]:
            assert b1[2] <= b2[0] or b2[2] <= b1[0] or b1[3] <= b2[1] or b2[3] <= b1[1]


def test_avg_color_of_solid_image():
    img = Image.new("RGB", (80, 80), (100, 150, 200))
    cells, _ = compute_grid(img, tile_size=(40, 40))
    for cell in cells:
        assert np.allclose(cell.avg_color, [100, 150, 200])


def test_remainder_pixels_ignored():
    # 105 / 40 = 2 tiles (80 px used, 25 px remainder)
    img = Image.new("RGB", (105, 105))
    cells, (cols, rows) = compute_grid(img, tile_size=(40, 40))
    assert cols == 2
    assert rows == 2
