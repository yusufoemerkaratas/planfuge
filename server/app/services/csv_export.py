import csv
from io import StringIO

from server.app.models import Opening, WeightConfig
from server.app.services.calculations import calculate_weight_kg, get_review_status

CSV_COLUMNS = [
    "Floor",
    "Construction phase/Plan name",
    "Length/cm",
    "Width/cm",
    "Height/cm",
    "Geometry",
    "Type",
    "Number",
    "Weight/kg",
    "Source PDF",
    "Grid coordinate",
    "Color zone",
    "Confidence",
    "Review status",
]


def to_csv_row(opening: Opening, config: WeightConfig = WeightConfig()) -> dict[str, object]:
    return {
        "Floor": opening.floor,
        "Construction phase/Plan name": opening.plan_name,
        "Length/cm": opening.length_cm,
        "Width/cm": opening.width_cm,
        "Height/cm": opening.height_cm,
        "Geometry": opening.geometry,
        "Type": opening.opening_type,
        "Number": opening.quantity,
        "Weight/kg": calculate_weight_kg(opening, config),
        "Source PDF": opening.source_pdf,
        "Grid coordinate": opening.grid_coordinate,
        "Color zone": opening.color_zone_id,
        "Confidence": "" if opening.confidence is None else opening.confidence,
        "Review status": get_review_status(opening, config),
    }


def serialize_csv(rows: list[dict[str, object]]) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
