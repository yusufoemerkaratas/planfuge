"""Launch the self-contained PlanFuge server and open it in a browser."""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

APP_NAME = "PlanFuge"


def bundle_root() -> Path:
    """Return PyInstaller's extraction root or the repository root in development."""
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root)
    return Path(__file__).resolve().parents[1]


def app_data_root() -> Path:
    """Return a writable per-user data directory without requiring admin rights."""
    override = os.environ.get("PLANFUGE_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / APP_NAME
    return Path.home() / ".planfuge"


def ensure_app_directories(root: Path) -> None:
    """Create all mutable directories used by API and pipeline services."""
    relative_directories = (
        "data/config",
        "data/imports",
        "data/metadata",
        "data/pages",
        "data/words",
        "outputs/candidates",
        "outputs/contract_exports",
        "outputs/crops",
        "outputs/exports",
        "outputs/overlays",
        "outputs/rendered",
        "outputs/reviews",
    )
    for relative_directory in relative_directories:
        (root / relative_directory).mkdir(parents=True, exist_ok=True)


def find_available_port(host: str = "127.0.0.1") -> int:
    """Ask Windows for a currently available local TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def configure_bundled_tesseract(root: Path) -> None:
    """Point pytesseract at the OCR files shipped beside the application."""
    executable = root / "tesseract" / "tesseract.exe"
    tessdata = root / "tesseract" / "tessdata"
    if not executable.is_file():
        return

    os.environ["TESSDATA_PREFIX"] = str(tessdata)
    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = str(executable)


def open_browser_when_ready(url: str, timeout_seconds: float = 30.0) -> None:
    """Wait for FastAPI health, then open the user's default browser once."""
    health_url = f"{url}/health"
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=1) as response:
                if response.status == 200:
                    webbrowser.open(url, new=2)
                    return
        except OSError:
            time.sleep(0.2)


def show_startup_error(message: str) -> None:
    """Show a useful dialog in the no-console Windows build."""
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, message, f"{APP_NAME} startup error", 0x10)
    else:
        print(message, file=sys.stderr)


def main() -> int:
    try:
        root = bundle_root()
        frontend_dir = root / "client_dist"
        if not (frontend_dir / "index.html").is_file():
            raise FileNotFoundError(f"Compiled frontend not found: {frontend_dir}")

        data_root = app_data_root()
        ensure_app_directories(data_root)
        configure_bundled_tesseract(root)
        os.environ["PLANFUGE_FRONTEND_DIR"] = str(frontend_dir)

        from server.app.api import app

        app.state.project_root = data_root
        host = "127.0.0.1"
        port = find_available_port(host)
        url = f"http://{host}:{port}"
        threading.Thread(target=open_browser_when_ready, args=(url,), daemon=True).start()

        import uvicorn

        # The packaged application uses PyInstaller's windowed mode, where
        # sys.stdout/sys.stderr are None. Uvicorn's default colour formatter
        # probes sys.stderr and therefore cannot be configured in that mode.
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            log_config=None,
            access_log=False,
        )
        return 0
    except Exception as exc:
        show_startup_error(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
