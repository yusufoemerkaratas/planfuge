import json
import tempfile
import unittest
from pathlib import Path

from server.app.services.review_saver import save_reviewed_candidates


class ReviewSaverTests(unittest.TestCase):
    def test_saves_candidates_with_timestamp_and_creates_directory(self) -> None:
        candidates = [
            {"candidate_id": "cand-001", "status": "verified"},
            {"candidate_id": "cand-002", "status": "rejected"},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            result = save_reviewed_candidates(root, "SP_U1_0003", candidates)

            self.assertEqual(result["status"], "success")
            self.assertTrue(result["path"].endswith("SP_U1_0003_reviewed_candidates.json"))

            # Verify file was written correctly
            saved_file = Path(result["path"])
            self.assertTrue(saved_file.exists())

            payload = json.loads(saved_file.read_text())
            self.assertEqual(payload["plan_id"], "SP_U1_0003")
            self.assertEqual(payload["candidate_count"], 2)
            self.assertIn("saved_at", payload)
            self.assertEqual(len(payload["candidates"]), 2)
            self.assertEqual(payload["candidates"][0]["candidate_id"], "cand-001")

    def test_saves_empty_candidates_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            result = save_reviewed_candidates(root, "SP_U1_0003", [])

            saved_file = Path(result["path"])
            self.assertTrue(saved_file.exists())

            payload = json.loads(saved_file.read_text())
            self.assertEqual(payload["candidate_count"], 0)
            self.assertEqual(payload["candidates"], [])


if __name__ == "__main__":
    unittest.main()
