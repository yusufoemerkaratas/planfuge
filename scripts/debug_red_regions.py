#!/usr/bin/env python3
"""Detect red markup regions in a rendered plan PNG and save a debug mask."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.image.red_annotation_detector import detect_red_regions, save_red_debug_mask


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="Path to data/pages/<plan_id>.png")
    parser.add_argument("--out", default="outputs", help="Output root directory")
    parser.add_argument("--plan-id", help="Plan ID. Defaults to the image filename stem.")
    parser.add_argument("--min-area", type=int, default=250, help="Minimum red region area in pixels")
    args = parser.parse_args()

    image_path = Path(args.image)
    plan_id = args.plan_id or image_path.stem
    regions, mask = detect_red_regions(image_path, min_area_px=args.min_area)
    mask_path = Path(args.out) / "debug" / f"{plan_id}_red_mask.png"
    save_red_debug_mask(mask, mask_path)

    print(f"Saved red mask: {mask_path}")
    print(f"Detected red regions: {len(regions)}")
    for region in regions:
        print(region)


if __name__ == "__main__":
    main()
