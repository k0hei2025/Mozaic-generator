"""KDTree-based color matching engine."""

from __future__ import annotations

import random

import numpy as np
from scipy.spatial import KDTree

from .tile_loader import Tile


class ColorMatcher:
    """Find the best-matching tile for a given RGB color.

    Uses a scipy KDTree for O(log n) nearest-neighbor lookups in RGB space.
    Querying for *k* neighbors and randomly picking one reduces visual
    repetition in the final mosaic.
    """

    def __init__(self, tiles: list[Tile], *, k: int = 40) -> None:
        self._tiles = tiles
        self._k = min(k, len(tiles))  # can't query more neighbors than tiles
        colors = np.array([t.color for t in tiles])
        self._tree = KDTree(colors)
        self._used_indices: set[int] = set()

    def match(
        self,
        target_color: np.ndarray,
        *,
        allow_reuse: bool = True,
    ) -> Tile:
        """Return the tile whose average color best matches *target_color*.

        When *allow_reuse* is True (default), the same tile may appear
        multiple times.  When False, each tile is used at most once — if
        all k candidates have been used, the pool is expanded until an
        unused tile is found.
        """
        k = self._k

        while k <= len(self._tiles):
            _, indices = self._tree.query(target_color, k=k)
            if k == 1:
                indices = [indices]
            else:
                indices = list(indices)

            if allow_reuse:
                idx = random.choice(indices)
                return self._tiles[idx]

            # Non-reuse: pick a random *unused* tile among candidates
            candidates = [i for i in indices if i not in self._used_indices]
            if candidates:
                idx = random.choice(candidates)
                self._used_indices.add(idx)
                return self._tiles[idx]

            # All k candidates used — widen the search
            k = min(k * 2, len(self._tiles))

        # Absolute fallback: all tiles exhausted, allow reuse of least-used
        idx = random.choice(list(range(len(self._tiles))))
        return self._tiles[idx]

    def reset(self) -> None:
        """Clear the used-tile tracker (for non-reuse mode)."""
        self._used_indices.clear()
