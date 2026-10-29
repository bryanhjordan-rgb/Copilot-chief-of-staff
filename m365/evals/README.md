# Skill evals

Scenario tests for each skill. Run them before importing a changed skill, and when you're comparing models (Q4). CI makes sure every skill has at least 3 cases (`python3 m365/scripts/skills.py validate`).

## Files

- `fixtures.yaml`: seed goals, items, today's calendar, and constraints. `TODAY±n` means relative days.
- `<skill>.yaml`: cases for one skill. Each case has:
  - `say`: what you type (or what the flow sends)
  - `given`: optional state beyond the fixtures
  - `expect`: what the reply must contain
  - `workbook`: what the sheet must look like afterwards
  - `must_not`: hard failures

## Running a pass (about 30 min)

1. Make a test copy of the workbook (`ChiefOfStaff-test.xlsx`). Point the agent's Excel tools at it, or use a second test agent.
2. Load `fixtures.yaml`: Goals rows and Items rows, with `TODAY` replaced by real dates. Put the calendar entries on a test calendar day, or run the brief cases on a day that resembles them.
3. Run each case in the Copilot Studio test pane, in file order. Cases inside a file build on each other.
4. Score each case:
   - **Pass:** every `expect` and `workbook` line holds, and no `must_not` line happens
   - **Partial:** one `expect` line misses, but no `must_not` happens
   - **Fail:** any `must_not` happens, or two or more `expect` lines miss
5. Download the test workbook and run `python3 m365/scripts/lint_workbook.py ChiefOfStaff-test.xlsx`. Any ERROR fails the case that wrote that row.
6. Record the run in `results/YYYY-MM-DD-<model>.md` (template below).

**Bar to import a changed skill:** no Fail, and at most 1 Partial in that skill's file.

## Bulk import

`python3 m365/scripts/skills.py export-evals` writes `dist/evals.csv` with one row per case: skill, id, given, say, expected, must_not. If your tenant has Copilot Studio's agent evaluation / test-set feature, map `say` → question and `expected` → expected response. Otherwise use the CSV as a printable checklist.

## Results template

```markdown
# Eval run — 2026-11-02 — claude-sonnet-5
Skills: prioritize 0.2.0, intake 0.2.0, daily-brief 0.2.0

| Case | Result | Note |
|------|--------|------|
| prioritize-01-what-now | pass | |
| intake-04-no-context | fail | invented a Teams link |

Summary: 18 pass / 1 partial / 1 fail → fix intake step 4, re-run intake
```

Failures that repeat across runs feed the same loop as live feedback: propose a ≤10-line skill patch, then re-run the file.
