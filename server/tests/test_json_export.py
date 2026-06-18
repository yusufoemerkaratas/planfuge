import json
import tempfile
import unittest
from pathlib import Path

from server.app.services.json_export import export_verified_openings


class JsonExportTests(unittest.TestCase):
    def test_export_filters_only_verified_and_strips_extra_fields(self) -> None:
        candidates = [
            {
                "candidate_id": "cand-001",
                "source": "cv",
                "status": "verified",
                "width_mm": 100,
                "extra_field": "should be stripped",
            },
            {
                "candidate_id": "cand-002",
                "source": "cv",
                "status": "rejected",
                "width_mm": 200,
            },
            {
                "candidate_id": "cand-003",
                "source": "cv",
                "status": "needs_review",
                "width_mm": 300,
            },
            {
                "candidate_id": "cand-004",
                "source": "cv",
                "status": "verified",
                "width_mm": 400,
                "height_mm": 500,
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = export_verified_openings(root, "SP_U1_0004", candidates)

            self.assertEqual(result["status"], "success")
            self.assertTrue(result["path"].endswith("SP_U1_0004_verified_openings.json"))

            saved_file = Path(result["path"])
            self.assertTrue(saved_file.exists())

            payload = json.loads(saved_file.read_text())
            self.assertEqual(payload["plan_id"], "SP_U1_0004")
            self.assertEqual(payload["opening_count"], 2)
            self.assertIn("exported_at", payload)

            openings = payload["openings"]
            self.assertEqual(len(openings), 2)
            
            # Verify filtering
            self.assertEqual(openings[0]["candidate_id"], "cand-001")
            self.assertEqual(openings[1]["candidate_id"], "cand-004")

            # Verify field stripping
            self.assertNotIn("extra_field", openings[0])
            self.assertNotIn("status", openings[0])  # Status shouldn't be in the final export per issue
            self.assertIn("width_mm", openings[0])
            self.assertIn("height_mm", openings[1])

    def test_export_empty_verified_list(self) -> None:
        candidates = [
            {
                "candidate_id": "cand-001",
                "status": "rejected",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = export_verified_openings(root, "SP_U1_0004", candidates)
            
            saved_file = Path(result["path"])
            payload = json.loads(saved_file.read_text())

            self.assertEqual(payload["opening_count"], 0)
            self.assertEqual(payload["openings"], [])


if __name__ == "__main__":
    unittest.main()
