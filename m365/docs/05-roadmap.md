# 05 — Roadmap & Iteration Log

**Status:** Draft v0.1 (2026-10-29)

Each phase ends with an exit test. Don't start the next phase until the current exit test passes, because shipping a usable loop matters more than covering every feature.

---

## Phase 0 — Tenant readiness & personalization (week 0–1)

**Goal:** Know what the tenant allows. Get goals and constraints into machine-readable form.

- [ ] Complete [07-tenant-readiness.md](07-tenant-readiness.md) with IT (licenses, environment, Dataverse, Work IQ, DLP, MCP allowance)
- [ ] Fill in root `CLAUDE.md` Parts 2–4 and `goals.yaml` (they get ported into `cos_goal` and the instructions)
- [ ] Record baselines: minutes to plan the day, % of tasks done on time (1 week, manual)
- [ ] Decide ADR-002 (Dataverse vs SharePoint Lists) based on the readiness results

**Exit test:** Every readiness row is answered, and either the chosen platform path is unblocked or a fallback is selected.

## Phase 1 — Conversational MVP (weeks 1–2)

**Goal:** Talk to the agent, add items, and get a prioritized day plan on demand.

- [ ] Create solution `ChiefOfStaff` and the tables from `schema/dataverse-tables.yaml`
- [ ] Create the agent (harness) and paste `agent/instructions.md`. Configure tools per `agent/agent-config.yaml`
- [ ] Import skills: `prioritize`, `intake`, `daily-brief` (run `scripts/skills.py package`)
- [ ] Import goals into `cos_goal`
- [ ] Publish to M365 Copilot + Teams (personal scope)
- [ ] Use for 5 workdays: "plan my day", "add …", "what now?"

**Exit test:** On 4 of 5 days the brief is accepted with ≤2 edits, and ≥90% of items have ≥1 link.

## Phase 2 — Automation & reconciliation (weeks 3–4)

**Goal:** The brief arrives without being asked, and completed work leaves a record.

- [ ] Workflow: daily brief at 07:00 → Teams adaptive card (`flows/daily-brief.md`)
- [ ] Import `reconcile` skill. Manual trigger first ("done with X")
- [ ] Workflow: completion detector (`flows/completion-detector.md`): linked thread replied / meeting ended / Planner task completed → ask "Mark complete?"
- [ ] Feedback capture on the brief card (Accept/Edit/Re-plan → `cos_feedback`)

**Exit test:** ≥90% of completed items have a `cos_record` with a signature and steps.

## Phase 3 — Learning loop (weeks 5–6)

**Goal:** The agent proposes skills from real usage and runs approved ones.

- [ ] Import `skill-miner` skill. Weekly workflow (`flows/weekly-skill-review.md`)
- [ ] Tools: `find_playbook`, `propose_skill`, `log_skill_run`, `log_feedback`
- [ ] First 3 playbooks approved and run at least 3× each
- [ ] Repeated-correction → patch proposals working

**Exit test:** ≥3 active playbooks, success rate ≥80%, and the weekly review is delivered 2 weeks in a row.

## Phase 4 — Graduation & expansion (week 7+)

- [ ] Graduate proven playbooks to native skills via PR → `scripts/skills.py package` → import
- [ ] CI: GitHub Action runs `scripts/skills.py validate` on PRs
- [ ] Port `/triage` (Outlook + Teams) and `/enrich` (people context) as skills
- [ ] Meeting prep / debrief skills (uses Teams meeting recap via Work IQ)
- [ ] Metrics view: weekly scorecard from `cos_brief`, `cos_record`, `cos_skill_run`
- [ ] Optional: Planner/To Do mirror for mobile visibility

---

## Iteration log

| # | Date | What changed | Next |
|---|------|--------------|------|
| 1 | 2026-10-29 | Scope, architecture, data model, skill lifecycle, ADRs, tenant checklist. Instructions draft. Skills v0.1: prioritize, intake, daily-brief, reconcile, skill-miner. Skill validator/packager. | Phase 0: run the readiness checklist with IT; fill CLAUDE.md placeholders + goals |
