# 07 — Tenant Readiness Checklist

Take this to IT / your Power Platform admin. Every row needs an answer before Phase 1.

| # | Check | How to verify | Needed for | Fallback if "no" |
|---|-------|---------------|-----------|------------------|
| R1 | Microsoft 365 Copilot license assigned to you | M365 admin center → your user → Licenses | Publishing to M365 Copilot; Work IQ | Teams-only publish (agent still works, with weaker context) |
| R2 | Copilot Studio maker access | Open copilotstudio.microsoft.com → can you create an agent? | Everything | Ask admin for maker role in a dev environment |
| R3 | Excel Online (Business) connector allowed; OneDrive for Business available | Copilot Studio → agent → Tools → Add tool → search "Excel Online (Business)" | ADR-006 store | SharePoint List with the same columns |
| R4 | GitHub Copilot harness available for new agents | Create agent → check orchestration/harness option | Native skills | Classic orchestration + playbooks only |
| R5 | Agent Skills tab available | Agent → Skills tab | Native skills | Playbooks only (Tier A) |
| R6 | Work IQ enabled (preview) | Agent → Knowledge/Tools → Work IQ | Intake research, reconcile evidence | Office 365 Outlook + Teams + SharePoint connectors |
| R7 | MCP servers allowed by DLP (Planner MCP, Outlook MCP) | Power Platform admin → Data policies | Planner mirror, richer tools | Standard connectors |
| R8 | Triggers / workflows allowed; Copilot Credits available for autonomous runs | Admin center → Copilot Studio → billing/capacity | Daily brief at 07:00, completion detector | On-demand only ("plan my day") |
| R9 | Publishing to Teams/M365 Copilot for personal use without org-wide approval | Admin: agent publishing policy | Daily use | Shared with self only via test chat |
| R10 | Allowed primary models (Claude Sonnet 5 / GPT-5.5) | Agent → Settings → Model | Quality tuning | Default model |
| R11 | Connector mix allowed in one DLP group (Excel Online (Business) + Office 365 Outlook + Teams) | Data policies | All tools in one agent | Split into separate flows |
| R12 | Data classification: may meeting/email summaries be stored in a OneDrive workbook? | Ask compliance | ResearchNotes / Outcome content | References-only mode (links, no summaries) |

## Notes to bring to IT

- Single-user agent, delegated auth only, no application permissions
- All data stays in the tenant (your OneDrive + M365)
- No autonomous outbound sends (every send needs user confirmation)
- Expected scheduled volume: ~2–4 runs/workday
