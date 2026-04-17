"""Tests for tile_loader module."""

import os

import numpy as np
from PIL import Image

from mozaik.tile_loader import Tile, load_tiles, _collect_image_paths


def test_collect_image_paths(sample_tiles_dir):
    paths = _collect_image_paths(sample_tiles_dir)
    assert len(paths) == 20
    assert all(p.endswith(".png") for p in paths)


def test_load_tiles_returns_correct_count(sample_tiles_dir):
    tiles = load_tiles(sample_tiles_dir, tile_size=(20, 20), show_progress=False)
    assert len(tiles) == 20


def test_tile_has_correct_size(sample_tiles_dir):
    tiles = load_tiles(sample_tiles_dir, tile_size=(30, 30), show_progress=False)
    for t in tiles:
        assert t.image.size == (30, 30)


def test_tile_color_is_3d_vector(sample_tiles_dir):
    tiles = load_tiles(sample_tiles_dir, tile_size=(20, 20), show_progress=False)
    for t in tiles:
        assert t.color.shape == (3,)
        assert np.all(t.color >= 0) and np.all(t.color <= 255)


def test_empty_dir_raises(tmp_dir):
    import pytest
    with pytest.raises(FileNotFoundError):
        load_tiles(tmp_dir, show_progress=False)


def test_cache_round_trip(sample_tiles_dir):
    tiles1 = load_tiles(sample_tiles_dir, tile_size=(20, 20), use_cache=True, show_progress=False)
    tiles2 = load_tiles(sample_tiles_dir, tile_size=(20, 20), use_cache=True, show_progress=False)
    assert len(tiles1) == len(tiles2)


def test_parallel_loading(sample_tiles_dir):
    tiles = load_tiles(sample_tiles_dir, tile_size=(20, 20), workers=2, show_progress=False)
    assert len(tiles) == 20
