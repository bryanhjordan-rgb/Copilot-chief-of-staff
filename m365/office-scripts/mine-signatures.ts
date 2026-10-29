/**
 * Office Script: mine completed Items for repeated work (skill candidates).
 *
 * Runs inside ChiefOfStaff.xlsx. Call it from the weekly-skill-review flow with
 * Excel Online (Business) > "Run script", passing asOf (yyyy-MM-dd) and
 * windowDays (default 30). Returns JSON the flow hands to the skill-miner skill,
 * so the agent only drafts and judges instead of counting rows.
 *
 * Reference implementation and tests: m365/scripts/mine.py (keep the two in sync;
 * the unittest suite checks they produce identical output).
 */

interface MinedItem {
  id: string;
  signature: string;
  completedOn: string;
  minutes: number | null;
  steps: string[][];
}

interface Candidate {
  signature: string;
  count: number;
  avgMinutes: number;
  cadence: string;
  commonSteps: string[];
  automationFit: number;
  score: number;
  estMinutesSaved: number;
  evidence: string[];
}

interface MiningResult {
  asOf: string;
  windowDays: number;
  itemsConsidered: number;
  candidates: Candidate[];
  coveredBySkills: string[];
}

const JUDGMENT_TOOLS = ["judgment", "call", "meeting", "in-person", "manual"];
const MAX_CANDIDATES = 3;
const EXAMPLE_ID = "I-EXAMPLE";

function main(workbook: ExcelScript.Workbook, asOf: string, windowDays: number = 30): string {
  const items = tableRows(workbook, "Items");
  const skills = tableRows(workbook, "Skills");
  return JSON.stringify(mine(items, skills, asOf, windowDays));
}

function tableRows(workbook: ExcelScript.Workbook, name: string): Record<string, string>[] {
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

function mine(
  items: Record<string, string>[],
  skills: Record<string, string>[],
  asOf: string,
  windowDays: number
): MiningResult {
  const end = dayNumber(asOf);
  const start = end - windowDays;
  const covered = activeSignatures(skills);

  const groups: Record<string, MinedItem[]> = {};
  let considered = 0;
  for (const row of items) {
    const signature = row["Signature"] || "";
    const completedOn = (row["CompletedOn"] || "").slice(0, 10);
    if (row["Status"] !== "done" || !signature || !completedOn || row["ID"] === EXAMPLE_ID) {
      continue;
    }
    const day = dayNumber(completedOn);
    if (isNaN(day) || day < start || day > end) {
      continue;
    }
    considered++;
    const minutes = parseFloat(row["MinutesSpent"]);
    const item: MinedItem = {
      id: row["ID"],
      signature: signature,
      completedOn: completedOn,
      minutes: isNaN(minutes) ? null : minutes,
      steps: parseSteps(row["Steps"] || ""),
    };
    if (!groups[signature]) {
      groups[signature] = [];
    }
    groups[signature].push(item);
  }

  const candidates: Candidate[] = [];
  const coveredFound: string[] = [];
  for (const signature of Object.keys(groups).sort()) {
    // Newest first; ties keep sheet order (sort is stable).
    const group = groups[signature].sort((a, b) =>
      a.completedOn < b.completedOn ? 1 : a.completedOn > b.completedOn ? -1 : 0
    );
    if (covered.indexOf(signature) >= 0) {
      coveredFound.push(signature);
      continue;
    }
    const timed = group.filter((g) => g.minutes !== null).map((g) => g.minutes as number);
    const avgMinutes = timed.length ? round1(timed.reduce((a, b) => a + b, 0) / timed.length) : 0;
    const cadence = detectCadence(group.map((g) => g.completedOn));
    const qualifies = group.length >= 3 || (group.length >= 2 && avgMinutes >= 20) || cadence !== "none";
    if (!qualifies) {
      continue;
    }
    const common = commonSteps(group);
    const toolSteps = common.filter((s) => JUDGMENT_TOOLS.indexOf(s[1]) < 0 && s[1] !== "");
    const fit = common.length ? round2(toolSteps.length / common.length) : 0;
    candidates.push({
      signature: signature,
      count: group.length,
      avgMinutes: avgMinutes,
      cadence: cadence,
      commonSteps: common.map((s) => `${s[0]} | ${s[1]}`),
      automationFit: fit,
      score: round1(group.length * avgMinutes * fit),
      estMinutesSaved: Math.round(avgMinutes * fit * 0.7),
      evidence: group.slice(0, 3).map((g) => g.id),
    });
  }
  candidates.sort((a, b) => b.score - a.score || (a.signature < b.signature ? -1 : 1));
  return {
    asOf: asOf,
    windowDays: windowDays,
    itemsConsidered: considered,
    candidates: candidates.slice(0, MAX_CANDIDATES),
    coveredBySkills: coveredFound,
  };
}

function activeSignatures(skills: Record<string, string>[]): string[] {
  const result: string[] = [];
  for (const row of skills) {
    if (row["Status"] !== "active") {
      continue;
    }
    for (const line of (row["Signatures"] || "").split("\n")) {
      if (line.trim()) {
        result.push(line.trim());
      }
    }
  }
  return result;
}

function parseSteps(text: string): string[][] {
  const steps: string[][] = [];
  for (const line of text.split("\n")) {
    const parts = line.split("|").map((p) => p.trim().toLowerCase());
    if (parts[0]) {
      steps.push([parts[0], parts.length > 1 ? parts[1] : ""]);
    }
  }
  return steps;
}

/** Steps (name + tool) present in at least two thirds of the group, in the most recent item's order. */
function commonSteps(group: MinedItem[]): string[][] {
  const needed = Math.ceil((group.length * 2) / 3);
  const counts: Record<string, number> = {};
  for (const item of group) {
    const seen: Record<string, boolean> = {};
    for (const step of item.steps) {
      const key = `${step[0]}|${step[1]}`;
      if (!seen[key]) {
        seen[key] = true;
        counts[key] = (counts[key] || 0) + 1;
      }
    }
  }
  const ordered: string[][] = [];
  const added: Record<string, boolean> = {};
  for (const item of group) {
    for (const step of item.steps) {
      const key = `${step[0]}|${step[1]}`;
      if (counts[key] >= needed && !added[key]) {
        added[key] = true;
        ordered.push(step);
      }
    }
  }
  return ordered;
}

/** "weekly" or "monthly" when every gap between completions fits that rhythm; else "none". */
function detectCadence(dates: string[]): string {
  if (dates.length < 2) {
    return "none";
  }
  const days = dates.map(dayNumber).sort((a, b) => a - b);
  const gaps: number[] = [];
  for (let i = 1; i < days.length; i++) {
    gaps.push(days[i] - days[i - 1]);
  }
  if (gaps.every((g) => g >= 6 && g <= 8)) {
    return "weekly";
  }
  if (gaps.every((g) => g >= 27 && g <= 32)) {
    return "monthly";
  }
  return "none";
}

function dayNumber(isoDate: string): number {
  const parts = isoDate.slice(0, 10).split("-").map((p) => parseInt(p, 10));
  if (parts.length !== 3 || parts.some((p) => isNaN(p))) {
    return NaN;
  }
  return Math.floor(Date.UTC(parts[0], parts[1] - 1, parts[2]) / 86400000);
}

function round1(n: number): number {
  return Math.round(n * 10) / 10;
}

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}
