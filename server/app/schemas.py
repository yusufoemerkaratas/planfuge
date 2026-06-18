from typing import ClassVar

from pydantic import BaseModel, Field, model_validator


class CamelCaseInputModel(BaseModel):
    aliases: ClassVar[dict[str, str]] = {
        "densityKgPerM3": "density_kg_per_m3",
        "maxWeightKg": "max_weight_kg",
        "lengthCm": "length_cm",
        "widthCm": "width_cm",
        "heightCm": "height_cm",
        "type": "opening_type",
        "planName": "plan_name",
        "sourcePdf": "source_pdf",
        "gridCoordinate": "grid_coordinate",
        "colorZoneId": "color_zone_id",
        "reviewRequired": "review_required",
    }

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data

        normalized = dict(data)
        for external_name, internal_name in cls.aliases.items():
            if external_name in normalized and internal_name not in normalized:
                normalized[internal_name] = normalized.pop(external_name)

        return normalized


class WeightConfigRequest(CamelCaseInputModel):
    density_kg_per_m3: float = 440
    max_weight_kg: float = 25


class OpeningRequest(CamelCaseInputModel):
    geometry: str
    length_cm: float
    width_cm: float
    height_cm: float
    quantity: int = 1
    opening_type: str = "Unknown"
    floor: str = "unknown"
    plan_name: str = "unknown"
    source_pdf: str = "unknown"
    grid_coordinate: str = "grid_unknown"
    color_zone_id: str = "zone_unknown"
    confidence: float | None = None
    review_required: bool = False


class CalculateOpeningRequest(OpeningRequest):
    config: WeightConfigRequest = Field(default_factory=WeightConfigRequest)


class CsvExportRequest(CamelCaseInputModel):
    openings: list[OpeningRequest] = Field(default_factory=list)
    config: WeightConfigRequest = Field(default_factory=WeightConfigRequest)
