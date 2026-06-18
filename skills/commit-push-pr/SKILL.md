---
name: commit-push-pr
description: Commit changes, push to feature branch, and create draft PR
targets:
  - "*"
---

# commit-push-pr Task

## Objective

Commit changes with conventional commits, push to feature branch, create draft PR with description.

## Instructions

1. **Pre-commit:** - `git status` to see changes - List modified/added/deleted files - Ask: "Proceed with PR for these changes?"

2. **Quality checks:** - Run project quality checks: linter, formatter, type checker, and any affected unit tests (use whatever commands the project provides) - If fails: report errors, ask to fix first - DO NOT proceed if checks fail unless explicitly instructed

3. **Commit details:** - Infer type (`feat`/`fix`/`docs`/`refactor`/`perf`/`test`/`chore`) from the diff and changed file context

4. **Commit message:** - Format: `<type>: <description>` - Examples: `feat: rearchitect function for time complexity`, `feat(api): change API response format`

5. **Commit:** - `git add .` (or specific files) - Commit with message - Show hash and message

6. **Branch strategy:** - Check: `git branch --show-current` - If `master`/`dev`: suggest `feat/<short-desc>`, ask create? - Create/checkout if approved - If already feature branch: proceed

7. **Push:** - First: `git push -u origin <branch>` - Subsequent: `git push origin <branch>` - Show result - If fails: report error, ask how to proceed

8. **PR description:** - Invoke `/pr-description` for the current branch and use its output as the draft PR body - Fill only PR-creation-specific details here: destination branch, screenshots, and GitHub metadata - Do not independently restate or recompute the PR description template

9. **Create draft PR:** - Detect base branch: `gh repo view --json defaultBranchRef -q '.defaultBranchRef.name'` - Do NOT assume `master` - PR title: use the conventional commit subject from step 4, but STRIP any ticket ID (e.g., `HOT-3785`, `ARC-123`, `JIRA-456`) — ticket IDs belong in the PR body/branch, not the title - Ask: "Create draft PR on GitHub targeting `<detected-base>`?" - If yes + GitHub MCP: `mcp_github_create_pull_request`, `draft: true`, base = detected branch - If no MCP: Provide description for copy-paste, instructions: "Visit https://github.com/<org>/<repo>/compare/<base>...<branch>"

10. **Summary:** - Commit hash/message - Branch pushed - PR URL or creation instructions - Follow-up: Run `/code-review`, request reviews, link issues, mark ready when appropriate

## TODO Composition

Create todos at task start:

1. `commit-push-pr-pre-commit` - "Review changes and confirm proceeding with PR"
2. `commit-push-pr-quality-checks` - "Run quality checks (lint, typecheck)"
3. `commit-push-pr-commit-details` - "Gather commit details (type, scope, description, breaking changes)"
4. `commit-push-pr-commit` - "Create commit with conventional commit message"
5. `commit-push-pr-branch-strategy` - "Verify/create feature branch"
6. `commit-push-pr-push` - "Push branch to remote"
7. `commit-push-pr-description` - "Consume PR description output from /pr-description"
8. `commit-push-pr-create` - "Create draft PR on GitHub"
9. `commit-push-pr-summary` - "Generate summary with commit, branch, and PR info"

Update status: Mark `in_progress` when starting each, `completed` when done.
