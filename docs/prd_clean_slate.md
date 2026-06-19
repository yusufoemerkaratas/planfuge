# PRD: Clean-Slate Repository Setup & Run-from-Scratch PDF Pipeline

## Problem Statement

The repository currently comes pre-packaged with several plan drawings, metadata, and pre-extracted candidates (specifically plans `SP_U1_0001` through `SP_U1_0006`). When a user starts the application for the first time, these pre-existing plans are displayed immediately. The user wants the application to start with a clean slate (no plans displayed) and requires all sample plan files to be removed from the Git history/repository. The system must prompt users to upload PDFs and execute the entire processing pipeline dynamically from scratch during their session.

## Solution

Remove all pre-loaded PDF imports, page images, metadata files, searchable-PDF words, and candidates JSONs from Git. Update the frontend onboarding view to display when no plans exist, guide the user to upload a plan, and adjust the backend bootstrapping and testing scripts to construct self-contained mock objects dynamically so they pass without relying on pre-packaged assets.

## User Stories

1. As a first-time system user, I want the dashboard to start in an empty state with a clear onboarding prompt, so that I know I must upload a plan PDF to begin.
2. As a system administrator, I want the Git repository to contain no pre-loaded ceiling plan drawings or candidate files, so that the codebase is lightweight and clean of customer assets.
3. As a developer, I want Git to ignore any uploaded PDFs or processed page images/candidates, so that I don't accidentally commit temporary session files.
4. As a test runner, I want the backend test suite and the integration smoke tests to run successfully without needing pre-loaded plans in the repository, so that testing is fast and fully self-contained.

## Implementation Decisions

- **Data Directory Cleanup:** Delete all default plans (`SP_U1_0001` through `SP_U1_0006`) from the repository directories:
  - `data/imports/`
  - `data/pages/`
  - `data/metadata/`
  - `data/words/`
  - `outputs/candidates/`
  - `outputs/contract_exports/`
    Keep these directories in git using empty `.gitkeep` files.
- **Git Ignore Configurations:** Update the project `.gitignore` rules to ensure any newly uploaded plans and their generated metadata, crops, and candidates are ignored by Git and never committed.
- **Onboarding UI:** Update the React sidebar empty state to display a clear onboarding prompt ("Upload New PDF") rather than instructing developers to manually add files to folders.
- **Bootstrapping Script Adjustment:** Modify `scripts/bootstrap_candidates.py` to skip mock generation if no plan files are present, preventing pre-processed files from appearing on fresh installations.
- **Self-Contained Integration Tests:** Modify the integration smoke test (`scripts/docker_smoke_test.py`) to dynamically generate a mock plan asset, run the API pipeline, assert success, and clean up afterwards, rather than expecting pre-packaged sample files.

## Testing Decisions

- **Graceful Empty State:** Verify the frontend sidebar displays the onboarding instructions correctly when `GET /api/plans` returns an empty array `[]`.
- **Dynamic Pipeline Testing:** Verify the background upload and processing flow using temporary PDF assets created dynamically during the test execution lifecycle.
- **Prior Art:** Existing unit tests in `server/tests/test_api.py` use `tempfile.TemporaryDirectory` to dynamically establish mock file paths. This pattern will be extended to cover the integration/smoke testing steps.

## Out of Scope

- A multi-user authentication system to isolate plans between different accounts.
- Automatic server-side cron jobs to clean up session files (plans will remain in the container volume for persistence across restarts but stay ignored by Git).
