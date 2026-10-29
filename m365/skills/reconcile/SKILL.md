---
name: reconcile
description: >-
  Closes an item properly: gathers completion evidence from linked mail, chats,
  meetings and files, writes a permanent completion record with outcome,
  decisions, artifacts, time and steps, updates goal progress, and creates
  follow-ups. Use for "done with …", "finished …", "close out …", or when the
  completion detector finds evidence. Do not use to drop an item without doing
  it (just set status=dropped).
metadata:
  version: "0.1.0"
  tier: "native"
  signatures: "close|item|self"
  tools: "dataverse, work-iq"
  status: "draft"
---

# Reconcile

## Goal
A `cos_record` exists that a future reader (or the skill miner) can use to understand what was done, how, and with what result, without re-reading the threads.

## Inputs
- An item id, or user text identifying the item. If it's ambiguous, show the 2–3 closest open items and ask which one.
- Trigger: `user` (user says done) or `detector` (evidence found; confirm before closing)

## Steps
1. **Confirm (detector only).** "Looks like **<title>** is done (<evidence>). Mark complete?" Stop until the user answers.
2. **Gather evidence** from the item's `cos_link` rows and Work IQ (since the item was created):
   - mail you sent on linked threads, meetings that took place, files edited, Teams messages posted
   - new artifacts not yet linked (a doc created, a deck shared) → add as `cos_link` with relation=output
3. **Steps.** Rebuild the ordered steps from `cos_activity` plus the evidence: `[{step, tool, minutes}]`. Estimate minutes where unknown and mark them `~`. **[judgment]**
4. **Signature.** Pick an existing signature from past `cos_record` rows if one fits. Otherwise mint `verb|object|counterpart` (lowercase, kebab-case). Reusing signatures matters more than precision, because mining depends on it.
5. **Write `cos_record`**: outcome (1–3 sentences), decisions, people, artifacts, minutes_spent, steps, signature, what_worked (one line if obvious, else empty).
   - If `confidential=true`: outcome = "Completed — see linked artifacts". Leave decisions empty. Artifacts are links only.
6. **Update the item**: status=done, completed_on=now, signature. Log `completed` and `reconciled` to `cos_activity`.
7. **Goal progress.** If the item is linked to a goal and plausibly moved a key result, propose a `goal_delta` (e.g., +0.05) and apply it when the user confirms. **[judgment]**
8. **Follow-ups.** Pull open asks from the evidence (someone waiting on the user, a promised next step) and offer to create items via intake.
9. **Playbook.** If the item ran a playbook, call `log_skill_run` (outcome, edits, minutes saved).
10. **Early finish.** If it was completed before `due_date`, say so in one line.

## Output

```
CLOSED <title> — <minutes> min · <signature>
outcome: <1–2 sentences>
artifacts: <link>, <link>
goal: <goal> +<delta>? (confirm)
follow-ups: <ask from Jane: send revised quote by Fri> — add?
```

## Guardrails
- Records are write-once. To correct one, log feedback rather than editing the record.
- Don't close an item from detector evidence without user confirmation.
- Store references, not copies, of email or meeting content longer than 2 sentences.

## Done when
- Item status=done with a `cos_record` containing signature and steps
- Follow-ups have been offered (or "none found")
