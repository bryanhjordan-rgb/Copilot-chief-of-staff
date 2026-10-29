# Workflow: Weekly skill review

**Phase:** 3 · **Trigger:** Recurrence, Friday 15:00 · **Est. credits:** 1 agent run/week

## Steps
1. **Guard:** **Excel → List rows** (Items, filter `Open eq 'No'`). If fewer than 5 rows have CompletedOn in the last 30 days, run the agent for the week summary only (no mining) and stop.
2. **Run agent** with:
   `Run skill-miner. Window: 30 days mining, 7 days summary. Present proposals for approval.`
3. **Compose + post** [`cards/weekly-review.card.json`](cards/weekly-review.card.json) (REVIEW_TITLE, REVIEW_MARKDOWN, REVIEW_DATE) and wait for a response.
4. **On response:** run the agent with the `decisions` text, `approve all`, or `reject all` (see [cards/README.md](cards/README.md)). Skill-miner step 9 applies the change to the Skills table.
5. **Monthly (first Friday):** append a cost line: count of agent runs triggered by workflows this month (from flow run history).

## Graduation hand-off (manual, Phase 4)
1. The agent outputs the SKILL.md for a graduating playbook (from its Skills row's Body).
2. In this repo: create `m365/skills/<name>/SKILL.md`, run `python3 m365/scripts/skills.py validate`, and open a PR.
3. After merge: `python3 m365/scripts/skills.py package` → import `dist/skills/<name>.zip` in Copilot Studio → Skills.
4. Update the Skills row: Tier=native, RepoPath=`m365/skills/<name>`.
