/**
 * Office Script: weekly scorecard — the success metrics from docs/01-scope.md.
 *
 * Runs inside ChiefOfStaff.xlsx. The weekly-skill-review flow calls it with
 * Excel Online (Business) > "Run script" (asOf = yyyy-MM-dd, windowDays = 7) and
 * passes the JSON to the skill-miner skill for the week summary.
 *
 * Reference implementation and tests: m365/scripts/scorecard.py (keep in sync;
 * the unittest suite checks they produce identical output).
 */

interface Scorecard {
  asOf: string;
  windowDays: number;
  itemsCompleted: number;
  onTimePct: number | null;
  completionRecordPct: number | null;
  openItems: number;
  linkCoveragePct: number | null;
  minutesByGoal: Record<string, number>;
  briefDays: number;
  briefAcceptedDays: number;
  skillsActive: number;
  skillsProposed: number;
  skillRuns: number;
  skillRunSuccessPct: number | null;
  estMinutesSaved: number;
}

const SCORECARD_EXAMPLE_ID = "I-EXAMPLE";

function main(workbook: ExcelScript.Workbook, asOf: string, windowDays: number = 7): string {
  return JSON.stringify(
    scorecard(rowsOf(workbook, "Items"), rowsOf(workbook, "Skills"), rowsOf(workbook, "Feedback"), asOf, windowDays)
  );
}

function rowsOf(workbook: ExcelScript.Workbook, name: string): Record<string, string>[] {
  const table = workbook.getTable(name);
  if (!table) {
    throw new Error(`Table ${name} not found`);
  }
  const values = table.getRange().getValues();
  const headers = values[0].map((h) => String(h));
  const rows: Record<string, string>[] = [];
  for (let r = 1; r < values.length; r++) {
    const row: Record<string, string> = {};
    headers.forEach((h, c) => {
      row[h] = String(values[r][c]).trim();
    });
    rows.push(row);
  }
  return rows;
}

function scorecard(
  allItems: Record<string, string>[],
  skills: Record<string, string>[],
  feedback: Record<string, string>[],
  asOf: string,
  windowDays: number
): Scorecard {
  const end = toDay(asOf);
  const start = end - windowDays + 1; // window includes asOf
  const inWindow = (value: string): boolean => {
    const day = value ? toDay(value.slice(0, 10)) : NaN;
    return !isNaN(day) && day >= start && day <= end;
  };
  const get = (row: Record<string, string>, key: string): string => row[key] || "";

  const items = allItems.filter((r) => get(r, "ID") && get(r, "ID") !== SCORECARD_EXAMPLE_ID);
  const done = items.filter((r) => get(r, "Status") === "done" && inWindow(get(r, "CompletedOn")));
  const due = done.filter((r) => get(r, "DueDate"));
  const onTime = due.filter((r) => get(r, "CompletedOn").slice(0, 10) <= get(r, "DueDate").slice(0, 10));
  const recorded = done.filter((r) => get(r, "Outcome") && get(r, "Steps") && get(r, "Signature"));
  const openItems = items.filter((r) => get(r, "Open") === "Yes");
  const linked = openItems.filter((r) => get(r, "SourceLink") || get(r, "ContextLinks"));

  const minutes: Record<string, number> = {};
  for (const r of done) {
    const m = leadingNumber(get(r, "MinutesSpent"));
    if (m !== null) {
      const goal = get(r, "Goal") || "none";
      minutes[goal] = (minutes[goal] || 0) + m;
    }
  }
  const minutesByGoal: Record<string, number> = {};
  for (const goal of Object.keys(minutes).sort()) {
    minutesByGoal[goal] = minutes[goal];
  }

  const windowFeedback = feedback.filter((f) => inWindow(get(f, "Date")));
  const briefs = windowFeedback.filter((f) => get(f, "TargetType") === "brief");
  const briefDays = unique(briefs.map((f) => get(f, "TargetRef")));
  const acceptedDays = unique(briefs.filter((f) => get(f, "Signal") === "accept").map((f) => get(f, "TargetRef")));

  const savedPerRun: Record<string, number> = {};
  for (const s of skills) {
    savedPerRun[get(s, "Name")] = leadingNumber(get(s, "EstMinSaved")) || 0;
  }
  const runs = windowFeedback.filter((f) => get(f, "TargetType") === "skill_run");
  const successes = runs.filter((f) => get(f, "Signal") === "success");

  return {
    asOf: asOf,
    windowDays: windowDays,
    itemsCompleted: done.length,
    onTimePct: percent(onTime.length, due.length),
    completionRecordPct: percent(recorded.length, done.length),
    openItems: openItems.length,
    linkCoveragePct: percent(linked.length, openItems.length),
    minutesByGoal: minutesByGoal,
    briefDays: briefDays.length,
    briefAcceptedDays: acceptedDays.length,
    skillsActive: skills.filter((s) => get(s, "Status") === "active").length,
    skillsProposed: skills.filter((s) => get(s, "Status") === "proposed").length,
    skillRuns: runs.length,
    skillRunSuccessPct: percent(successes.length, runs.length),
    estMinutesSaved: successes.reduce((sum, f) => sum + (savedPerRun[get(f, "TargetRef")] || 0), 0),
  };
}

function percent(part: number, whole: number): number | null {
  return whole ? Math.floor((100 * part) / whole + 0.5) : null;
}

function unique(values: string[]): string[] {
  return values.filter((v, i) => values.indexOf(v) === i);
}

function leadingNumber(text: string): number | null {
  const match = /^\s*(-?\d+(\.\d+)?)/.exec(text);
  return match ? parseFloat(match[1]) : null;
}

function toDay(isoDate: string): number {
  const parts = isoDate.slice(0, 10).split("-").map((p) => parseInt(p, 10));
  if (parts.length !== 3 || parts.some((p) => isNaN(p))) {
    return NaN;
  }
  return Math.floor(Date.UTC(parts[0], parts[1] - 1, parts[2]) / 86400000);
}
