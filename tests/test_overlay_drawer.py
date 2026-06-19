import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image


class OverlayDrawerTests(unittest.TestCase):
    def test_draw_candidates_overlay(self) -> None:
        from src.candidates.overlay_drawer import draw_candidates_overlay

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            
            # Create a mock plan PNG
            img = Image.new("RGB", (1000, 1000), color="white")
            image_path = root / "mock_plan.png"
            img.save(image_path)

            # Create mock candidates JSON
            candidates_data = {
                "plan_id": "mock_plan",
                "candidates": [
                    {
                        "candidate_id": "cand-001",
                        "bbox_image": [100, 150, 200, 100],
                        "status": "needs_review"
                    },
                    {
                        "candidate_id": "cand-002",
                        "bbox_image": [400, 500, 50, 50],
                        "status": "verified"
                    }
                ]
            }
            candidates_path = root / "mock_candidates.json"
            candidates_path.write_text(json.dumps(candidates_data), encoding="utf-8")

            output_path = root / "mock_overlay.png"

            # Execute drawer
            draw_candidates_overlay(image_path, candidates_path, output_path)

            # Assert output exists
            self.assertTrue(output_path.is_file())

            # Load generated overlay and check dimensions
            with Image.open(output_path) as overlay_img:
                self.assertEqual(overlay_img.size, (1000, 1000))


if __name__ == "__main__":
    unittest.main()
