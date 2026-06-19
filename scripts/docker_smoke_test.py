#!/usr/bin/env python3
"""Verify the externally observable Docker Compose runtime."""

from __future__ import annotations

import argparse
import json
import urllib.request


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

    health_body, _ = fetch(base_url, "/health")
    health = json.loads(health_body)
    if health.get("status") != "ok":
        raise SystemExit(f"Unexpected health response: {health}")

    html, content_type = fetch(base_url, "/")
    if content_type != "text/html" or b'id="root"' not in html:
        raise SystemExit("Frontend HTML did not load")

    plans_body, _ = fetch(base_url, "/api/plans")
    plans = json.loads(plans_body).get("plans", [])
    if not plans:
        raise SystemExit("No plans were discovered")

    candidates_body, _ = fetch(base_url, f"/api/candidates/{plans[0]}")
    candidate_count = json.loads(candidates_body).get("candidate_count", 0)
    if candidate_count < 1:
        raise SystemExit(f"No candidates were loaded for {plans[0]}")

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
        f"{candidate_count} candidates in {plans[0]}, calculations operational"
    )


if __name__ == "__main__":
    main()
