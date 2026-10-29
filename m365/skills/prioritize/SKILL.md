---
name: prioritize
description: >-
  Scores and ranks items on the user's list with a fixed 0-100 rubric and states
  explicit tradeoffs. Use for "what now?", "what should I work on?", "rank these",
  "what should I drop?", after intake adds an item, and inside daily-brief. Do not
  use to create items (use intake) or to close them (use reconcile).
metadata:
  version: "0.1.0"
  tier: "native"
  signatures: "rank|items|self"
  tools: "dataverse, get_free_blocks"
  status: "draft"
---

# Prioritize

## Goal
Every open item has a current `priority_score`, `priority_tier`, `score_breakdown`, `rationale`, and `next_action`, and the user sees the top of the list with the tradeoffs spelled out.

## Inputs
- Optional: a set of item ids (default: all `cos_item` with status in inbox, triaged, scheduled, in_progress, waiting, blocked)
- Today's date and timezone
- Active `cos_goal` rows

## Rubric (0–100)

| Factor | Points | Rule |
|--------|--------|------|
| Deadline pressure | 0–30 | overdue 30 · due today 25 · ≤2 days 20 · ≤7 days 12 · later 5 · no due date 0 |
| Goal fit | 0–25 | linked to goal priority 1 → 25 · priority 2 → 18 · priority 3 → 12 · personal goal → 8 · none → 0 |
| Stakeholder weight | 0–15 | exec/board/key customer 15 · manager or direct team 10 · peer 6 · other 2 · self only 0 |
| Unblocks others | 0–15 | someone is blocked now 15 · someone waits within 2 days 8 · no 0 |
| Leverage | 0–10 | decision, delegation, or reusable system 10 · normal 5 · busywork 0 |
| Age | 0–5 | open >14 days 5 · >7 days 3 · else 0 |

Tiers: **P1 ≥70 · P2 50–69 · P3 30–49 · P4 <30**.

Overrides (apply after scoring, and note them in the rationale):
- `status=waiting` or `blocked` → keep the score but exclude from the plan. Surface the "waiting on" person.
- No goal fit and score <30 → recommend **drop** or **delegate**.
- Effort ≥90 min with energy=deep → schedule only into a single free block ≥90 min.

## Steps
1. Load the items, goals, and links (`dataverse`).
2. For each item, compute each factor. Use links to infer stakeholder weight (sender/attendee roles) and blocking (an explicit ask with a date). **[judgment]** for leverage and stakeholder role when not obvious.
3. Write `priority_score`, `priority_tier`, `score_breakdown` (JSON of factor → points), a one-sentence `rationale`, and a verb-first `next_action`. Log `prioritized` to `cos_activity`.
4. If ranking for today: call `get_free_blocks(today)` and check whether P1 effort fits. If it doesn't, say what has to move.
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
- Never change `due_date` (it's external). Propose `do_date` changes instead.
- Don't inflate scores to make the list look urgent. If nothing is P1, say so.

## Done when
- Every in-scope item has a score, tier, breakdown, rationale, and next action
- The user has seen the top items and at least one explicit tradeoff (if more than 3 items are open)
