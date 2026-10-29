"""Tests for m365/scripts. Run: python3 -m unittest discover -s m365/tests -v"""

import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


skills = load("skills")
build_workbook = load("build_workbook")
lint_workbook = load("lint_workbook")
mine = load("mine")
render_instructions = load("render_instructions")


class WorkbookTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.path = self.tmp / "ChiefOfStaff.xlsx"
        build_workbook.build(self.path)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def set_cells(self, sheet, row, values):
        """Write {header: value} into a data row of the table on `sheet`."""
        wb = load_workbook(self.path)
        ws = wb[sheet]
        headers = [c.value for c in ws[1]]
        for header, value in values.items():
            # .value assignment, not cell(value=...), so None clears the cell
            ws.cell(row=row, column=headers.index(header) + 1).value = value
        wb.save(self.path)

    def lint_errors(self):
        report, _, _ = lint_workbook.lint(self.path)
        return report.errors


class BuildWorkbookTests(WorkbookTestCase):
    def test_tables_and_keys_match_schema(self):
        wb = load_workbook(self.path)
        found = {name for ws in wb.worksheets for name in ws.tables}
        self.assertEqual(found, {"Items", "Goals", "Skills", "Feedback"})
        self.assertEqual(wb.sheetnames[0], "List")
        self.assertEqual(wb["List"]["A1"].value, "ID")

    def test_rebuild_is_byte_stable(self):
        second = self.tmp / "second.xlsx"
        build_workbook.build(second)
        self.assertEqual(self.path.read_bytes(), second.read_bytes())

    def test_dates_are_text_formatted(self):
        ws = load_workbook(self.path)["List"]
        headers = [c.value for c in ws[1]]
        due = ws.cell(row=2, column=headers.index("DueDate") + 1)
        self.assertEqual(due.number_format, "@")
        self.assertIsInstance(due.value, str)


class GoalsImportTests(WorkbookTestCase):
    GOALS = (
        "quarter: Q4 2026\nlast_updated: '2026-10-01'\n"
        "objectives:\n"
        "  - {name: Hire analysts, priority: 3, key_results: [Fill 2 roles], progress: 0.5, status: on_track}\n"
        "  - {name: Close renewals, priority: 1, target: $2M, key_results: [Contoso, Fabrikam], status: at_risk}\n"
        "personal:\n  - {name: Run 3x a week, progress: 0.2}\n"
    )

    def test_goals_are_ordered_and_personal_goals_prefixed(self):
        goals = self.tmp / "goals.yaml"
        goals.write_text(self.GOALS, encoding="utf-8")
        rows = build_workbook.goal_rows(goals)
        self.assertEqual([r["ID"] for r in rows], ["G1", "G2", "PG1"])
        self.assertEqual(rows[0]["Goal"], "Close renewals")
        self.assertEqual(rows[0]["KeyResults"], "Contoso\nFabrikam")
        self.assertEqual(rows[0]["Quarter"], "Q4 2026")

    def test_goals_land_in_table_and_lint_clean(self):
        goals = self.tmp / "goals.yaml"
        goals.write_text(self.GOALS, encoding="utf-8")
        build_workbook.build(self.path, goals)
        ws = load_workbook(self.path)["Goals"]
        self.assertEqual(ws.tables["Goals"].ref, "A1:I4")
        self.assertEqual(self.lint_errors(), [])


