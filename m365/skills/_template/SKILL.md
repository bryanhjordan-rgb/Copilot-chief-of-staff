---
name: skill-name
description: >-
  One or two sentences: what this skill does AND when to use it. Include trigger
  phrases. Add "Do not use for …" to prevent mis-routing. Max 1024 characters.
metadata:
  version: "0.1.0"
  tier: "native"
  signatures: "verb|object|counterpart"
  tools: "excel, work-iq"
  status: "draft"
---

# Skill name

## Goal
One sentence: the outcome when this skill finishes successfully.

## Inputs
- What the skill needs (item id, date, user text). Say what to do if one is missing: ask once or assume and flag.

## Steps
1. Concrete, ordered steps. Name the tool for each tool call.
2. Mark judgment steps as **[judgment]** so the miner can score automation fit.
3. Keep side effects explicit. Anything outbound is **draft only**.

## Output
The exact shape the user sees (template block) and which workbook cells get written.

## Guardrails
- What this skill must never do.

## Done when
- Checklist of observable completion criteria. If this ran as a playbook, update the Skills row (Runs, Successes, LastUsed) and add a Feedback row (TargetType skill_run).
