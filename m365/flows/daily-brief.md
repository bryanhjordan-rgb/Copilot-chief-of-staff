# Workflow: Daily brief (07:00)

**Phase:** 2 · **Trigger:** Recurrence, Mon–Fri 07:00 user timezone · **Est. credits:** 1 agent run/day

## Steps
1. **Recurrence** trigger (weekdays only). Skip if today is a holiday listed in the user's calendar as an all-day OOO event.
2. **Dataverse → List rows** `cos_item` where status in (inbox, triaged, scheduled, in_progress, waiting, blocked). Only the count is needed here, for a guard.
3. **Condition:** If there are 0 open items and 0 meetings, post "Clear day — nothing open. Want to plan goal work?" and stop.
4. **Run agent** (Microsoft 365 Copilot / agent node) with the prompt:
   `Run daily-brief for <yyyy-mm-dd>. Invocation: scheduled. Return the brief markdown and the cos_brief id.`
5. **Teams → Post adaptive card** to the user's chat with the agent:
   - Body: brief markdown (Top 3, Plan, Heads up, Not today)
   - Actions: **Accept** · **Edit** (opens chat with the agent, prefilled "Edit today's brief: ") · **Re-plan**
6. **On card response**:
   - Accept → `log_feedback(brief, <id>, accept)` and set `cos_brief.status=accepted`
   - Re-plan → run the agent: `Re-plan today. Reason: user requested.`
7. **Failure path:** If the agent run fails, post "Brief failed to generate — say 'plan my day' to run it manually." Log the error.

## Test
- Run manually with a seeded day of 5 items and 3 meetings. Check that the card renders, the links open, and the Accept button writes `cos_feedback`.
