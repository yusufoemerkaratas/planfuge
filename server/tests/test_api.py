import csv
import io
import json
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from fastapi import HTTPException

from server.app.api import (
    app,
    calculate_opening,
    export_verified_csv_endpoint,
    export_verified_json_endpoint,
    get_candidate_crop_image,
    get_candidate_crop_image_from_pdf_bbox,
    get_candidates,
    get_crop_image,
    get_metadata,
    get_overlay_image,
    get_pipeline_status,
    get_plan_image,
    get_plans,
    get_reviews,
    get_sample_candidates,
    health,
    openings_csv,
    save_reviews,
)
from server.app.schemas import CalculateOpeningRequest, CsvExportRequest


class ApiTests(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        response = health()

        self.assertEqual(response["status"], "ok")

    def test_calculate_endpoint_returns_weight_and_csv_row(self) -> None:
        request = CalculateOpeningRequest.model_validate(
            {
                "geometry": "rectangular",
                "lengthCm": 20,
                "widthCm": 50,
                "heightCm": 25,
                "quantity": 2,
                "type": "Ceiling",
            }
        )

        response = calculate_opening(request)

        self.assertEqual(response["weightKg"], 22)
        self.assertEqual(response["reviewStatus"], "ready")
        self.assertEqual(response["csvRow"]["Type"], "Ceiling")

    def test_csv_endpoint_returns_csv(self) -> None:
        request = CsvExportRequest.model_validate(
            {
                "openings": [
                    {
                        "geometry": "round",
                        "lengthCm": 15,
                        "widthCm": 15,
                        "heightCm": 30,
                        "quantity": 3,
                    }
                ]
            }
        )

        response = openings_csv(request)
        body = response.body.decode("utf-8")

        self.assertIn("text/csv", response.media_type)
        self.assertTrue(body.startswith("Floor,Construction phase/Plan name"))
        self.assertIn("round", body)

    def test_candidates_endpoint_loads_valid_candidates(self) -> None:
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

            app.state.project_root = root
            data = get_candidates("SP_U1_0003")

        self.assertEqual(data["plan_id"], "SP_U1_0003")
        self.assertEqual(data["candidate_count"], 1)
        self.assertEqual(data["source"], "file")
        self.assertEqual(data["candidates"][0]["candidate_id"], "cand-001")

    def test_candidates_endpoint_missing_file_returns_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            app.state.project_root = root
            data = get_candidates("SP_U1_9999")

        self.assertEqual(data["candidate_count"], 0)
        self.assertTrue(any("not found" in w for w in data["warnings"]))

    def test_candidate_crop_is_rendered_from_current_bbox(self) -> None:
        from PIL import Image

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pages_dir = root / "data" / "pages"
            pages_dir.mkdir(parents=True)
            source = Image.new("RGB", (100, 80), "white")
            source.paste("red", (20, 10, 40, 30))
            source.save(pages_dir / "PLAN-1.png")
            app.state.project_root = root

            response = get_candidate_crop_image("PLAN-1", 20, 10, 20, 20, padding=5)
            rendered = Image.open(io.BytesIO(response.body))

        self.assertEqual(rendered.size, (30, 30))
        self.assertEqual(rendered.getpixel((5, 5)), (255, 0, 0))

    def test_candidate_crop_is_rendered_from_pdf_bbox(self) -> None:
        from PIL import Image

        scale = 300 / 72
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pages_dir = root / "data" / "pages"
            pages_dir.mkdir(parents=True)
            source = Image.new("RGB", (100, 80), "white")
            source.paste("red", (20, 10, 40, 30))
            source.save(pages_dir / "PLAN-2.png")
            app.state.project_root = root

            response = get_candidate_crop_image_from_pdf_bbox(
                "PLAN-2",
                20 / scale,
                10 / scale,
                40 / scale,
                30 / scale,
                padding=5,
            )
            rendered = Image.open(io.BytesIO(response.body))

        self.assertEqual(rendered.size, (30, 30))
        self.assertEqual(rendered.getpixel((5, 5)), (255, 0, 0))

    def test_large_plan_images_disable_pillow_pixel_limit(self) -> None:
        from PIL import Image

        self.assertIsNone(Image.MAX_IMAGE_PIXELS)

    def test_candidate_crop_rejects_bbox_outside_image(self) -> None:
        from PIL import Image

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pages_dir = root / "data" / "pages"
            pages_dir.mkdir(parents=True)
            Image.new("RGB", (20, 20), "white").save(pages_dir / "PLAN-1.png")
            app.state.project_root = root

            with self.assertRaises(HTTPException) as raised:
                get_candidate_crop_image("PLAN-1", 30, 30, 5, 5, padding=0)

        self.assertEqual(raised.exception.status_code, 422)

    def test_sample_candidates_endpoint_returns_sample_data(self) -> None:
        sample_payload = {
            "plan_id": "SAMPLE_DEMO",
            "candidates": [
                {
                    "candidate_id": "sample-wdb-001",
                    "source": "sample",
                    "label_type": "WDB",
                    "raw_text": "WDB 20/50 d=25",
                    "bbox_image": [1200, 3400, 180, 90],
                    "width_mm": 200,
                    "height_mm": 500,
                    "status": "needs_review",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            samples_dir = root / "data" / "samples"
            samples_dir.mkdir(parents=True)
            sample_file = samples_dir / "sample_candidates.json"
            sample_file.write_text(json.dumps(sample_payload))

            app.state.project_root = root
            data = get_sample_candidates()

        self.assertEqual(data["source"], "sample")
        self.assertEqual(data["candidate_count"], 1)
        self.assertEqual(data["candidates"][0]["source"], "sample")

        data["candidates"][0]["status"] = "verified"
        with tempfile.TemporaryDirectory() as temp_dir:
            app.state.project_root = Path(temp_dir)
            response = export_verified_json_endpoint("SP_U1_0002", data["candidates"])
            exported = json.loads(response.body)

        self.assertEqual(exported["opening_count"], 1)

    def test_metadata_endpoint_loads_valid_metadata(self) -> None:
        payload = {
            "plan_id": "SP_U1_0002",
            "image_width_px": 18896,
            "scale_text_visible": "M1:50",
            "source_type": "rendered_png",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            metadata_dir = root / "data" / "metadata"
            metadata_dir.mkdir(parents=True)
            metadata_file = metadata_dir / "SP_U1_0002_metadata.json"
            metadata_file.write_text(json.dumps(payload))

            app.state.project_root = root
            data = get_metadata("SP_U1_0002")

        self.assertEqual(data["plan_id"], "SP_U1_0002")
        self.assertTrue(data["exists"])
        self.assertEqual(data["metadata"]["image_width_px"], 18896)
        self.assertEqual(data["metadata"]["scale_text_visible"], "M1:50")

    def test_metadata_endpoint_missing_file_returns_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            app.state.project_root = root
            data = get_metadata("SP_U1_9999")

        self.assertEqual(data["plan_id"], "SP_U1_9999")
        self.assertFalse(data["exists"])
        self.assertTrue(any("not found" in w for w in data["warnings"]))

    def test_save_reviews_endpoint_saves_payload(self) -> None:
        payload = [
            {"candidate_id": "cand-001", "status": "verified"},
            {"candidate_id": "cand-002", "status": "rejected"},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            app.state.project_root = root
            data = save_reviews("SP_U1_0003", payload)

            self.assertEqual(data["status"], "success")
            self.assertTrue("SP_U1_0003_reviewed_candidates.json" in data["path"])

            # Verify side effect
            saved_file = Path(data["path"])
            self.assertTrue(saved_file.exists())
            saved_data = json.loads(saved_file.read_text())
            self.assertEqual(saved_data["plan_id"], "SP_U1_0003")
            self.assertEqual(saved_data["candidate_count"], 2)

    def test_get_reviews_endpoint_loads_draft(self) -> None:
        payload = {
            "plan_id": "SP_U1_0003",
            "saved_at": "2023-10-01T12:00:00Z",
            "candidate_count": 1,
            "candidates": [
                {
                    "candidate_id": "cand-001",
                    "source": "cv",
                    "bbox_image": [10, 20, 30, 40],
                    "status": "verified",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            reviews_dir = root / "outputs" / "reviews"
            reviews_dir.mkdir(parents=True)
            review_file = reviews_dir / "SP_U1_0003_reviewed_candidates.json"
            review_file.write_text(json.dumps(payload))

            app.state.project_root = root
            data = get_reviews("SP_U1_0003")

        self.assertEqual(data["plan_id"], "SP_U1_0003")
        self.assertEqual(data["candidate_count"], 1)
        self.assertEqual(data["source"], "review")
        self.assertEqual(data["candidates"][0]["status"], "verified")

    def test_json_export_endpoint_saves_and_filters_payload(self) -> None:
        payload = [
            {"candidate_id": "cand-001", "status": "verified", "diameter_mm": 100},
            {"candidate_id": "cand-002", "status": "rejected", "diameter_mm": 200},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            app.state.project_root = Path(temp_dir)
            response = export_verified_json_endpoint("SP_U1_0001", payload)
            exported = json.loads(response.body)

        self.assertEqual(exported["opening_count"], 1)
        self.assertEqual(exported["openings"][0]["Length/cm"], 10.0)

    def test_csv_export_endpoint_saves_and_filters_payload(self) -> None:
        payload = [
            {"candidate_id": "cand-001", "status": "verified", "diameter_mm": 100},
            {"candidate_id": "cand-002", "status": "rejected", "diameter_mm": 200},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            app.state.project_root = Path(temp_dir)
            response = export_verified_csv_endpoint("SP_U1_0001", payload)
            rows = list(csv.DictReader(io.StringIO(response.body.decode("utf-8-sig"))))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Length/cm"], "10.0")

    def test_csv_export_includes_unverified_geometry_as_review_required(self) -> None:
        payload = [
            {"candidate_id": "cand-001", "status": "needs_review", "diameter_mm": 100},
            {"candidate_id": "cand-002", "status": "rejected", "diameter_mm": 200},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            app.state.project_root = Path(temp_dir)
            response = export_verified_csv_endpoint("SP_U1_0001", payload)
            csv_text = response.body.decode("utf-8-sig")
            rows = list(csv.DictReader(io.StringIO(csv_text)))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Length/cm"], "10.0")
        self.assertEqual(rows[0]["Review status"], "review_required")

    def test_csv_export_keeps_spatially_distant_openings_separate(self) -> None:
        payload = [
            {
                "candidate_id": "cand-001",
                "status": "verified",
                "diameter_mm": 100,
                "bbox_image": [100, 100, 20, 20],
            },
            {
                "candidate_id": "cand-002",
                "status": "verified",
                "diameter_mm": 100,
                "bbox_image": [5000, 5000, 20, 20],
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            app.state.project_root = Path(temp_dir)
            response = export_verified_csv_endpoint("SP_U1_0001", payload)
            rows = list(csv.DictReader(io.StringIO(response.body.decode("utf-8-sig"))))

        self.assertEqual(len(rows), 2)
        self.assertEqual([row["Number"] for row in rows], ["1", "1"])

    def test_csv_export_groups_nearby_openings_with_total_weight(self) -> None:
        payload = [
            {
                "candidate_id": "cand-001",
                "status": "verified",
                "diameter_mm": 100,
                "bbox_image": [100, 100, 20, 20],
            },
            {
                "candidate_id": "cand-002",
                "status": "verified",
                "diameter_mm": 100,
                "bbox_image": [200, 200, 20, 20],
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            app.state.project_root = Path(temp_dir)
            response = export_verified_csv_endpoint("SP_U1_0001", payload)
            rows = list(csv.DictReader(io.StringIO(response.body.decode("utf-8-sig"))))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Number"], "2")
        self.assertEqual(rows[0]["Weight/kg"], "2.1")

    def test_csv_export_marks_confident_opening_with_explicit_height_ready(self) -> None:
        payload = [
            {
                "candidate_id": "cand-001",
                "status": "verified",
                "diameter_mm": 100,
                "bbox_pdf": [0, 0, 10, 10],
                "bbox_image": [0, 0, 40, 40],
                "confidence": 0.9,
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            words_dir = root / "data" / "words"
            words_dir.mkdir(parents=True)
            (words_dir / "SP_U1_0001_words.json").write_text(
                json.dumps([{"text": "d=25cm", "x0": 0, "y0": 0, "x1": 10, "y1": 10}])
            )
            app.state.project_root = root
            response = export_verified_csv_endpoint("SP_U1_0001", payload)
            rows = list(csv.DictReader(io.StringIO(response.body.decode("utf-8-sig"))))

        self.assertEqual(rows[0]["Height/cm"], "25.0")
        self.assertEqual(rows[0]["Review status"], "ready")

    def test_csv_export_marks_low_confidence_opening_for_review(self) -> None:
        candidate = {
            "candidate_id": "cand-001",
            "status": "verified",
            "diameter_mm": 100,
            "bbox_pdf": [0, 0, 10, 10],
            "confidence": 0.59,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            words_dir = root / "data" / "words"
            words_dir.mkdir(parents=True)
            (words_dir / "SP_U1_0001_words.json").write_text(
                json.dumps([{"text": "d=25cm", "x0": 0, "y0": 0, "x1": 10, "y1": 10}])
            )
            app.state.project_root = root
            response = export_verified_csv_endpoint("SP_U1_0001", [candidate])
            rows = list(csv.DictReader(io.StringIO(response.body.decode("utf-8-sig"))))

        self.assertEqual(rows[0]["Review status"], "review_required")
        self.assertEqual(candidate["status"], "verified")

    def test_csv_export_marks_default_height_opening_for_review(self) -> None:
        payload = [
            {
                "candidate_id": "cand-001",
                "status": "verified",
                "diameter_mm": 100,
                "confidence": 0.9,
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            app.state.project_root = Path(temp_dir)
            response = export_verified_csv_endpoint("SP_U1_0001", payload)
            rows = list(csv.DictReader(io.StringIO(response.body.decode("utf-8-sig"))))

        self.assertEqual(rows[0]["Height/cm"], "30.0")
        self.assertEqual(rows[0]["Review status"], "review_required")

    def test_csv_export_uses_plan_config_default_height(self) -> None:
        payload = [
            {
                "candidate_id": "cand-001",
                "status": "verified",
                "diameter_mm": 100,
                "confidence": 0.9,
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "data" / "config"
            config_dir.mkdir(parents=True)
            (config_dir / "SP_U1_0001_config.json").write_text(
                json.dumps({"plan_id": "SP_U1_0001", "default_height_cm": 45})
            )
            app.state.project_root = root
            response = export_verified_csv_endpoint("SP_U1_0001", payload)
            rows = list(csv.DictReader(io.StringIO(response.body.decode("utf-8-sig"))))

        self.assertEqual(rows[0]["Height/cm"], "45.0")
        self.assertEqual(rows[0]["Review status"], "review_required")

    def test_csv_export_recommends_splitting_overweight_group(self) -> None:
        payload = [
            {
                "candidate_id": "cand-001",
                "status": "verified",
                "diameter_mm": 500,
                "confidence": 0.9,
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            app.state.project_root = Path(temp_dir)
            response = export_verified_csv_endpoint("SP_U1_0001", payload)
            rows = list(csv.DictReader(io.StringIO(response.body.decode("utf-8-sig"))))

        self.assertGreater(float(rows[0]["Weight/kg"]), 25.0)
        self.assertEqual(rows[0]["Review status"], "split_recommended")

    def test_pipeline_status_endpoint_returns_flags(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create one dummy file to test partial true state
            (root / "outputs" / "crops").mkdir(parents=True)

            app.state.project_root = root
            data = get_pipeline_status("SP_U1_0009")

            self.assertEqual(data["plan_id"], "SP_U1_0009")
            self.assertTrue(data["files"]["crops_dir"])
            self.assertFalse(data["files"]["export_csv"])

    def test_get_plans_endpoint_returns_discovered_plans(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pages_dir = root / "data" / "pages"
            pages_dir.mkdir(parents=True)
            (pages_dir / "SP_U1_0001.png").touch()
            (pages_dir / "SP_U1_0002.png").touch()

            app.state.project_root = root
            data = get_plans()

            self.assertIn("plans", data)
            self.assertEqual(len(data["plans"]), 2)
            self.assertEqual(data["plans"][0], "SP_U1_0001")

    def test_get_plan_image_returns_file_or_404(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pages_dir = root / "data" / "pages"
            pages_dir.mkdir(parents=True)

            # Create a dummy image
            dummy_image = pages_dir / "SP_U1_0001.png"
            dummy_image.write_bytes(b"dummy_png_bytes")

            app.state.project_root = root
            response = get_plan_image("SP_U1_0001")
            self.assertEqual(response.body, b"dummy_png_bytes")
            with self.assertRaises(HTTPException) as missing:
                get_plan_image("MISSING")
            self.assertEqual(missing.exception.status_code, 404)

    def test_get_crop_image_returns_file_or_404(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            crops_dir = root / "outputs" / "crops"
            crops_dir.mkdir(parents=True)

            # Create a dummy crop image
            dummy_image = crops_dir / "SP_U1_0001_crop1.png"
            dummy_image.write_bytes(b"dummy_crop_bytes")

            app.state.project_root = root
            response = get_crop_image("SP_U1_0001_crop1.png")
            self.assertEqual(response.body, b"dummy_crop_bytes")
            with self.assertRaises(HTTPException) as missing:
                get_crop_image("missing_crop.png")
            self.assertEqual(missing.exception.status_code, 404)

    def test_get_overlay_image_returns_file_or_404(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            overlays_dir = root / "outputs" / "overlays"
            overlays_dir.mkdir(parents=True)

            # Create a dummy overlay image
            dummy_image = overlays_dir / "SP_U1_0001_overlay.png"
            dummy_image.write_bytes(b"dummy_overlay_bytes")

            app.state.project_root = root
            response = get_overlay_image("SP_U1_0001")
            self.assertEqual(response.body, b"dummy_overlay_bytes")
            with self.assertRaises(HTTPException) as missing:
                get_overlay_image("MISSING")
            self.assertEqual(missing.exception.status_code, 404)

    def test_import_pdf_rejects_non_pdf(self) -> None:
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.post(
            "/api/import/pdf", files={"file": ("test.txt", b"plain text", "text/plain")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Only PDF files are accepted.")

    def test_import_pdf_duplicate_hash(self) -> None:
        import hashlib

        from fastapi.testclient import TestClient

        pdf_content = b"%PDF-1.4 dummy pdf content"
        pdf_hash = hashlib.sha256(pdf_content).hexdigest()

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            # Create a mock metadata file with duplicate hash
            metadata_dir = root / "data" / "metadata"
            metadata_dir.mkdir(parents=True)
            metadata_file = metadata_dir / "SP_U1_0001_metadata.json"
            metadata_file.write_text(json.dumps({"plan_id": "SP_U1_0001", "pdf_hash": pdf_hash}))

            # Touch the target PNG so the API knows it is fully present
            pages_dir = root / "data" / "pages"
            pages_dir.mkdir(parents=True, exist_ok=True)
            (pages_dir / "SP_U1_0001.png").touch()

            app.state.project_root = root
            client = TestClient(app)
            response = client.post(
                "/api/import/pdf", files={"file": ("new_plan.pdf", pdf_content, "application/pdf")}
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "duplicate")
            self.assertEqual(data["plan_id"], "SP_U1_0001")

    @unittest.mock.patch("subprocess.run")
    def test_import_pdf_async_and_status(self, mock_run) -> None:
        import unittest.mock

        from fastapi.testclient import TestClient

        pdf_content = b"%PDF-1.4 dummy pdf content for async"

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            def mock_subprocess(*args, **kwargs):
                from server.app.api import JOBS

                self.assertEqual(JOBS.get("async_plan"), "processing")

                # Mock create outputs
                png_dir = root / "outputs" / "rendered"
                png_dir.mkdir(parents=True, exist_ok=True)
                (png_dir / "async_plan.png").touch()

                cand_dir = root / "outputs" / "candidates"
                cand_dir.mkdir(parents=True, exist_ok=True)
                (cand_dir / "async_plan_candidates.json").touch()

                res = unittest.mock.MagicMock()
                res.returncode = 0
                return res

            mock_run.side_effect = mock_subprocess

            app.state.project_root = root
            client = TestClient(app)
            response = client.post(
                "/api/import/pdf",
                files={"file": ("async_plan.pdf", pdf_content, "application/pdf")},
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "processing")
            self.assertEqual(data["plan_id"], "async_plan")

            # Since TestClient runs BackgroundTasks synchronously, it should be completed now
            status_response = client.get("/api/status/async_plan")
            self.assertEqual(status_response.status_code, 200)
            self.assertEqual(status_response.json()["status"], "completed")

            # Verify that Phase 4 logic copied outputs/rendered/async_plan.png to data/pages/async_plan.png
            copied_png = root / "data" / "pages" / "async_plan.png"
            self.assertTrue(copied_png.is_file())

    def test_download_pipeline_csv(self) -> None:
        from fastapi.testclient import TestClient

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_dir = root / "outputs" / "contract_exports"
            csv_dir.mkdir(parents=True)
            csv_file = csv_dir / "SP_U1_0001_contract.csv"
            csv_file.write_text("Floor,Quantity\nU1,5", encoding="utf-8")

            app.state.project_root = root
            client = TestClient(app)
            response = client.get("/api/downloads/csv/SP_U1_0001")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "Floor,Quantity\nU1,5")
            self.assertEqual(response.headers["content-type"], "text/csv; charset=utf-8")

            # Missing CSV returns 404
            response_missing = client.get("/api/downloads/csv/MISSING")
            self.assertEqual(response_missing.status_code, 404)

    @unittest.mock.patch("subprocess.run")
    def test_import_pdf_generates_overlay(self, mock_run) -> None:
        import unittest.mock

        from fastapi.testclient import TestClient

        pdf_content = b"%PDF-1.4 dummy pdf content for overlay test"

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            def mock_subprocess(*args, **kwargs):
                # 1. Create rendered page PNG
                png_dir = root / "outputs" / "rendered"
                png_dir.mkdir(parents=True, exist_ok=True)
                (png_dir / "overlay_plan.png").touch()

                # 2. Create candidates json
                cand_dir = root / "outputs" / "candidates"
                cand_dir.mkdir(parents=True, exist_ok=True)
                (cand_dir / "overlay_plan_candidates.json").touch()

                # 3. Create overlay image
                overlay_dir = root / "outputs" / "overlays"
                overlay_dir.mkdir(parents=True, exist_ok=True)
                (overlay_dir / "overlay_plan_overlay.png").write_bytes(b"mocked_overlay_bytes")

                res = unittest.mock.MagicMock()
                res.returncode = 0
                return res

            mock_run.side_effect = mock_subprocess

            app.state.project_root = root
            client = TestClient(app)
            response = client.post(
                "/api/import/pdf",
                files={"file": ("overlay_plan.pdf", pdf_content, "application/pdf")},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "processing")

            # Verify the status shows completed and the overlay image is available
            status_response = client.get("/api/status/overlay_plan")
            self.assertEqual(status_response.status_code, 200)
            status_data = status_response.json()
            self.assertEqual(status_data["status"], "completed")

            # This assertion should FAIL because the backend pipeline script does not yet create the overlay image.
            self.assertTrue(status_data["files"]["overlay_image"])

            # Verify that requesting the overlay image returns the saved image content
            overlay_img_response = client.get("/api/images/overlays/overlay_plan")
            self.assertEqual(overlay_img_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
