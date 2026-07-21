from __future__ import annotations

import os
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from windows.launcher import app_data_root, ensure_app_directories, find_available_port


class WindowsLauncherTests(unittest.TestCase):
    def test_app_data_root_prefers_explicit_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"PLANFUGE_DATA_DIR": temp_dir}):
                self.assertEqual(app_data_root(), Path(temp_dir).resolve())

    def test_ensure_app_directories_creates_runtime_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ensure_app_directories(root)
            self.assertTrue((root / "data/imports").is_dir())
            self.assertTrue((root / "data/pages").is_dir())
            self.assertTrue((root / "outputs/candidates").is_dir())
            self.assertTrue((root / "outputs/reviews").is_dir())

    def test_find_available_port_returns_bindable_local_port(self) -> None:
        port = find_available_port()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", port))


if __name__ == "__main__":
    unittest.main()
