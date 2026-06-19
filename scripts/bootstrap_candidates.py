#!/usr/bin/env python3
"""Generate missing candidate files from tracked searchable-PDF words."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.candidates.pdf_words_candidate_extractor import extract_candidates_json


def bootstrap_candidates(project_root: Path) -> dict[str, int]:
    words_dir = project_root / "data" / "words"
    candidates_dir = project_root / "outputs" / "candidates"
    result = {"generated": 0, "existing": 0, "failed": 0}

    if not words_dir.is_dir():
        return result

    for words_path in sorted(words_dir.glob("*_words.json")):
        plan_id = words_path.stem.removesuffix("_words")
        output_path = candidates_dir / f"{plan_id}_candidates.json"
        if output_path.is_file():
            result["existing"] += 1
            continue

        try:
            extract_candidates_json(
                words_path,
                output_path,
                plan_id=plan_id,
                project_root=project_root,
            )
            result["generated"] += 1
        except (OSError, ValueError, json.JSONDecodeError):
            result["failed"] += 1

    return result


def main() -> None:
    result = bootstrap_candidates(Path.cwd())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
