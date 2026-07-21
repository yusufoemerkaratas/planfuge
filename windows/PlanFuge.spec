# PyInstaller specification for the self-contained Windows browser launcher.

from __future__ import annotations

import os
from pathlib import Path

repo_root = Path(SPECPATH).parent
frontend_dir = repo_root / "client" / "dist"
tesseract_dir = Path(os.environ.get("PLANFUGE_TESSERACT_DIR", ""))

if not (frontend_dir / "index.html").is_file():
    raise SystemExit("Build client/dist first with: npm --prefix client run build")
if not (tesseract_dir / "tesseract.exe").is_file():
    raise SystemExit("PLANFUGE_TESSERACT_DIR must point to a Windows Tesseract installation")

datas = [
    (str(frontend_dir), "client_dist"),
    (str(tesseract_dir), "tesseract"),
]

a = Analysis(
    [str(repo_root / "windows" / "launcher.py")],
    pathex=[str(repo_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "uvicorn.logging",
        "uvicorn.loops.auto",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan.on",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["streamlit"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PlanFuge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PlanFuge",
)
