#!/usr/bin/env python3
"""Weekly scorecard: the success metrics from docs/01-scope.md, computed from the workbook.

Usage:
  python3 m365/scripts/scorecard.py path/to/ChiefOfStaff.xlsx --as-of 2026-10-30 [--window 7]

Reference implementation of m365/office-scripts/weekly-scorecard.ts (the weekly flow
runs that inside Excel). The unittest suite checks both produce identical JSON.
Percentages are whole numbers rounded half-up, like JavaScript's Math.round.
"""

import argparse
import json
from pathlib import Path

from mine import EXAMPLE_ID, day_number, js_round, parse_float, read_rows


def pct(part, whole):
    return js_round(100 * part / whole) if whole else None


def scorecard(items, skills, feedback, as_of, window_days=7):
    end = day_number(as_of)
    start = end - window_days + 1  # window includes as_of: 7 days = as_of and the 6 days before

    def in_window(value):
        day = day_number(value[:10]) if value else None
        return day is not None and start <= day <= end

    items = [r for r in items if r.get("ID") and r.get("ID") != EXAMPLE_ID]
    done = [r for r in items if r.get("Status") == "done" and in_window(r.get("CompletedOn", ""))]
    due = [r for r in done if r.get("DueDate")]
    on_time = [r for r in due if r["CompletedOn"][:10] <= r["DueDate"][:10]]
    recorded = [r for r in done if r.get("Outcome") and r.get("Steps") and r.get("Signature")]
    open_items = [r for r in items if r.get("Open") == "Yes"]
    linked = [r for r in open_items if r.get("SourceLink") or r.get("ContextLinks")]

    minutes_by_goal = {}
    for r in done:
        minutes = parse_float(r.get("MinutesSpent", ""))
        if minutes is not None:
            goal = r.get("Goal") or "none"
            minutes_by_goal[goal] = minutes_by_goal.get(goal, 0) + minutes

    window_feedback = [f for f in feedback if in_window(f.get("Date", ""))]
    briefs = [f for f in window_feedback if f.get("TargetType") == "brief"]
    brief_days = sorted({f.get("TargetRef", "") for f in briefs})
    accepted_days = sorted({f.get("TargetRef", "") for f in briefs if f.get("Signal") == "accept"})

    saved_per_run = {s.get("Name"): parse_float(s.get("EstMinSaved", "")) or 0 for s in skills}
    runs = [f for f in window_feedback if f.get("TargetType") == "skill_run"]
    successes = [f for f in runs if f.get("Signal") == "success"]

    return {
        "asOf": as_of,
        "windowDays": window_days,
        "itemsCompleted": len(done),
        "onTimePct": pct(len(on_time), len(due)),
        "completionRecordPct": pct(len(recorded), len(done)),
        "openItems": len(open_items),
        "linkCoveragePct": pct(len(linked), len(open_items)),
        "minutesByGoal": {goal: minutes_by_goal[goal] for goal in sorted(minutes_by_goal)},
        "briefDays": len(brief_days),
        "briefAcceptedDays": len(accepted_days),
        "skillsActive": sum(1 for s in skills if s.get("Status") == "active"),
        "skillsProposed": sum(1 for s in skills if s.get("Status") == "proposed"),
        "skillRuns": len(runs),
        "skillRunSuccessPct": pct(len(successes), len(runs)),
        "estMinutesSaved": sum(saved_per_run.get(f.get("TargetRef"), 0) for f in successes),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--as-of", required=True, help="YYYY-MM-DD")
    parser.add_argument("--window", type=int, default=7)
    args = parser.parse_args()
    tables = {name: read_rows(args.workbook, name) for name in ("Items", "Skills", "Feedback")}
    print(json.dumps(scorecard(tables["Items"], tables["Skills"], tables["Feedback"], args.as_of, args.window), indent=2))


if __name__ == "__main__":
    main()
