# 01 — Scope: M365 Chief of Staff Agent

**Status:** Draft v0.1 (2026-10-29)
**Owner:** {{YOUR_NAME}}
**Platform:** Microsoft 365 Copilot + Copilot Studio (work tenant)

---

## 1. Problem

Work context is spread across Outlook, Teams, meetings, SharePoint/OneDrive, Planner, and To Do. No single place answers *"what should I do today, in what order, and why?"*. Completed work leaves no durable record of how it got done, so repeat work gets rebuilt from scratch every time.

## 2. Vision

An agent in Microsoft 365 Copilot (and Teams) that acts as a chief of staff:

1. **Builds a prioritized daily activity list** — every item has a rationale, a next action, and links to the emails, chats, meetings, files, and people it depends on.
2. **Takes intake by conversation** — "add X" → the agent investigates, links context, scores it, and slots it into the plan.
3. **Reconciles completed work** — when an item closes, the agent captures outcome, artifacts, decisions, and time spent into a permanent record.
4. **Learns and generates skills** — mines completed work and feedback for repeat patterns, proposes new skills with evidence, and graduates proven ones into native Copilot Studio skills.

The Claude Code kit at the repo root is the design reference. Its principles (goal-aligned prioritization, never send without approval, push back on low-leverage work, close loops) carry over unchanged.

## 3. Jobs to be done

| # | Job | Trigger | Output |
|---|-----|---------|--------|
| J1 | Plan my day | 07:00 schedule, or "plan my day" | Daily brief: Top 3 outcomes, timeboxed plan against the calendar, linked items, drop/delegate list |
| J2 | Capture and investigate | "Add …", forward an email, @mention in Teams | New item with linked context, research notes, score, suggested due/do date |
| J3 | Re-prioritize | New item lands, calendar changes, "what now?" | Updated ranking with explicit tradeoffs ("doing X means Y slips") |
| J4 | Reconcile completion | Item marked done, or completion evidence detected (reply sent, meeting held, doc updated) | Completion record linked to artifacts; goal progress, contact notes, and follow-ups updated |
| J5 | Identify skill opportunities | Weekly review, or the same pattern recurring | Skill proposal: evidence, draft SKILL.md, estimated time saved |
| J6 | Improve from feedback | User corrects or rejects output | Feedback logged; instruction or skill change proposed |

## 4. In scope (v1)

- Conversational agent in M365 Copilot Chat and Teams
- System of record: one Excel workbook in OneDrive (`ChiefOfStaff.xlsx`) holding the list with context, goals, skills, and feedback (ADR-006)
- Daily brief, generated on schedule and on demand
- Intake → investigate → prioritize loop
- Completion reconciliation, triggered manually first and by detection later
- Skill lifecycle: observe → mine → propose → approve → run → measure → graduate or retire
- Goals and constraints, ported from `goals.yaml` and CLAUDE.md Part 2

## 5. Out of scope (v1). Revisit after Phase 3.

- Sending messages on its own. Drafts only; every send needs explicit "Send/Y" (inherited guardrail).
- Accepting or declining meetings on the user's behalf
- Personal channels (Gmail, WhatsApp, iMessage). The root Claude Code kit covers those.
- Multi-user or team deployment. Single user first.
- Inbox triage across all channels (Phase 4 port of `/triage`)
- Relationship CRM enrichment (Phase 4 port of `/enrich`)

## 6. Success metrics

| Metric | Baseline (measure in Phase 0) | Target by end of Phase 3 |
|--------|-------------------------------|--------------------------|
| Daily brief accepted with ≤2 edits | n/a | ≥80% of workdays |
| Items with ≥1 linked context artifact | n/a | ≥90% |
| Items completed by due date | measure | +25% vs baseline |
| Completed items with a completion record | 0% | ≥90% |
| Skills proposed / approved / active | 0 | ≥6 / ≥3 / ≥3 |
| Estimated minutes saved per week by skills | 0 | ≥120 |
| Time to plan the day | measure | <5 min |

## 7. Constraints and assumptions (flagged)

- **A1:** The user has a Microsoft 365 Copilot license and Copilot Studio maker rights in a work environment. *Verify in Phase 0.*
- **A2:** The Excel Online (Business) connector is allowed in the agent's environment (it's a Standard connector). The workbook lives in your OneDrive.
- **A3:** IT allows Work IQ (preview) or, failing that, the standard Office 365 Outlook / Teams / Planner connectors.
- **A4:** Scheduled (autonomous) runs consume Copilot Credits billed to the tenant. Volume is low: ~2–4 runs/day.
- **A5:** Copilot Studio skills (SKILL.md, open Agent Skills format) are early. Import is done in the UI, with no public create/update API found as of 2026-10. The design therefore keeps a runtime "playbook" tier that works without republishing (see 04-skill-lifecycle.md).
- **C1:** Tenant DLP policies may block mixing connectors (e.g., HTTP + Office 365). Phase 0 must check this.
- **C2:** Agent instructions are kept under 8,000 characters. Detailed procedures live in skills, not in instructions.
