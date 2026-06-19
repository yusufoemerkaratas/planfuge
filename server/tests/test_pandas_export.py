import tempfile
import unittest
from pathlib import Path

import pandas as pd

from server.app.services.pandas_export import export_verified_openings_csv


class PandasExportTests(unittest.TestCase):
    def test_export_filters_only_verified_and_formats_columns(self) -> None:
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
                "candidate_id": "cand-004",
                "source": "cv",
                "status": "verified",
                "width_mm": 400,
                "height_mm": 500,
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = export_verified_openings_csv(root, "SP_U1_0006", candidates)

            self.assertEqual(result["status"], "success")
            self.assertTrue(result["path"].endswith("SP_U1_0006_verified_openings.csv"))
            self.assertEqual(result["exported_count"], 2)

            saved_file = Path(result["path"])
            self.assertTrue(saved_file.exists())

            # Verify using pandas
            df = pd.read_csv(saved_file)
            self.assertEqual(len(df), 2)

            columns = list(df.columns)
            self.assertIn("candidate_id", columns)
            self.assertIn("source", columns)
            self.assertIn("width_mm", columns)
            self.assertNotIn("extra_field", columns)
            self.assertNotIn("status", columns)

            # Check data
            self.assertEqual(df.iloc[0]["candidate_id"], "cand-001")
            self.assertEqual(df.iloc[1]["candidate_id"], "cand-004")
            self.assertEqual(df.iloc[0]["width_mm"], 100.0)
            self.assertEqual(df.iloc[1]["width_mm"], 400.0)
            self.assertEqual(df.iloc[1]["height_mm"], 500.0)

            # Missing columns like diameter_mm should be created and be NaN/empty
            self.assertTrue("diameter_mm" in columns)
            self.assertTrue(pd.isna(df.iloc[0]["diameter_mm"]))

    def test_export_empty_verified_list(self) -> None:
        candidates = [
            {
                "candidate_id": "cand-001",
                "status": "rejected",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = export_verified_openings_csv(root, "SP_U1_0006", candidates)

            self.assertEqual(result["exported_count"], 0)

            saved_file = Path(result["path"])
            df = pd.read_csv(saved_file)
            self.assertEqual(len(df), 0)

            columns = list(df.columns)
            self.assertIn("candidate_id", columns)
            self.assertIn("width_mm", columns)


if __name__ == "__main__":
    unittest.main()
