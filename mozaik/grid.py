"""Divide a target image into a grid of cells."""

from __future__ import annotations

from typing import NamedTuple

import numpy as np
from PIL import Image

from .utils import average_color


class GridCell(NamedTuple):
    row: int
    col: int
    box: tuple[int, int, int, int]  # (left, upper, right, lower)
    avg_color: np.ndarray  # shape (3,)


def compute_grid(
    image: Image.Image,
    tile_size: tuple[int, int],
) -> tuple[list[GridCell], tuple[int, int]]:
    """Partition *image* into a grid whose cells match *tile_size*.

    Parameters
    ----------
    image : PIL.Image.Image
        The target image (RGB).
    tile_size : tuple[int, int]
        (width, height) of each grid cell / tile.

    Returns
    -------
    cells : list[GridCell]
        One entry per grid cell with position, bounding box, and average color.
    grid_dims : tuple[int, int]
        (columns, rows) — the number of tiles in each direction.
    """
    img_w, img_h = image.size
    tile_w, tile_h = tile_size

    cols = img_w // tile_w
    rows = img_h // tile_h

    cells: list[GridCell] = []
    for row in range(rows):
        for col in range(cols):
            left = col * tile_w
            upper = row * tile_h
            box = (left, upper, left + tile_w, upper + tile_h)
            region = image.crop(box)
            color = average_color(region)
            cells.append(GridCell(row=row, col=col, box=box, avg_color=color))

    return cells, (cols, rows)
