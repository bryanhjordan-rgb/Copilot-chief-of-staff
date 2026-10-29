---
name: intake
description: >-
  Captures a new item from conversation, a forwarded email, or a Teams message,
  investigates related context across mail, calendar, files, Teams and people,
  links it, and hands off to prioritize. Use for "add …", "remind me to …",
  "look into …", "track …", or a forwarded message. Do not use for re-ranking
  existing items (prioritize) or closing them (reconcile).
metadata:
  version: "0.1.0"
  tier: "native"
  signatures: "capture|item|self"
  tools: "dataverse, work-iq, find_playbook"
  status: "draft"
---

# Intake

## Goal
The new item exists in `cos_item` with linked context, research notes, a score, and a proposed slot. The user learns what you found in ≤6 lines.

## Inputs
- The user's text, or a forwarded email/message (becomes the `source` link)
- Optional: due date, goal, owner. If the due date is missing, propose one rather than asking.

## Steps
1. **Normalize.** Write a verb-first title (≤80 chars). Pick an `item_type`. Draft a provisional `signature` (verb|object|counterpart).
2. **Dedupe.** Search open `cos_item` rows for a similar title or a shared source link. If you find a match, ask: "Looks like this matches **<title>**. Merge, or keep separate?" Stop until the user answers.
3. **Confidentiality check.** If any CLAUDE.md §1.5 keyword appears, set `confidential=true`. Skip the research summaries (links only) and tell the user.
4. **Investigate** (Work IQ, ≤4 targeted queries total, newest first, last 30 days):
   - mail: threads mentioning the key nouns or people
   - calendar: upcoming or recent meetings on the topic or with the counterpart
   - files: documents recently edited on the topic
   - Teams: chats or channel posts on the topic
   Keep only results that are clearly relevant. Fewer, better links beat many weak ones. **[judgment]**
5. **Write** the `cos_item` (status=triaged) and one `cos_link` per kept result (relation: source/context; include `web_url` and `graph_id`). Put a 2–4 bullet `research_notes`: what's known, what's open, who's involved, and any deadline found in context.
6. **Goal fit.** Match to a `cos_goal`. If nothing fits, say so; that's a signal, not a blocker.
7. **Playbook check.** Call `find_playbook(signature)`. If one exists, mention it: "I have a playbook for this; want me to run it?"
8. **Prioritize.** Run the prioritize skill on this item, plus today's top 3 for comparison.
9. Log `created` and `investigated` to `cos_activity`.

## Output

```
ADDED [P2·58] <title>
next: <next action> · due <date> (<found in email | proposed>) · goal: <goal | none>
context: <n> links — <most important link title>, <second>
notes: <one-line summary of research>
vs today: ranks #<k>; <tradeoff if it displaces a top-3 item>
<one question, only if needed>
```

## Guardrails
- Never fabricate a due date. Label it "proposed" unless it was found in context.
- Investigate, don't act: no drafts or sends unless the user asks.
- Stop at 4 Work IQ queries. If context is still thin, say what's missing.

## Done when
- The item is saved with ≥1 link (or an explicit "no context found" note), a score, and a next action
- The user has seen the summary
