import json
import tempfile
import unittest
from pathlib import Path

from server.app.services.candidate_loader import load_sample_candidates

SAMPLE_PAYLOAD = {
    "plan_id": "SAMPLE_DEMO",
    "candidate_count": 3,
    "candidates": [
        {
            "candidate_id": "sample-wdb-001",
            "source": "sample",
            "label_type": "WDB",
            "raw_text": "WDB 20/50 d=25",
            "bbox_image": [1200, 3400, 180, 90],
            "status": "needs_review",
        },
        {
            "candidate_id": "sample-ddb-002",
            "source": "sample",
            "label_type": "DDB",
            "raw_text": "DDB d=60",
            "bbox_image": [4500, 2100, 150, 75],
            "status": "needs_review",
        },
        {
            "candidate_id": "sample-unknown-003",
            "source": "sample",
            "raw_text": "??? 15/30",
            "bbox_image": [7800, 5200, 200, 100],
            "confidence": 0.42,
            "status": "needs_review",
        },
    ],
}


class SampleCandidateTests(unittest.TestCase):
    def test_loads_sample_candidates_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            samples_dir = root / "data" / "samples"
            samples_dir.mkdir(parents=True)
            sample_file = samples_dir / "sample_candidates.json"
            sample_file.write_text(json.dumps(SAMPLE_PAYLOAD))

            result = load_sample_candidates(root)

        self.assertEqual(result.plan_id, "SAMPLE_DEMO")
        self.assertEqual(result.candidate_count, 3)
        self.assertEqual(result.source, "sample")

    def test_sample_data_is_labeled_as_sample_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            samples_dir = root / "data" / "samples"
            samples_dir.mkdir(parents=True)
            sample_file = samples_dir / "sample_candidates.json"
            sample_file.write_text(json.dumps(SAMPLE_PAYLOAD))

            result = load_sample_candidates(root)

        self.assertEqual(result.source, "sample")
        for candidate in result.candidates:
            self.assertEqual(candidate["source"], "sample")

    def test_sample_mode_does_not_use_real_candidates_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            samples_dir = root / "data" / "samples"
            samples_dir.mkdir(parents=True)
            sample_file = samples_dir / "sample_candidates.json"
            sample_file.write_text(json.dumps(SAMPLE_PAYLOAD))

            # Also create a real candidate file — should NOT be loaded
            real_dir = root / "outputs" / "candidates"
            real_dir.mkdir(parents=True)
            real_file = real_dir / "SAMPLE_DEMO_candidates.json"
            real_file.write_text(json.dumps({"plan_id": "SAMPLE_DEMO", "candidates": []}))

            result = load_sample_candidates(root)

        self.assertEqual(result.source, "sample")
        self.assertEqual(result.candidate_count, 3)

    def test_missing_sample_file_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            result = load_sample_candidates(root)

        self.assertEqual(result.candidate_count, 0)
        self.assertTrue(any("not found" in e for e in result.errors))


if __name__ == "__main__":
    unittest.main()
