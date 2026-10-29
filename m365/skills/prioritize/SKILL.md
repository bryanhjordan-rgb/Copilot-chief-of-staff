---
name: prioritize
description: >-
  Scores and ranks items on the user's list with a fixed 0-100 rubric and states
  explicit tradeoffs. Use for "what now?", "what should I work on?", "rank these",
  "what should I drop?", after intake adds an item, and inside daily-brief. Do not
  use to create items (use intake) or to close them (use reconcile).
metadata:
  version: "0.2.2"
  tier: "native"
  signatures: "rank|items|self"
  tools: "excel, outlook-calendar"
  status: "draft"
---

# Prioritize

## Goal
Every open item has a current Score, Tier, ScoreBreakdown, Rationale, and NextAction in the Items table, and the user sees the top of the list with the tradeoffs spelled out.

## Inputs
- Optional: a set of item IDs (default: Items where `Open eq 'Yes'`)
- Today's date and timezone
- Goals table

## Rubric (0–100)

| Factor | Points | Rule |
|--------|--------|------|
| Deadline pressure | 0–30 | overdue 30 · due today 25 · ≤2 days 20 · ≤7 days 12 · later 5 · no due date 0 |
| Goal fit | 0–25 | work goal (G*) priority 1 → 25 · priority 2 → 18 · priority 3+ → 12 · personal goal (PG*) → 8 · none → 0 |
| Stakeholder weight | 0–15 | "Key people" from the instructions, exec/board, key customer 15 · manager or direct team 10 · peer 6 · other 2 · self only 0 |
| Unblocks others | 0–15 | someone is blocked now 15 · someone waits within 2 days 8 · no 0 |
| Leverage | 0–10 | decision, delegation, or reusable system 10 · normal 5 · busywork 0 |
| Age | 0–5 | Created >14 days ago 5 · >7 days 3 · else 0 |

Tiers: **P1 ≥70 · P2 50–69 · P3 30–49 · P4 <30**.

Overrides (apply after scoring, and note them in the Rationale):
- Status `waiting` or `blocked` → keep the score but exclude from the plan. Surface WaitingOn.
- No goal fit and score <30 → recommend **drop** or **delegate**.
- EffortMin ≥90 with Energy=deep → schedule only into a single free block ≥90 min.

## Steps
1. `list_rows(Items, filter: Open eq 'Yes')` and `list_rows(Goals)`.
2. For each item, compute each factor. Use People, SourceLink and ContextLinks to infer stakeholder weight (sender/attendee roles) and blocking (an explicit ask with a date). **[judgment]** for leverage and stakeholder role when not obvious.
3. `update_row(Items, ID)` with Score, Tier, ScoreBreakdown (`deadline=25; goal=18; stakeholder=10; unblocks=0; leverage=5; age=0`), a one-sentence Rationale, a verb-first NextAction, and Updated. Only write rows whose values changed. That keeps calls under the connector limit (100/min).
4. If ranking for today: get today's calendar and compute free blocks (≥25 min, between the earliest-meeting and home-by constraints). Check whether P1 effort fits. If it doesn't, say what has to move.
5. Present the result.

## Output

```
PRIORITIES — <date>
1. [P1·84] <title> — <next action> — due <date> — <n> links
   why: <rationale>
2. [P1·72] …
3. [P2·61] …

TRADEOFF: <doing #1 and #2 today pushes #3 to <day>>
DROP / DELEGATE: <title> (score <n>, no goal fit) → <suggested delegate or "drop">
WAITING ON: <person> for <title> (since <date>)
```

Show at most 7 items unless the user asks for more.

## Guardrails
- Never change DueDate (it's external). Propose DoDate changes instead.
- Don't inflate scores to make the list look urgent. If nothing is P1, say so.

## Done when
- Every in-scope item has a Score, Tier, ScoreBreakdown, Rationale, and NextAction
- The user has seen the top items and at least one explicit tradeoff (if more than 3 items are open)
