import json
import os
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = PROJECT_ROOT / "docker" / "backend-entrypoint.sh"
SMOKE_TEST = PROJECT_ROOT / "scripts" / "docker_smoke_test.py"


class SmokeApiHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_json({"status": "ok"})
            return
        if self.path == "/api/plans":
            self.send_json({"plans": []})
            return
        if self.path == "/":
            body = b'<html><div id="root"></div></html>'
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if self.path != "/api/openings/calculate":
            self.send_error(404)
            return
        content_length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(content_length)
        self.send_json({"volumeCm3": 6000, "weightKg": 2.6})

    def send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


class DockerSessionRuntimeTests(unittest.TestCase):
    def test_entrypoint_replaces_stale_runtime_and_executes_application(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_root = Path(temp_dir)
            stale_page = runtime_root / "data" / "pages" / "SP_U1_0004.png"
            stale_candidate = runtime_root / "outputs" / "candidates" / "SP_U1_0004_candidates.json"
            stale_page.parent.mkdir(parents=True)
            stale_candidate.parent.mkdir(parents=True)
            stale_page.write_bytes(b"stale page")
            stale_candidate.write_text("{}", encoding="utf-8")

            command_marker = runtime_root / "application-started"
            environment = os.environ.copy()
            environment["PLANFUGE_RUNTIME_ROOT"] = str(runtime_root)

            result = subprocess.run(
                [
                    "sh",
                    str(ENTRYPOINT),
                    "sh",
                    "-c",
                    f"touch '{command_marker}'",
                ],
                cwd=PROJECT_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(stale_page.exists())
            self.assertFalse(stale_candidate.exists())
            self.assertTrue((runtime_root / "data" / "pages").is_dir())
            self.assertTrue((runtime_root / "data" / "imports").is_dir())
            self.assertTrue((runtime_root / "outputs" / "candidates").is_dir())
            self.assertTrue((runtime_root / "outputs" / "exports").is_dir())
            self.assertTrue(command_marker.is_file())

    def test_compose_backend_has_no_persistent_runtime_volumes(self) -> None:
        result = subprocess.run(
            ["docker", "compose", "config", "--format", "json"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        compose_config = json.loads(result.stdout)
        backend = compose_config["services"]["backend"]
        self.assertEqual(backend.get("volumes", []), [])

    def test_smoke_test_accepts_a_fresh_runtime_with_no_plans(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), SmokeApiHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()
        try:
            host, port = server.server_address
            result = subprocess.run(
                [
                    "python3",
                    str(SMOKE_TEST),
                    "--base-url",
                    f"http://{host}:{port}",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            server.shutdown()
            server.server_close()
            server_thread.join()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0 plans", result.stdout)


if __name__ == "__main__":
    unittest.main()
