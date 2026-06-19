"""Plan configuration model and loader."""

import json
from pathlib import Path
from typing import Any


def _positive_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{field} must be a positive number")
    return float(value)


def _grid_positions(value: Any, field: str) -> list[list[Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    positions: list[list[Any]] = []
    for item in value:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or isinstance(item[0], bool)
            or not isinstance(item[0], (int, float))
            or not isinstance(item[1], str)
            or not item[1]
        ):
            raise ValueError(f"{field} entries must be [pixel, label] pairs")
        positions.append([float(item[0]), item[1]])
    return positions


def _grid_points(value: Any) -> list[list[Any]]:
    if not isinstance(value, list):
        raise ValueError("grid.points must be a list")
    points: list[list[Any]] = []
    for item in value:
        if (
            not isinstance(item, list)
            or len(item) != 3
            or not all(isinstance(coordinate, (int, float)) for coordinate in item[:2])
            or not isinstance(item[2], str)
            or not item[2]
        ):
            raise ValueError("grid.points entries must be [x, y, label] triples")
        points.append([float(item[0]), float(item[1]), item[2]])
    return points


def _color_zones(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("color_zones must be a list")
    for zone in value:
        if not isinstance(zone, dict) or not isinstance(zone.get("zone_id"), str):
            raise ValueError("each color zone must have a string zone_id")
        polygon = zone.get("polygon")
        if not isinstance(polygon, list) or len(polygon) < 3:
            raise ValueError("each color zone polygon must contain at least three points")
        for point in polygon:
            if (
                not isinstance(point, list)
                or len(point) != 2
                or not all(isinstance(v, (int, float)) for v in point)
            ):
                raise ValueError("color zone points must be [x, y] pairs")
    return value


class PlanConfig:
    def __init__(self, plan_id: str, data: dict[str, Any] | None = None) -> None:
        self.plan_id = plan_id
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise ValueError("plan config must be a JSON object")
        if data.get("plan_id", plan_id) != plan_id:
            raise ValueError("plan_id must match the requested plan")

        self.scale = int(_positive_number(data.get("scale", 50), "scale"))
        self.default_height_cm = _positive_number(
            data.get("default_height_cm", 30.0), "default_height_cm"
        )

        grid_data = data.get("grid", {})
        if not isinstance(grid_data, dict):
            raise ValueError("grid must be an object")
        self.grid_anchors = grid_data.get("anchors")
        if self.grid_anchors is not None and not isinstance(self.grid_anchors, dict):
            raise ValueError("grid.anchors must be an object")
        self.column_positions = _grid_positions(
            grid_data.get("column_positions", []), "grid.column_positions"
        )
        self.row_positions = _grid_positions(
            grid_data.get("row_positions", []), "grid.row_positions"
        )
        self.grid_points = _grid_points(grid_data.get("points", []))
        self.color_zones = _color_zones(data.get("color_zones", []))

    @classmethod
    def load_for_plan(cls, project_root: Path, plan_id: str) -> "PlanConfig":
        config_path = project_root / "data" / "config" / f"{plan_id}_config.json"
        if not config_path.is_file():
            return cls(plan_id)

        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
            return cls(plan_id, data)
        except Exception as e:
            # Fall back to defaults on error
            print(f"Warning: Failed to load config for plan {plan_id}: {e}")
            return cls(plan_id)