class FixturesTests(WorkbookTestCase):
    FIXTURES = Path(__file__).resolve().parent.parent / "evals" / "fixtures.yaml"

    def build_fixtures(self):
        from datetime import date
        build_workbook.build(self.path, fixtures_path=self.FIXTURES, today=date(2026, 11, 2))

    def test_relative_dates_resolve(self):
        self.build_fixtures()
        rows = {r["ID"]: r for r in mine.read_rows(self.path, "Items")}
        self.assertNotIn("I-EXAMPLE", rows)
        self.assertEqual(rows["I-SEED-005"]["DueDate"], "2026-11-02")      # TODAY
        self.assertEqual(rows["I-SEED-001"]["DueDate"], "2026-11-03")      # TODAY+1
        self.assertEqual(rows["I-SEED-006"]["CompletedOn"], "2026-10-26T09:00")  # datetime column
        goals = {r["ID"]: r for r in mine.read_rows(self.path, "Goals")}
        self.assertEqual(goals["G2"]["LastUpdate"], "2026-10-24")         # TODAY-9

    def test_fixture_workbook_lints_clean_and_mines_like_the_eval_expects(self):
        self.build_fixtures()
        self.assertEqual(self.lint_errors(), [])
        result = mine.mine(mine.read_rows(self.path, "Items"), mine.read_rows(self.path, "Skills"), "2026-11-02")
        [candidate] = result["candidates"]  # skill-miner-01-propose
        self.assertEqual(candidate["signature"], "send|weekly-status|leadership")
        self.assertEqual((candidate["count"], candidate["avgMinutes"]), (3, 35))
        self.assertEqual(candidate["evidence"], ["I-SEED-006", "I-SEED-007", "I-SEED-008"])

    def test_unknown_fixture_column_fails(self):
        bad = self.tmp / "bad.yaml"
        bad.write_text("items:\n  - {ID: I-X, Titel: typo}\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            build_workbook.build(self.path, fixtures_path=bad)


class LintWorkbookTests(WorkbookTestCase):
    def test_fresh_workbook_is_clean(self):
        self.assertEqual(self.lint_errors(), [])

    def test_open_must_match_status(self):
        self.set_cells("List", 2, {"Open": "Yes"})  # example row is Status=done
        self.assertTrue(any("Open=Yes but Status=done" in e for e in self.lint_errors()))

    def test_bad_link_line(self):
        self.set_cells("List", 2, {"ContextLinks": "see the email from Jane"})
        self.assertTrue(any("ContextLinks line" in e for e in self.lint_errors()))

    def test_non_iso_date(self):
        self.set_cells("List", 2, {"DueDate": "11/05/2026"})
        self.assertTrue(any("DueDate='11/05/2026'" in e for e in self.lint_errors()))

    def test_done_requires_signature(self):
        self.set_cells("List", 2, {"Signature": None})
        self.assertTrue(any("done but Signature is empty" in e for e in self.lint_errors()))

    def test_unknown_goal_on_real_item(self):
        self.set_cells("List", 2, {"ID": "I-20261029-081200", "Goal": "G9"})
        self.assertTrue(any("Goal='G9' not found" in e for e in self.lint_errors()))

    def test_confidential_hides_notes(self):
        self.set_cells("List", 2, {"Confidential": "Yes"})  # example has ResearchNotes
        errors = self.lint_errors()
        self.assertTrue(any("Confidential=Yes but ResearchNotes" in e for e in errors))

    def test_choice_value_outside_schema(self):
        self.set_cells("List", 2, {"Status": "finished"})
        self.assertTrue(any("Status='finished' not in" in e for e in self.lint_errors()))

    def test_skill_successes_cannot_exceed_runs(self):
        self.set_cells("Skills", 2, {"Name": "send-weekly-status", "Runs": 2, "Successes": 3})
        self.assertTrue(any("Successes (3) > Runs (2)" in e for e in self.lint_errors()))


class CardTests(unittest.TestCase):
    CARDS = Path(__file__).resolve().parent.parent / "flows" / "cards"
    ACTIONS = {
        "daily-brief": {"accept", "edit", "replan"},
        "weekly-review": {"decide", "approve_all", "reject_all"},
        "completion-confirm": {"complete", "not_yet"},
    }

    def strings(self, node):
        if isinstance(node, dict):
            for value in node.values():
                yield from self.strings(value)
        elif isinstance(node, list):
            for value in node:
                yield from self.strings(value)
        elif isinstance(node, str):
            yield node

    def test_cards(self):
        readme = (self.CARDS / "README.md").read_text(encoding="utf-8")
        for name, actions in self.ACTIONS.items():
            with self.subTest(card=name):
                card = json.loads((self.CARDS / f"{name}.card.json").read_text(encoding="utf-8"))
                self.assertEqual(card["type"], "AdaptiveCard")
                self.assertEqual(card["version"], "1.5")  # highest version Teams renders
                for s in self.strings(card):
                    if "{{" in s:
                        self.assertRegex(s, r"^\{\{[A-Z_]+\}\}$", "tokens must be whole string values")
                        self.assertIn(f"`{s[2:-2]}`", readme, "token must be documented")
                submitted = {a["data"]["action"] for a in card["actions"] if a["type"] == "Action.Submit"}
                self.assertEqual(submitted, actions)
                for action in actions:
                    self.assertIn(f"`{action}`", readme)


def done(item_id, signature, completed_on, minutes, steps, status="done"):
    return {"ID": item_id, "Status": status, "Signature": signature, "CompletedOn": completed_on,
            "MinutesSpent": minutes, "Steps": steps}


STATUS_STEPS = "collect updates | teams | 15\ndraft status | outlook | 15\nsend | outlook | 5"
MINING_ITEMS = [
    done("I-1", "send|weekly-status|leadership", "2026-10-22T16:00", "35", STATUS_STEPS),
    done("I-2", "send|weekly-status|leadership", "2026-10-15T16:00", "40", STATUS_STEPS),
    done("I-3", "send|weekly-status|leadership", "2026-10-08T16:00", "30",
         "collect updates | teams | 12\nreview with manager | meeting | 10\nsend | outlook | 5"),
    done("I-4", "prepare|pricing-review|customer", "2026-10-20T10:00", "30",
         "read thread | outlook | 10\ndecide discount | judgment | 10"),
    done("I-5", "prepare|pricing-review|customer", "2026-10-03T10:00", "34.5",
         "read thread | outlook | 12\ndecide discount | judgment | 12"),
    done("I-6", "review|contract|legal", "2026-10-21T09:00", "15", "read | word | 15"),
    done("I-7", "file|expenses|self", "2026-10-25T09:00", "10", "upload | concur | 10"),
    done("I-8", "file|expenses|self", "2026-10-18T09:00", "10", "upload | concur | 10"),
    done("I-9", "file|expenses|self", "2026-10-11T09:00", "10", "upload | concur | 10"),
    done("I-10", "send|weekly-status|leadership", "2026-08-01T16:00", "35", STATUS_STEPS),  # outside window
    done("I-11", "send|weekly-status|leadership", "2026-10-27T16:00", "35", STATUS_STEPS, status="in_progress"),
    done("I-EXAMPLE", "send|weekly-status|leadership", "2026-10-28T16:00", "35", STATUS_STEPS),  # template row
]
MINING_SKILLS = [
    {"Name": "file-expenses", "Status": "active", "Signatures": "file|expenses|self"},
    {"Name": "old-skill", "Status": "retired", "Signatures": "review|contract|legal"},
]


class MiningTests(unittest.TestCase):
    OFFICE_SCRIPTS = Path(__file__).resolve().parent.parent / "office-scripts"

    def test_reference_mining(self):
        result = mine.mine(MINING_ITEMS, MINING_SKILLS, "2026-10-29", 30)
        self.assertEqual(result["itemsConsidered"], 9)
        self.assertEqual(result["coveredBySkills"], ["file|expenses|self"])
        by_sig = {c["signature"]: c for c in result["candidates"]}
        self.assertEqual(set(by_sig), {"send|weekly-status|leadership", "prepare|pricing-review|customer"})

        status = by_sig["send|weekly-status|leadership"]
        self.assertEqual(status["count"], 3)
        self.assertEqual(status["avgMinutes"], 35)
        self.assertEqual(status["cadence"], "weekly")
        self.assertEqual(status["evidence"], ["I-1", "I-2", "I-3"])  # newest first
        # "draft status" is in 2 of 3 items (kept); "review with manager" in 1 of 3 (dropped)
        self.assertEqual(status["commonSteps"], ["collect updates | teams", "draft status | outlook", "send | outlook"])
        self.assertEqual(status["automationFit"], 1)

        pricing = by_sig["prepare|pricing-review|customer"]
        self.assertEqual(pricing["avgMinutes"], 32.3)  # half-up like Math.round, not banker's 32.2
        self.assertEqual(pricing["automationFit"], 0.5)  # judgment step doesn't count
        self.assertEqual(pricing["cadence"], "none")  # qualifies on count 2 + avg >= 20

    def test_office_script_matches_reference(self):
        if not shutil.which("tsc") or not shutil.which("node"):
            self.skipTest("tsc/node not installed")
        tmp = Path(tempfile.mkdtemp())
        try:
            subprocess.run(
                ["tsc", "--strict", "--target", "ES2019", "--lib", "ES2019", "--outDir", str(tmp),
                 str(self.OFFICE_SCRIPTS / "excelscript.d.ts"), str(self.OFFICE_SCRIPTS / "mine-signatures.ts")],
                check=True, capture_output=True, text=True,
            )
            for window in (30, 7, 90):
                with self.subTest(window=window):
                    payload = {"call": "mine", "args": [MINING_ITEMS, MINING_SKILLS, "2026-10-29", window]}
                    out = subprocess.run(
                        ["node", str(Path(__file__).parent / "run_office_script.js"), str(tmp / "mine-signatures.js")],
                        input=json.dumps(payload), check=True, capture_output=True, text=True,
                    ).stdout
                    self.assertEqual(json.loads(out), mine.mine(MINING_ITEMS, MINING_SKILLS, "2026-10-29", window))
        finally:
            shutil.rmtree(tmp)


class RenderInstructionsTests(unittest.TestCase):
    AGENT = Path(__file__).resolve().parent.parent / "agent"

    def template(self):
        return (self.AGENT / "instructions.md").read_text(encoding="utf-8")

    def example(self):
        import yaml
        return yaml.safe_load((self.AGENT / "profile.example.yaml").read_text(encoding="utf-8"))

    def test_example_profile_renders_completely(self):
        text = render_instructions.render(self.template(), self.example())
        self.assertNotIn("{{", text)
        self.assertLessEqual(len(text), render_instructions.MAX_CHARS)
        self.assertIn("- Fridays after 2 PM are no-meeting focus time\n", text)
        self.assertIn("Key people (always Tier 1 in triage, full stakeholder weight): Sam Lee (manager)", text)

    def test_no_constraints_drops_the_line(self):
        profile = self.example()
        profile["constraints"], profile["key_people"] = [], []
        text = render_instructions.render(self.template(), profile)
        self.assertIn("No meetings before 8:30 AM.\n\n## Guardrails", text)

    def test_missing_value_is_named(self):
        profile = self.example()
        del profile["home_by"]
        with self.assertRaisesRegex(render_instructions.ProfileError, "home_by"):
            render_instructions.render(self.template(), profile)

    def test_too_long_is_rejected(self):
        profile = self.example()
        profile["tone"] = "x" * 3000
        with self.assertRaisesRegex(render_instructions.ProfileError, "chars"):
            render_instructions.render(self.template(), profile)


class SkillsValidatorTests(unittest.TestCase):
    def test_repo_skills_validate(self):
        self.assertTrue(skills.validate())

    def test_bad_skill_is_reported(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            bad = tmp / "Bad_Skill"
            bad.mkdir()
            (bad / "SKILL.md").write_text(
                "---\nname: Bad_Skill\ndescription: x\nmetadata:\n  version: 1\n"
                "  signatures: \"capture-item\"\n  tools: \"excel\"\n---\n# x\n## Goal\n## Steps\n",
                encoding="utf-8",
            )
            errors = " ".join(skills.validate_skill(bad))
            self.assertIn("kebab-case", errors)
            self.assertIn("metadata.version must be a quoted string", errors)
            self.assertIn("verb|object|counterpart", errors)
            self.assertIn("missing section '## Guardrails'", errors)
        finally:
            shutil.rmtree(tmp)

    def test_missing_evals_are_reported(self):
        self.assertEqual(skills.validate_evals("no-such-skill"), ["no-such-skill: missing evals/no-such-skill.yaml"])


if __name__ == "__main__":
    unittest.main()
