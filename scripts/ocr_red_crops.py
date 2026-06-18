#!/usr/bin/env python3
"""Run local OCR on cropped red-region images."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.image.ocr_crops import run_ocr_on_crops, check_tesseract_availability


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan-id",
        required=True,
        help="Plan ID (e.g. SP_U1_0003)",
    )
    parser.add_argument(
        "--crops-json",
        help="Path to the red crops JSON metadata file. Defaults to outputs/debug/<plan_id>_red_crops.json",
    )
    parser.add_argument(
        "--out",
        help="Path to save the OCR results JSON file. Defaults to outputs/debug/<plan_id>_ocr_results.json",
    )
    parser.add_argument(
        "--psm",
        type=int,
        default=6,
        help="Tesseract Page Segmentation Mode (PSM). Defaults to 6.",
    )
    args = parser.parse_args()

    plan_id = args.plan_id
    
    # Resolve default paths
    crops_json_path = (
        Path(args.crops_json)
        if args.crops_json
        else REPO_ROOT / "outputs" / "debug" / f"{plan_id}_red_crops.json"
    )
    out_json_path = (
        Path(args.out)
        if args.out
        else REPO_ROOT / "outputs" / "debug" / f"{plan_id}_ocr_results.json"
    )

    if not crops_json_path.exists():
        print(f"Error: Crops metadata file not found at {crops_json_path}", file=sys.stderr)
        print("Please run scripts/extract_red_crops.py first to generate crops.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(crops_json_path, "r", encoding="utf-8") as f:
            crops_metadata = json.load(f)
    except Exception as e:
        print(f"Error reading crops metadata file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(crops_metadata)} crop(s) for plan {plan_id}.")

    # Check tesseract availability
    if not check_tesseract_availability():
        print("Warning: Tesseract OCR is not fully available (pytesseract or system binary missing).", file=sys.stderr)
        print("Proceeding with graceful fallback (ocr_available=False for all crops).", file=sys.stderr)

    print(f"Running OCR on crops (PSM={args.psm})...")
    results = run_ocr_on_crops(crops_metadata, psm=args.psm)

    # Ensure output directory exists
    out_json_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing OCR results JSON: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully saved OCR results to: {out_json_path}")


if __name__ == "__main__":
    main()
