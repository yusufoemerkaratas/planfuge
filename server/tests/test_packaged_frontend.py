from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from server.app.api import mount_packaged_frontend


class PackagedFrontendTests(unittest.TestCase):
    def test_mount_serves_index_without_shadowing_existing_api_routes(self) -> None:
        test_app = FastAPI()

        @test_app.get("/api/ping")
        def ping() -> dict[str, str]:
            return {"status": "ok"}

        with tempfile.TemporaryDirectory() as temp_dir:
            frontend_dir = Path(temp_dir)
            (frontend_dir / "index.html").write_text("<h1>PlanFuge</h1>", encoding="utf-8")

            self.assertTrue(mount_packaged_frontend(frontend_dir, target_app=test_app))
            client = TestClient(test_app)
            self.assertEqual(client.get("/api/ping").json(), {"status": "ok"})
            self.assertIn("PlanFuge", client.get("/").text)

    def test_mount_rejects_missing_frontend(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertFalse(mount_packaged_frontend(temp_dir, target_app=FastAPI()))


if __name__ == "__main__":
    unittest.main()
