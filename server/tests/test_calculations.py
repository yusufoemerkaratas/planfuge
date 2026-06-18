import unittest

from server.app.models import (
    GEOMETRY_RECTANGULAR,
    GEOMETRY_ROUND,
    STATUS_READY,
    STATUS_SPLIT_RECOMMENDED,
    Opening,
    WeightConfig,
)
from server.app.services.calculations import calculate_weight_kg, get_review_status
from server.app.services.csv_export import CSV_COLUMNS, serialize_csv, to_csv_row


class OpeningCalculationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = WeightConfig(density_kg_per_m3=440, max_weight_kg=25)

    def test_calculates_rectangular_opening_weight_for_grouped_row(self) -> None:
        opening = Opening(
            geometry=GEOMETRY_RECTANGULAR,
            length_cm=20,
            width_cm=50,
            height_cm=25,
            quantity=2,
        )

        self.assertEqual(calculate_weight_kg(opening, self.config), 22)

    def test_calculates_round_opening_weight_using_diameter(self) -> None:
        opening = Opening(
            geometry=GEOMETRY_ROUND,
            length_cm=15,
            width_cm=15,
            height_cm=30,
            quantity=3,
        )

        self.assertEqual(calculate_weight_kg(opening, self.config), 7)

    def test_flags_rows_above_maximum_printable_weight(self) -> None:
        opening = Opening(
            geometry=GEOMETRY_RECTANGULAR,
            length_cm=80,
            width_cm=50,
            height_cm=35,
        )

        self.assertEqual(get_review_status(opening, self.config), STATUS_SPLIT_RECOMMENDED)

    def test_maps_opening_to_csv_contract(self) -> None:
        opening = Opening(
            floor="U1",
            plan_name="BFS_88160_A_T_5_SP_U1_0001_06",
            geometry=GEOMETRY_RECTANGULAR,
            opening_type="Ceiling",
            length_cm=20,
            width_cm=50,
            height_cm=25,
            quantity=2,
            source_pdf="SP_U1_0001.pdf",
            grid_coordinate="H-17",
            color_zone_id="zone-002",
            confidence=0.88,
        )

        row = to_csv_row(opening, self.config)

        self.assertEqual(list(row.keys()), CSV_COLUMNS)
        self.assertEqual(row["Weight/kg"], 22)
        self.assertEqual(row["Review status"], STATUS_READY)

    def test_serializes_csv_values_with_stable_column_order(self) -> None:
        row = {
            "Floor": "U1",
            "Construction phase/Plan name": "Plan, with comma",
            "Length/cm": 10,
            "Width/cm": 10,
            "Height/cm": 30,
            "Geometry": "round",
            "Type": "Ceiling",
            "Number": 3,
            "Weight/kg": 7,
            "Source PDF": "SP_U1_0001.pdf",
            "Grid coordinate": "M-21",
            "Color zone": "zone-001",
            "Confidence": 0.92,
            "Review status": "ready",
        }

        csv_body = serialize_csv([row])

        self.assertTrue(csv_body.startswith("Floor,Construction phase/Plan name,Length/cm"))
        self.assertIn('"Plan, with comma"', csv_body)


if __name__ == "__main__":
    unittest.main()

