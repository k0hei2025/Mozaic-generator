"""Assemble matched tiles into the final mosaic image."""

from __future__ import annotations

import numpy as np
from PIL import Image
from tqdm import tqdm

from .color_matcher import ColorMatcher
from .grid import GridCell
from .tile_loader import Tile
from .utils import blend_tile


def compose_mosaic(
    cells: list[GridCell],
    grid_dims: tuple[int, int],
    tile_size: tuple[int, int],
    matcher: ColorMatcher,
    *,
    allow_reuse: bool = True,
    blend_alpha: float = 0.0,
    enlargement: int = 1,
    show_progress: bool = True,
) -> Image.Image:
    """Build the final mosaic image.

    Parameters
    ----------
    cells : list[GridCell]
        Grid cells from ``grid.compute_grid``.
    grid_dims : tuple[int, int]
        (columns, rows) of the grid.
    tile_size : tuple[int, int]
        (width, height) of each tile.
    matcher : ColorMatcher
        Prebuilt color matcher with loaded tiles.
    allow_reuse : bool
        Whether the same tile image may appear more than once.
    blend_alpha : float
        0.0 = pure tile, up to 1.0 = solid target color overlay.
        Values around 0.2–0.4 give a subtle tint that improves coherence.
    enlargement : int
        Scale factor for the output (1 = same grid dimensions, 2 = 2x, etc.).
    show_progress : bool
        Display a tqdm progress bar.

    Returns
    -------
    PIL.Image.Image
        The completed mosaic.
    """
    cols, rows = grid_dims
    tw, th = tile_size

    out_tile_w = tw * enlargement
    out_tile_h = th * enlargement

    canvas = Image.new("RGB", (cols * out_tile_w, rows * out_tile_h))

    for cell in tqdm(cells, desc="Composing mosaic", disable=not show_progress):
        tile: Tile = matcher.match(cell.avg_color, allow_reuse=allow_reuse)
        tile_img = tile.image

        if enlargement > 1:
            tile_img = tile_img.resize((out_tile_w, out_tile_h), Image.LANCZOS)

        if blend_alpha > 0:
            tile_img = blend_tile(tile_img, cell.avg_color, alpha=blend_alpha)

        paste_x = cell.col * out_tile_w
        paste_y = cell.row * out_tile_h
        canvas.paste(tile_img, (paste_x, paste_y))

    return canvas
