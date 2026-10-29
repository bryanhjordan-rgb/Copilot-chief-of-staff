---
name: meeting-prep
description: >-
  Prepares the user for an upcoming meeting: purpose, what they want out of it,
  who's attending and their recent context, open items and promises involving
  them, relevant docs and prior recaps, risks, and three talking points. Use for
  "prep me for …", "what's my next meeting about?", "brief me on the 2pm", or a
  meeting flagged as needing prep in the daily brief. Do not use after the
  meeting (meeting-debrief).
metadata:
  version: "0.1.0"
  tier: "native"
  signatures: "prepare|meeting-brief|self"
  tools: "work-iq, outlook-calendar, excel"
  status: "draft"
---

# Meeting prep

## Goal
The user walks into the meeting knowing why it exists, what outcome to push for, and what each attendee cares about, in under 2 minutes of reading.

## Inputs
- The meeting: named ("the Contoso review"), relative ("my next meeting", "the 2pm"), or passed by the daily brief. If several match, list them and ask once.

## Steps
1. **Find the meeting** in the calendar: subject, time, organizer, attendees, agenda/body, attachments, Teams link.
2. **Related items.** `list_rows(Items, filter: Open eq 'Yes')`. Keep items whose ContextLinks reference this meeting, or whose People overlap the attendees. Note any `meeting_prep` item for this meeting.
3. **Attendee context** (Work IQ, ≤3 queries total, last 30 days): latest mail and Teams threads with the external attendees and the most senior internal attendee; anything the user promised them or that they're waiting on. **[judgment]** Skip attendees with no recent interaction.
4. **History.** If it's a recurring series or a follow-up, pull the last occurrence's recap (Teams meeting recap or notes) and any open action items from it.
5. **Docs.** Files attached to the invite or edited recently on the topic, at most 3.
6. **Frame.** Purpose (from the agenda, or inferred and labelled as inferred), the user's desired outcome (from linked items and goals), risks or tensions, and 3 talking points or questions. **[judgment]**
7. **Write back** (only if a `meeting_prep` item exists for this meeting): `update_row(Items, ID)` with ResearchNotes = the 3 talking points + outcome, Status=in_progress, Updated, and a History line `<now> agent prepped`.

## Output

```
PREP — <subject> · <time> (<duration>) · <in N min | Thu 11:00>
Purpose: <one line> (<from agenda | inferred>)
Your outcome: <what to leave with>

WHO
- <name> (<role/company>) — <last interaction + what they care about>
- …

OPEN WITH THEM
- [P1·84] <item> — <status> · you owe: <promise> · they owe: <waiting on>

LAST TIME (<date>)
- Decided: <…> · Open actions: <…>

READ FIRST: [<doc title>](<url>), [<doc>](<url>)

RISKS: <one line>
SAY / ASK
1. <talking point>
2. <talking point>
3. <question>
```

Confidential meetings (CLAUDE.md §1.5 keywords in the subject or agenda): show WHO and READ FIRST links only, and note that details were skipped.

## Guardrails
- Don't contact attendees, accept, decline, or move the meeting.
- Don't invent attendee roles or history. If you can't find recent context for a person, say so.
- Keep it to one screen. Cut WHO to the 4 most relevant people.

## Done when
- The prep is shown; the linked meeting_prep item (if any) has the talking points in ResearchNotes and Status=in_progress
