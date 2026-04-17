# CLAUDE.md — Mozaik Generator

## Project Overview
Photomosaic image generator that replaces regions of a target image with
best-matching tile images from a library. Uses KDTree-based color matching
in RGB space with k-nearest-neighbor random selection to reduce repetition.

## Quick Start
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run via module
python3 -m mozaik --target photo.jpg --tiles-dir ./tiles --output mosaic.png

# Run tests
python3 -m pytest tests/ -v
```

## Project Structure
```
mozaik/
  __init__.py        — package metadata + version
  __main__.py        — entry point for `python -m mozaik`
  cli.py             — argparse CLI (flags: --target, --tiles-dir, --output, etc.)
  mosaic.py          — orchestrator: wires load → match → grid → compose → save
  tile_loader.py     — recursively load/resize tiles, compute avg RGB, optional caching
  color_matcher.py   — KDTree nearest-neighbor matching with k candidates + random pick
  grid.py            — divide target image into M×N cells, compute avg color per cell
  composer.py        — paste matched tiles onto output canvas
  utils.py           — shared helpers (load_image, resize_and_crop, average_color, blend_tile)
tests/
  conftest.py        — fixtures: tmp dirs, sample tile sets, gradient target image
  test_*.py          — unit tests for each module
```

## Architecture
Pipeline: `target image → grid cells → color match each cell → compose canvas → save`

Key algorithm choices:
- **KDTree** (scipy.spatial.KDTree) for O(log n) color lookups
- **k=40 nearest neighbors** + random selection to avoid tile repetition
- **Center-crop + resize** for tiles to avoid distortion
- **Optional blend** (alpha overlay) for smoother visual coherence

## Conventions
- Python 3.9+, type hints throughout
- Dependencies: Pillow, NumPy, SciPy, tqdm
- Tests: pytest, fixtures in conftest.py
- No classes except where state is needed (ColorMatcher)
- Functions are the default unit of organization

## Common Commands
```bash
python3 -m pytest tests/ -v              # run tests
python3 -m pytest tests/ -v --cov=mozaik # with coverage
python3 -m mozaik --help                 # CLI help
```
