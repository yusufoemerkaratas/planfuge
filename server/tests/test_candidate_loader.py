import json
import tempfile
import unittest
from pathlib import Path

from server.app.services.candidate_loader import load_candidates, load_reviewed_candidates


class CandidateLoaderTests(unittest.TestCase):
    def test_loads_valid_candidate_json_and_returns_validated_result(self) -> None:
        payload = {
            "plan_id": "SP_U1_0003",
            "candidates": [
                {
                    "candidate_id": "cand-001",
                    "source": "cv",
                    "bbox_image": [10, 20, 30, 40],
                    "status": "needs_review",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidates_dir = root / "outputs" / "candidates"
            candidates_dir.mkdir(parents=True)
            candidate_file = candidates_dir / "SP_U1_0003_candidates.json"
            candidate_file.write_text(json.dumps(payload))

            result = load_candidates(root, "SP_U1_0003")

        self.assertEqual(result.plan_id, "SP_U1_0003")
        self.assertEqual(result.candidate_count, 1)
        self.assertEqual(result.candidates[0]["candidate_id"], "cand-001")
        self.assertEqual(result.errors, [])
        self.assertEqual(result.source, "file")

    def test_missing_file_returns_warning_and_empty_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            result = load_candidates(root, "SP_U1_9999")

        self.assertEqual(result.plan_id, "SP_U1_9999")
        self.assertEqual(result.candidate_count, 0)
        self.assertEqual(result.candidates, [])
        self.assertEqual(result.source, "empty")
        self.assertTrue(any("not found" in w for w in result.warnings))
        self.assertEqual(result.errors, [])

    def test_malformed_json_returns_error_and_empty_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidates_dir = root / "outputs" / "candidates"
            candidates_dir.mkdir(parents=True)
            candidate_file = candidates_dir / "SP_U1_0003_candidates.json"
            candidate_file.write_text("{broken json!!!")

            result = load_candidates(root, "SP_U1_0003")

        self.assertEqual(result.plan_id, "SP_U1_0003")
        self.assertEqual(result.candidate_count, 0)
        self.assertEqual(result.candidates, [])
        self.assertTrue(any("failed to read" in e for e in result.errors))

    def test_invalid_candidates_propagate_validation_errors(self) -> None:
        payload = {
            "plan_id": "SP_U1_0003",
            "candidates": [{"candidate_id": "bad-001", "status": "needs_review"}],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidates_dir = root / "outputs" / "candidates"
            candidates_dir.mkdir(parents=True)
            candidate_file = candidates_dir / "SP_U1_0003_candidates.json"
            candidate_file.write_text(json.dumps(payload))

            result = load_candidates(root, "SP_U1_0003")

        self.assertEqual(result.candidates, [])
        self.assertTrue(any("missing required field source" in e for e in result.errors))
        self.assertEqual(result.source, "file")

    def test_optional_fields_are_filled_with_null(self) -> None:
        payload = {
            "plan_id": "SP_U1_0003",
            "candidates": [
                {
                    "candidate_id": "cand-005",
                    "source": "cv",
                    "bbox_image": [10, 20, 30, 40],
                    "status": "needs_review",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidates_dir = root / "outputs" / "candidates"
            candidates_dir.mkdir(parents=True)
            candidate_file = candidates_dir / "SP_U1_0003_candidates.json"
            candidate_file.write_text(json.dumps(payload))

            result = load_candidates(root, "SP_U1_0003")

        self.assertIsNone(result.candidates[0]["raw_text"])
        self.assertIsNone(result.candidates[0]["label_type"])
        self.assertTrue(any("missing optional field" in w for w in result.warnings))

    def test_filters_legacy_unparsed_ocr_regions_from_raw_candidates(self) -> None:
        payload = {
            "plan_id": "SP_U1_0003",
            "candidates": [
                {
                    "candidate_id": "opening",
                    "source": "png_red_annotation_ocr",
                    "label_type": "WDB",
                    "width_mm": 700,
                    "height_mm": 200,
                    "bbox_image": [10, 20, 30, 40],
                    "status": "needs_review",
                },
                {
                    "candidate_id": "noise",
                    "source": "png_red_annotation_ocr",
                    "label_type": None,
                    "bbox_image": [50, 60, 30, 40],
                    "status": "needs_review",
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidates_dir = root / "outputs" / "candidates"
            candidates_dir.mkdir(parents=True)
            (candidates_dir / "SP_U1_0003_candidates.json").write_text(json.dumps(payload))

            result = load_candidates(root, "SP_U1_0003")

        self.assertEqual(result.candidate_count, 1)
        self.assertEqual(result.candidates[0]["candidate_id"], "opening")

    def test_filters_measurement_free_pdf_word_candidates(self) -> None:
        payload = {
            "plan_id": "SP_U1_0003",
            "candidates": [
                {
                    "candidate_id": "no-geometry",
                    "source": "pdf_words",
                    "label_type": "WDB",
                    "bbox_image": [10, 20, 30, 40],
                    "status": "needs_review",
                },
                {
                    "candidate_id": "with-geometry",
                    "source": "pdf_words",
                    "label_type": "DDB",
                    "width_mm": 300,
                    "height_mm": 400,
                    "bbox_image": [50, 60, 30, 40],
                    "status": "needs_review",
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidates_dir = root / "outputs" / "candidates"
            candidates_dir.mkdir(parents=True)
            (candidates_dir / "SP_U1_0003_candidates.json").write_text(json.dumps(payload))

            result = load_candidates(root, "SP_U1_0003")

        self.assertEqual(result.candidate_count, 1)
        self.assertEqual(result.candidates[0]["candidate_id"], "with-geometry")

    def test_keeps_unparsed_regions_in_saved_reviews(self) -> None:
        payload = {
            "plan_id": "SP_U1_0003",
            "candidates": [
                {
                    "candidate_id": "reviewed-noise",
                    "source": "png_red_annotation_ocr",
                    "label_type": None,
                    "bbox_image": [50, 60, 30, 40],
                    "status": "rejected",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            reviews_dir = root / "outputs" / "reviews"
            reviews_dir.mkdir(parents=True)
            (reviews_dir / "SP_U1_0003_reviewed_candidates.json").write_text(json.dumps(payload))

            result = load_reviewed_candidates(root, "SP_U1_0003")

        self.assertEqual(result.candidate_count, 1)


if __name__ == "__main__":
    unittest.main()
