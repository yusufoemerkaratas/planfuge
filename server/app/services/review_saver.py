import json
from datetime import UTC, datetime
from pathlib import Path


def save_reviewed_candidates(project_root: Path, plan_id: str, candidates: list[dict]) -> dict:
    reviews_dir = project_root / "outputs" / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    file_path = reviews_dir / f"{plan_id}_reviewed_candidates.json"

    payload = {
        "plan_id": plan_id,
        "saved_at": datetime.now(UTC).isoformat(),
        "candidate_count": len(candidates),
        "candidates": candidates,
    }

    file_path.write_text(json.dumps(payload, indent=2))

    return {
        "status": "success",
        "path": str(file_path.absolute()),
    }
