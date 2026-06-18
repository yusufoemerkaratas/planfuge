# Backend Structure

The backend is organized as a Python FastAPI service.

## Directories

- `app`: API, domain models, and services
- `app/services`: calculation and CSV export logic
- `docs`: backend-facing contracts
- `tests`: Python backend tests

Keep API handlers thin. Put business rules in services and data access behind
small, testable interfaces.

## Current Structure

```text
server/
├── app/
│   ├── api.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── services/
│       ├── calculations.py
│       └── csv_export.py
├── docs/
│   └── csv-export-contract.md
├── tests/
│   ├── test_api.py
│   └── test_calculations.py
└── README.md
```

## API Endpoints

- `GET /health`
- `GET /api/export/contract`
- `POST /api/openings/calculate`
- `POST /api/openings/csv`
- `GET /docs` for FastAPI's interactive API documentation

## Commands

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s server/tests
uvicorn server.app.main:app --reload
```
