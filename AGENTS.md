# Project Operating Rules

## Mandatory Skill Workflow

For every new execution, issue, or GitHub issue-driven task in this repository:

1. Read all current project skill files under `skills/*/SKILL.md` before planning or implementation.
2. Apply the skills in sequence when they are relevant to the requested work:
   - `write-a-skill`
   - `create-prd`
   - `tdd`
   - `commit-push-pr`
   - `create-issues`
   - `grill-me`
   - `code-review`
   - `simplify-changes`
3. If a skill explicitly forbids repository changes during its workflow, obey that skill before moving to any later implementation step.
4. Before starting a GitHub issue from `gh`, fetch and read the full issue context, then reread the skill files.
5. Plan first, then implement in vertical slices where possible.
6. When TDD applies, use red-green-refactor with one behavior at a time.
7. Before commit, push, or PR work, follow `skills/commit-push-pr/SKILL.md`.
8. For review requests, follow `skills/code-review/SKILL.md` and lead with findings.
9. After code changes, run the relevant checks and simplify only recently touched code according to `skills/simplify-changes/SKILL.md`.

These rules are project-level instructions and should remain in force throughout the project unless the user explicitly changes them.
