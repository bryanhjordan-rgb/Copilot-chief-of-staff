---
name: skill-miner
description: >-
  Weekly review that mines completed items, skill runs and feedback for repeated
  work and repeated corrections, then proposes new playbooks, patches to
  existing skills or instructions, and retirements, each with evidence and
  estimated time saved. Use for the scheduled weekly review, "what should be a
  skill?", "review my week", or when the same correction appears twice. Do not
  use to execute a playbook.
metadata:
  version: "0.2.0"
  tier: "native"
  signatures: "review|skills|self"
  tools: "excel"
  status: "draft"
---

# Skill miner

## Goal
The user gets a short weekly review: what got done, where time went, and 0–3 concrete skill proposals they can approve with one word.

## Inputs
- Window: last 30 days for mining, last 7 days for the week summary
- Thresholds (from m365/docs/04-skill-lifecycle.md §3). Use these defaults unless the user changed them:
  - same signature ≥3× in 30d, OR ≥2× with avg ≥20 min, OR a fixed cadence for ≥2 cycles
  - same feedback theme ≥2× → patch proposal

## Steps
1. **Load.** `list_rows(Items, filter: Open eq 'No')` (keep rows with Status=done and CompletedOn in the window), `list_rows(Skills)`, and `list_rows(Feedback)` (Date in window).
2. **Week summary.** From items completed in the last 7 days: count, minutes by Goal, % completed on or before DueDate, and brief acceptance (Feedback rows with TargetType=brief: accept vs edit/reject).
3. **Group** 30-day completed items by Signature. For each group: count, avg MinutesSpent, cadence (weekday or monthly pattern in CompletedOn), and common step sequence (Steps lines appearing in ≥2/3 of the items, in order).
4. **Exclude** signatures already in an active Skills row's Signatures. For those skills, check the health of their runs instead: Successes/Runs <50% over ≥4 runs → propose revision or retirement. LastUsed >60d (playbook) / >90d (native) → propose retirement.
5. **Score candidates**: `count × avg_minutes × automation_fit`, where automation_fit = the share of common steps that are tool calls rather than **[judgment]** steps. Keep the top 3.
6. **Draft** a SKILL.md for each candidate using `m365/skills/_template/SKILL.md`:
   - name: kebab-case from the signature (e.g., `prepare-pricing-review`)
   - description: when to use it, its trigger phrases, and when not to
   - steps: the common step sequence, with judgment steps marked; outbound actions are draft-only
   - metadata.signatures: the group signature(s)
   - est minutes saved = avg_minutes × (automation_fit × 0.7), rounded
7. **Feedback themes.** Group Feedback rows with Applied=No by Theme. For any theme ≥2×, draft a ≤10-line patch to the relevant skill or instructions, quoting the user's words.
8. **Propose.** For each new skill draft, `add_row(Skills)` with Name, Version=0.1.0, Tier=playbook, Status=proposed, Description, Signatures, Body (the full SKILL.md), Evidence (item IDs), EstMinSaved, Runs=0, Successes=0. Present everything in one message.
9. **Apply decisions.**
   - "approve <name>" → `update_row(Skills, Name)` Status=active, ApprovedOn=now
   - "reject <name>" → Status=rejected (don't re-propose the same signature for 60 days)
   - "approve patch <n>" → set Applied=Yes and ResultingChange on the related Feedback rows, and give the user the exact text change (playbooks: update the Skills Body; native skills or instructions: a change for the repo)
10. **Graduation.** For playbooks with Runs ≥5 and Successes/Runs ≥80%, offer: "Ready to make <name> a native skill? I'll output the SKILL.md for the repo."

## Output

```
WEEKLY REVIEW — <date range>
Closed <n> items (<x>% on time) · <h>h on goal work vs <h>h other · brief accepted <a>/<b> days
Top time sink: <signature> — <n>× · <m> min

PROPOSALS
1. NEW SKILL  prepare-pricing-review — 4× in 30d, avg 45 min → saves ~25 min/run (~100 min/mo)
   evidence: I-20261003-…, I-20261010-…, I-20261024-…
   risks: pricing approval stays manual; drafts only
   [approve 1 / edit 1 / reject 1]
2. PATCH  prioritize — "stop ranking internal syncs above customer asks" (said 2×)
   change: stakeholder weight: internal recurring sync → 2 (was 10)
   [approve 2 / reject 2]
3. RETIRE  weekly-vendor-chase — unused 64 days

GRADUATE: send-weekly-status (7 runs, 86%) → native? [yes/no]
```

If nothing meets the thresholds, say: "No new skill candidates this week." Then show the week summary only.

## Guardrails
- Max 3 new skill proposals per week. Approval fatigue kills the loop.
- Never activate, patch, or retire anything without explicit approval.
- Generated skills must never include send/accept/delete steps without a confirmation gate.

## Done when
- Week summary delivered; proposals written to Skills (Status=proposed); user decisions applied
