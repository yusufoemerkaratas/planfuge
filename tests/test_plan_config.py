import json
import tempfile
import unittest
from pathlib import Path

from src.config.plan_config import PlanConfig


class PlanConfigTests(unittest.TestCase):
    def test_loads_and_validates_complete_plan_config(self) -> None:
        payload = {
            "plan_id": "SP_U1_0005",
            "scale": 50,
            "default_height_cm": 25,
            "grid": {
                "anchors": {
                    "top_left_pixel": [0, 0],
                    "top_left_coord": "A-1",
                    "bottom_right_pixel": [1000, 1000],
                    "bottom_right_coord": "B-2",
                },
                "column_positions": [[0, "A"], [1000, "B"]],
                "row_positions": [[0, "1"], [1000, "2"]],
            },
            "color_zones": [
                {"zone_id": "zone-1", "polygon": [[0, 0], [100, 0], [100, 100], [0, 100]]}
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "data" / "config"
            config_dir.mkdir(parents=True)
            (config_dir / "SP_U1_0005_config.json").write_text(json.dumps(payload))

            config = PlanConfig.load_for_plan(root, "SP_U1_0005")

        self.assertEqual(config.scale, 50)
        self.assertEqual(config.default_height_cm, 25.0)
        self.assertEqual(config.column_positions, [[0.0, "A"], [1000.0, "B"]])
        self.assertEqual(config.color_zones[0]["zone_id"], "zone-1")

    def test_invalid_schema_falls_back_to_safe_defaults(self) -> None:
        payload = {
            "plan_id": "WRONG_PLAN",
            "scale": -50,
            "default_height_cm": 0,
            "grid": {"column_positions": {"bad": "shape"}},
            "color_zones": "not-a-list",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "data" / "config"
            config_dir.mkdir(parents=True)
            (config_dir / "SP_U1_0005_config.json").write_text(json.dumps(payload))

            config = PlanConfig.load_for_plan(root, "SP_U1_0005")

        self.assertEqual(config.plan_id, "SP_U1_0005")
        self.assertEqual(config.scale, 50)
        self.assertEqual(config.default_height_cm, 30.0)
        self.assertEqual(config.column_positions, [])
        self.assertEqual(config.color_zones, [])


if __name__ == "__main__":
    unittest.main()
