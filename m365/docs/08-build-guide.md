# 08 — Phase 1 Build Guide (Copilot Studio)

**Goal:** a working conversational chief of staff, in about 90 minutes. You can say "add …", "plan my day", and "what now?" in Microsoft 365 Copilot or Teams, and the agent reads and writes `ChiefOfStaff.xlsx`.

**Before you start:** readiness rows R2 (maker access) and R3 (Excel connector allowed) in [07-tenant-readiness.md](07-tenant-readiness.md) must be "yes". Copilot Studio menus move often, so if a label below doesn't match, look for the nearest equivalent and note it in the iteration log.

---

## Step 1 — Put the workbook in OneDrive (5 min)

1. Get the file: `m365/workbook/ChiefOfStaff.xlsx` from the repo, or rebuild it with `python3 m365/scripts/build_workbook.py`.
2. In OneDrive for Business, create the folder **Apps › ChiefOfStaff** and upload the file there.
3. Open it in **Excel for the web**. Check that it has 5 sheets (List, Goals, Skills, Feedback, Guide), and that **Table Design** shows the table names `Items`, `Goals`, `Skills`, `Feedback`.
4. On the **Goals** sheet, replace the blank row with your real goals: `G1`, `G2`, … with Priority 1 = highest. Use the same goals as `goals.yaml`.
5. Close the tab. The connector can't write while an edit session is mid-save.

## Step 2 — Create the agent (10 min)

1. Go to copilotstudio.microsoft.com and pick your work environment (top right).
2. **Create › New agent**. Skip the conversational setup and use **Configure**.
3. **Name:** `Chief of Staff`. **Description:** copy it from `agent/agent-config.yaml`.
4. **Orchestration / harness:** choose the GitHub Copilot harness if offered (R4). Otherwise use generative orchestration.
5. **Model:** Claude Sonnet 5 if it's allowed (R10). Otherwise use the default. You'll A/B test later (Q4).
6. **Instructions:** fill the `{{PLACEHOLDERS}}` in `agent/instructions.md` (name, role, company, home-by time, earliest meeting, tone), paste it in, and save.
   - Check the length first: `python3 m365/scripts/skills.py check-instructions` must report ≤ 8000.

## Step 3 — Add the Excel tools (20 min)

Add **four** tools from the **Excel Online (Business)** connector. For each one: **Tools › Add a tool › Connector › Excel Online (Business) ›** pick the action, then sign in with your work account.

Set these inputs the same way on all four:

| Input | Value | How |
|-------|-------|-----|
| Location | `OneDrive for Business` (or `me`) | Set as a fixed value, not filled by AI |
| Document Library | `OneDrive` | Fixed value |
| File | `/Apps/ChiefOfStaff/ChiefOfStaff.xlsx` | Fixed value (use the file picker) |
| Table | — | **Filled by AI**, so one tool serves all four tables |

Then set these per action:

| Tool name (rename it) | Action | Extra settings | Description for the agent (paste) |
|-----------------------|--------|----------------|-----------------------------------|
| `list_rows` | List rows present in a table | DateTime Format = ISO 8601. Filter Query, Order By, Select Query, Top Count = filled by AI | "Read rows from the Items, Goals, Skills, or Feedback table. Use Filter Query `Open eq 'Yes'` for open items. Only one filter function per column." |
| `get_row` | Get a row | Key Column + Key Value = filled by AI. DateTime Format = ISO 8601 | "Read one row by key. Keys: Items→ID, Goals→ID, Skills→Name, Feedback→ID." |
| `add_row` | Add a row into a table | Row = filled by AI | "Add one row. Always supply the key (ID or Name). Dates are ISO text." |
| `update_row` | Update a row | Key Column, Key Value, item properties = filled by AI | "Update cells in one row by key. Blank fields stay unchanged. To append to History, get_row first." |

If the Table input can't be AI-filled in your tenant, create one set of tools per table instead (`list_items`, `add_item`, …). Start with Items + Goals; Skills and Feedback aren't needed until Phase 3.

**Confirmation:** none on these four tools (internal data, no outbound effect).

