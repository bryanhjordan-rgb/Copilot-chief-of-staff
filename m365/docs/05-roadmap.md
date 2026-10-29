# 05 — Roadmap & Iteration Log

**Status:** Draft v0.1 (2026-10-29)

Each phase ends with an exit test. Don't start the next phase until the current exit test passes, because shipping a usable loop matters more than covering every feature.

---

## Phase 0 — Tenant readiness & personalization (week 0–1)

**Goal:** Know what the tenant allows. Get goals and constraints into machine-readable form.

- [ ] Complete [07-tenant-readiness.md](07-tenant-readiness.md) with IT (licenses, environment, Excel connector, Work IQ, DLP, MCP allowance)
- [ ] Fill in root `CLAUDE.md` Parts 2–4 and `goals.yaml` (they get copied into the Goals sheet and the instructions)
- [ ] Record baselines: minutes to plan the day, % of tasks done on time (1 week, manual)

**Exit test:** Every readiness row is answered, and either the chosen platform path is unblocked or a fallback is selected.

## Phase 1 — Conversational MVP (weeks 1–2)

**Goal:** Talk to the agent, add items, and get a prioritized day plan on demand.
**How:** follow [08-build-guide.md](08-build-guide.md).

- [ ] Build the workbook (`python3 m365/scripts/build_workbook.py`) or use the committed `m365/workbook/ChiefOfStaff.xlsx`. Upload it to OneDrive `/Apps/ChiefOfStaff/`
- [ ] Create the agent (harness) and paste `agent/instructions.md`. Configure tools per `agent/agent-config.yaml`
- [ ] Import skills: `prioritize`, `intake`, `daily-brief` (run `scripts/skills.py package`)
- [ ] Enter goals in the Goals sheet (G1, G2, …)
- [ ] Add Excel Online (Business) actions as tools (list/get/add/update rows) pointed at the workbook
- [ ] Publish to M365 Copilot + Teams (personal scope)
- [ ] Use for 5 workdays: "plan my day", "add …", "what now?"

**Exit test:** On 4 of 5 days the brief is accepted with ≤2 edits, and ≥90% of items have ≥1 link.

## Phase 2 — Automation & reconciliation (weeks 3–4)

**Goal:** The brief arrives without being asked, and completed work leaves a record.

- [ ] Workflow: daily brief at 07:00 → Teams adaptive card (`flows/daily-brief.md`)
- [ ] Import `reconcile` skill. Manual trigger first ("done with X")
- [ ] Import `triage` skill (read + draft only; sends need "Send")
- [ ] Workflow: completion detector (`flows/completion-detector.md`): linked thread replied / meeting ended / Planner task completed → ask "Mark complete?"
- [ ] Feedback capture on the brief card (Accept/Edit/Re-plan → Feedback row)

**Exit test:** ≥90% of completed items have Outcome, Steps, and Signature filled.

## Phase 3 — Learning loop (weeks 5–6)

**Goal:** The agent proposes skills from real usage and runs approved ones.

- [ ] Import `skill-miner` skill. Weekly workflow (`flows/weekly-skill-review.md`)
- [ ] First 3 playbooks approved and run at least 3× each
- [ ] Repeated-correction → patch proposals working

**Exit test:** ≥3 active playbooks, success rate ≥80%, and the weekly review is delivered 2 weeks in a row.

## Phase 4 — Graduation & expansion (week 7+)

- [ ] Graduate proven playbooks to native skills via PR → `scripts/skills.py package` → import
- [x] CI: GitHub Action runs `scripts/skills.py validate` and builds the workbook on PRs
- [x] Port `/triage` (Outlook + Teams) as a skill
- [ ] Port `/enrich` (people context) as a skill
- [ ] Meeting prep / debrief skills (uses Teams meeting recap via Work IQ)
- [ ] Metrics view: weekly scorecard from Items, Skills, and Feedback (a Summary sheet, or Power BI on the workbook)
- [ ] Revisit ADR-006: migrate to Dataverse/SharePoint Lists if Excel limits bite
- [ ] Optional: Planner/To Do mirror for mobile visibility

---

## Iteration log

| # | Date | What changed | Next |
|---|------|--------------|------|
| 1 | 2026-10-29 | Scope, architecture, data model, skill lifecycle, ADRs, tenant checklist. Instructions draft. Skills v0.1: prioritize, intake, daily-brief, reconcile, skill-miner. Skill validator/packager. | Phase 0: run the readiness checklist with IT; fill CLAUDE.md placeholders + goals |
| 2 | 2026-10-29 | Store switched from Dataverse to a single Excel workbook (ADR-006): schema/workbook.yaml, generated ChiefOfStaff.xlsx, skills v0.2 and flows rewritten for the Excel connector. Custom tools dropped; Phase 1 needs only Excel + Work IQ/Outlook. | Upload workbook, wire Excel tools, run Phase 1 |
| 3 | 2026-10-29 | Phase 1 build guide (08-build-guide.md) with an 8-step smoke test. | Evals |
| 4 | 2026-10-29 | Skill evals: fixtures + 20 cases across 5 skills, pass/partial/fail scoring, import bar; validator requires ≥3 cases per skill; export to CSV. | Workbook linter + tests |
| 5 | 2026-10-29 | Workbook linter (schema, Open/Status sync, link/date/signature formats, confidential rules, references, link-coverage metric) + 15 unittest cases for build/lint/validate; all wired into CI. Fixed: example row referenced a non-existent goal. | Seed Goals from goals.yaml |
| 6 | 2026-10-29 | `build_workbook.py --goals goals.yaml`: objectives → G1… by priority, personal goals → PG1…; warns on template examples. Prioritize rubric distinguishes G*/PG* (0.2.1). 2 new tests. | Adaptive cards |
| 7 | 2026-10-29 | Adaptive Cards 1.5 for the daily brief (Accept / Send edit / Re-plan), weekly review (decide / approve all / reject all), and completion confirmation (Mark complete / Not yet), with token + response mapping. Flows wired to them; daily-brief and skill-miner return card-safe markdown when scheduled; reconcile skips re-asking after card confirmation (+1 eval). Card tests. | Office Script for mining |
| 8 | 2026-10-29 | `mine-signatures` Office Script (groups done items by signature in the window; count, avg minutes, weekly/monthly cadence, ⅔ common steps, automation fit, score, est. saved, evidence; excludes active skills) + Python twin `mine.py`; parity test compiles the TS with tsc and compares outputs under Node. Weekly flow runs it before the agent; skill-miner 0.2.2 consumes it. | Triage skill |
| 9 | 2026-10-29 | `triage` skill (Outlook + Teams): 3 tiers, already-handled and open-item dedupe, key-person rule from P1/P2 People, confidentiality check, calendar-verified scheduling drafts, Send/Draft/Track/Edit actions, draft edits logged as Feedback; 5 evals; added to instructions routing. CI actions bumped to checkout@v5 / setup-python@v6 (Node 20 deprecation). | Meeting prep/debrief skills |
