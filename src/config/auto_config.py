"""Automatic grid and zone detection from a rendered plan PNG.

Generates a PlanConfig without any manual pixel input by:
1. Detecting the outer border box (dark rectangle enclosing the plan area).
2. Scanning the top header strip for evenly-spaced tick marks (grid column lines).
3. Scanning the left strip for evenly-spaced row ticks.
4. Labelling columns as A, B, C... and rows as 1, 2, 3...
5. Writing the result to data/config/{plan_id}_config.json.
"""

from __future__ import annotations

import json
import string
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # architectural plans can be very large


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _find_border_box(arr: np.ndarray) -> tuple[int, int, int, int]:
    """Return (x_min, y_min, x_max, y_max) of the dark outer border frame.

    The plan is surrounded by a thin black rectangular border.  We detect it
    by looking for the outermost rows/columns where ≥60 % of pixels are dark.
    """
    dark = (arr < 80).astype(np.uint8)
    h, w = dark.shape

    frac_threshold = 0.4

    # Left border: first column with enough dark pixels
    col_dark_frac = dark.sum(axis=0) / h
    x_candidates = np.where(col_dark_frac > frac_threshold)[0]
    x_min = int(x_candidates[0]) if len(x_candidates) else 0
    x_max = int(x_candidates[-1]) if len(x_candidates) else w - 1

    row_dark_frac = dark.sum(axis=1) / w
    y_candidates = np.where(row_dark_frac > frac_threshold)[0]
    y_min = int(y_candidates[0]) if len(y_candidates) else 0
    y_max = int(y_candidates[-1]) if len(y_candidates) else h - 1

    return x_min, y_min, x_max, y_max


def _detect_ticks_in_strip(
    strip: np.ndarray,
    axis: int,
    min_spacing: int = 200,
) -> list[int]:
    """Detect evenly-spaced tick/line positions in a 1-D projection of a strip.

    Parameters
    ----------
    strip:
        2-D grayscale array (small strip of the plan image).
    axis:
        0 → project along rows (detect columns, i.e. vertical ticks).
        1 → project along columns (detect rows, i.e. horizontal ticks).
    min_spacing:
        Minimum pixel distance between two distinct tick positions.

    Returns
    -------
    List of pixel positions (in the full-image coordinate space is handled by
    the caller who adds the offset).
    """
    # Count dark pixels along the chosen axis
    dark = (strip < 80).astype(np.uint8)
    projection = dark.sum(axis=axis)

    # Local maxima where there are many dark pixels (= a grid line)
    threshold = max(5, projection.max() * 0.15)
    candidates = np.where(projection > threshold)[0]

    if len(candidates) == 0:
        return []

    # Group nearby candidates and take the centroid of each group
    groups: list[list[int]] = []
    current: list[int] = [int(candidates[0])]
    for c in candidates[1:]:
        if c - current[-1] < 30:
            current.append(int(c))
        else:
            groups.append(current)
            current = [int(c)]
    groups.append(current)

    positions = [int(np.mean(g)) for g in groups]

    # Filter out positions that are too close together
    filtered: list[int] = [positions[0]]
    for p in positions[1:]:
        if p - filtered[-1] >= min_spacing:
            filtered.append(p)

    return filtered


