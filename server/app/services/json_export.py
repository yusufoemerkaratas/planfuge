import json
from datetime import datetime, timezone
from pathlib import Path


EXPORT_FIELDS = {
    "candidate_id",
    "source",
    "label_type",
    "raw_text",
    "bbox_image",
    "crop_path",
    "width_mm",
    "height_mm",
    "diameter_mm",
    "ra_value",
    "ok_value",
    "reference",
    "confidence",
    "review_comment",
}


def export_verified_openings(project_root: Path, plan_id: str, candidates: list[dict]) -> dict:
    exports_dir = project_root / "outputs" / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = exports_dir / f"{plan_id}_verified_openings.json"
    
    verified_openings = []
    for cand in candidates:
        if cand.get("status") == "verified":
            filtered_cand = {k: v for k, v in cand.items() if k in EXPORT_FIELDS}
            verified_openings.append(filtered_cand)
    
    payload = {
        "plan_id": plan_id,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "opening_count": len(verified_openings),
        "openings": verified_openings,
    }
    
    file_path.write_text(json.dumps(payload, indent=2))
    
    return {
        "status": "success",
        "path": str(file_path.absolute()),
    }
