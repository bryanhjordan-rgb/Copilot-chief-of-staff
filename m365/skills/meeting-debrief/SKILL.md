---
name: meeting-debrief
description: >-
  Turns a meeting that just happened into records and next steps: pulls the
  Teams recap or transcript (or the user's notes), extracts decisions and action
  items, creates list items for the user's actions and waiting-on items for
  others', drafts a follow-up note, and closes the linked meeting-prep item. Use
  for "debrief the …", "what came out of that meeting?", "capture actions from
  …", or right after a meeting the user prepped for. Do not use before the
  meeting (meeting-prep).
metadata:
  version: "0.1.0"
  tier: "native"
  signatures: "debrief|meeting|self"
  tools: "work-iq, outlook, excel"
  status: "draft"
---

# Meeting debrief

## Goal
Nothing agreed in the meeting is lost: the user's actions are on the list, others' commitments are tracked as waiting-on, decisions are recorded, and a follow-up note is ready to send.

## Inputs
- The meeting: named or "the last meeting". It must have ended.
- Source, in order of preference: Teams meeting recap / transcript (Work IQ), meeting chat, or notes the user pastes. If none exists, ask the user for 3 bullets: decisions, my actions, their actions.

## Steps
1. **Find the meeting** and confirm that it ended. Get attendees and the Teams link.
2. **Get the content.** Recap or transcript via Work IQ. If there's none, use the meeting chat; if that's empty too, ask once for bullets.
3. **Extract** **[judgment]**:
   - Decisions: what was agreed, by whom
   - User's actions: verb-first, with a due date only if one was stated
   - Others' actions: owner + what + when
   - Open questions
   Quote nothing longer than one sentence from the transcript.
4. **Dedupe** against open Items (same SourceLink meeting or similar title). Update an existing item rather than duplicating it.
5. **Show** the extraction and the proposed item changes. Wait for "OK" or edits. Don't write before then.
6. **Write** (after OK):
   - Each user action → `add_row(Items)` via the intake rules, without re-investigation: Source=meeting, SourceLink `[meeting] <subject> (<date>) | <url>`, People = attendees involved, Type task/follow_up
   - Each others' action that matters to the user's goals → `add_row(Items)` with Status=waiting, WaitingOn=<owner>, DueDate if stated, Type=follow_up
   - The linked `meeting_prep` item (if any) → close it through the reconcile rules: Outcome = decisions in 1–3 sentences, Artifacts = the recap link
7. **Follow-up note.** Draft a short recap email or Teams message to the attendees (decisions + owners + dates) in the user's voice. **Draft only.** It goes out only on "Send".
8. **Prioritize** the new items against today's list and state any tradeoff in one line.

## Output

```
DEBRIEF — <subject> (<date>)
DECIDED
- <decision>
YOUR ACTIONS → new items
- [P2·58] <action> — due <date | none stated>
THEIR ACTIONS → waiting on
- <owner>: <action> — by <date>
OPEN QUESTIONS
- <question>

Follow-up draft to <attendees>:
"<draft>"
[OK to write items · Edit · Send follow-up]
```

## Guardrails
- Never send the follow-up without "Send".
- Don't assign actions to people who didn't agree to them in the meeting. If an owner is unclear, mark it "owner unclear" and ask.
- Confidential meetings: record decisions as "see recap" plus the link only. No transcript excerpts.
- Don't write any rows before the user confirms the extraction.

## Done when
- The user confirmed the extraction; action and waiting-on items exist with the meeting as SourceLink; the prep item is closed; the follow-up draft is shown
