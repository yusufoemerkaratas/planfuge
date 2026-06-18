import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MetadataLoadResult:
    plan_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    exists: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def load_metadata(project_root: Path, plan_id: str) -> MetadataLoadResult:
    metadata_path = project_root / "data" / "metadata" / f"{plan_id}_metadata.json"

    if not metadata_path.is_file():
        return MetadataLoadResult(
            plan_id=plan_id,
            exists=False,
            warnings=[f"metadata file not found: {metadata_path}"],
        )

    try:
        raw_text = metadata_path.read_text(encoding="utf-8")
        payload = json.loads(raw_text)
    except (json.JSONDecodeError, OSError) as exc:
        return MetadataLoadResult(
            plan_id=plan_id,
            exists=False,
            errors=[f"failed to read metadata file: {exc}"],
        )

    if not isinstance(payload, dict):
        return MetadataLoadResult(
            plan_id=plan_id,
            exists=False,
            errors=["metadata file must contain a JSON object"],
        )

    # Ensure plan_id matches the requested one or fallback
    actual_plan_id = payload.get("plan_id", plan_id)

    return MetadataLoadResult(
        plan_id=actual_plan_id,
        metadata=payload,
        exists=True,
    )
