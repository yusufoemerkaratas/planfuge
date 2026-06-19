# PlanFuge

PlanFuge (Plan2Print) is an automated construction plan analysis and opening verification platform designed for concrete 3D printing preparation. It supports the ingestion, visual review, and structured export of wall/slab openings, ceiling recesses, and drilling locations from blueprint drawings.

The project is intentionally **human-in-the-loop (HITL)**: it does not claim fully automatic construction-plan understanding. It creates structured candidate opening coordinates using computer vision and OCR, renders evidence overlays to a reviewer, and exports production-ready verification datasets for downstream fabricators.

---

## Key Features

* **Asynchronous PDF Processing:** Ingests high-resolution blueprint PDFs, automatically generating layout configuration parameters and rendering them at 300 DPI.
* **Hybrid Candidate Extraction:** Combines red annotation detection (CV) with Tesseract OCR on crop regions, falling back to searchable PDF word coordinate coordinates if OCR is noisy.
* **High-Resolution CV Overlay Generation:** Draws status-coded bounding box overlays (Blue for `verified`, Red for `needs_review`) and candidate ID labels directly on the drawing with dynamically scaling border stroke widths and font sizes.
* **Physics-Based Calculations:** Automatically computes volume ($cm^3$) and weight ($kg$) configurations of openings based on default concrete density and dimensions.
* **Automated Exporters:** Generates finalized contract CSVs and verified openings JSON models ready for Concrete 3D printing preparation.
* **Automated CI/CD:** Fully integrated with GitHub Actions to run linters, client tests, and backend unit/integration tests (120+ tests) on every pull request.

---

## Technology Stack

* **Frontend:** React, Vite, TypeScript, Tailwind CSS, Lucide Icons
* **Backend:** FastAPI (Python), Uvicorn, Pydantic, HTTPX
* **PDF Processing:** PyMuPDF (fitz)
* **Computer Vision:** Pillow (PIL) and NumPy
* **OCR engine:** Tesseract OCR (via `pytesseract`)
* **Data Processing:** pandas
* **Testing:** Python `unittest` framework, FastAPI TestClient

---

## Repository Structure

```text
.github/workflows/   GitHub Actions CI/CD workflows
client/              React + Vite frontend dashboard
docker/              Dockerfiles for multi-stage builds
docs/                Product requirements (PRD) and internal architectural documents
server/              FastAPI backend source code and test suite
src/                 Core computer vision, OCR extraction, and parser modules
scripts/             Extraction pipeline execution and utility scripts
data/                Ignored inputs (imports, rendered pages, config files)
outputs/             Ignored outputs (candidate JSONs, crops, overlays, exports)
tests/               Python unit and integration tests for CV and pipeline logic
```

---

## Pipeline Data Flow

```mermaid
graph TD
    A[Upload PDF] --> B[Render Page to PNG 300 DPI]
    B --> C[Auto-generate Grid Config]
    C --> D[Run CV Red Annotation Detector]
    D --> E[Crop Candidate Regions]
    E --> F[Run Tesseract OCR & PDF Word Fallback]
    F --> G[Parse Dimensions & Save Candidates JSON]
    G --> H[Draw Visual Bounding Box Overlay PNG]
    H --> I[Dashboard UI Review & CSV/JSON Export]
```

1. **PDF Import:** PDFs uploaded to `/api/import/pdf` are stored in `data/imports/`.
2. **Page Rendering:** PyMuPDF renders the first page of the PDF into a 300 DPI high-resolution PNG in `outputs/rendered/`.
3. **Auto-Configuration:** Analyzes grid coordinates and scale text to populate the plan metadata config in `data/config/`.
4. **Computer Vision & OCR:** Extracts coordinates from red-highlighted areas on the drawing, crops those areas, and extracts bounding-box text using Tesseract OCR.
5. **Pillow Overlay Drawer:** Reads the candidate list, scales the stroke line thickness proportionally to the dimensions, draws hollow status-colored rectangles (Red/Blue), writes text labels, and saves the final PNG to `outputs/overlays/`.
6. **Dashboard Interaction:** Serves the overlay at `/api/images/overlays/{plan_id}` when the reviewer checks "Show Overlay", enabling cross-referencing between bounding box markers and tabular calculations.

---

## Setup & Execution

### 1. Docker Compose (Recommended)

Docker Compose handles Python, Node, Nginx, and Tesseract dependencies automatically. From the repository root, run:

```bash
docker compose up --build -d
```

Open your browser to:
```text
http://localhost:8080
```

Verify that the local containers are healthy and reachable using the integration smoke test:
```bash
python3 scripts/docker_smoke_test.py
```

### 2. Manual Local Development

If you prefer to run the components locally without Docker:

#### System Dependency (Tesseract OCR)
Install the Tesseract binary and language packs (English & German):
```bash
# Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng

# Fedora
sudo dnf install tesseract tesseract-langpack-deu tesseract-langpack-eng
```

#### Backend Setup
```bash
# Initialize virtual env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start FastAPI server
uvicorn server.app.api:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend Setup
```bash
cd client
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173). The Vite dev server will proxy API calls to the FastAPI backend at `http://127.0.0.1:8000`.

---

## Testing

The project maintains high testing standards for all calculation modules, parsers, and endpoints.

### Python Tests (Backend & Pipeline)
Run all 120+ backend unit and integration tests from the project root:
```bash
# Discover and run all unit tests
python3 -m unittest discover -s server/tests
python3 -m unittest discover -s tests
```

### Frontend Tests (React)
Run frontend unit and lint checks:
```bash
cd client
npm run lint
npm run test
```

### GitHub Actions CI
The CI runner on every Push and Pull Request to `master` builds the environment, installs system dependencies (`tesseract-ocr`), runs backend unittests, and lint-checks/builds the client dashboard.
