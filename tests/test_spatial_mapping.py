import unittest
import csv
import tempfile
from pathlib import Path
import json

from server.app.services.contract_candidate_export import export_contract_openings_csv
from src.config.plan_config import PlanConfig
from src.config.spatial_mapping import (
    assign_candidate_spatial_fields,
    color_zone_for_point,
    grid_coordinate_for_point,
)


class SpatialMappingTests(unittest.TestCase):
    def test_maps_candidate_on_rotated_grid_using_control_points(self) -> None:
        config = PlanConfig(
            "SP_U1_0005",
            {
                "plan_id": "SP_U1_0005",
                "grid": {
                    "points": [
                        [100, 100, "A-1"],
                        [200, 120, "B-1"],
                        [80, 200, "A-2"],
                        [180, 220, "B-2"],
                    ]
                },
            },
        )

        self.assertEqual(grid_coordinate_for_point(176, 216, config), "B-2")

    def test_adds_grid_coordinate_to_candidate_output(self) -> None:
        config = PlanConfig(
            "SP_U1_0005",
            {
                "plan_id": "SP_U1_0005",
                "grid": {
                    "column_positions": [[0, "G"], [100, "H"]],
                    "row_positions": [[0, "16"], [100, "17"]],
                },
            },
        )
        candidates = [{"candidate_id": "OP-001", "bbox_image": [90, 90, 20, 20]}]

        assign_candidate_spatial_fields(candidates, config)

        self.assertEqual(candidates[0]["grid_coordinate"], "H-17")

    def test_maps_inside_border_and_outside_polygon_points(self) -> None:
        config = PlanConfig(
            "SP_U1_0005",
            {
                "plan_id": "SP_U1_0005",
                "color_zones": [
                    {
                        "zone_id": "phase-red",
                        "name": "Red phase",
                        "polygon": [[0, 0], [100, 0], [100, 100], [0, 100]],
                    }
                ],
            },
        )

        self.assertEqual(color_zone_for_point(50, 50, config)[0], "phase-red")
        self.assertEqual(color_zone_for_point(100, 50, config)[0], "phase-red")
        self.assertEqual(color_zone_for_point(101, 50, config), ("zone_unknown", None))

        candidates = [{"bbox_image": [40, 40, 20, 20]}]
        assign_candidate_spatial_fields(candidates, config)
        self.assertEqual(candidates[0]["color_zone_id"], "phase-red")
        self.assertEqual(candidates[0]["color_zone_name"], "Red phase")

    def test_contract_csv_contains_configured_grid_coordinate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "data" / "config"
            config_dir.mkdir(parents=True)
            (config_dir / "SP_U1_0005_config.json").write_text(
                json.dumps(
                    {
                        "plan_id": "SP_U1_0005",
                        "grid": {
                            "column_positions": [[0, "G"], [100, "H"]],
                            "row_positions": [[0, "16"], [100, "17"]],
                        },
                        "color_zones": [
                            {
                                "zone_id": "phase-red",
                                "polygon": [[80, 80], [120, 80], [120, 120], [80, 120]],
                            }
                        ],
                    }
                )
            )
            export_contract_openings_csv(
                root,
                "SP_U1_0005",
                [{"bbox_image": [90, 90, 20, 20], "diameter_mm": 100, "status": "verified"}],
            )
            export_path = root / "outputs" / "exports" / "SP_U1_0005_verified_openings.csv"
            with export_path.open(newline="") as exported_file:
                row = next(csv.DictReader(exported_file))

        self.assertEqual(row["Grid coordinate"], "H-17")
        self.assertEqual(row["Color zone"], "phase-red")


if __name__ == "__main__":
    unittest.main()
