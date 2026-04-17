"""Shared test fixtures."""

import os
import tempfile

import numpy as np
import pytest
from PIL import Image


@pytest.fixture()
def tmp_dir():
    """Provide a temporary directory that is cleaned up after the test."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture()
def sample_tiles_dir(tmp_dir):
    """Create a directory with 20 small solid-color tile images."""
    rng = np.random.RandomState(42)
    for i in range(20):
        color = tuple(rng.randint(0, 256, size=3).tolist())
        img = Image.new("RGB", (40, 40), color)
        img.save(os.path.join(tmp_dir, f"tile_{i:03d}.png"))
    return tmp_dir


@pytest.fixture()
def target_image_path(tmp_dir):
    """Create a small gradient target image."""
    img = Image.new("RGB", (200, 200))
    pixels = img.load()
    for y in range(200):
        for x in range(200):
            pixels[x, y] = (x % 256, y % 256, (x + y) % 256)
    path = os.path.join(tmp_dir, "target.png")
    img.save(path)
    return path
