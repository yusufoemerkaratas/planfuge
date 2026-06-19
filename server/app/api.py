import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from server.app.models import Opening, WeightConfig
from server.app.schemas import (
    CalculateOpeningRequest,
    CsvExportRequest,
    OpeningRequest,
    WeightConfigRequest,
)
from server.app.services.calculations import (
    calculate_volume_cm3,
    calculate_weight_kg,
    get_review_status,
)
from server.app.services.candidate_loader import (
    load_candidates,
    load_reviewed_candidates,
    load_sample_candidates,
)
from server.app.services.contract_export import generate_contract_csv, generate_contract_json
from server.app.services.csv_export import CSV_COLUMNS, serialize_csv, to_csv_row
from server.app.services.metadata_loader import load_metadata
from server.app.services.pipeline_status import check_pipeline_status
from server.app.services.plan_discovery import discover_plans
from server.app.services.review_saver import save_reviewed_candidates

JOBS: dict[str, str] = {}


app = FastAPI(title="Plan2Print API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "plan2print-api"}


@app.get("/api/export/contract")
def export_contract() -> dict[str, object]:
    config = WeightConfig()
    return {
        "columns": CSV_COLUMNS,
        "maxWeightKg": config.max_weight_kg,
        "densityKgPerM3": config.density_kg_per_m3,
    }


@app.post("/api/openings/calculate")
def calculate_opening(request: CalculateOpeningRequest) -> dict[str, object]:
    opening = opening_from_request(request)
    config = weight_config_from_request(request.config)

    return {
        "volumeCm3": round(calculate_volume_cm3(opening), 3),
        "weightKg": calculate_weight_kg(opening, config),
        "reviewStatus": get_review_status(opening, config),
        "csvRow": to_csv_row(opening, config),
    }


@app.post("/api/openings/csv")
def openings_csv(request: CsvExportRequest) -> Response:
    config = weight_config_from_request(request.config)
    openings = [opening_from_request(opening) for opening in request.openings]
    rows = [to_csv_row(opening, config) for opening in openings]
    return Response(content=serialize_csv(rows), media_type="text/csv")


def opening_from_request(request: OpeningRequest) -> Opening:
    return Opening(
        geometry=request.geometry,
        length_cm=request.length_cm,
        width_cm=request.width_cm,
        height_cm=request.height_cm,
        quantity=request.quantity,
        opening_type=request.opening_type,
        floor=request.floor,
        plan_name=request.plan_name,
        source_pdf=request.source_pdf,
        grid_coordinate=request.grid_coordinate,
        color_zone_id=request.color_zone_id,
        confidence=request.confidence,
        review_required=request.review_required,
    )


def weight_config_from_request(request: WeightConfigRequest) -> WeightConfig:
    return WeightConfig(
        density_kg_per_m3=request.density_kg_per_m3,
        max_weight_kg=request.max_weight_kg,
    )


def _get_project_root() -> Path:
    if hasattr(app.state, "project_root"):
        return app.state.project_root
    return Path.cwd()


@app.get("/api/candidates/sample")
def get_sample_candidates() -> dict:
    result = load_sample_candidates(_get_project_root())
    return asdict(result)


@app.get("/api/candidates/{plan_id}")
def get_candidates(plan_id: str) -> dict:
    result = load_candidates(_get_project_root(), plan_id)
    return asdict(result)


@app.get("/api/metadata/{plan_id}")
def get_metadata(plan_id: str) -> dict:
    result = load_metadata(_get_project_root(), plan_id)
    return asdict(result)


@app.get("/api/reviews/{plan_id}")
def get_reviews(plan_id: str) -> dict:
    result = load_reviewed_candidates(_get_project_root(), plan_id)
    return asdict(result)


@app.post("/api/reviews/{plan_id}")
def save_reviews(plan_id: str, candidates: list[dict[str, Any]]) -> dict:
    return save_reviewed_candidates(_get_project_root(), plan_id, candidates)


@app.post("/api/exports/json/{plan_id}")
def export_verified_json_endpoint(plan_id: str, candidates: list[dict[str, Any]]) -> Response:
    content = generate_contract_json(_get_project_root(), plan_id, candidates)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={plan_id}_contract.json"},
    )


@app.post("/api/exports/csv/{plan_id}")
def export_verified_csv_endpoint(plan_id: str, candidates: list[dict[str, Any]]) -> Response:
    content = generate_contract_csv(_get_project_root(), plan_id, candidates)
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={plan_id}_contract.csv"},
    )


