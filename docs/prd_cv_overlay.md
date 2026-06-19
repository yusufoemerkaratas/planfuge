# PRD: CV Overlay Generation in PDF Processing Pipeline

## Problem Statement

In the PlanFuge dashboard, the user can toggle the "CV Overlay" view to see candidate bounding boxes drawn on top of the original drawing image. However, when a new plan is uploaded and processed, the backend processing pipeline does not generate this overlay image (`*_overlay.png`). As a result, the `CV Overlay` status is displayed as "Missing" (yellow dot), and toggle-loading the overlay image in the viewer fails.

## Solution

Integrate a visual overlay drawer stage into the backend PDF processing pipeline. Once candidate coordinates are successfully extracted and written to candidates JSON, load the rendered plan page PNG, draw colored rectangles around all candidate bounding boxes with their corresponding candidate IDs, and save the resulting image to the overlays outputs directory.

## User Stories

1. As a plan reviewer, I want to toggle the CV Overlay view on the dashboard, so that I can visually verify where candidate openings were detected on the construction plan drawing.
2. As a system operator, I want the backend pipeline to generate the overlay image automatically on upload, so that I do not need to execute separate manual visualization scripts.
3. As a developer, I want the overlay drawing logic to run safely in the background, so that the main upload request does not block or timeout while drawing large images.
4. As a test runner, I want the pipeline to fail cleanly and delete any half-finished overlay files if drawing encounters an error, so that I do not get corrupt image files.

## Implementation Decisions

- **Pipeline Integration:** Add a drawing step at the end of the async pipeline task execution. This step will run after the candidate JSON file is successfully created.
- **Overlay Image Creation:** Load the rendered page PNG using Python's `Pillow` library, create an `ImageDraw` drawer, iterate through all candidates in the JSON, and draw rectangles around the coordinates.
- **Drawing Style:** Bounding boxes will be drawn as hollow colored rectangles (e.g. red for needs_review, blue for verified status) with a thick border line proportional to the high-resolution image size (e.g. 5-10 pixels thick). Add the candidate ID text near each bounding box.
- **Directory Setup:** Ensure the backend automatically creates `outputs/overlays/` if it does not exist before writing.
- **Robust Font Fallback:** Use Pillow's built-in default font for drawing labels to avoid missing font dependencies in Docker containers.

## Testing Decisions

- **Drawer Unit Test:** Write a unit test that mock-calls the drawer function with a test plan PNG and candidate JSON payload, asserting that the overlay PNG is successfully created in the correct outputs directory and contains the expected dimensions.
- **Pipeline Integration Test:** Verify that the integration smoke test executes the full pipeline end-to-end and successfully verifies that the `overlay_image` status flag is returned as `Available`.

## Out of Scope

- Dynamically re-drawing the overlay file on the server in real-time as individual candidates are updated or saved in the frontend table.
- Custom fonts or overlay image styling configurations (e.g. different colors, border opacities) customizable by users via the UI.
