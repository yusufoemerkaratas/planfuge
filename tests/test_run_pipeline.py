from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import fitz

from scripts.run_pipeline_on_pdfs import process_pdf


class CallablePipelineTests(unittest.TestCase):
    def test_process_pdf_uses_explicit_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pdf_path = root / "data" / "imports" / "test_plan.pdf"
            pdf_path.parent.mkdir(parents=True)

            document = fitz.open()
            page = document.new_page()
            page.insert_text((72, 72), "WDB 20/30")
            document.save(pdf_path)
            document.close()

            export_path = root / "outputs" / "exports" / "test_plan.csv"
            export_path.parent.mkdir(parents=True)
            export_path.write_text("header\n", encoding="utf-8")

            def draw_overlay(*, output_path, **_kwargs) -> None:
                Path(output_path).write_bytes(b"overlay")

            with (
                patch("scripts.run_pipeline_on_pdfs.auto_generate_config"),
                patch("scripts.run_pipeline_on_pdfs.run_png_extraction_pipeline", return_value=[]),
                patch(
                    "scripts.run_pipeline_on_pdfs.export_contract_openings_csv",
                    return_value={"path": str(export_path)},
                ),
                patch(
                    "src.candidates.overlay_drawer.draw_candidates_overlay",
                    side_effect=draw_overlay,
                ),
            ):
                result = process_pdf(pdf_path, project_root=root)

            self.assertEqual(result["plan_id"], "test_plan")
            self.assertTrue((root / "data" / "words" / "test_plan_words.json").is_file())
            self.assertTrue((root / "outputs" / "rendered" / "test_plan.png").is_file())
            self.assertTrue((root / "outputs" / "overlays" / "test_plan_overlay.png").is_file())


if __name__ == "__main__":
    unittest.main()
