---
name: code-review
description: >-
  Review a PR, branch, or local changes with severity-ranked findings and
  independent bug-fix verification. Use when the user asks for /code-review,
  review, code review, PR review, branch review, or changed-file review.
---
# Code Review

## Quick start

Review the intended change first, then report only actionable findings ordered by severity.

Decide what to review in this order:

1. If the user provides a PR URL, PR number, branch name, or explicit target, review that target.
2. If no target is provided, review staged and changed files in the current working tree.
3. If the target is ambiguous, ask the user to clarify before reviewing.

## Workflows

### 1. Choose Review Target

For PRs or branches, identify the base branch and inspect:

- `git diff <base-branch>...HEAD`
- `git log <base-branch>...HEAD --oneline`

For local changes, inspect staged and unstaged diffs, and note which files are untracked.

### 2. Review Priorities

Focus on bugs, regressions, security risks, data loss, concurrency hazards, broken contracts, missing validation, migration risks, and meaningful test gaps. Keep style, naming, and preference comments out unless they block correctness or maintainability.

Ground every finding in code evidence. Explain why the behavior is wrong, when it happens, and what impact it has. Do not propose broad rewrites unless the current design creates a concrete risk.

### 3. Bug-Fix Verification

If the target appears to be a bug fix, verify the fix independently before completing the review. Decide this from the branch name, commit messages, diff, tests, issue references, and user prompt. If it is unclear whether the change is a bug fix, ask the user to clarify.

Follow this required flow even when the branch already includes test coverage:

1. Understand the change and infer the intended bug, expected behavior, and acceptance criteria.
2. Write your own temporary reproduction artifact, using the smallest suitable mechanism:
   - a bash script for CLI, integration, build, config, or workflow bugs
   - a unit or integration test for code-level behavior
3. Keep the artifact temporary and separate from the reviewed change unless the user asks to keep it.
4. Check out the base branch or use a clean worktree for the base branch.
5. Run the exact reproduction artifact against the base branch and confirm the bug reproduces.
6. Return to the fix branch.
7. Run the exact same artifact against the fix branch and confirm it passes.
8. If the base branch does not reproduce the bug, or the fix branch does not pass, raise that as a finding or blocker.

Do not let the implementation's existing tests define acceptance by themselves. Use the change intent to write independent acceptance criteria and verify those criteria with the same reproduction artifact on base and fix.

### 4. Severity Levels

Use these severities:

- **Blocker**: Must fix before merge. Causes severe production breakage, data loss, security exposure, failed core workflows, or an unverified/failed bug fix claim.
- **High**: Likely user-facing bug, regression, security or reliability risk, broken API contract, unsafe migration, or missing critical validation.
- **Medium**: Real correctness, maintainability, test, or edge-case issue with limited blast radius.
- **Low**: Minor issue that is worth fixing but does not materially affect behavior or safety.

### 5. Output Format

Lead with findings, ordered by severity. If there are no findings, say so clearly.

For each finding include:

- severity
- affected file or area
- concise problem statement
- impact
- suggested fix or direction

After findings, include only brief supporting context:

- bug-fix reproduction result, when applicable
- verification commands run
- residual risks or checks not run

Do not bury findings under summaries. Do not fix the code unless the user explicitly asks.
