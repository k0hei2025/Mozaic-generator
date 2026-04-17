# Mozaik Generator

A Python photomosaic generator that creates composite images by replacing regions of a target image with best-matching tiles from an image library.

## How It Works

1. **Load** a target image and a directory of tile images
2. **Divide** the target into a grid of cells
3. **Match** each cell to the closest tile using KDTree nearest-neighbor search in RGB color space
4. **Compose** the final mosaic by pasting matched tiles onto a canvas

The algorithm queries **k=40 nearest neighbors** and randomly selects one, reducing visual repetition while maintaining color accuracy.

## Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.9+.

## Usage

```bash
# Basic usage
python -m mozaik --target photo.jpg --tiles-dir ./my_tiles --output mosaic.png

# With options
python -m mozaik \
  --target photo.jpg \
  --tiles-dir ./my_tiles \
  --output mosaic.png \
  --tile-size 30x30 \
  --k-neighbors 40 \
  --blend 0.2 \
  --enlarge 2 \
  --workers 4 \
  --cache
```

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `-t, --target` | *required* | Path to target image |
| `-d, --tiles-dir` | *required* | Directory of tile images (recursive) |
| `-o, --output` | `mosaic_output.jpg` | Output file path |
| `--tile-size` | `40x40` | Tile dimensions (WxH or single int) |
| `-k, --k-neighbors` | `40` | Nearest-color candidates per match |
| `--no-reuse` | off | Prevent same tile appearing twice |
| `--blend` | `0.0` | Blend tiles toward target color (0.0–1.0) |
| `--enlarge` | `1` | Output scale multiplier |
| `-w, --workers` | `1` | Parallel workers for tile loading |
| `--cache` | off | Cache tile colors to disk |
| `-q, --quiet` | off | Suppress progress bars |

## Tips

- You need **at least a few hundred tile images** for good results
- Tile images can be any size — they're automatically cropped and resized
- Use `--blend 0.2` for smoother visual coherence
- Use `--enlarge 2` or `3` for higher-resolution output
- Use `--workers 4` to speed up tile loading on multi-core machines
- Use `--cache` to skip recomputing tile colors on repeated runs

## Running Tests

```bash
python -m pytest tests/ -v
```

## License

MIT
