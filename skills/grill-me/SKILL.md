---
name: grill-me
description: >-
  Interview the user about a plan or design with focused pressure until key
  assumptions, tradeoffs, and decisions are clear. Use when the user wants to
  stress-test a plan, get grilled, or mentions "grill me".
---

# Grill Me

Interview the user firmly about the plan until there is shared understanding.
Walk the important branches of the design tree, resolving dependent decisions
one by one, but do not chase every edge case or move into a new category
outside the original topic.

For each question, ask one question at a time and use exactly this mandatory
format. Ask around 15-20 questions total. Option A MUST always be the recommended
answer.

Your question format MUST be:

### Question <number>/<total-question>: Question..
Explanation if question is not clear/easy enough.

A: Approach A... (recommended)
B: Approach B...
C: Approach C...

MUST keep the options concise, and clear, and put the recommendation only in A.

MUST NOT code, edit files, run implementation commands, create tickets, write
PRDs, or make any repository changes while using this skill. This skill is only
for questioning and summarizing.

MUST stop after question 15. Say the grilling is enough for now, summarize the
clarified plan, decisions, and remaining risks, then stop. The only allowed
next-step prompt is: ask the user to either run `/create-prd` or give a separate
future command. Do not start that next step yourself.
