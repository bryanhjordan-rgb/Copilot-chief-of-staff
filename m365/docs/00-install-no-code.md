# 00 — Install Without Running Code

**For:** a standard Microsoft 365 + Copilot tenant where you may build agents in Copilot Studio but can't run scripts.
**You need:** a browser, Excel for the web, Copilot Studio, and this repo on github.com. Nothing gets installed on your machine.
**Time:** about 75 minutes for the core agent.

The workbook is built once. After you upload it, the agent reads and updates that same file through the Excel Online (Business) connector. You never regenerate or replace it.

Every file below is already built and committed. On GitHub, open the file and click **Download raw file** (the download icon, top right of the file view).

| File in this repo | What it is | Used in |
|-------------------|-----------|---------|
| `m365/workbook/ChiefOfStaff.xlsx` | Empty workbook: List, Goals, Skills, Feedback, People, Guide | Step 1 |
| `m365/agent/instructions.md` | Agent instructions with 8 blanks to fill | Step 3 |
| `m365/kit/skills/*.zip` | One zip per skill, ready to upload | Step 6 |

Copilot Studio labels move around. If a menu below doesn't match, use the closest equivalent.

---

## Step 0 — Five checks before you start (5 min)

Check these in your own tenant. If any answer is "no", ask IT for that row of [07-tenant-readiness.md](07-tenant-readiness.md).

1. **Copilot Studio:** you can open copilotstudio.microsoft.com and click **Create** (R2).
2. **Excel connector:** in a test agent, **Tools › Add a tool**, search "Excel Online (Business)". It's listed (R3).
3. **Skills tab:** the agent has a **Skills** tab (R5). If not, see the fallback in Step 6.
4. **Work IQ:** **Knowledge** or **Tools** lists Work IQ (R6). If not, use the connector fallback in Step 5.
5. **Publish to Teams / M365 Copilot** for yourself (R9).

## Step 1 — Put the workbook in OneDrive (5 min)

1. Download `m365/workbook/ChiefOfStaff.xlsx` from GitHub.
2. In OneDrive for Business, create the folders **Apps › ChiefOfStaff** and upload the file there. Keep the name `ChiefOfStaff.xlsx`.
3. Open it in **Excel for the web**. You should see 6 sheets: List, Goals, Skills, Feedback, People, Guide.
4. Click any cell in the List sheet's table. **Table Design** should show the name `Items`. The other tables are named `Goals`, `Skills`, `Feedback`, `People`. Don't rename them, and don't rename or reorder headers.

## Step 2 — Fill your goals and people (10 min)

Type straight into Excel for the web. Delete the blank starter row in each table if you don't use it.

**Goals** (the agent ranks everything against these):

| Column | Enter | Example |
|--------|-------|---------|
| ID | `G1`, `G2`, … for work; `PG1`, … for personal | `G1` |
| Goal | One line | `Close FY27 budget` |
| Priority | 1 = highest | `1` |
| Target | What done looks like | `Approved by CFO by Nov 30` |
| KeyResults | One per line (Alt+Enter for a new line in a cell) | `Draft to finance by Nov 8` |
| Progress | 0.0–1.0 | `0.2` |
| Status | `on_track`, `at_risk`, `behind`, or `complete` | `on_track` |
| Quarter | Any label | `Q4 2026` |
| LastUpdate | `YYYY-MM-DD` | `2026-10-29` |

Three to five goals is enough.

**People** (optional; only the relationship-check skill uses it): Email (lowercase), Name, Tier (`1` = check in every 14 days, `2` = 30, `3` = 60), Role. Leave the other columns blank; the agent fills them in.

Leave **List**, **Skills**, and **Feedback** as they are. The agent writes to them. The `I-EXAMPLE` row on List shows the cell formats; Open=No keeps the agent from treating it as work.

**Close the Excel tab when you're done.** The connector can't write while an edit session is saving.

## Step 3 — Prepare the instructions (10 min)

1. On GitHub, open `m365/agent/instructions.md`, click **Raw**, select all, and paste into Notepad (or any plain-text editor).
2. Replace each blank, including the curly braces. Notepad's **Edit › Replace** handles the repeats.

