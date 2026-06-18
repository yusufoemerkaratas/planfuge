import tempfile
import unittest
from pathlib import Path

from scripts.check_backend_inputs import check_backend_inputs, format_report


class BackendInputSmokeCheckTests(unittest.TestCase):
    def test_reports_available_and_missing_optional_files_without_failing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "data/pages").mkdir(parents=True)
            (root / "data/metadata").mkdir(parents=True)
            (root / "outputs/exports").mkdir(parents=True)
            (root / "data/pages/SP_U1_0003.png").touch()

            result = check_backend_inputs(root, "SP_U1_0003")
            report = format_report(result)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("[OK] data/pages/SP_U1_0003.png", report)
        self.assertIn("[WARN] data/metadata/SP_U1_0003_metadata.json", report)
        self.assertIn("[WARN] outputs/candidates/SP_U1_0003_candidates.json", report)
        self.assertIn("[OK] outputs/exports", report)

    def test_missing_plan_image_is_the_only_error_condition(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "data/pages").mkdir(parents=True)
            (root / "outputs/exports").mkdir(parents=True)

            result = check_backend_inputs(root, "SP_U1_9999")
            report = format_report(result)

        self.assertEqual(result.exit_code, 1)
        self.assertIn("[ERROR] data/pages/SP_U1_9999.png", report)
        self.assertIn("[OK] outputs/exports", report)

    def test_exports_path_must_be_a_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "data/pages").mkdir(parents=True)
            (root / "outputs").mkdir()
            (root / "data/pages/SP_U1_0003.png").touch()
            (root / "outputs/exports").touch()

            result = check_backend_inputs(root, "SP_U1_0003")
            report = format_report(result)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("[WARN] outputs/exports", report)


if __name__ == "__main__":
    unittest.main()
