"""Command-line interface for mozaik."""

from __future__ import annotations

import argparse
import os
import sys

from . import __version__


def _parse_tile_size(value: str) -> tuple[int, int]:
    """Parse 'WxH' or a single int (square tiles)."""
    if "x" in value:
        parts = value.split("x", 1)
        return int(parts[0]), int(parts[1])
    n = int(value)
    return n, n


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mozaik",
        description="Generate photomosaic images from a tile library.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # Required
    p.add_argument(
        "-t", "--target",
        required=True,
        help="Path to the target / source image.",
    )
    p.add_argument(
        "-d", "--tiles-dir",
        required=True,
        help="Directory containing tile images (searched recursively).",
    )

    # Output
    p.add_argument(
        "-o", "--output",
        default="mosaic_output.jpg",
        help="Output file path (default: mosaic_output.jpg).",
    )

    # Tuning
    p.add_argument(
        "--tile-size",
        type=_parse_tile_size,
        default=(40, 40),
        metavar="WxH",
        help="Tile dimensions in pixels, e.g. 40x40 or 40 (default: 40x40).",
    )
    p.add_argument(
        "-k", "--k-neighbors",
        type=int,
        default=40,
        help="Number of nearest-color candidates per tile (default: 40).",
    )
    p.add_argument(
        "--no-reuse",
        action="store_true",
        help="Prevent the same tile from being used more than once.",
    )
    p.add_argument(
        "--blend",
        type=float,
        default=0.0,
        metavar="ALPHA",
        help="Blend tiles toward target color (0.0–1.0, default: 0.0).",
    )
    p.add_argument(
        "--enlarge",
        type=int,
        default=1,
        metavar="N",
        help="Output scale multiplier (default: 1).",
    )

    # Performance
    p.add_argument(
        "-w", "--workers",
        type=int,
        default=1,
        help="Parallel workers for tile loading (default: 1).",
    )
    p.add_argument(
        "--cache",
        action="store_true",
        help="Cache tile color data to disk for faster reloads.",
    )
    p.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress bars.",
    )

    return p


def _validate(args: argparse.Namespace) -> None:
    """Validate CLI arguments, exit with a helpful message on failure."""
    if not os.path.isfile(args.target):
        sys.exit(f"Error: target image not found: {args.target}")
    if not os.path.isdir(args.tiles_dir):
        sys.exit(f"Error: tiles directory not found: {args.tiles_dir}")
    if args.blend < 0 or args.blend > 1:
        sys.exit("Error: --blend must be between 0.0 and 1.0")
    if args.enlarge < 1:
        sys.exit("Error: --enlarge must be >= 1")
    if args.k_neighbors < 1:
        sys.exit("Error: -k must be >= 1")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    _validate(args)

    # Lazy import so --help stays fast
    from .mosaic import generate_mosaic

    out = generate_mosaic(
        target_path=args.target,
        tiles_dir=args.tiles_dir,
        output_path=args.output,
        tile_size=args.tile_size,
        k_neighbors=args.k_neighbors,
        allow_reuse=not args.no_reuse,
        blend_alpha=args.blend,
        enlargement=args.enlarge,
        workers=args.workers,
        use_cache=args.cache,
        show_progress=not args.quiet,
    )

    print(f"\nMosaic saved to {out}")