| Replace | With | Example |
|---------|------|---------|
| `{{YOUR_NAME}}` | Full name | `Jordan Example` |
| `{{YOUR_FIRST_NAME}}` | First name (sign-off) | `Jordan` |
| `{{YOUR_ROLE}}` | Title | `Director of Operations` |
| `{{YOUR_COMPANY}}` | Company | `Contoso` |
| `{{DINNER_TIME}}` | Hard stop | `5:30 PM` |
| `{{EARLIEST_MEETING_TIME}}` | Earliest meeting | `8:30 AM` |
| `{{YOUR_TONE_DESCRIPTION}}` | 1–3 sentences on how you write | `Direct but warm. Short sentences, no filler.` |
| `{{ADD_YOUR_CONSTRAINTS}}` | Other hard constraints, one per `- ` line, or delete the line | `Fridays after 2 PM are focus time` |

3. Optional: under **Hard constraints**, add one line naming the people whose asks always count as top priority:
   `- Key people (always Tier 1 in triage, full stakeholder weight): Sam Lee (manager); Priya Patel (CFO)`
4. Search the text for `{{`. Nothing should be left. Keep the total under 8,000 characters; the template is about 5,700, so short answers are fine.

## Step 4 — Create the agent and add the Excel tools (25 min)

1. copilotstudio.microsoft.com › pick your work environment (top right) › **Create › New agent** › skip the chat setup and use **Configure**.
2. **Name:** `Chief of Staff`. **Description:** `Prioritizes your day, investigates new items, reconciles completed work, and proposes skills from repeated work.`
3. **Orchestration:** the GitHub Copilot harness if offered, otherwise generative orchestration. **Model:** Claude Sonnet 5 if allowed, otherwise the default.
4. **Instructions:** paste your text from Step 3. Save.
5. Add four tools: **Tools › Add a tool › Connector › Excel Online (Business)** › pick the action › sign in with your work account. On all four, set:

| Input | Value | How |
|-------|-------|-----|
| Location | `OneDrive for Business` | Fixed value |
| Document Library | `OneDrive` | Fixed value |
| File | `/Apps/ChiefOfStaff/ChiefOfStaff.xlsx` | Fixed value, chosen with the file picker |
| Table | — | **Filled by AI**, so one tool covers all five tables |

| Rename the tool to | Action | Also set | Paste as the tool description |
|--------------------|--------|----------|-------------------------------|
| `list_rows` | List rows present in a table | DateTime Format = ISO 8601; turn on Pagination; Filter Query, Order By, Select Query, Top Count = filled by AI | Read rows from the Items, Goals, Skills, Feedback, or People table. Use Filter Query `Open eq 'Yes'` for open items. Only one filter function per column. |
| `get_row` | Get a row | Key Column + Key Value = filled by AI; DateTime Format = ISO 8601 | Read one row by key. Keys: Items→ID, Goals→ID, Skills→Name, Feedback→ID, People→Email. |
| `add_row` | Add a row into a table | Row = filled by AI | Add one row. Always supply the key (ID, Name, or Email). Dates are ISO text. |
| `update_row` | Update a row | Key Column, Key Value, row fields = filled by AI | Update cells in one row by key. Blank fields stay unchanged. To append to History, get_row first. |

No confirmation on these four. They only touch your workbook.

If your tenant won't let Table be filled by AI, make one set per table instead (`list_items`, `add_item`, …), starting with Items and Goals.

## Step 5 — Give it your mail, calendar, Teams, and files (10 min)

Pick one:

- **Work IQ (preferred):** **Knowledge** (or **Tools**) › **Work IQ** › enable mail, calendar, files, Teams, and people.
- **Connectors (fallback):** from **Office 365 Outlook** add *Search email (V2)*, *Get emails (V3)*, *Get calendar view of events (V3)*; from **Microsoft Teams** add *Search messages*. Fix the mailbox and calendar to yours; let AI fill the rest.

If you add *Send an email (V2)* or *Post message*, set **Ask the user before running = Yes**. The instructions already forbid sending without your "Send", and this makes the platform enforce it too. *Draft an email* needs no confirmation.

## Step 6 — Upload skills (5 min)

