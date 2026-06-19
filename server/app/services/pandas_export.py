from pathlib import Path

import pandas as pd

EXPORT_COLUMNS = [
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
]


def export_verified_openings_csv(project_root: Path, plan_id: str, candidates: list[dict]) -> dict:
    exports_dir = project_root / "outputs" / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    file_path = exports_dir / f"{plan_id}_verified_openings.csv"

    verified_openings = []
    for cand in candidates:
        if cand.get("status") == "verified":
            verified_openings.append(cand)

    df = pd.DataFrame(verified_openings)

    # Ensure all required columns exist, fill with NaN if missing
    for col in EXPORT_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    # Keep only the requested columns in the correct order
    df = df[EXPORT_COLUMNS]

    df.to_csv(file_path, index=False)

    return {
        "status": "success",
        "path": str(file_path.absolute()),
        "exported_count": len(verified_openings),
    }
