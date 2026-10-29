# 06 — Decisions (ADRs) & Open Questions

---

## ADR-001 — Copilot Studio agent (harness) as the runtime

**Status:** Proposed (2026-10-29)

**Context:** The agent must run on a schedule, react to events, keep durable state, and generate and run skills, all inside the work tenant.

**Decision:** A Copilot Studio agent on the GitHub Copilot harness, published to M365 Copilot and Teams.

**Why:**
- Native SKILL.md skills (open Agent Skills format), so skills authored in this repo are portable
- Workflows and MCP servers as tools (GA, Aug 2026)
- Triggers and workflows support scheduled and event-driven runs. Declarative agents can't do this.
- Dataverse in the same environment. Entra Agent ID for audit.
- Model choice: Claude Sonnet 5 or GPT-5.5 as the primary model (GA)

**Rejected:** Declarative agent (no triggers). Custom engine via Agents SDK/Foundry (ops overhead; kept as an escape hatch).

**Revisit if:** the harness blocks Dataverse tools, or credit costs exceed budget.

---

## ADR-002 — Dataverse as system of record; Planner/To Do as optional mirror

**Status:** Proposed. **Depends on Phase 0** (Dataverse availability).

**Context:** Items need custom fields (score, rationale, goal, signature) and relations (links, records, skill runs). Planner basic plans lack custom fields, and To Do has no relational links.

**Decision:** Dataverse tables per `schema/dataverse-tables.yaml`. Optionally mirror open P1/P2 items to Planner or To Do for mobile and Outlook visibility (one-way, agent → Planner, with completion synced back).

**Fallback:** SharePoint Lists with the same columns (lookups become ID columns). This loses some relational querying, but every user has Lists.

---

## ADR-003 — Two-tier skills (runtime playbooks + native skills)

**Status:** Proposed

**Context:** No documented API exists to create or update Copilot Studio skills. Import happens in the UI. The learning loop shouldn't depend on a manual step.

**Decision:** Approved proposals go live immediately as playbooks (rows in `cos_skill`, loaded via a `find_playbook` tool). Proven playbooks graduate to native skills through git + manual import. See 04-skill-lifecycle.md §5.

---

## ADR-004 — Repo as "agent-as-code" source of truth

**Status:** Proposed

**Decision:** Instructions, skills, schema, and workflow specs live in `m365/`. Copilot Studio is the deployment target. Changes go through PRs, with `scripts/skills.py validate` as the gate. The root Claude Code kit stays as the design reference and personal-channel assistant.

**Why:** Diffable history of how the agent's behavior changed. Claude Code can author and refactor skills in the repo.

---

## ADR-005 — Drafts only; no autonomous outbound actions in v1

**Status:** Accepted (inherited from CLAUDE.md §1.4)

Every send, post, accept, or delete requires explicit user confirmation, enforced by tool confirmation settings and by the instructions.

---

## Open questions

| # | Question | Blocks | Owner |
|---|----------|--------|-------|
| Q1 | Do you have Copilot Studio maker access and a Dataverse environment in your work tenant? | Phase 1 | You + IT |
| Q2 | Is Work IQ (preview) enabled, and are MCP servers allowed by DLP? | Intake quality | IT |
| Q3 | Daily brief delivery: Teams card (recommended), Copilot chat, or email? | Phase 2 | You |
| Q4 | Primary model: Claude Sonnet 5 or GPT-5.5? Recommend testing both on the same week of briefs. | Phase 1 tuning | You |
| Q5 | Should P1/P2 items mirror to Planner or To Do for mobile? | Phase 4 | You |
