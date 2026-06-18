#!/usr/bin/env python3
"""Detect red regions in a plan PNG and save padded crops for each region."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.image.crop_regions import crop_red_regions
from src.image.red_annotation_detector import detect_red_regions, save_red_debug_mask


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image",
        required=True,
        help="Path to data/pages/<plan_id>.png",
    )
    parser.add_argument("--out", default="outputs", help="Output root directory")
    parser.add_argument("--plan-id", help="Plan ID. Defaults to the image filename stem.")
    parser.add_argument(
        "--padding",
        type=int,
        default=80,
        help="Padding around each red bbox",
    )
    parser.add_argument(
        "--min-area",
        type=int,
        default=250,
        help="Minimum red region area in pixels",
    )
    args = parser.parse_args()

    image_path = Path(args.image)
    plan_id = args.plan_id or image_path.stem
    output_root = Path(args.out)
    regions, mask = detect_red_regions(image_path, min_area_px=args.min_area)

    mask_path = output_root / "debug" / f"{plan_id}_red_mask.png"
    save_red_debug_mask(mask, mask_path)

    crop_metadata = crop_red_regions(
        image=image_path,
        regions=regions,
        output_dir=output_root / "crops",
        plan_id=plan_id,
        padding_px=args.padding,
    )
    metadata_path = output_root / "debug" / f"{plan_id}_red_crops.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(crop_metadata, indent=2), encoding="utf-8")

    print(f"Detected red regions: {len(regions)}")
    print(f"Saved red mask: {mask_path}")
    print(f"Saved crops: {len(crop_metadata)}")
    print(f"Saved crop metadata: {metadata_path}")


if __name__ == "__main__":
    main()
