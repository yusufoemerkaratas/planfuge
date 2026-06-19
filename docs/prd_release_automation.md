# PRD: GitHub Release Automation Workflow

## Problem Statement

Manually creating software releases on GitHub is slow and error-prone. It requires developer intervention to build production assets locally, zip the files, create release drafts in the GitHub UI, manually write release changelogs, and upload the build archives. This manual process slows down release cycles and lacks professional DevOps CI/CD automation.

## Solution

Create a GitHub Actions workflow (`.github/workflows/release.yml`) that triggers automatically when a version tag (`v*`) is pushed to the repository. The workflow will run frontend checks and test suites, compile production assets, package the compiled frontend `dist/` directory into a ZIP archive, draft a new GitHub release, automatically generate the release notes from the commit history, and upload the ZIP archive as a release asset.

## User Stories

1. As a project maintainer, I want to push a version tag like `v1.0.0`, so that a GitHub release draft is automatically created with the correct version number.
2. As a project user, I want to download pre-compiled frontend assets directly from the release page, so that I can inspect and preview the production build without installing local development node modules.
3. As a developer, I want the release notes to be automatically generated from the git commit history, so that I don't have to manually write changelogs for every release.
4. As a test runner, I want the release workflow to run lint and test gates first, so that a release is never drafted if the code contains broken tests or lint errors.

## Implementation Decisions

- **Workflow Trigger:** Triggers automatically on pushes of tags matching `v*` (e.g. `v1.0.0`, `v2.1.0-alpha`). Also supports manual triggers (`workflow_dispatch`) for dry-runs.
- **Draft Status:** Releases are created as a `Draft` to allow maintainers to review, edit, and publish them manually.
- **Auto-Generated Notes:** Employs GitHub's native release notes generator to automatically list pull requests and contributors since the last release.
- **Release Assets:** Compiles the React dashboard, packages the resulting `client/dist/` directory into `planfuge-frontend-{tag}.zip`, and uploads it to the release draft.
- **Action Libraries:** Uses the official `actions/checkout`, `actions/setup-node`, and community-standard `softprops/action-gh-release` steps.
- **Access Control:** Requires repository write permissions (`contents: write`) for the workflow runner to publish the draft.

## Testing Decisions

- **Dry-Run Mode:** The workflow will support a `workflow_dispatch` input parameter called `dry_run`. When set to true, it will run all tests, build the assets, and create the ZIP archive without drafting a release on GitHub, allowing developers to test the build and packaging safely.

## Out of Scope

- Automating the deployment of the backend or frontend containers to cloud hosting platforms.
- Creating and pushing docker image tags to Docker Hub/GitHub Container Registry.
- Auto-merging release branches or automatically incrementing versions in `package.json`.
