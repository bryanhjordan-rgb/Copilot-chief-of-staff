# Workflow: Weekly skill review

**Phase:** 3 · **Trigger:** Recurrence, Friday 15:00 · **Est. credits:** 1 agent run/week

## Steps
1. **Guard:** If there are fewer than 5 `cos_record` rows in the last 30 days, post the week summary only (no mining) and stop.
2. **Run agent** with:
   `Run skill-miner. Window: 30 days mining, 7 days summary. Present proposals for approval.`
3. **Teams → Post adaptive card** with the review and one action set per proposal (**Approve** / **Reject**). **Edit** opens chat.
4. **On response:** run the agent with `approve <n>` / `reject <n>`. The skill-miner step 8 applies the change.
5. **Monthly (first Friday):** append a cost line: count of agent runs triggered by workflows this month (from flow run history).

## Graduation hand-off (manual, Phase 4)
1. The agent outputs the SKILL.md for a graduating playbook.
2. In this repo: create `m365/skills/<name>/SKILL.md`, run `python3 m365/scripts/skills.py validate`, and open a PR.
3. After merge: `python3 m365/scripts/skills.py package` → import `dist/skills/<name>.zip` in Copilot Studio → Skills.
4. Set `cos_skill.tier=native` and `repo_path`.