1. From `m365/kit/skills/` on GitHub, download `prioritize.zip`, `intake.zip`, and `daily-brief.zip`.
2. Agent › **Skills › Upload** each zip. Don't unzip them first. Check that each shows a name and description.
3. Add the rest when you want them; no code is needed for any of them:

| Skill | Add when | Needs |
|-------|----------|-------|
| `triage` | You want "triage" / "clear my inbox" | Step 5 mail + Teams access |
| `meeting-prep`, `meeting-debrief` | You want "prep me for the 2pm" / "debrief …" | Calendar access; Teams recaps or pasted notes for debrief |
| `reconcile` | You want "done with …" to write a completion record | — |
| `relationship-check` | You filled the People sheet | — |
| `skill-miner` | After a few weeks of completed items | — |

**No Skills tab?** Unzip on your PC (right-click › Extract All; that isn't running code), open `SKILL.md` in Notepad, and create one **Topic** per skill: the trigger is the `description:` line, the body is everything below the second `---`.

## Step 7 — Test, then publish (15 min)

1. In the test pane, run the 8-row smoke test in [08-build-guide.md, Step 6](08-build-guide.md#step-6--smoke-test-in-the-test-pane-15-min). After each row, open the workbook and check the result.
2. **Publish › Channels › Microsoft 365 Copilot** and **Teams**, available to you only.
3. Pin it in Teams. In M365 Copilot Chat it's under **Agents**. Re-run "Add: …" and "Plan my day" there.

Common failures:
- *"Table not found":* Table isn't filled by AI, or the sheet name (`List`) was used instead of the table name (`Items`).
- *Dates come back as numbers:* DateTime Format isn't ISO 8601 on `list_rows` / `get_row`.
- *"The file is locked":* the workbook is open mid-edit, or the connector used it in the last ~6 minutes. Close it and retry.
- *It invents links:* note it in the iteration log ([05-roadmap.md](05-roadmap.md)); don't patch the instructions ad hoc.

---

## Living with one workbook

- **Never replace the file.** Uploading a fresh copy over it wipes your list. Edit the live one in Excel for the web.
- **Hand edits are fine** in Excel for the web: Status, dates, notes, deleting a row. If you set Status to `done` or `dropped`, set Open to `No` too.
- **Use Excel for the web, not desktop Excel**, if a scheduled flow might be running. Desktop sessions and the connector conflict.
- **If a later version of this repo adds a column**, add it at the right-hand edge of that table in Excel for the web, with the header spelled exactly as in `m365/schema/workbook.yaml`. Don't insert columns in the middle or rename existing ones.
- **Health check without code:** filter List by Open = Yes and confirm each row has a Status other than `done`/`dropped` and something in SourceLink or ContextLinks. Your Phase 1 target: 90% or more have a link.

## What you skip, and what replaces it

| The other guides say | Without code |
|----------------------|--------------|
| `build_workbook.py`, `--goals` | Download the committed workbook; type goals in Step 2 |
| `render_instructions.py` | Notepad find-and-replace, Step 3 |
| `skills.py package` | Download the prebuilt zips from `m365/kit/skills/` |
| `lint_workbook.py` | The health check above |
| `skills.py` evals | Type each case from `m365/evals/<skill>.yaml` into the test pane and compare against `expect` |
| Office Scripts (Phase 3 weekly review) | Optional. They run inside Excel (Automate tab), which some admins disable. Without them, say "review my week" and the skill-miner skill works from the rows directly |
| New skills from skill-miner | Approve them as **playbooks**: rows in the Skills table that go live at once, no upload. To promote one to a native skill, the agent gives you its SKILL.md text: save it in Notepad as `SKILL.md`, right-click › **Send to › Compressed (zipped) folder**, rename the zip to the skill name, and upload it in Step 6 |

## Later: scheduled runs (Phase 2, optional, still no code)

The 07:00 brief and the completion detector are Copilot Studio / Power Automate flows built in the designer. They need triggers and Copilot Credits allowed (R8). Specs: [flows/daily-brief.md](../flows/daily-brief.md) and [flows/completion-detector.md](../flows/completion-detector.md); card JSON to paste is in [flows/cards/](../flows/cards/). Until then, say "plan my day" each morning.

Daily phrases: [09-daily-use.md](09-daily-use.md).
