# Windows browser bundle

The Windows bundle is intended for non-technical users. It runs the existing FastAPI backend on
an automatically selected localhost port and opens the compiled React frontend in the default
browser. It does not require Docker, Python, Node.js, or a separately installed OCR engine.

## User experience

1. Download `PlanFuge-Setup-<version>.exe` from GitHub Releases.
2. Run the per-user installer; administrator access is not required.
3. Start PlanFuge from the Start menu or desktop shortcut.
4. The launcher creates `%LOCALAPPDATA%\PlanFuge`, starts the local API, and opens the browser.

The server binds only to `127.0.0.1`, not to the LAN. A free ephemeral port is selected on every
launch to avoid conflicts with development services and other installed applications.

## Automated release

Pushing a `v*` tag runs `.github/workflows/release.yml`. After the normal release checks pass, the
Windows job:

1. installs Tesseract OCR and Inno Setup;
2. builds the React production assets;
3. packages Python, FastAPI, OCR dependencies, frontend assets, and Tesseract with PyInstaller;
4. creates a per-user installer with Inno Setup;
5. uploads the installer and its SHA-256 file to the draft GitHub Release.

The workflow can also be started manually from the feature branch. Manual runs upload the installer
as a workflow artifact without creating or modifying a GitHub Release.

## Local Windows build

Install Python 3.12, Node.js 22, Tesseract OCR, and Inno Setup 6. Then run PowerShell from the
repository root:

```powershell
./windows/build.ps1 -Version 1.1.0
```

The installer is written to `dist\installer`.

## Signing

The current workflow produces an unsigned installer. Windows SmartScreen may display an unknown
publisher warning. Production distribution should add Authenticode signing after acquiring a code
signing certificate; the certificate and password must be stored as encrypted GitHub secrets.
