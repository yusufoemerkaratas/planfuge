from dataclasses import dataclass

GEOMETRY_ROUND = "round"
GEOMETRY_RECTANGULAR = "rectangular"

TYPE_CEILING = "Ceiling"
TYPE_WALL = "Wall"
TYPE_UNKNOWN = "Unknown"

STATUS_READY = "ready"
STATUS_REVIEW_REQUIRED = "review_required"
STATUS_SPLIT_RECOMMENDED = "split_recommended"


@dataclass(frozen=True)
class WeightConfig:
    density_kg_per_m3: float = 440
    max_weight_kg: float = 25


@dataclass(frozen=True)
class Opening:
    geometry: str
    length_cm: float
    width_cm: float
    height_cm: float
    quantity: int = 1
    opening_type: str = TYPE_UNKNOWN
    floor: str = "unknown"
    plan_name: str = "unknown"
    source_pdf: str = "unknown"
    grid_coordinate: str = "grid_unknown"
    color_zone_id: str = "zone_unknown"
    confidence: float | None = None
    review_required: bool = False
