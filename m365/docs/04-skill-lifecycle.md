# 04 — Skill Lifecycle (self-improving loop)

**Status:** Draft v0.1 (2026-10-29)

The agent gets better in two ways: it **generates new skills** from repeated work, and it **refines existing behavior** from feedback. Both feed into a single pipeline with a human approval gate.

---

## 1. Lifecycle

```mermaid
stateDiagram-v2
  [*] --> Observed: completion records + feedback
  Observed --> Candidate: skill-miner finds pattern
  Candidate --> Proposed: draft SKILL.md + evidence
  Proposed --> Rejected: user declines
  Proposed --> Playbook: user approves (live immediately)
  Playbook --> Native: ≥5 runs, ≥80% success, user OK
  Playbook --> Retired: unused 60d or success <50%
  Native --> Retired: unused 90d or superseded
  Native --> Native: feedback → version bump
  Rejected --> [*]
  Retired --> [*]
```

| Stage | Where it lives | Who acts | Exit criteria |
|-------|----------------|----------|---------------|
| Observed | Items completion columns (Steps, Signature, MinutesSpent), Feedback table | Reconcile skill, feedback logging | — |
| Candidate | Skill-miner working set | Weekly skill review workflow | Pattern meets the thresholds below |
| Proposed | Skills table (Status=proposed) | Agent drafts; user reviews in chat or card | User approves or rejects |
| Playbook | Skills table (Tier=playbook, Status=active) | Agent reads the Body at runtime | Graduation thresholds |
| Native | `m365/skills/<name>/SKILL.md` → imported into Copilot Studio | User merges PR and imports zip | Version bumps on feedback |
| Retired | Skills table (Status=retired) | Weekly review | — |

## 2. Signals the agent records

1. **Completion records** (Items completion columns): a normalized `Signature` (verb + object type + counterpart type, e.g. `prepare|pricing-review|customer`) and an ordered `Steps` list (tools used, artifacts touched, minutes).
2. **Skill runs**: Runs/Successes/LastUsed counters on the Skills row, plus a Feedback row per run (Signal success/partial/fail).
3. **Feedback** (Feedback table): accept/edit/reject on briefs, items, and drafts. Explicit corrections ("always CC my manager on pricing") are stored verbatim.
4. **Recurrence hints**: the same item title pattern on the same weekday or monthly cadence.

## 3. Mining thresholds (initial — tune after Phase 3)

A pattern becomes a **candidate** when any of these hold over a rolling 30 days:

| Rule | Threshold |
|------|-----------|
| Same signature completed | ≥3 times |
| Same signature, avg handling time | ≥20 min and ≥2 occurrences |
| Fixed cadence detected (weekly/monthly) | ≥2 cycles |
| Same correction repeated | ≥2 times → **instruction/skill patch** proposal, not a new skill |

Counting and grouping run deterministically in the [`mine-signatures` Office Script](../office-scripts/README.md), with a tested Python twin in `scripts/mine.py`. The agent only drafts and judges.

Candidates are ranked by `frequency × avg_minutes × automation_fit` (automation_fit 0–1: how many steps are tool calls vs. judgment calls).

## 4. Proposal format

Every proposal shown to the user contains:

```
SKILL PROPOSAL: <name>                                   [approve / edit / reject]
Pattern:   <signature> — seen <n>x in 30d, avg <m> min
Evidence:  <IDs of the 3 most recent completed Items rows>
Saves:     ~<x> min/run, ~<y> min/month
Draft:     <SKILL.md, collapsed>
Risks:     <judgment steps that stay manual; data touched; anything it sends (drafts only)>
```

The draft follows [skills/_template/SKILL.md](../skills/_template/SKILL.md) and must pass `scripts/skills.py validate`.

## 5. Two tiers, and why

Copilot Studio skills are imported through the UI, and no create/update API is documented (as of 2026-10). Waiting for a manual import would stall the feedback loop, so:

- **Tier A — Playbook (runtime).** On approval, the SKILL.md text is stored in the Skills row's Body. The agent's instructions say: *before starting a task, check Skills for an active row whose Signatures include the task's signature; if one exists, follow its Body.* It goes live immediately with no republish.
- **Tier B — Native skill.** Once a playbook proves itself (≥5 runs, ≥80% success, the user agrees), the agent exports it. The user (or Claude Code in this repo) commits it to `m365/skills/<name>/` via PR, CI validates it, `scripts/skills.py package` builds the zip, and the user imports it. Native skills get on-demand loading and travel with the agent through solutions/ALM.

If Copilot Studio later exposes a skills API, Tier B import becomes a workflow step and Tier A remains as the staging area.

## 6. Feedback → behavior changes

| Feedback type | Action |
|---------------|--------|
| One-off edit to a draft/brief | Log only |
| Same correction ≥2× | Propose a patch (≤10 lines) to the relevant skill or the instructions; user approves (mirrors CLAUDE.md Part 9) |
| Skill run rated fail/partial | Feedback row (TargetType skill_run); 3 fails in 10 runs → propose revision or retirement |
| Brief rejected | Ask one question: "What was wrong — ranking, missing item, or timing?" Log the answer |

## 7. Guardrails on generated skills

- Generated skills may **draft** but never **send**, accept meetings, or delete data.
- A skill touching confidential keywords (CLAUDE.md §1.5) is flagged in its proposal and stores references only.
- No skill is activated without explicit user approval. No silent self-modification.
- Each skill declares the tools it expects. The agent refuses to run it if a tool is unavailable, rather than improvising.
