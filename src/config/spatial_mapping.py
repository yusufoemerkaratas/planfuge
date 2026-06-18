"""Map image pixel coordinates to configured plan locations."""

from __future__ import annotations

import math

from src.config.plan_config import PlanConfig


def _nearest_axis_label(positions: list[list], value: float) -> str | None:
    if not positions:
        return None
    return min(positions, key=lambda position: abs(position[0] - value))[1]


def grid_coordinate_for_point(x: float, y: float, config: PlanConfig) -> str:
    """Return the closest configured grid coordinate for an image point."""
    if config.grid_points:
        return min(
            config.grid_points,
            key=lambda point: math.hypot(point[0] - x, point[1] - y),
        )[2]

    column = _nearest_axis_label(config.column_positions, x)
    row = _nearest_axis_label(config.row_positions, y)
    if column is None or row is None:
        return "grid_unknown"
    return f"{column}-{row}"


def _point_on_segment(x: float, y: float, start: list[float], end: list[float]) -> bool:
    cross = (x - start[0]) * (end[1] - start[1]) - (y - start[1]) * (end[0] - start[0])
    if not math.isclose(cross, 0.0, abs_tol=1e-9):
        return False
    return (
        min(start[0], end[0]) <= x <= max(start[0], end[0])
        and min(start[1], end[1]) <= y <= max(start[1], end[1])
    )


def _point_in_polygon(x: float, y: float, polygon: list[list[float]]) -> bool:
    inside = False
    previous = polygon[-1]
    for current in polygon:
        if _point_on_segment(x, y, previous, current):
            return True
        if (current[1] > y) != (previous[1] > y):
            intersection_x = (previous[0] - current[0]) * (y - current[1]) / (previous[1] - current[1]) + current[0]
            if x < intersection_x:
                inside = not inside
        previous = current
    return inside


def color_zone_for_point(x: float, y: float, config: PlanConfig) -> tuple[str, str | None]:
    """Return the first configured polygon zone containing an image point."""
    for zone in config.color_zones:
        if _point_in_polygon(x, y, zone["polygon"]):
            return zone["zone_id"], zone.get("name")
    return "zone_unknown", None


def assign_candidate_spatial_fields(candidates: list[dict], config: PlanConfig) -> None:
    """Add configured grid and color-zone fields to candidates in place."""
    for candidate in candidates:
        bbox = candidate.get("bbox_image")
        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            candidate["grid_coordinate"] = "grid_unknown"
            candidate["color_zone_id"] = "zone_unknown"
            candidate["color_zone_name"] = None
            continue
        center_x = bbox[0] + bbox[2] / 2
        center_y = bbox[1] + bbox[3] / 2
        candidate["grid_coordinate"] = grid_coordinate_for_point(center_x, center_y, config)
        zone_id, zone_name = color_zone_for_point(center_x, center_y, config)
        candidate["color_zone_id"] = zone_id
        candidate["color_zone_name"] = zone_name
