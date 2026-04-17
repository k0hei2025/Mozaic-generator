"""Main orchestrator — wires all pipeline stages together."""

from __future__ import annotations

import os

from PIL import Image

from .color_matcher import ColorMatcher
from .composer import compose_mosaic
from .grid import compute_grid
from .tile_loader import load_tiles
from .utils import load_image


def generate_mosaic(
    target_path: str,
    tiles_dir: str,
    output_path: str,
    *,
    tile_size: tuple[int, int] = (40, 40),
    k_neighbors: int = 40,
    allow_reuse: bool = True,
    blend_alpha: float = 0.0,
    enlargement: int = 1,
    workers: int = 1,
    use_cache: bool = False,
    show_progress: bool = True,
) -> str:
    """Generate a photomosaic and save it to *output_path*.

    Parameters
    ----------
    target_path : str
        Path to the source / target image.
    tiles_dir : str
        Directory containing tile images (searched recursively).
    output_path : str
        Where to write the resulting mosaic.
    tile_size : tuple[int, int]
        Width and height of each tile in pixels.
    k_neighbors : int
        Number of nearest-color candidates to consider (higher = more variety).
    allow_reuse : bool
        Allow the same tile image to be used more than once.
    blend_alpha : float
        Blend tiles toward the target region color (0.0–1.0).
    enlargement : int
        Output scale multiplier (2 = twice the grid resolution).
    workers : int
        Parallel workers for tile loading.
    use_cache : bool
        Cache tile color vectors to disk for faster reloads.
    show_progress : bool
        Display progress bars.

    Returns
    -------
    str
        The absolute path to the saved mosaic image.
    """
    # 1. Load target image
    target = load_image(target_path)

    # 2. Load & prepare tile library
    tiles = load_tiles(
        tiles_dir,
        tile_size=tile_size,
        workers=workers,
        use_cache=use_cache,
        show_progress=show_progress,
    )

    # 3. Build color matcher
    matcher = ColorMatcher(tiles, k=k_neighbors)

    # 4. Divide target into grid
    cells, grid_dims = compute_grid(target, tile_size)

    # 5. Compose final mosaic
    mosaic = compose_mosaic(
        cells,
        grid_dims,
        tile_size,
        matcher,
        allow_reuse=allow_reuse,
        blend_alpha=blend_alpha,
        enlargement=enlargement,
        show_progress=show_progress,
    )

    # 6. Save
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    mosaic.save(output_path)

    return os.path.abspath(output_path)
