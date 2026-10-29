---
name: relationship-check
description: >-
  Keeps important relationships from going quiet: checks when the user last
  had a real two-way interaction with each person on the People sheet,
  flags who is overdue or about to be for their tier's cadence, and suggests a
  specific, personal reason to reach out, with an optional draft. Also adds or
  re-tiers people and records dated notes. Use for "relationship check", "who am
  I losing touch with?", "who should I reach out to?", "add Dana as tier 1",
  "note that Dana is moving to Lisbon". Do not use for inbox triage (triage) or
  meeting prep (meeting-prep).
metadata:
  version: "0.1.0"
  tier: "native"
  signatures: "check|relationships|self"
  tools: "excel, work-iq, outlook"
  status: "draft"
---

# Relationship check

## Goal
No Tier 1 or 2 relationship drifts past its cadence without the user deciding to let it. Every overdue person comes with a concrete, personal reason to reach out.

## Inputs
- Mode: `check` (default), `add <person> [tier]`, `retier <person> <tier>`, or `note <person>: <text>`
- Cadence: CadenceDays if set, otherwise Tier 1 = 14 days, Tier 2 = 30, Tier 3 = 60
- Today's date

## Steps

### check
1. `list_rows(People)`. Ignore rows with an empty Email.
2. **Due date** per person = LastContact + cadence. Status: **overdue** (due date before today), **approaching** (within 5 days), **healthy** otherwise. A person with no LastContact counts as overdue.
3. **Refresh before flagging.** For each overdue or approaching person (at most 10, Tier 1 first), look for a newer two-way interaction since LastContact via Work IQ: an email they sent you or you sent them with a reply, a Teams chat with messages from both sides, or a meeting you both attended. Broadcasts, CC-only mail, and large meetings (>8 people) don't count. **[judgment]**
   - Found something newer → `update_row(People, Email)` with LastContact, LastChannel, Updated. Recompute the status.
4. **Reason to reach out** for each person still overdue or approaching, in this order of preference **[judgment]**:
   - an open item with them in People (a promise you owe them, or something they're waiting on)
   - a dated note that's become relevant (a move, a launch, a milestone)
   - something recent from their side (a post, a promotion, a project in a shared thread)
   - otherwise a light check-in tied to a shared goal or the last conversation topic
   Write it to NextTouch and set Updated.
5. **Present** (format below). Overdue people first, then approaching; Tier 1 before Tier 2 before Tier 3. Show at most 8.
6. **On request:** "Draft 2" → a short message in the user's voice (email or Teams, whichever was their LastChannel), **draft only**. "Track 2" → create an item via the intake rules (Type=follow_up, People=<email>, DueDate=their due date). "Snooze 3" → set CadenceDays to double the current cadence for this person and say so. "Skip" → nothing.

### add / retier / note
- **add:** look the person up (Work IQ people) to fill Name, Email (lowercase), and Role; confirm the tier if none was given (suggest one from interaction frequency). Then `add_row(People)` with LastContact = the latest two-way interaction found.
- **retier:** `update_row(People, Email)` with the new Tier and Updated.
- **note:** append `"<text> (added YYYY-MM-DD)"` as a new line in Notes (read the row first, because update overwrites).

## Output

```
RELATIONSHIPS — <date> · <n> overdue · <m> approaching · <k> healthy

OVERDUE
1. Dana Ortiz (T1, mentor) — 21 days, cadence 14 · last: in person
   Reason: she's moving to Lisbon in December. Ask how the move is going and get a coffee in before she goes.
   [Draft 1 · Track 1 · Snooze 1]
2. Riley Shah (T2, former colleague) — 45 days, cadence 30 · last: email
   Reason: …

APPROACHING
3. Alex Kim (T2, Contoso AE) — due in 3 days · open: I-SEED-001 pricing review, you owe them pricing
```

If nobody is overdue or approaching: "All key relationships are within cadence."

## Guardrails
- Never send anything. Drafts only; sending needs "Send".
- Only record notes the user told you, or facts from your own interactions with the person. Don't scrape personal details from elsewhere.
- Confidential topics (CLAUDE.md §1.5) never go into Notes or NextTouch.
- Snooze and retier change the cadence only when the user asks. Never quietly drop someone.
- Stale is a prompt, not a verdict. Some relationships ebb and flow; don't nag about the same person more than once a week.

## Done when
- Overdue and approaching people are listed with a reason; refreshed LastContact values and NextTouch are written; the user's draft, track, and snooze choices are applied
