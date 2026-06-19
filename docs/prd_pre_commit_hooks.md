## Problem Statement

The Planfuge repository has no automated code-quality gates at commit time. A developer can commit Python code that is poorly formatted, has unused imports, or fails a type check without receiving any feedback until CI runs — or not at all. The same applies to the TypeScript/React frontend: ESLint and Prettier are installed as dev dependencies but are never enforced before a commit lands. This creates inconsistent style across the codebase and forces reviewers to catch formatting issues in pull requests rather than having them prevented at the source.

## Solution

Introduce a `pre-commit` hook configuration (`.pre-commit-config.yaml`) that runs automatically every time a developer types `git commit`. The hooks format and lint only the files that are staged for the commit, giving fast feedback without scanning the entire repository. A companion `pyproject.toml` centralises Python tool configuration (Black and Ruff). The existing `ci.yml` GitHub Actions workflow gains a `pre-commit run --all-files` step so the same checks are enforced in CI even if a developer bypassed local hooks with `--no-verify`. Instructions for installing the hooks are added to `README.md`.

## User Stories

1. As a developer, I want Python files to be auto-formatted by Black before each commit, so that I never need to think about formatting manually.
2. As a developer, I want Ruff to catch unused imports and common errors in Python code before each commit, so that style violations never reach the remote branch.
3. As a developer, I want TypeScript and JavaScript files to be formatted by Prettier before each commit, so that the frontend codebase stays consistently styled.
4. As a developer, I want ESLint to run on staged frontend files before each commit, so that lint errors are caught locally before CI.
5. As a developer, I want `mypy` to type-check staged Python files before each commit, so that obvious type errors are surfaced immediately.
6. As a developer, I want `tsc --noEmit` to run on staged TypeScript files before each commit, so that TypeScript compilation errors are caught before pushing.
7. As a developer, I want a failing hook to block the commit and show a clear error message, so that I know exactly what to fix.
8. As a developer, I want Black to automatically fix formatting so that I can simply re-stage and re-commit without manual edits.
9. As a CI maintainer, I want `pre-commit run --all-files` added to the CI workflow, so that the same quality gates are enforced on every push even if local hooks were skipped.
10. As a new contributor, I want clear setup instructions in `README.md`, so that I can install the hooks with a single command (`pre-commit install`).

## Implementation Decisions

- **`pre-commit` framework**: A single `.pre-commit-config.yaml` at the repository root declares all hooks. This file is committed to version control so every developer gets the same configuration automatically after running `pre-commit install`.
- **Scope — staged files only**: All hooks use the default `pre-commit` behaviour of running only on files staged with `git add`. This keeps hook execution fast (sub-second for small changes).
- **Python hooks**:
  - `black` — formats Python files in-place; if it rewrites a file, the commit is aborted so the developer can re-stage the formatted version.
  - `ruff` — lints Python files; configured to auto-fix safe issues (`--fix`).
  - `mypy` — type-checks Python files with `--ignore-missing-imports` to avoid noise from third-party libraries that lack stubs.
- **Frontend hooks**:
  - `prettier` — formats `.ts`, `.tsx`, `.js`, `.jsx`, `.json`, `.css`, `.md` files in-place.
  - `eslint` — runs the project's existing ESLint config on staged `.ts`/`.tsx` files; fails on errors.
  - `tsc --noEmit` — runs TypeScript compilation check on the entire `client/` project (not per-file, since TSC needs the full project graph).
- **`pyproject.toml`**: Black and Ruff configuration (line length 100, target Python 3.11, selected rule sets) are declared here instead of inline in `.pre-commit-config.yaml` to keep them reusable from the CLI as well.
- **Exclusions**: The `outputs/` directory (generated artefacts) and `client/dist/` (production build) are excluded from all hooks via the top-level `exclude` pattern in `.pre-commit-config.yaml`.
- **CI integration**: A new `lint` job is added to `ci.yml` that installs `pre-commit` and runs `pre-commit run --all-files`. This job runs in parallel with the existing `backend-tests` and `frontend-build` jobs.
- **No commit-message enforcement**: Conventional commit format is not mandated — this is a single-developer project and the overhead is not justified.

## Testing Decisions

- A good test for this feature is behavioural: "does a deliberately malformatted Python file get rejected at commit time?" Manual end-to-end verification is the appropriate test strategy here, since the hooks themselves are maintained by upstream tool authors and do not need unit tests.
- **Manual verification steps**:
  1. Run `pre-commit install` and confirm the hook is registered in `.git/hooks/pre-commit`.
  2. Stage a Python file with intentional formatting violations → `git commit` → confirm Black reformats it and the commit is blocked.
  3. Stage a Python file with an unused import → `git commit` → confirm Ruff flags and auto-removes it.
  4. Stage a TypeScript file with a Prettier violation → `git commit` → confirm Prettier rewrites it.
  5. Run `pre-commit run --all-files` on the repository and confirm it exits 0 (clean codebase).
- **CI verification**: After merging, confirm the new `lint` job in `ci.yml` turns green on GitHub Actions.

## Out of Scope

- `commit-msg` hooks or conventional commit enforcement.
- `pre-push` hooks — `pre-commit` is sufficient.
- Adding `mypy` stubs or resolving pre-existing type errors across the entire codebase — only new/staged files are checked, and `--ignore-missing-imports` suppresses third-party noise.
- Automating `pre-commit install` via `pyproject.toml` post-install scripts — developers run it manually once after cloning.
- Secret-scanning or security hooks (e.g. `detect-secrets`).

## Further Notes

- The project currently has no `pyproject.toml`. Creating one solely for Black and Ruff config is low overhead and sets up a natural home for future Python tooling configuration (e.g. pytest settings).
- `prettier` will be added as a `devDependency` in `client/package.json` if not already present, so `npx prettier` resolves to the pinned version rather than a global install.
- Developers who do not want to install the hooks can still push — the CI gate is the enforcement backstop.
