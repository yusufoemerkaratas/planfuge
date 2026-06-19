# Product Requirements Document (PRD): PDF Import & Processing Area

## Problem Statement

The user currently can only view pre-loaded/static plans and candidates in the web application dashboard. There is no way to upload new technical plan PDFs from the local machine, trigger the OCR and candidate extraction pipeline dynamically, or download a CSV report containing the extracted measurements directly from the web interface. This limits the application to a static viewer rather than a fully interactive pipeline tool.

## Solution

We will add an interactive PDF import area to the frontend, including a visual drag-and-drop zone. When a user drops or selects a plan PDF, they can process it. The frontend will communicate with the backend API to upload the file, track processing status, run the OCR and measurement extraction pipeline, save the outputs dynamically, and allow direct download of the generated candidates as a CSV file.

## User Stories

1. As an engineer, I want to drag and drop a PDF plan file onto the dashboard, so that I can easily upload it for candidate extraction.
2. As an engineer, I want to see visual validation (e.g., file type and file size validation) during the drag-and-drop interaction, so that I know I am uploading a valid PDF plan.
3. As an engineer, I want to click a "Process Plan" button, so that I can trigger the candidate extraction pipeline for the uploaded file.
4. As an engineer, I want to see a visual progress indicator showing the status of the pipeline (Uploading, OCR Processing, Extracting, Completed, or Failed), so that I know how much time is left and if the process succeeded.
5. As an engineer, I want the system to process files one at a time via a queue, so that the server resources are not overwhelmed by concurrent OCR tasks.
6. As an engineer, I want to be prompted if I upload a duplicate PDF file (based on content hash), so that I can choose to view the existing results or re-run the pipeline.
7. As an engineer, I want to download the generated candidate list as a CSV file directly from the user interface once processing completes, so that I can use it in other CAD or spreadsheet tools.
8. As an engineer, I want the newly processed plan to automatically appear in my plan selection sidebar, so that I can view its original page image, overlays, and candidates list instantly.

## Implementation Decisions

### Frontend Components

- **Drag-and-Drop Uploader:** A new React component rendered on the main panel when no active plan is selected. Features:
  - Dropzone area with dashed borders highlighting on drag-over.
  - File picker input as fallback.
  - Selected file details (name, size) with a "Remove" button.
  - "Process PDF" action button.
- **Pipeline Progress Screen:** Rendered while the file is uploading/processing. Show progress steps and a loading spinner.
- **Upload Plan Button:** A small "Upload PDF" button at the top of the sidebar plan selector to clear the active plan selection and show the uploader.

### Backend Endpoints

- **Update PDF Import API:** Modify `POST /api/import/pdf` (or implement a corresponding endpoint) to run the pipeline.
  - Check file hash (SHA-256) to detect duplicates. If a match exists, return status `duplicate` with the plan ID.
  - Save PDF to `data/imports/`.
  - Process via background worker (or FastAPI `BackgroundTasks`).
  - Copy the rendered original PNG from `outputs/rendered/{plan_id}.png` to `data/pages/{plan_id}.png` so it is discovered by the frontend list.
- **Job Status API:** Implement/enhance `GET /api/status/{plan_id}` to return the status of the background task (`pending`, `processing`, `completed`, `failed`).

### Integration Flow

- Frontend sends `multipart/form-data` to `POST /api/import/pdf`.
- Backend starts background job, returns `{ "plan_id": "<id>", "status": "processing" }` (or `duplicate`).
- Frontend polls status endpoint until success or failure.
- Upon completion, the frontend refreshes the plan list, selects the new plan, and loads its candidates.

## Testing Decisions

- **Unit & Integration Tests:**
  - Mock uploads using FastAPI `TestClient` to verify files are stored correctly.
  - Test SHA-256 duplicate detection.
  - Test status tracking behavior.
- **Frontend Verification:**
  - Manual testing of the drag-and-drop dropzone highlight state, file picker, and progress screen.

## Out of Scope

- Real-time multi-page PDF navigation (focus is solely on the first page/page 0 as per current pipeline design).
- User authentication and multi-user queues.

## Further Notes

- The default height for openings is derived from the configuration of the plan.
