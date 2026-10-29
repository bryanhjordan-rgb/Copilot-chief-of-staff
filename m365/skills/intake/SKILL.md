---
name: intake
description: >-
  Captures a new item from conversation, a forwarded email, or a Teams message,
  investigates related context across mail, calendar, files, Teams and people,
  writes it to the list with links, and hands off to prioritize. Use for "add …",
  "remind me to …", "look into …", "track …", or a forwarded message. Do not use
  for re-ranking existing items (prioritize) or closing them (reconcile).
metadata:
  version: "0.2.0"
  tier: "native"
  signatures: "capture|item|self"
  tools: "excel, work-iq"
  status: "draft"
---

# Intake

## Goal
The new item exists as a row in the Items table with linked context, research notes, a score, and a proposed slot. The user learns what you found in ≤6 lines.

## Inputs
- The user's text, or a forwarded email/message (becomes the SourceLink)
- Optional: due date, goal, owner. If the due date is missing, propose one rather than asking.

## Steps
1. **Normalize.** Write a verb-first Title (≤80 chars). Pick a Type. Draft a provisional signature (verb|object|counterpart) for the playbook check.
2. **Dedupe.** `list_rows(Items, filter: Open eq 'Yes')`. Look for a similar Title or the same SourceLink. If you find a match, ask: "Looks like this matches **<title>**. Merge, or keep separate?" Stop until the user answers.
3. **Confidentiality check.** If any CLAUDE.md §1.5 keyword appears, set Confidential=Yes. Skip ResearchNotes (links only) and tell the user.
4. **Investigate** (Work IQ, ≤4 targeted queries total, newest first, last 30 days):
   - mail: threads mentioning the key nouns or people
   - calendar: upcoming or recent meetings on the topic or with the counterpart
   - files: documents recently edited on the topic
   - Teams: chats or channel posts on the topic
   Keep only results that are clearly relevant. Fewer, better links beat many weak ones. **[judgment]**
5. **Goal fit.** `list_rows(Goals)` and match one. If nothing fits, leave Goal empty and say so; that's a signal, not a blocker.
6. **Write** with `add_row(Items)`:
   - ID `I-YYYYMMDD-HHMMSS`, Open=Yes, Status=triaged, Owner=me, Source, Created and Updated = now
   - SourceLink: `[email] <subject> | <url>` (if from a message)
   - ContextLinks: one kept result per line, `[meeting|file|teams|email|person] <title> | <url>`
   - People: emails of the people involved, one per line
   - ResearchNotes: 2–4 bullets covering what's known, what's open, who's involved, and any deadline found in context
   - DueDate (only if found in context; otherwise propose it in chat), EffortMin, Energy, Goal
   - History: `<now> agent created from <source>` and `<now> agent investigated (<n> links)`
7. **Playbook check.** `list_rows(Skills, filter: Status eq 'active')` and look for a row whose Signatures include the provisional signature. If one exists, mention it: "I have a playbook for this; want me to run it?"
8. **Prioritize.** Run the prioritize skill on this item, plus today's top 3 for comparison.

## Output

```
ADDED [P2·58] <title>   (I-20261029-081200)
next: <next action> · due <date> (<found in email | proposed>) · goal: <goal | none>
context: <n> links — <most important link title>, <second>
notes: <one-line summary of research>
vs today: ranks #<k>; <tradeoff if it displaces a top-3 item>
<one question, only if needed>
```

## Guardrails
- Never fabricate a due date. Write DueDate only when it was found in context; otherwise propose it in chat.
- Investigate, don't act: no drafts or sends unless the user asks.
- Stop at 4 Work IQ queries. If context is still thin, say what's missing.

## Done when
- The row is saved with a SourceLink or ≥1 ContextLinks line (or "no context found" in ResearchNotes), a Score, and a NextAction
- The user has seen the summary
