import unittest

from src.candidates.validation import compare_candidates_to_examples, compute_iou, is_center_inside


class TestValidation(unittest.TestCase):
    def test_compute_iou(self):
        # Equal boxes -> IoU = 1.0
        self.assertAlmostEqual(compute_iou([0, 0, 10, 10], [0, 0, 10, 10]), 1.0)
        # Non-overlapping -> IoU = 0.0
        self.assertEqual(compute_iou([0, 0, 10, 10], [20, 20, 5, 5]), 0.0)
        # Partial overlap
        # box1: [0, 0, 10, 10], area = 100
        # box2: [5, 0, 10, 10], area = 100
        # intersection: [5, 0, 5, 10], area = 50
        # union: 100 + 100 - 50 = 150
        # IoU: 50 / 150 = 0.333333
        self.assertAlmostEqual(compute_iou([0, 0, 10, 10], [5, 0, 10, 10]), 1 / 3)

    def test_is_center_inside(self):
        # Center of box1 is (5, 5). Box2 is [0, 0, 10, 10]. Center of box1 is inside box2.
        self.assertTrue(is_center_inside([0, 0, 10, 10], [0, 0, 10, 10]))
        # Center of box1 is (15, 15). Box2 is [0, 0, 10, 10]. Outside.
        self.assertFalse(is_center_inside([10, 10, 10, 10], [0, 0, 10, 10]))

    def test_compare_candidates_to_examples_matching(self):
        candidates = [
            {"candidate_id": "OP-001", "bbox_image": [10, 10, 20, 20], "raw_text": "WDB 50/50"},
            {"candidate_id": "OP-002", "bbox_image": [100, 100, 20, 20], "raw_text": "Random"},
        ]

        examples = [
            {
                "example_id": "EX-001",
                "rough_bbox_image": [12, 12, 18, 18],  # high overlap / center inside
                "is_opening_relevant": True,
                "expected_text": "WDB 50/50",
            },
            {
                "example_id": "EX-002",
                "rough_bbox_image": [200, 200, 10, 10],  # missed relevant
                "is_opening_relevant": True,
                "expected_text": "Missed Label",
            },
            {
                "example_id": "EX-003",
                "rough_bbox_image": [102, 102, 18, 18],  # matches a non-relevant
                "is_opening_relevant": False,
                "expected_text": "Comment Annotation",
            },
        ]

        report = compare_candidates_to_examples(candidates, examples, iou_threshold=0.1)

        # Relevant matches
        self.assertEqual(len(report["matched_relevant"]), 1)
        self.assertEqual(report["matched_relevant"][0]["example_id"], "EX-001")
        self.assertEqual(report["matched_relevant"][0]["candidate_id"], "OP-001")
        self.assertEqual(report["matched_relevant"][0]["expected_text"], "WDB 50/50")
        self.assertEqual(report["matched_relevant"][0]["raw_text"], "WDB 50/50")

        # Relevant misses
        self.assertEqual(len(report["missed_relevant"]), 1)
        self.assertEqual(report["missed_relevant"][0]["example_id"], "EX-002")

        # Non-relevant matches
        self.assertEqual(len(report["matched_non_relevant"]), 1)
        self.assertEqual(report["matched_non_relevant"][0]["example_id"], "EX-003")
        self.assertEqual(report["matched_non_relevant"][0]["candidate_id"], "OP-002")

        # Non-relevant unmatched
        self.assertEqual(len(report["unmatched_non_relevant"]), 0)

        # Unmatched candidates detections
        # Candidate OP-001 matched EX-001. Candidate OP-002 matched EX-003. So 0 unmatched candidates.
        self.assertEqual(len(report["unmatched_candidates"]), 0)

    def test_compare_candidates_to_examples_unmatched_candidates(self):
        candidates = [
            {
                "candidate_id": "OP-001",
                "bbox_image": [500, 500, 20, 20],
                "raw_text": "New Detection",
            }
        ]
        examples = []

        report = compare_candidates_to_examples(candidates, examples)
        self.assertEqual(len(report["unmatched_candidates"]), 1)
        self.assertEqual(report["unmatched_candidates"][0]["candidate_id"], "OP-001")


if __name__ == "__main__":
    unittest.main()
