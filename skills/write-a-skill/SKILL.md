---
name: write-a-skill
description: >-
  Create concise agent skills with proper frontmatter, clear triggers, and
  progressive disclosure. Use when the user wants to create, rewrite, refine, or
  review a skill.
---
# Write a Skill

## Quick Start

Create or update `SKILL.md` with:

```md
---
name: skill-name
description: What it does. Use when specific trigger/context appears.
---

## Quick Start
[Minimal usage guidance]

## Workflow
[Only the steps needed to run the skill]
```

## Workflow

1. Clarify the skill's task, triggers, inputs, outputs, and required tools.
2. Write the shortest useful `SKILL.md`.
3. Split rarely needed details into one-level references, e.g. `REFERENCE.md`.
4. Add scripts only for deterministic, repeated, or error-prone operations.
5. Review for clear triggers, concise instructions, and no stale/time-sensitive
   facts.

## Rules

- MUST keep `SKILL.md` under 100 lines unless complexity truly requires more.
- MUST make the description specific enough for trigger selection.
- MUST write the description in third person and include "Use when..."
- MUST prefer direct instructions over explanations.
- MUST avoid speculative sections, deep nesting, and broad background material.
- MUST keep references one level deep.

## Structure

```text
skill-name/
├── SKILL.md
├── REFERENCE.md
├── EXAMPLES.md
└── scripts/
    └── helper.js
```
