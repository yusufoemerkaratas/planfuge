#!/usr/bin/env python3
"""Compare generated candidates against manual checked examples."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.candidates.validation import compare_candidates_to_examples


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan-id",
        required=True,
        help="Plan ID (e.g. SP_U1_0003)",
    )
    parser.add_argument(
        "--candidates-json",
        help="Path to candidates JSON. Defaults to outputs/candidates/<plan_id>_candidates.json",
    )
    parser.add_argument(
        "--examples-json",
        help="Path to examples JSON. Defaults to data/annotations/<plan_id>_examples.json",
    )
    parser.add_argument(
        "--iou-threshold",
        type=float,
        default=0.1,
        help="IoU threshold for box overlap match. Defaults to 0.1",
    )
    args = parser.parse_args()

    plan_id = args.plan_id
    
    # Resolve default paths
    candidates_path = (
        Path(args.candidates_json)
        if args.candidates_json
        else REPO_ROOT / "outputs" / "candidates" / f"{plan_id}_candidates.json"
    )
    examples_path = (
        Path(args.examples_json)
        if args.examples_json
        else REPO_ROOT / "data" / "annotations" / f"{plan_id}_examples.json"
    )

    # Validate candidates file presence
    if not candidates_path.exists():
        print(f"Error: Candidates file not found: {candidates_path}", file=sys.stderr)
        print(f"Please run scripts/extract_candidates_from_png.py first.", file=sys.stderr)
        sys.exit(1)

    # Validate examples file presence
    if not examples_path.exists():
        print(f"Error: Examples file not found: {examples_path}", file=sys.stderr)
        print(f"Please create data/annotations/{plan_id}_examples.json first.", file=sys.stderr)
        sys.exit(1)

    # Load candidates JSON
    try:
        with open(candidates_path, "r", encoding="utf-8") as f:
            # Check if it has candidates key or is a list (fallback mode vs end-to-end list)
            data = json.load(f)
            if isinstance(data, dict) and "candidates" in data:
                candidates = data["candidates"]
            else:
                candidates = data
    except json.JSONDecodeError as jde:
        print(f"Error: Candidates JSON file is malformed: {jde}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading candidates: {e}", file=sys.stderr)
        sys.exit(1)

    # Load examples JSON
    try:
        with open(examples_path, "r", encoding="utf-8") as f:
            examples = json.load(f)
    except json.JSONDecodeError as jde:
        print(f"Error: Examples JSON file is malformed: {jde}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading examples: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(candidates)} candidate(s) from {candidates_path}")
    print(f"Loaded {len(examples)} example(s) from {examples_path}")

    # Compare candidates to examples
    report = compare_candidates_to_examples(
        candidates=candidates,
        examples=examples,
        iou_threshold=args.iou_threshold
    )

    total_relevant = sum(1 for ex in examples if ex.get("is_opening_relevant", True))
    matched_relevant_count = len(report["matched_relevant"])
    
    recall_rate = (matched_relevant_count / total_relevant) if total_relevant > 0 else 0.0

    print("\n--- Validation Quality Gate Report ---")
    print(f"Total candidates: {len(candidates)}")
    print(f"Total examples: {len(examples)}")
    print(f"Total relevant examples: {total_relevant}")
    print(f"Matched relevant examples: {matched_relevant_count}")
    print(f"Relevant Recall Rate: {recall_rate:.2%} ({matched_relevant_count}/{total_relevant})")

    print("\nMatched Relevant Examples:")
    if not report["matched_relevant"]:
        print("  None")
    for item in report["matched_relevant"]:
        text_info = ""
        if item.get("expected_text") or item.get("raw_text"):
            text_info = f" (Expected: '{item.get('expected_text')}' | OCR: '{item.get('raw_text')}')"
        print(f"  {item['example_id']} matched with candidate {item['candidate_id']}{text_info}")

    print("\nMissed Relevant Examples:")
    if not report["missed_relevant"]:
        print("  None")
    for item in report["missed_relevant"]:
        text_info = f" (Expected: '{item.get('expected_text')}')" if item.get("expected_text") else ""
        print(f"  {item['example_id']}{text_info}")

    print("\nNon-Relevant Examples Matched:")
    if not report["matched_non_relevant"]:
        print("  None")
    for item in report["matched_non_relevant"]:
        print(f"  {item['example_id']} matched with candidate {item['candidate_id']}")

    print("\nUnmatched Candidates Detections:")
    print(f"  Count: {len(report['unmatched_candidates'])}")
    # Print a few unmatched candidates to stdout for inspection
    if report["unmatched_candidates"]:
        print("  Sample unmatched candidate IDs:")
        sample_ids = [c["candidate_id"] for c in report["unmatched_candidates"][:5]]
        print(f"    {', '.join(sample_ids)} ...")

    sys.exit(0)


if __name__ == "__main__":
    main()
