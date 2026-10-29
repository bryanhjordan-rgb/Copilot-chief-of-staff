---
name: reconcile
description: >-
  Closes an item properly: gathers completion evidence from linked mail, chats,
  meetings and files, writes the completion record (outcome, decisions,
  artifacts, time, steps, signature) onto the item's row, updates goal progress,
  and creates follow-ups. Use for "done with …", "finished …", "close out …", or
  when the completion detector finds evidence. Do not use to drop an item without
  doing it (just set Status=dropped, Open=No).
metadata:
  version: "0.2.1"
  tier: "native"
  signatures: "close|item|self"
  tools: "excel, work-iq"
  status: "draft"
---

# Reconcile

## Goal
The item's completion columns let a future reader (or the skill miner) understand what was done, how, and with what result, without re-reading the threads.

## Inputs
- An item ID, or user text identifying the item. If it's ambiguous, show the 2–3 closest open items and ask which one.
- Trigger: `user` (user says done) or `detector` (evidence found; confirm before closing)

## Steps
1. **Confirm (detector only).** "Looks like **<title>** is done (<evidence>). Mark complete?" Stop until the user answers. Skip this when the message says "User confirmed", because the completion card already asked.
2. **Read** the row with `get_row(Items, ID)`.
3. **Gather evidence** from the SourceLink and ContextLinks, plus Work IQ since Created:
   - mail you sent on linked threads, meetings that took place, files edited, Teams messages posted
   - new artifacts (a doc created, a deck shared) → these go in Artifacts
4. **Steps.** Rebuild the ordered steps from History plus the evidence, one per line as `step | tool | minutes`. Prefix estimated minutes with `~`. **[judgment]**
5. **Signature.** `list_rows(Items, filter: Open eq 'No', select: Signature)` and reuse an existing signature if one fits. Otherwise mint `verb|object|counterpart` (lowercase, kebab-case). Reusing signatures matters more than precision, because mining depends on it.
6. **Write** with one `update_row(Items, ID)`:
   - Status=done, Open=No, CompletedOn=now, Updated=now
   - Outcome (1–3 sentences), Decisions, Artifacts (`[type] Title | url` per line), MinutesSpent, Steps, Signature
   - SkillUsed (if a playbook or skill drove the work)
   - History: existing text + `<now> agent reconciled`
   - If Confidential=Yes: Outcome = "Completed — see linked artifacts". Leave Decisions empty. Artifacts are links only.
7. **Goal progress.** If Goal is set and the item plausibly moved a key result, propose a progress increase (e.g., +0.05). When the user confirms, `update_row(Goals, ID)` with the new Progress and LastUpdate=today. **[judgment]**
8. **Follow-ups.** Pull open asks from the evidence (someone waiting on the user, a promised next step). Offer to create items via intake, then write their IDs to FollowUps.
9. **Playbook run.** If SkillUsed is a playbook: `update_row(Skills, Name)` incrementing Runs (and Successes if the user didn't have to redo the work), set LastUsed, and `add_row(Feedback)` with TargetType=skill_run, TargetRef=<skill name>, Signal=success|partial|fail.
10. **Early finish.** If it was completed before DueDate, say so in one line.

## Output

```
CLOSED <title> — <minutes> min · <signature>
outcome: <1–2 sentences>
artifacts: <link>, <link>
goal: <goal> +<delta>? (confirm)
follow-ups: <ask from Jane: send revised quote by Fri> — add?
```

## Guardrails
- The completion columns are write-once. If something is wrong later, log a Feedback row rather than overwriting them.
- Don't close an item from detector evidence without user confirmation.
- Store references, not copies, of email or meeting content longer than 2 sentences.

## Done when
- The row has Status=done, Open=No, and Outcome, Steps, and Signature filled
- Follow-ups have been offered (or "none found")
