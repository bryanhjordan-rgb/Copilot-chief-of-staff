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
│   ├── 07-tenant-readiness.md  # checklist for IT (do this first)
│   └── 08-build-guide.md       # Phase 1 step-by-step in Copilot Studio
├── agent/
│   ├── instructions.md         # agent instructions template (<8k chars, checked)
│   ├── profile.example.yaml    # your values → render_instructions.py fills the template
│   └── agent-config.yaml       # tools, knowledge, triggers, model
├── skills/                     # SKILL.md (open Agent Skills format)
│   ├── _template/
│   ├── prioritize/  intake/  daily-brief/  reconcile/  skill-miner/  triage/
│   ├── meeting-prep/  meeting-debrief/
├── evals/                      # scenario tests per skill + fixtures (README explains scoring)
├── schema/workbook.yaml        # workbook schema (source of truth)
├── workbook/ChiefOfStaff.xlsx  # generated — upload to OneDrive
├── tests/                      # unittest suite for the scripts
├── office-scripts/             # TypeScript run inside the workbook (deterministic skill mining)
├── flows/                      # workflow specs: daily-brief, completion-detector, weekly-skill-review
│   └── cards/                  # Adaptive Card templates the flows post to Teams
└── scripts/
    ├── skills.py               # validate + package skills for import
    ├── build_workbook.py       # build ChiefOfStaff.xlsx from the schema
    ├── lint_workbook.py        # check a live workbook against schema + cell conventions
    ├── mine.py                 # reference implementation of the mining Office Script
    └── render_instructions.py  # profile.yaml → dist/instructions.md (paste into Copilot Studio)
```

## Working with skills

```bash
pip install pyyaml
python3 m365/scripts/skills.py validate   # frontmatter, naming, sections, instruction length, evals present
python3 m365/scripts/skills.py package    # → dist/skills/<name>.zip for Copilot Studio → Skills → Upload
python3 m365/scripts/skills.py export-evals  # → dist/evals.csv
```

## The workbook (v1 store)

```bash
pip install pyyaml openpyxl
python3 m365/scripts/build_workbook.py    # → m365/workbook/ChiefOfStaff.xlsx (empty template)
python3 m365/scripts/build_workbook.py ~/ChiefOfStaff.xlsx --goals goals.yaml   # with your goals filled in
```

Upload `ChiefOfStaff.xlsx` to OneDrive (`/Apps/ChiefOfStaff/`). The **List** sheet is the daily list. Goals, Skills, and Feedback support prioritization and the learning loop. Change columns in `schema/workbook.yaml` and rebuild; don't edit the headers by hand. Layout and connector rules: [03-data-model.md](docs/03-data-model.md).

Check a live copy at any time (download it from OneDrive first):

```bash
python3 m365/scripts/lint_workbook.py ~/Downloads/ChiefOfStaff.xlsx
```

It flags rows that would trip up the agent or skew the metrics: Open/Status out of sync, malformed links or dates, done items missing a signature, confidential items with notes, broken Goal/Skill references. It also prints the share of open items with at least one link (the Phase 1 exit metric).

CI runs `validate`, a workbook build, the linter, and `python3 -m unittest discover -s m365/tests` on every PR that touches `m365/`.

## Start here

1. [07-tenant-readiness.md](docs/07-tenant-readiness.md) — confirm what your tenant allows
2. [08-build-guide.md](docs/08-build-guide.md) — Phase 1 build, step by step, with smoke tests
3. [05-roadmap.md](docs/05-roadmap.md) — phases and exit tests
4. Copy `agent/profile.example.yaml` to `agent/profile.yaml`, fill it in, and run `python3 m365/scripts/render_instructions.py`
