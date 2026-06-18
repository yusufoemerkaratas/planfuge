# Running PlanFuge

The PlanFuge MVP consists of a FastAPI backend and a Vite+React frontend.
Both need to be running simultaneously to access the full application.

## 1. Start the Backend (API)

Open a terminal in the root `Plan2Print` directory and start the FastAPI server:

```bash
# Make sure your virtual environment is active
source .venv/bin/activate

# Run the backend on port 8000
uvicorn server.app.api:app --reload
```
The backend API will be available at: http://localhost:8000

## 2. Start the Frontend (UI)

Open a *second* terminal, navigate to the `client` directory, and start the Vite development server:

```bash
cd client
npm run dev
```

The terminal will output a local URL (e.g., http://localhost:5173). Open this URL in your browser to view the PlanFuge dashboard.