@app.get("/api/downloads/csv/{plan_id}")
def download_pipeline_csv(plan_id: str) -> Response:
    project_root = _get_project_root()
    csv_path = project_root / "outputs" / "contract_exports" / f"{plan_id}_contract.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="Contract CSV not found")
    with open(csv_path, encoding="utf-8") as f:
        content = f.read()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={plan_id}_contract.csv"},
    )


@app.get("/api/status/{plan_id}")
def get_pipeline_status(plan_id: str) -> dict:
    status_info = check_pipeline_status(_get_project_root(), plan_id)
    if plan_id in JOBS:
        status_info["status"] = JOBS[plan_id]
    elif status_info["files"].get("candidates_json"):
        status_info["status"] = "completed"
    else:
        status_info["status"] = "unknown"
    return status_info


@app.get("/api/plans")
def get_plans() -> dict:
    return {"plans": discover_plans(_get_project_root())}


@app.get("/api/images/pages/{plan_id}")
def get_plan_image(plan_id: str) -> Response:
    image_path = _get_project_root() / "data" / "pages" / f"{plan_id}.png"
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    with open(image_path, "rb") as f:
        content = f.read()
    return Response(content=content, media_type="image/png")


@app.get("/api/images/crops/{filename}")
def get_crop_image(filename: str) -> Response:
    image_path = _get_project_root() / "outputs" / "crops" / filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Crop image not found")

    with open(image_path, "rb") as f:
        content = f.read()
    return Response(content=content, media_type="image/png")


@app.get("/api/images/overlays/{plan_id}")
def get_overlay_image(plan_id: str) -> Response:
    image_path = _get_project_root() / "outputs" / "overlays" / f"{plan_id}_overlay.png"
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Overlay image not found")

    with open(image_path, "rb") as f:
        content = f.read()
    return Response(content=content, media_type="image/png")


def run_pipeline_task(project_root: Path, pdf_path: Path, plan_id: str) -> None:
    script = project_root / "scripts" / "run_pipeline_on_pdfs.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--pdf", str(pdf_path)],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        # Log stdout/stderr so we can debug pipeline run in Docker logs
        if result.stdout:
            print(f"--- Pipeline Stdout for {plan_id} ---", flush=True)
            print(result.stdout, flush=True)
        if result.stderr:
            print(f"--- Pipeline Stderr for {plan_id} ---", flush=True)
            print(result.stderr, flush=True)

        if result.returncode == 0:
            JOBS[plan_id] = "completed"
            rendered_png = project_root / "outputs" / "rendered" / f"{plan_id}.png"
            target_png = project_root / "data" / "pages" / f"{plan_id}.png"
            if rendered_png.is_file():
                target_png.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(rendered_png, target_png)
        else:
            JOBS[plan_id] = "failed"
            print(f"Pipeline failed for {plan_id} with exit code {result.returncode}", flush=True)
    except Exception as e:
        JOBS[plan_id] = "failed"
        print(f"Pipeline failed for {plan_id} with exception: {e}", flush=True)


@app.post("/api/import/pdf")
async def import_pdf(file: UploadFile, background_tasks: BackgroundTasks) -> dict:
    """Accept a PDF upload, run the extraction pipeline in a background task, return status."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    project_root = _get_project_root()
    contents = await file.read()
    pdf_hash = hashlib.sha256(contents).hexdigest()

    # 1. SHA-256 duplicate detection
    metadata_dir = project_root / "data" / "metadata"
    if metadata_dir.is_dir():
        for meta_path in metadata_dir.glob("*.json"):
            try:
                meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
                if isinstance(meta_data, dict) and meta_data.get("pdf_hash") == pdf_hash:
                    return {
                        "status": "duplicate",
                        "plan_id": meta_data.get(
                            "plan_id", meta_path.stem.removesuffix("_metadata")
                        ),
                    }
            except Exception:
                pass

    import_dir = project_root / "data" / "imports"
    import_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = import_dir / file.filename
    pdf_path.write_bytes(contents)

    plan_id = pdf_path.stem

    # Write metadata file with hash (preserving existing fields if the file already exists)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata_file = metadata_dir / f"{plan_id}_metadata.json"
    meta_content = {}
    if metadata_file.is_file():
        try:
            meta_content = json.loads(metadata_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    meta_content["plan_id"] = plan_id
    meta_content["pdf_hash"] = pdf_hash
    metadata_file.write_text(json.dumps(meta_content, indent=2), encoding="utf-8")

    # Set state to processing and run background task
    JOBS[plan_id] = "processing"
    background_tasks.add_task(run_pipeline_task, project_root, pdf_path, plan_id)

    return {"plan_id": plan_id, "status": "processing"}
