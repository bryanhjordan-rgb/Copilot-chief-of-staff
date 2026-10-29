# M365 Chief of Staff Agent

A chief-of-staff agent for Microsoft 365 Copilot, built in Copilot Studio. It:

- **builds a prioritized daily activity list**, with each item linked to its context (emails, chats, meetings, files, people)
- **takes items by conversation** ("add …"), investigates them, and slots them into the plan
- **reconciles completed work** into permanent records
- **generates skills** from repeated work and feedback, with your approval

This folder is the agent's source of truth ("agent-as-code"). Copilot Studio is the deployment target. The Claude Code kit at the repo root is the design reference.

## Layout

```
m365/
├── docs/
│   ├── 01-scope.md             # vision, jobs, in/out of scope, metrics, assumptions
│   ├── 02-architecture.md      # platform choice, components, core flows, security
│   ├── 03-data-model.md        # workbook layout, cell conventions, connector constraints
│   ├── 04-skill-lifecycle.md   # observe → mine → propose → playbook → native
│   ├── 05-roadmap.md           # phases, exit tests, iteration log
│   ├── 06-decisions.md         # ADRs + open questions
│   └── 07-tenant-readiness.md  # checklist for IT (do this first)
├── agent/
│   ├── instructions.md         # agent instructions (<8k chars, checked)
│   └── agent-config.yaml       # tools, knowledge, triggers, model
├── skills/                     # SKILL.md (open Agent Skills format)
│   ├── _template/
│   ├── prioritize/  intake/  daily-brief/  reconcile/  skill-miner/
├── schema/workbook.yaml        # workbook schema (source of truth)
├── workbook/ChiefOfStaff.xlsx  # generated — upload to OneDrive
├── flows/                      # workflow specs: daily-brief, completion-detector, weekly-skill-review
└── scripts/
    ├── skills.py               # validate + package skills for import
    └── build_workbook.py       # build ChiefOfStaff.xlsx from the schema
```

## Working with skills

```bash
pip install pyyaml
python3 m365/scripts/skills.py validate   # frontmatter, naming, sections, instruction length
python3 m365/scripts/skills.py package    # → dist/skills/<name>.zip for Copilot Studio → Skills → Upload
```

## The workbook (v1 store)

```bash
pip install pyyaml openpyxl
python3 m365/scripts/build_workbook.py    # → m365/workbook/ChiefOfStaff.xlsx
```

Upload `ChiefOfStaff.xlsx` to OneDrive (`/Apps/ChiefOfStaff/`). The **List** sheet is the daily list. Goals, Skills, and Feedback support prioritization and the learning loop. Change columns in `schema/workbook.yaml` and rebuild; don't edit the headers by hand. Layout and connector rules: [03-data-model.md](docs/03-data-model.md).

CI runs `validate` and a workbook build on every PR that touches `m365/`.

## Start here

1. [07-tenant-readiness.md](docs/07-tenant-readiness.md) — confirm what your tenant allows
2. [05-roadmap.md](docs/05-roadmap.md) — Phase 0 → Phase 1 build steps
3. Fill the `{{PLACEHOLDERS}}` in `agent/instructions.md` (same values as the root `CLAUDE.md`)
