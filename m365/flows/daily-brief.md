# Workflow: Daily brief (07:00)

**Phase:** 2 · **Trigger:** Recurrence, Mon–Fri 07:00 user timezone · **Est. credits:** 1 agent run/day

## Steps
1. **Recurrence** trigger (weekdays only). Skip if today has an all-day OOO event on the user's calendar.
2. **Excel → List rows present in a table** (Items, filter `Open eq 'Yes'`, Top Count 1). Only the count is needed here, for a guard.
3. **Condition:** If there are 0 open items and 0 meetings, post "Clear day — nothing open. Want to plan goal work?" and stop.
4. **Run agent** (Microsoft 365 Copilot / agent node) with the prompt:
   `Run daily-brief for <yyyy-mm-dd>. Invocation: scheduled. Return the brief markdown.`
5. **Compose** the card from [`cards/daily-brief.card.json`](cards/daily-brief.card.json): BRIEF_TITLE = first line of the brief, BRIEF_MARKDOWN = the rest, BRIEF_DATE = today.
6. **Teams → Post adaptive card in a chat or channel and wait for a response** (Flow bot → your chat).
7. **Switch on `data.action`** (full mapping in [cards/README.md](cards/README.md)):
   - accept → **Excel → Add a row** to Feedback: ID `F-<yyyyMMdd-HHmmss>`, Date, TargetType=brief, TargetRef=<date>, Signal=accept, Applied=No
   - edit → run the agent with `Edit today's brief: <editText>`, then add a Feedback row with Signal=edit, Detail=<editText>
   - replan → run the agent: `Re-plan today. Reason: user requested.` Post the result as a new card
8. **Failure path:** If the agent run fails, post "Brief failed to generate — say 'plan my day' to run it manually." Log the error.

## Test
- Seed the workbook with 5 open items and put 3 meetings on the calendar, then run the flow manually. Check that the card renders, the links open, DoDate/PlannedSlot get written to the planned rows, and Accept adds a Feedback row.
