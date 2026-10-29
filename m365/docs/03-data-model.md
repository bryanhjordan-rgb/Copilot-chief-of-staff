# 03 — Data Model (Excel workbook)

**Status:** v0.2 (2026-10-29). Store changed from Dataverse to an Excel workbook (ADR-006).
**Definitions:** [`../schema/workbook.yaml`](../schema/workbook.yaml) is the source of truth. `scripts/build_workbook.py` generates [`../workbook/ChiefOfStaff.xlsx`](../workbook/ChiefOfStaff.xlsx) from it.

## Workbook layout

| Sheet | Excel table | Key | Purpose |
|-------|-------------|-----|---------|
| Guide | — | — | Column reference, generated from the schema |
| **List** | `Items` | ID | **The daily activity list.** One row per item: plan, context, and completion record inline |
| Goals | `Goals` | ID | Active objectives (from `goals.yaml`); drives goal-fit scoring |
| Skills | `Skills` | Name | Skill registry: proposals, playbooks, native skills, run counters |
| Feedback | `Feedback` | ID | Accept/edit/reject/corrections, plus skill-run outcomes |

## Items: column groups

Header colors in the sheet match these groups.

| Group | Columns | Written by |
|-------|---------|-----------|
| **Plan** | ID, Open, Status, Tier, Score, Title, NextAction, DueDate, DoDate, PlannedSlot, EffortMin, Energy, Goal, Owner, WaitingOn | intake, prioritize, daily-brief |
| **Why** | Rationale, ScoreBreakdown | prioritize |
| **Context** | Type, Source, SourceLink, ContextLinks, People, ResearchNotes, Confidential | intake |
| **Tracking** | Created, Updated, History | every write |
| **Completion record** | CompletedOn, Outcome, Decisions, Artifacts, MinutesSpent, Steps, Signature, SkillUsed, FollowUps | reconcile (write-once) |

The first 6 columns (ID → Title) are frozen, so the list stays readable when scrolling right into context.

## Cell conventions

| What | Format | Example |
|------|--------|---------|
| Item ID | `I-YYYYMMDD-HHMMSS` | `I-20261029-081200` |
| Dates | ISO text | `2026-11-05`, `2026-10-29T08:12` |
| Links | one per line: `[type] Title \| url` | `[meeting] Contoso renewal review \| https://teams.microsoft.com/...` |
| History | one per line: `YYYY-MM-DD HH:MM actor action detail` | `2026-10-29 08:13 agent investigated (3 links)` |
| Steps | one per line: `step \| tool \| minutes` (`~` = estimate) | `update pricing model \| excel \| 25` |
| ScoreBreakdown | `factor=points; …` | `deadline=20; goal=18; stakeholder=10; unblocks=8; leverage=5; age=0` |
| Signature | `verb\|object\|counterpart` | `prepare\|pricing-review\|customer` |

The `I-EXAMPLE` row in the generated workbook shows every format filled in. Open=No keeps the agent from treating it as work.

## Why it's shaped this way (connector constraints)

The Excel Online (Business) connector sets the rules:

- **Data must be in tables, with a key column.** Get/Update a row look rows up by key.
- **Alphanumeric column names.** Filter, Order By, and Select reject spaces and symbols, hence `NextAction`, not "Next action".
- **One filter function per column.** "Status is not done and not dropped" can't be expressed, so `Open` (Yes/No) makes "all open items" a single filter: `Open eq 'Yes'`.
- **Update overwrites.** Appending to History needs a Get first, then an Update.
- **No formulas, no hidden columns.** Recalculation causes timeouts and duplicate inserts, and hidden columns break OData queries. Success rate is computed by the agent as Successes/Runs.
- **Writes can lag up to 30 s; the file can lock for up to 6 min after connector use; 100 calls/min.** Concurrent editing from Excel desktop + connector isn't supported. Read freely, but edit through the agent or Excel for the web, and not while the agent is writing.
- **25 MB file limit, 256 rows by default without pagination.** Pagination is turned on in the tool, and open items are queried by filter. At a few rows a day this is years of headroom. Archive done rows yearly if it ever matters.

## Mapping from the Claude Code kit

| Root kit file | Workbook equivalent |
|---------------|---------------------|
| `goals.yaml` | Goals table (one-time copy) |
| `my-tasks.yaml` | Items table |
| `contacts/*.md` | Phase 4: People context from Work IQ, or a Contacts sheet |
| `schedules.yaml` | Copilot Studio triggers / workflows (`m365/flows/`) |
| `commands/*.md` | `m365/skills/*/SKILL.md` |

## Keeping prose and schema in sync

Skills, flows, and evals refer to columns in prose (`Status=done`, `Open eq 'Yes'`, `update_row(Items, …)`). `skills.py validate` checks every such reference against `schema/workbook.yaml`: unknown columns, dropdown values outside the allowed list, and unknown tables all fail CI. To rename a column, change the schema, run validate, and fix what it reports.

## Migration path

When the list outgrows Excel (a second user, heavy concurrency, or real relational queries), move each table to a Dataverse table or SharePoint List with the same column names. The skills reference columns by name, so the changes are confined to the tool definitions and the "Data rules" section of the instructions.
