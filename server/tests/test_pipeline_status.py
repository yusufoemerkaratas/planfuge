import tempfile
import unittest
from pathlib import Path

from server.app.services.pipeline_status import check_pipeline_status


class PipelineStatusTests(unittest.TestCase):
    def test_empty_state_returns_all_false(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = check_pipeline_status(root, "SP_U1_0009")

            self.assertEqual(result["plan_id"], "SP_U1_0009")
            files = result["files"]
            self.assertFalse(files["page_image"])
            self.assertFalse(files["metadata_json"])
            self.assertFalse(files["candidates_json"])
            self.assertFalse(files["crops_dir"])
            self.assertFalse(files["overlay_image"])
            self.assertFalse(files["review_json"])
            self.assertFalse(files["export_json"])
            self.assertFalse(files["export_csv"])

    def test_partial_state_returns_correct_flags(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create some dummy files
            (root / "data" / "pages").mkdir(parents=True)
            (root / "data" / "pages" / "SP_U1_0009.png").touch()

            (root / "outputs" / "crops").mkdir(parents=True)

            (root / "outputs" / "exports").mkdir(parents=True)
            (root / "outputs" / "exports" / "SP_U1_0009_verified_openings.csv").touch()

            result = check_pipeline_status(root, "SP_U1_0009")
            files = result["files"]

            self.assertTrue(files["page_image"])
            self.assertFalse(files["metadata_json"])
            self.assertFalse(files["candidates_json"])
            self.assertTrue(files["crops_dir"])
            self.assertFalse(files["overlay_image"])
            self.assertFalse(files["review_json"])
            self.assertFalse(files["export_json"])
            self.assertTrue(files["export_csv"])


if __name__ == "__main__":
    unittest.main()
