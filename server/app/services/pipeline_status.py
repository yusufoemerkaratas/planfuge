from pathlib import Path


def check_pipeline_status(project_root: Path, plan_id: str) -> dict:
    return {
        "plan_id": plan_id,
        "files": {
            "page_image": (project_root / "data" / "pages" / f"{plan_id}.png").is_file(),
            "metadata_json": (
                project_root / "data" / "metadata" / f"{plan_id}_metadata.json"
            ).is_file(),
            "candidates_json": (
                project_root / "outputs" / "candidates" / f"{plan_id}_candidates.json"
            ).is_file(),
            "crops_dir": (project_root / "outputs" / "crops").is_dir(),
            "overlay_image": (
                project_root / "outputs" / "overlays" / f"{plan_id}_overlay.png"
            ).is_file(),
            "review_json": (
                project_root / "outputs" / "reviews" / f"{plan_id}_reviewed_candidates.json"
            ).is_file(),
            "export_json": (
                project_root / "outputs" / "exports" / f"{plan_id}_verified_openings.json"
            ).is_file(),
            "export_csv": (
                project_root / "outputs" / "exports" / f"{plan_id}_verified_openings.csv"
            ).is_file(),
        },
    }
