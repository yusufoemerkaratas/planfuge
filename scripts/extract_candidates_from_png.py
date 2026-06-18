#!/usr/bin/env python3
"""Convert red regions and OCR results into reviewable opening candidates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.candidates.png_candidate_extractor import extract_candidates_from_png_data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan-id",
        required=True,
        help="Plan ID (e.g. SP_U1_0003)",
    )
    parser.add_argument(
        "--crops-json",
        help="Path to the red crops JSON metadata. Defaults to outputs/debug/<plan_id>_red_crops.json",
    )
    parser.add_argument(
        "--ocr-json",
        help="Path to the OCR results JSON. Defaults to outputs/debug/<plan_id>_ocr_results.json",
    )
    parser.add_argument(
        "--out-dir",
        help="Output directory to save candidates JSON. Defaults to outputs/candidates",
    )
    args = parser.parse_args()

    plan_id = args.plan_id
    
    # Resolve default paths
    crops_json_path = (
        Path(args.crops_json)
        if args.crops_json
        else REPO_ROOT / "outputs" / "debug" / f"{plan_id}_red_crops.json"
    )
    ocr_json_path = (
        Path(args.ocr-json) if hasattr(args, "ocr-json") else None  # safe fallback
    )
    # Correct key resolved
    ocr_json_path = (
        Path(args.ocr_json)
        if args.ocr_json
        else REPO_ROOT / "outputs" / "debug" / f"{plan_id}_ocr_results.json"
    )
    out_dir_path = (
        Path(args.out_dir)
        if args.out_dir
        else REPO_ROOT / "outputs" / "candidates"
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

    # Load OCR results optionally
    ocr_results = None
    if ocr_json_path.exists():
        try:
            with open(ocr_json_path, "r", encoding="utf-8") as f:
                ocr_results = json.load(f)
            print(f"Loaded OCR results from {ocr_json_path}")
        except Exception as e:
            print(f"Warning: Failed to load OCR results from {ocr_json_path}: {e}", file=sys.stderr)
    else:
        print(f"Warning: OCR results not found at {ocr_json_path}. Continuing without OCR text.")

    # Run extraction
    candidates = extract_candidates_from_png_data(crops_metadata, ocr_results)

    # Save outputs
    out_dir_path.mkdir(parents=True, exist_ok=True)
    out_json_path = out_dir_path / f"{plan_id}_candidates.json"

    try:
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing candidates JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Gather metrics
    sources = [c["source"] for c in candidates]
    label_types = [str(c["label_type"]) for c in candidates]

    source_counts = Counter(sources)
    label_type_counts = Counter(label_types)

    print("\n--- Extraction Metrics ---")
    print(f"Total candidates: {len(candidates)}")
    
    print("\nCounts by source:")
    for src in ("png_red_annotation_ocr", "png_red_annotation_region"):
        print(f"  {src}: {source_counts.get(src, 0)}")
        
    print("\nCounts by label_type:")
    for ltype in ("WDB", "DDB", "UZDB", "DDP", "None"):
        print(f"  {ltype}: {label_type_counts.get(ltype, 0)}")

    print(f"\nSaved candidates JSON to: {out_json_path}")


if __name__ == "__main__":
    main()
