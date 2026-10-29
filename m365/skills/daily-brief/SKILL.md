---
name: daily-brief
description: >-
  Builds the user's prioritized daily activity list: Top 3 outcomes, a
  timeboxed plan fitted to today's calendar, linked context for each item,
  meetings needing prep, and a drop/delegate list. Use for "plan my day",
  "morning brief", "what does today look like", "re-plan", and the scheduled
  07:00 run. Do not use for adding a single item (intake).
metadata:
  version: "0.2.2"
  tier: "native"
  signatures: "plan|day|self"
  tools: "excel, work-iq, outlook-calendar"
  status: "draft"
---

# Daily brief

## Goal
The user knows the 3 outcomes that matter today, when they'll do them, and what they're explicitly not doing. The brief fits on one screen, and the plan is written back to the Items table.

## Inputs
- Date (default today, user timezone). Never guess the weekday; derive it from the date.
- Invocation: scheduled (post as a card, no follow-up questions) or interactive (may ask one question)

## Steps
1. **Calendar.** Get today's meetings. Flag: hard-constraint conflicts (home-by, earliest meeting), back-to-backs with no buffer, meetings with no agenda, and meetings needing prep (external attendees, exec attendees, or an open item whose ContextLinks include the meeting).
2. **Free blocks.** From the calendar, compute free blocks ≥25 min between the earliest-meeting and home-by constraints.
3. **Overnight intake (light).** Quick Work IQ scan of mail and Teams since the last brief for explicit asks with deadlines aimed at the user. Don't create items yet; list up to 3 as "suggested adds".
4. **Rank.** Run the prioritize skill on all open items.
5. **Top 3.** Pick the 3 highest-scoring items that fit today's free blocks. Prefer items due ≤2 days or linked to a priority-1 goal. **[judgment]** If a P1 can't fit, say what meeting or item would have to move.
6. **Plan.** Assign items to free blocks: deep work into the longest morning blocks, shallow work into short gaps. Put meeting prep in the block before the meeting, and offer "say 'prep me for <meeting>'" (meeting-prep skill).
7. **Goals pulse.** `list_rows(Goals)`. Name any priority-1/2 goal with no item planned today, or with LastUpdate 7+ days ago.
8. **Drop/delegate.** Up to 3 items with score <30 and no goal fit.
9. **Write back.** For each planned item, `update_row(Items, ID)` with DoDate=today, PlannedSlot (`HH:MM-HH:MM`), Status=scheduled (unless in_progress), Updated, and append `<now> agent scheduled <slot>` to History.
10. **Deliver.** Scheduled: return the brief for the workflow to post as a card, in card-safe markdown: line 1 is the header; then `**TOP 3**`-style bold labels instead of headings, `- ` bullets, `[title](url)` links, and no tables or code fences. Interactive: show it and end with one question.

## Output

```
<Weekday>, <date> — <n> meetings, <h>h free

TOP 3
1. [P1·84] <title> — <next action>  ⏱ <start–end>   🔗 <link>, <link>
2. [P1·73] …
3. [P2·64] …

PLAN
08:30–10:00  <item 1>
10:00–10:30  Prep: <meeting> (<why prep is needed>)
10:30–11:00  <meeting>
…

HEADS UP
- <constraint conflict / back-to-back / meeting with no agenda>

GOALS
- <goal> — nothing planned today; <n> days since progress

NOT TODAY
- <title> → drop | delegate to <name> | defer to <day>

SUGGESTED ADDS
- <sender>: "<ask>" (due <date>) — add?
```

Render links from the "[type] Title | url" cells as clickable links. Then: "Accept, or tell me what to change."

## Guardrails
- Never schedule over a hard constraint. If a meeting already violates one, flag it; never move it yourself.
- Don't propose times to other people. This plan is for the user only.
- Keep it to one screen: at most 7 plan rows besides meetings, 3 heads-ups, and 3 suggested adds.

## Done when
- Planned items have DoDate and PlannedSlot written, and the brief is delivered
- When the user accepts or edits, `add_row(Feedback)` with TargetType=brief, TargetRef=<date>, Signal=accept|edit, Detail=<their edit>
