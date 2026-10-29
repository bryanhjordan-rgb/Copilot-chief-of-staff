---
name: triage
description: >-
  Scans Outlook mail and Teams chats/mentions since the last triage, sorts what
  needs the user into Tier 1 (respond now), Tier 2 (today) and Tier 3 (FYI),
  drafts replies in the user's voice, and offers to track real work as list
  items. Use for "triage", "clear my inbox", "what needs me?", "anything
  urgent?", "triage quick". Do not use for a single known email the user wants
  answered (just draft it) or for adding one item (intake).
metadata:
  version: "0.1.1"
  tier: "native"
  signatures: "triage|inbox|self"
  tools: "work-iq, outlook, teams, excel"
  status: "draft"
---

# Triage

## Goal
Every message that needs the user is surfaced once, ranked, and either has a send-ready draft or is offered as a tracked item. Nothing is sent without "Send".

## Inputs
- Mode: `quick` (Tier 1 only, no drafts), `digest` (drafts for Tier 1, summaries for Tier 2), or default (drafts for Tier 1 and 2)
- Window: the last 24 hours, or since the previous triage in this conversation if there was one. The user can override it ("triage since Monday").

## Steps
1. **Time and context.** Get the current time and today's calendar, so "today" and "urgent" are anchored to where the user is in their day.
2. **Scan** (Work IQ, or the Outlook/Teams connectors):
   - Outlook: messages to the user (To, not just CC) in the window, unread or unreplied. Skip newsletters, automated notifications, and calendar responses.
   - Teams: 1:1 and group chats with unread messages addressed to the user, plus @mentions in channels.
3. **Already handled?** Drop a message when the user has replied on the thread or chat since it arrived, or when it matches an open item's SourceLink. If it matches an open item, mention the item instead of re-surfacing the message.
4. **Key people.** Treat a sender as key if they're in the People cell of any open P1/P2 item, are the user's manager or a direct report (Work IQ people), or are listed on the "Key people" line of the instructions. **[judgment]** for anyone else senior.
5. **Tier** each message:
   | Tier | Rule |
   |------|------|
   | 1 — respond now | key person and a direct ask, someone blocked, a deadline today or tomorrow, or explicit urgency |
   | 2 — today | needs a thoughtful reply or decision, a deadline this week, or waiting >2 days |
   | 3 — FYI | informational, CC-only, no ask |
   **[judgment]** Ties go up a tier if the message relates to an active goal.
6. **Confidentiality.** If the thread hits a CLAUDE.md §1.5 keyword and the reply would go via Teams or work email, show the confidentiality warning before drafting.
7. **Draft** replies (per mode) in the user's voice from the instructions: short, contractions, "Thanks". Summarize long threads; don't quote them. For anything involving times, follow the calendar verification protocol: check free/busy and propose 2–3 specific slots, or say "I'll send times once I've checked my calendar." Never write "let me know what works".
8. **Real work.** If answering requires work beyond a reply (prepare, review, decide, research), offer it as an item: "Track as item?" Accepted items go through the intake rules (SourceLink = the message, skip re-investigation of that thread).
9. **Present** (format below) and wait.
10. **Act on approval.** "Send 2" → send that draft (the send tool asks for confirmation). "Draft 2" → save it as an Outlook draft. "Track 3" → create the item. "Edit 2: …" → revise and show again. Skip anything not mentioned.
11. **Learn.** For every draft the user edited before sending, add a Feedback row: TargetType=draft, Signal=edit, Detail=<what they changed>, Theme like `tone:too-formal` or `length:too-long`.

## Output

```
TRIAGE — <time> · scanned <n> mail, <m> Teams · <k> need you

TIER 1 — respond now
1. <sender> — <subject/summary> (<mail|teams>, waiting <age>)
   Draft: "<reply>"
   [Send 1 · Draft 1 · Edit 1]

TIER 2 — today
2. <sender> — <summary> (<channel>)
   Draft: "<reply>"
3. <sender> — <ask that needs real work> → Track as item? (est. <min> min, due <date>)

TIER 3 — FYI
- <sender>: <one line> · <sender>: <one line>

Already on your list: <item title> (new message from <sender>)
```

If nothing needs the user: "Inbox clear — nothing needs you right now."

## Guardrails
- NEVER send, post, or reply without an explicit "Send" for that specific draft. "Send all" is allowed only after every draft has been shown.
- Never propose meeting times without checking the calendar first.
- Never put the scheduling burden on the recipient.
- Don't archive, delete, flag, or mark as read anything. Triage only reads and drafts.
- Don't re-surface a message that was already shown in a previous triage unless something new arrived on it.

## Done when
- Every Tier 1/2 message has a draft (default mode) or a summary (digest), or has been offered as an item
- The user's send, draft, and track decisions are executed, and edits are logged as Feedback
