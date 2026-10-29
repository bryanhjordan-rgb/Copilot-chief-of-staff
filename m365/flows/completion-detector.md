# Workflow: Completion detector

**Phase:** 2 · **Trigger:** Recurrence, Mon–Fri every 2h 09:00–17:00 · **Est. credits:** 0–4 agent runs/day (only when evidence is found)

The detector itself is deterministic. It calls the agent only when it has evidence, which keeps credit use low.

## Evidence rules (any one is enough to ask)

| Link on an open item | Evidence | Check |
|----------------------|----------|-------|
| SourceLink `[email]` | User sent a reply on the thread after Created | Outlook → Get emails (Sent Items, same conversation) |
| ContextLinks `[meeting]` with Type=meeting_prep | Meeting end time has passed | Outlook → Get calendar view (today) and match the meeting |
| Artifacts / ContextLinks `[file]` with Status=in_progress | File modified by the user after Created | OneDrive/SharePoint → Get file metadata using path |
| `[planner]` link | Planner task percentComplete = 100 | Planner → Get task |

## Steps
1. **Excel → List rows** (Items, filter `Open eq 'Yes'`). Parse SourceLink and ContextLinks lines (`[type] Title | url`).
2. Skip items whose History has a `completion_asked` line in the last 24h.
3. For each item, evaluate the rules. Collect `{ID, evidence_text}`.
4. If there's any evidence: run the agent with
   `Run reconcile in detector mode for these items: <json>. Ask the user to confirm each.`
5. For each item asked about: **Get a row**, then **Update a row** with History + `<now> flow completion_asked <evidence>`.

## Notes
- A meeting-prep item whose meeting has passed is the highest-confidence signal. Start with that rule alone if time is short.
- Excel is locked for up to 6 minutes after connector use. Keep this flow's writes to one batch at the end.
