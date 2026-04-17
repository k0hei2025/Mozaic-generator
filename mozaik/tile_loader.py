"""Load, resize, and index tile images from a directory."""

from __future__ import annotations

import hashlib
import json
import os
import pickle
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import NamedTuple

import numpy as np
from PIL import Image
from tqdm import tqdm

from .utils import SUPPORTED_EXTENSIONS, average_color, resize_and_crop


class Tile(NamedTuple):
    image: Image.Image
    color: np.ndarray  # shape (3,)
    path: str


def _load_single_tile(path: str, size: tuple[int, int]) -> Tile | None:
    """Load and prepare one tile (used by both serial and parallel paths)."""
    try:
        img = Image.open(path).convert("RGB")
        img = resize_and_crop(img, size)
        color = average_color(img)
        return Tile(image=img, color=color, path=path)
    except Exception:
        return None


def _collect_image_paths(directory: str) -> list[str]:
    """Recursively collect image file paths from *directory*."""
    paths: list[str] = []
    for root, _, files in os.walk(directory):
        for fname in files:
            if Path(fname).suffix.lower() in SUPPORTED_EXTENSIONS:
                paths.append(os.path.join(root, fname))
    return sorted(paths)


def _cache_path(directory: str, tile_size: tuple[int, int]) -> Path:
    """Deterministic cache file path based on directory content + tile size."""
    key = f"{os.path.abspath(directory)}:{tile_size}"
    digest = hashlib.md5(key.encode()).hexdigest()[:12]
    return Path(directory) / f".mozaik_cache_{digest}.pkl"


def load_tiles(
    directory: str,
    tile_size: tuple[int, int] = (40, 40),
    *,
    workers: int = 1,
    use_cache: bool = False,
    show_progress: bool = True,
) -> list[Tile]:
    """Load all tile images from *directory*.

    Parameters
    ----------
    directory : str
        Path to the folder containing tile images (searched recursively).
    tile_size : tuple[int, int]
        (width, height) each tile will be resized to.
    workers : int
        Number of parallel workers.  1 = serial (default).
    use_cache : bool
        If True, cache computed color vectors to disk for reuse.
    show_progress : bool
        Show a tqdm progress bar.

    Returns
    -------
    list[Tile]
        Loaded tiles with precomputed average colors.
    """
    cache_file = _cache_path(directory, tile_size) if use_cache else None

    # Try loading from cache
    if cache_file and cache_file.exists():
        try:
            with open(cache_file, "rb") as f:
                cached = pickle.load(f)
            # Re-load images (we only cache colors + paths)
            tiles: list[Tile] = []
            for path, color in tqdm(cached, desc="Loading cached tiles", disable=not show_progress):
                try:
                    img = Image.open(path).convert("RGB")
                    img = resize_and_crop(img, tile_size)
                    tiles.append(Tile(image=img, color=np.array(color), path=path))
                except Exception:
                    continue
            if tiles:
                return tiles
        except Exception:
            pass  # Cache corrupted — fall through to fresh load

    paths = _collect_image_paths(directory)
    if not paths:
        raise FileNotFoundError(f"No images found in {directory}")

    tiles = []

    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_load_single_tile, p, tile_size): p for p in paths}
            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc="Loading tiles",
                disable=not show_progress,
            ):
                result = future.result()
                if result is not None:
                    tiles.append(result)
    else:
        for p in tqdm(paths, desc="Loading tiles", disable=not show_progress):
            result = _load_single_tile(p, tile_size)
            if result is not None:
                tiles.append(result)

    # Write cache
    if cache_file and tiles:
        try:
            data = [(t.path, t.color.tolist()) for t in tiles]
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
        except Exception:
            pass

    return tiles
