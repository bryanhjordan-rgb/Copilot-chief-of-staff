# Workflow: Completion detector

**Phase:** 2 · **Trigger:** Recurrence, Mon–Fri every 2h 09:00–17:00 · **Est. credits:** 0–4 agent runs/day (only when evidence is found)

The detector itself is deterministic. It calls the agent only when it has evidence, which keeps credit use low.

## Evidence rules (any one is enough to ask)

| Link type on an open item | Evidence | Check |
|---------------------------|----------|-------|
| email (relation=source) | User sent a reply on the thread after the item's creation | Outlook → Get emails (Sent Items, conversationId = graph_id) |
| meeting (relation=context, item_type=meeting_prep) | Meeting end time has passed | Outlook calendar → Get event (graph_id) |
| file (relation=output) | File modified by the user after item creation and item is in_progress | SharePoint/OneDrive → Get file properties |
| planner_task | Planner task percentComplete = 100 | Planner → Get task |

## Steps
1. List open `cos_item` rows that have ≥1 link of the types above. Skip items asked about in the last 24h (track this in `cos_activity` action=`completion_asked`).
2. For each item, evaluate the rules. Collect `{item_id, evidence_text}`.
3. If there's any evidence: run the agent with
   `Run reconcile in detector mode for these items: <json>. Ask the user to confirm each.`
4. Log `completion_asked` to `cos_activity` for each item asked about.

## Notes
- A meeting-prep item whose meeting has passed is the highest-confidence signal. Start with that rule alone if time is short.
