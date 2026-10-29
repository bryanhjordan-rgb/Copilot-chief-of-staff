---
name: skill-miner
description: >-
  Weekly review that mines completion records, skill runs and feedback for
  repeated work and repeated corrections, then proposes new playbooks, patches
  to existing skills or instructions, and retirements, each with evidence and
  estimated time saved. Use for the scheduled weekly review, "what should be a
  skill?", "review my week", or when the same correction appears twice. Do not
  use to execute a playbook.
metadata:
  version: "0.1.0"
  tier: "native"
  signatures: "review|skills|self"
  tools: "dataverse, propose_skill"
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
1. **Week summary.** From `cos_record` and `cos_brief` in the last 7 days: items closed, minutes by goal, % closed by due date, brief acceptance rate.
2. **Group** `cos_record` (30d) by `signature`. For each group: count, avg minutes, cadence (weekday or monthly pattern), and common step sequence (steps appearing in ≥2/3 of the records, in order).
3. **Exclude** signatures already covered by an active `cos_skill` (check the `signatures` column). Instead, check those skills' `cos_skill_run` rows: success <50% over ≥4 runs → propose revision or retirement. Unused 60d (playbook) / 90d (native) → propose retirement.
4. **Score candidates**: `count × avg_minutes × automation_fit`, where automation_fit = share of common steps that are tool calls rather than **[judgment]** steps. Keep the top 3.
5. **Draft** a SKILL.md for each candidate using `m365/skills/_template/SKILL.md`:
   - name: kebab-case from the signature (e.g., `prepare-pricing-review`)
   - description: when to use it, its trigger phrases, and when not to
   - steps: the common step sequence, with judgment steps marked; outbound actions are draft-only
   - metadata.signatures: the group signature(s)
   - est minutes saved = avg_minutes × (automation_fit × 0.7), rounded
6. **Feedback themes.** Group `cos_feedback` (30d, applied=false) by `theme`. For any theme ≥2×, draft a ≤10-line patch to the relevant skill or instructions, quoting the user's words.
7. **Propose.** Call `propose_skill` for each new skill draft (status=proposed). Present everything in one message.
8. On "approve <name>": set the cos_skill status=active, tier=playbook, approved_on=now. On "reject <name>": status=rejected (and don't re-propose the same signature for 60 days). On "approve patch <n>": mark the related feedback applied=true and give the user the exact text change to make (playbooks: update `cos_skill.body`; native skills/instructions: a change for the repo).
9. **Graduation.** For playbooks with ≥5 runs and ≥80% success, offer: "Ready to make <name> a native skill? I'll output the SKILL.md for the repo."

## Output

```
WEEKLY REVIEW — <date range>
Closed <n> items (<x>% on time) · <h>h on goal work vs <h>h other · brief accepted <a>/<b> days
Top time sink: <signature> — <n>× · <m> min

PROPOSALS
1. NEW SKILL  prepare-pricing-review — 4× in 30d, avg 45 min → saves ~25 min/run (~100 min/mo)
   evidence: <record link>, <record link>, <record link>
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
- Week summary delivered; proposals written to `cos_skill` (status=proposed); user decisions applied
