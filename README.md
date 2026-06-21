# PlanFuge

This repository is a fork of [beyzabetulay/planfuge](https://github.com/beyzabetulay/planfuge) containing enhancements, test suites, and Docker configuration developed on top of the Riedel Bau Hackathon Challenge prototype.

PlanFuge extracts candidate slab opening coordinates from construction plan PDFs, provides a web interface for manual review/validation, and exports the verified data.

---

## Features

- **Candidate Extraction:** Extracts candidate coordinates from construction plan PDFs using PyMuPDF and Tesseract OCR.
- **Interactive Review UI:** A React interface with an interactive SVG overlay matching the PDF layout. Selecting elements highlights corresponding table rows.
- **Evidence Overlay:** Generates a visual status overlay showing detected regions.
- **Data Export:** Supports saving review drafts and exporting final results to CSV/JSON.
- **Dark Mode:** Supports theme toggling (saved in local storage).
- **Docker Compose Setup:** A complete setup that starts the backend and frontend services.
- **CI/CD & Pre-commit:** GitHub Actions for tests/linting and pre-commit hooks for formatting.

---

## Development Prerequisites

- Python 3.11+
- Node.js 22+
- Tesseract OCR (with English and German languages)
- Docker & Compose (optional)

## Pre-Commit Setup

Install the pre-commit hooks to automatically format and lint code before committing:

```bash
pip install pre-commit
pre-commit install
```

This runs:

- `black` & `ruff` for Python.
- `prettier` & `eslint` for TypeScript/React.
- `tsc --noEmit` for TypeScript type checks.

To run hooks manually:

```bash
pre-commit run --all-files
```

---

## Technology Stack

- **Frontend:** React, Vite, TypeScript, Tailwind CSS, Lucide Icons
- **Backend:** FastAPI, Uvicorn, Pydantic
- **PDF/CV:** PyMuPDF, Pillow, NumPy, Tesseract OCR (via `pytesseract`)
- **Data:** pandas
- **Testing:** unittest, TestClient

---

## Repository Structure

```text
.github/workflows/   GitHub CI/CD workflows
client/              React frontend source
docker/              Dockerfiles and entrypoints
docs/                Requirements and design docs
server/              FastAPI backend source and tests
src/                 Candidate extraction and OCR parsing logic
scripts/             Pipeline runner and package scripts
data/                Input PDFs and configs (git-ignored)
outputs/             Crops, overlays, and exports (git-ignored)
tests/               Python pipeline integration tests
```

---

## Setup & Execution

### 1. Using Docker Compose (Recommended)

To build and start the application services:

```bash
docker compose up --build -d
```

The Docker environment mounts the host `./data` and `./outputs` directories. Uploaded PDFs, generated crops, overlays, and review drafts are persisted on the host machine across container restarts.

Access the frontend dashboard at:

```text
http://localhost:8080
```

Verify backend and container health using:

```bash
python3 scripts/docker_smoke_test.py
```

### 2. Manual Local Development

#### System Dependency (Tesseract OCR)

Install the Tesseract binary and language packs:

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng
```

#### Backend Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server.app.api:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend Setup

```bash
cd client
npm ci
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

---

## Testing

### Backend & Pipeline Tests

```bash
python3 -m unittest discover -s server/tests
python3 -m unittest discover -s tests
```

### Frontend Checks

```bash
cd client
npm run test
npm run lint
npm run build
```

---

## Releases & Packaging

The repository includes a release packager script:

```bash
python3 scripts/package_release.py --version 1.0.1
```

Tagging a commit with `v*` and pushing it to GitHub triggers the release workflow, which packages:

1. `planfuge-{version}.zip` (Source bundle)
2. `planfuge-frontend-{version}.zip` (Compiled frontend assets)
3. `SHA256SUMS` (Checksum manifest)