## Step 4 — Add context (15 min)

Pick **one** path:

- **A. Work IQ (preferred, R6):** **Knowledge** (or **Tools**) **› Work IQ ›** enable mail, calendar, files, Teams, and people.
- **B. Connectors (fallback):** add from **Office 365 Outlook**: *Search email (V2)*, *Get emails (V3)*, *Get calendar view of events (V3)*. Add from **Microsoft Teams**: *Search messages*. Fill all inputs with AI except the mailbox and calendar (yours).

**Drafts and sends:** if you add *Draft an email* / *Send an email (V2)*, set **Ask the user before running = Yes** on the send tool (ADR-005).

## Step 5 — Import skills (10 min)

1. `pip install pyyaml && python3 m365/scripts/skills.py package` → produces `dist/skills/*.zip`.
2. Agent **› Skills › Upload**: import `prioritize.zip`, `intake.zip`, and `daily-brief.zip`.
3. Check that each one shows its name and description. `reconcile` and `skill-miner` wait until Phase 2/3.
4. **No Skills tab (R5 = no)?** Paste the body of each SKILL.md into the instructions under a heading only if there's room. Otherwise create one **Topic** per skill whose trigger is its description and whose body is the skill text.

## Step 6 — Smoke test in the test pane (15 min)

Run these in order. After each one, open the workbook and check the result.

| # | Say | Expect in chat | Expect in workbook |
|---|-----|----------------|--------------------|
| 1 | "What are my goals?" | Your Goals rows | — |
| 2 | "Add: send Q4 budget draft to finance by Friday" | ADDED summary with tier, score, next action, due date, links (or "no context found") | New row on List: `I-…` ID, Open=Yes, Status=triaged, Score, Rationale, ScoreBreakdown, History line |
| 3 | "Add: look into renewing the analytics vendor contract" | Summary plus at most one question | Second row. ContextLinks filled if anything relevant exists |
| 4 | "Add: send Q4 budget draft to finance" | Dedupe question ("matches … merge?") | No new row until you answer |
| 5 | "What now?" | Ranked list with at least one TRADEOFF line | Score, Tier, and Rationale updated |
| 6 | "Plan my day" | Brief with TOP 3, PLAN fitted around meetings, NOT TODAY | DoDate and PlannedSlot set on planned rows; Status=scheduled |
| 7 | "Draft an email to finance about the budget" | Draft shown; it asks before sending | — |
| 8 | "Accept" | Acknowledged | New Feedback row: TargetType=brief, Signal=accept |

**Common failures:**
- *"Table not found"* → the Table input isn't AI-filled, or the name was typed as the sheet name (`List`) instead of the table name (`Items`).
- *Dates come back as numbers* → DateTime Format isn't set to ISO 8601 on the read tools.
- *"The file is locked"* → you have it open mid-edit, or the connector used it within the last ~6 minutes. Close it and retry.
- *Anything else looks off in the sheet* → download it and run `python3 m365/scripts/lint_workbook.py ChiefOfStaff.xlsx`.
- *Agent invents links* → tighten intake step 4 and log the failure in the iteration log. Don't patch the instructions ad hoc.

## Step 7 — Publish (5 min)

1. **Publish**, then **Channels › Microsoft 365 Copilot** and **Teams**. Availability: just you (R9).
2. In Teams, pin the agent. In M365 Copilot Chat, find it under **Agents**.
3. Re-run smoke tests 2 and 6 from Teams.

## Step 8 — Start the Phase 1 week

- Every morning: "plan my day". During the day: "add …" for anything new and "what now?" when you switch tasks.
- When something's done, just mark Status `done` and Open `No` yourself. The `reconcile` skill comes in Phase 2.
- Each evening, add one line to the iteration log in [05-roadmap.md](05-roadmap.md): brief accepted? how many edits? what was wrong?
- Before importing any changed skill, run its file in [`m365/evals/`](../evals/README.md).
- Exit test (end of week): briefs accepted with ≤2 edits on 4 of 5 days, and ≥90% of items have at least one link.
