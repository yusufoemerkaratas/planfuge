import json
import tempfile
import unittest
from pathlib import Path

from server.app.services.metadata_loader import load_metadata


class MetadataLoaderTests(unittest.TestCase):
    def test_loads_valid_metadata_json(self) -> None:
        payload = {
            "plan_id": "SP_U1_0002",
            "file_path": "data/pages/SP_U1_0002.png",
            "image_width_px": 18896,
            "image_height_px": 9934,
            "source_type": "rendered_png",
            "original_pdf_available": True,
            "scale_text_visible": "M1:50",
            "contains_red_markups": True,
            "notes": "",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            metadata_dir = root / "data" / "metadata"
            metadata_dir.mkdir(parents=True)
            metadata_file = metadata_dir / "SP_U1_0002_metadata.json"
            metadata_file.write_text(json.dumps(payload))

            result = load_metadata(root, "SP_U1_0002")

        self.assertEqual(result.plan_id, "SP_U1_0002")
        self.assertTrue(result.exists)
        self.assertEqual(result.metadata["image_width_px"], 18896)
        self.assertEqual(result.metadata["scale_text_visible"], "M1:50")
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_missing_file_returns_warning_and_exists_false(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            result = load_metadata(root, "SP_U1_9999")

        self.assertFalse(result.exists)
        self.assertEqual(result.metadata, {})
        self.assertTrue(any("not found" in w for w in result.warnings))

    def test_malformed_json_returns_error_and_exists_false(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            metadata_dir = root / "data" / "metadata"
            metadata_dir.mkdir(parents=True)
            metadata_file = metadata_dir / "SP_U1_0002_metadata.json"
            metadata_file.write_text("{broken json!!!")

            result = load_metadata(root, "SP_U1_0002")

        self.assertFalse(result.exists)
        self.assertEqual(result.metadata, {})
        self.assertTrue(any("failed to read" in e for e in result.errors))

    def test_non_dict_json_returns_error_and_exists_false(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            metadata_dir = root / "data" / "metadata"
            metadata_dir.mkdir(parents=True)
            metadata_file = metadata_dir / "SP_U1_0002_metadata.json"
            metadata_file.write_text('["not", "a", "dict"]')

            result = load_metadata(root, "SP_U1_0002")

        self.assertFalse(result.exists)
        self.assertEqual(result.metadata, {})
        self.assertTrue(any("must contain a JSON object" in e for e in result.errors))


if __name__ == "__main__":
    unittest.main()
