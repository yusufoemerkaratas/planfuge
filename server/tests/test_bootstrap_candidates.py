import json
import tempfile
import unittest
from pathlib import Path

from scripts.bootstrap_candidates import bootstrap_candidates


class BootstrapCandidatesTests(unittest.TestCase):
    def test_generates_missing_candidate_files_from_tracked_pdf_words(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            words_dir = root / "data" / "words"
            words_dir.mkdir(parents=True)
            (words_dir / "SP_U1_0003_words.json").write_text(json.dumps([
                {
                    "text": "DDB130/140",
                    "x0": 5,
                    "y0": 7,
                    "x1": 80,
                    "y1": 20,
                    "page": 1,
                }
            ]))

            result = bootstrap_candidates(root)

            self.assertEqual(result, {"generated": 1, "existing": 0, "failed": 0})
            output_path = root / "outputs" / "candidates" / "SP_U1_0003_candidates.json"
            payload = json.loads(output_path.read_text())
            self.assertEqual(payload["candidate_count"], 1)
            self.assertIsNone(payload["candidates"][0]["diameter_mm"])
            self.assertEqual(payload["candidates"][0]["width_mm"], 1300)


if __name__ == "__main__":
    unittest.main()
