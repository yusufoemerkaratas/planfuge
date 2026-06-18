import unittest
from src.candidates.png_candidate_extractor import extract_candidates_from_png_data, validate_candidate


class TestPngCandidateExtractor(unittest.TestCase):
    def setUp(self):
        self.crops_metadata = [
            {
                "region_id": "RED-001",
                "crop_path": "outputs/crops/SP_U1_0003_RED-001.png",
                "bbox_image": [10, 20, 30, 40],
                "crop_bbox_image": [0, 10, 40, 50]
            },
            {
                "region_id": "RED-002",
                "crop_path": "outputs/crops/SP_U1_0003_RED-002.png",
                "bbox_image": [100, 200, 50, 60],
                "crop_bbox_image": [90, 190, 70, 80]
            }
        ]

        self.ocr_results = [
            {
                "region_id": "RED-001",
                "crop_path": "outputs/crops/SP_U1_0003_RED-001.png",
                "ocr_text": "WDB 70/20 OK -60 UKRD",
                "ocr_available": True
            },
            {
                "region_id": "RED-002",
                "crop_path": "outputs/crops/SP_U1_0003_RED-002.png",
                "ocr_text": "Random Noise Text",
                "ocr_available": True
            }
        ]

    def test_extract_candidates_with_ocr(self):
        # RED-001 is parseable, RED-002 is unparseable
        candidates = extract_candidates_from_png_data(self.crops_metadata, self.ocr_results)

        self.assertEqual(len(candidates), 2)

        # RED-001 (parseable)
        c1 = candidates[0]
        self.assertEqual(c1["candidate_id"], "OP-001")
        self.assertEqual(c1["source"], "png_red_annotation_ocr")
        self.assertEqual(c1["label_type"], "WDB")
        self.assertEqual(c1["raw_text"], "WDB 70/20 OK -60 UKRD")
        self.assertEqual(c1["bbox_image"], [10, 20, 30, 40])
        self.assertEqual(c1["width_mm"], 700)
        self.assertEqual(c1["height_mm"], 200)
        self.assertIsNone(c1["diameter_mm"])
        self.assertIsNone(c1["ra_value"])
        self.assertEqual(c1["ok_value"], -60)
        self.assertEqual(c1["reference"], "UKRD")
        self.assertEqual(c1["confidence"], 0.85)
        self.assertEqual(c1["status"], "needs_review")

        # RED-002 (unparseable)
        c2 = candidates[1]
        self.assertEqual(c2["candidate_id"], "OP-002")
        self.assertEqual(c2["source"], "png_red_annotation_ocr")
        self.assertIsNone(c2["label_type"])
        self.assertEqual(c2["raw_text"], "Random Noise Text")
        self.assertEqual(c2["bbox_image"], [100, 200, 50, 60])
        self.assertIsNone(c2["width_mm"])
        self.assertIsNone(c2["height_mm"])
        self.assertIsNone(c2["diameter_mm"])
        self.assertIsNone(c2["ra_value"])
        self.assertIsNone(c2["ok_value"])
        self.assertIsNone(c2["reference"])
        self.assertEqual(c2["confidence"], 0.5)
        self.assertEqual(c2["status"], "needs_review")

    def test_extract_candidates_missing_ocr_results(self):
        # If ocr_results is None
        candidates = extract_candidates_from_png_data(self.crops_metadata, ocr_results=None)

        self.assertEqual(len(candidates), 2)
        for i, c in enumerate(candidates):
            self.assertEqual(c["candidate_id"], f"OP-{i+1:03d}")
            self.assertEqual(c["source"], "png_red_annotation_region")
            self.assertIsNone(c["label_type"])
            self.assertEqual(c["raw_text"], "")
            self.assertEqual(c["confidence"], 0.3)
            self.assertEqual(c["status"], "needs_review")

    def test_extract_candidates_empty_ocr_text(self):
        ocr_results_empty = [
            {
                "region_id": "RED-001",
                "crop_path": "outputs/crops/SP_U1_0003_RED-001.png",
                "ocr_text": "   ",
                "ocr_available": True
            }
        ]
        candidates = extract_candidates_from_png_data(self.crops_metadata[:1], ocr_results_empty)
        self.assertEqual(len(candidates), 1)
        c = candidates[0]
        self.assertEqual(c["raw_text"], "")
        self.assertEqual(c["confidence"], 0.3)
        self.assertEqual(c["source"], "png_red_annotation_ocr")

    def test_validate_candidate_valid(self):
        valid_candidate = {
            "candidate_id": "OP-001",
            "source": "png_red_annotation_ocr",
            "label_type": "WDB",
            "raw_text": "WDB 70/20 OK -60 UKRD",
            "bbox_image": [10, 20, 30, 40],
            "crop_path": "outputs/crops/SP_U1_0003_RED-001.png",
            "width_mm": 700,
            "height_mm": 200,
            "diameter_mm": None,
            "ra_value": None,
            "ok_value": -60,
            "reference": "UKRD",
            "confidence": 0.85,
            "status": "needs_review"
        }
        # Should not raise any exception
        validate_candidate(valid_candidate)

    def test_validate_candidate_invalid_types(self):
        # Invalid bbox_image type (not list of 4 numbers)
        invalid_bbox = {
            "candidate_id": "OP-001",
            "source": "png_red_annotation_ocr",
            "label_type": None,
            "raw_text": "",
            "bbox_image": "10,20,30,40",
            "crop_path": None,
            "width_mm": None,
            "height_mm": None,
            "diameter_mm": None,
            "ra_value": None,
            "ok_value": None,
            "reference": None,
            "confidence": 0.3,
            "status": "needs_review"
        }
        with self.assertRaises((TypeError, ValueError)):
            validate_candidate(invalid_bbox)

        # Invalid width_mm type (should be int or None)
        invalid_width = invalid_bbox.copy()
        invalid_width["bbox_image"] = [10, 20, 30, 40]
        invalid_width["width_mm"] = "700"
        with self.assertRaises((TypeError, ValueError)):
            validate_candidate(invalid_width)

        # Invalid status value
        invalid_status = invalid_bbox.copy()
        invalid_status["bbox_image"] = [10, 20, 30, 40]
        invalid_status["status"] = "unknown_status"
        with self.assertRaises((TypeError, ValueError)):
            validate_candidate(invalid_status)


if __name__ == "__main__":
    unittest.main()