def _assign_labels(positions: list[int], use_letters: bool) -> list[tuple[int, str]]:
    """Map pixel positions to sequential grid labels.

    Columns → A, B, C …  (use_letters=True)
    Rows    → 1, 2, 3 …  (use_letters=False)
    """
    result: list[tuple[int, str]] = []
    alphabet = string.ascii_uppercase
    for i, pos in enumerate(positions):
        label = alphabet[i % len(alphabet)] if use_letters else str(i + 1)
        result.append((pos, label))
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_grid_from_png(
    png_path: Path,
) -> dict[str, Any]:
    """Detect grid anchor information from a rendered plan PNG.

    Returns a dict suitable for the ``grid`` key of a plan config JSON:

    .. code-block:: json

        {
          "anchors": {
            "top_left_pixel": [x, y],
            "top_left_coord": "A-1",
            "bottom_right_pixel": [x, y],
            "bottom_right_coord": "Z-20"
          },
          "column_positions": [[x, "A"], [x, "B"], ...],
          "row_positions": [[y, "1"], [y, "2"], ...]
        }
    """
    img = Image.open(png_path).convert("L")
    arr = np.array(img)
    h, w = arr.shape

    x_min, y_min, x_max, y_max = _find_border_box(arr)

    # The title/legend block is typically the first 1–4 % of the width on the left
    title_block_width = max(200, int((x_max - x_min) * 0.02))
    content_x_min = x_min + title_block_width

    # Strip heights for tick detection (top header ~4 % of plan height)
    strip_h = max(100, int((y_max - y_min) * 0.05))
    strip_w = max(100, int((x_max - x_min) * 0.04))

    # ---- Column ticks from the top header strip ----
    top_strip = arr[y_min : y_min + strip_h, content_x_min:x_max]
    col_positions_rel = _detect_ticks_in_strip(top_strip, axis=0, min_spacing=300)
    col_positions = [p + content_x_min for p in col_positions_rel]

    # ---- Row ticks from the left strip ----
    left_strip = arr[y_min:y_max, x_min : x_min + strip_w]
    row_positions_rel = _detect_ticks_in_strip(left_strip, axis=1, min_spacing=200)
    row_positions = [p + y_min for p in row_positions_rel]

    # If detection failed, fall back to evenly-divided grid based on the border
    if len(col_positions) < 2:
        n_cols = max(2, round((x_max - content_x_min) / 600))
        col_positions = [
            content_x_min + int(i * (x_max - content_x_min) / n_cols) for i in range(n_cols + 1)
        ]

    if len(row_positions) < 2:
        n_rows = max(2, round((y_max - y_min) / 600))
        row_positions = [y_min + int(i * (y_max - y_min) / n_rows) for i in range(n_rows + 1)]

    col_labels = _assign_labels(col_positions, use_letters=True)
    row_labels = _assign_labels(row_positions, use_letters=False)

    tl_coord = f"{col_labels[0][1]}-{row_labels[0][1]}"
    br_coord = f"{col_labels[-1][1]}-{row_labels[-1][1]}"

    return {
        "anchors": {
            "top_left_pixel": [col_positions[0], row_positions[0]],
            "top_left_coord": tl_coord,
            "bottom_right_pixel": [col_positions[-1], row_positions[-1]],
            "bottom_right_coord": br_coord,
        },
        "column_positions": [[p, lbl] for p, lbl in col_labels],
        "row_positions": [[p, lbl] for p, lbl in row_labels],
    }


def auto_generate_config(
    plan_id: str,
    png_path: Path,
    project_root: Path,
    scale: int = 50,
    default_height_cm: float = 30.0,
    overwrite: bool = False,
) -> Path:
    """Detect grid from *png_path* and write ``{plan_id}_config.json``.

    Parameters
    ----------
    plan_id:
        Identifier string, e.g. ``"SP_U1_0002"``.
    png_path:
        Path to the rendered plan PNG.
    project_root:
        Root of the plan2print project (used to locate ``data/config/``).
    scale:
        Drawing scale (e.g. 50 means 1:50).  Kept as a sensible default.
    default_height_cm:
        Fallback height for openings without an explicit height label.
    overwrite:
        If False (default), an existing config is left untouched.

    Returns
    -------
    Path to the written config file.
    """
    config_dir = project_root / "data" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / f"{plan_id}_config.json"

    if config_path.exists() and not overwrite:
        print(f"  Config already exists, skipping auto-detection: {config_path}")
        return config_path

    print(f"  Auto-detecting grid from: {png_path.name}")
    grid_info = detect_grid_from_png(png_path)

    n_cols = len(grid_info["column_positions"])
    n_rows = len(grid_info["row_positions"])
    tl = grid_info["anchors"]["top_left_coord"]
    br = grid_info["anchors"]["bottom_right_coord"]
    print(f"    Detected {n_cols} columns × {n_rows} rows  ({tl} → {br})")

    config: dict[str, Any] = {
        "plan_id": plan_id,
        "scale": scale,
        "default_height_cm": default_height_cm,
        "grid": grid_info,
        "color_zones": [],
        "_auto_generated": True,
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"    Saved auto-config: {config_path}")
    return config_path
