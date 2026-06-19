#!/usr/bin/env python3
"""Verify the externally observable Docker Compose runtime."""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

# Paths relative to the project root where this script runs
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMP_PNG = PROJECT_ROOT / "data" / "pages" / "SMOKE_TEST_TEMP.png"
TEMP_JSON = PROJECT_ROOT / "outputs" / "candidates" / "SMOKE_TEST_TEMP_candidates.json"


def fetch(base_url: str, path: str) -> tuple[bytes, str]:
    with urllib.request.urlopen(f"{base_url}{path}", timeout=20) as response:
        return response.read(), response.headers.get_content_type()


def post_json(base_url: str, path: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    # Ensure directories exist
    TEMP_PNG.parent.mkdir(parents=True, exist_ok=True)
    TEMP_JSON.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary mock assets
    TEMP_PNG.write_text("dummy page png content", encoding="utf-8")
    TEMP_JSON.write_text(
        json.dumps(
            {
                "plan_id": "SMOKE_TEST_TEMP",
                "candidate_count": 1,
                "candidates": [
                    {
                        "candidate_id": "smoke-001",
                        "source": "file",
                        "label_type": "WDB",
                        "raw_text": "WDB 10/20",
                        "bbox_image": [100, 100, 50, 50],
                        "crop_path": None,
                        "width_mm": 100,
                        "height_mm": 200,
                        "diameter_mm": None,
                        "ra_value": None,
                        "ok_value": None,
                        "reference": None,
                        "confidence": 1.0,
                        "review_comment": None,
                        "status": "needs_review",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    try:
        health_body, _ = fetch(base_url, "/health")
        health = json.loads(health_body)
        if health.get("status") != "ok":
            raise SystemExit(f"Unexpected health response: {health}")

        html, content_type = fetch(base_url, "/")
        if content_type != "text/html" or b'id="root"' not in html:
            raise SystemExit("Frontend HTML did not load")

        plans_body, _ = fetch(base_url, "/api/plans")
        plans = json.loads(plans_body).get("plans", [])
        if "SMOKE_TEST_TEMP" not in plans:
            raise SystemExit("Mock smoke test plan was not discovered")

        candidates_body, _ = fetch(base_url, "/api/candidates/SMOKE_TEST_TEMP")
        candidate_count = json.loads(candidates_body).get("candidate_count", 0)
        if candidate_count < 1:
            raise SystemExit("No candidates were loaded for SMOKE_TEST_TEMP")

        calculation = post_json(
            base_url,
            "/api/openings/calculate",
            {
                "geometry": "rectangular",
                "lengthCm": 10,
                "widthCm": 20,
                "heightCm": 30,
            },
        )
        if calculation.get("volumeCm3") != 6000 or calculation.get("weightKg") != 2.6:
            raise SystemExit(f"Unexpected calculation response: {calculation}")

        print(
            f"Docker runtime OK: {len(plans)} plans, "
            f"{candidate_count} candidates in SMOKE_TEST_TEMP, calculations operational"
        )
    finally:
        # Clean up temporary assets
        if TEMP_PNG.is_file():
            TEMP_PNG.unlink()
        if TEMP_JSON.is_file():
            TEMP_JSON.unlink()


if __name__ == "__main__":
    main()
