# 09 — Daily Use

How to work with the agent once it's live. Talk to it in Microsoft 365 Copilot Chat or Teams; the list lives in `ChiefOfStaff.xlsx` (List sheet), which you can read any time.

---

## The rhythm

| When | You do | The agent does |
|------|--------|----------------|
| **07:00** (Phase 2+) | Read the brief card. **Accept**, type an edit, or **Re-plan**. | Posts Top 3, a timed plan, heads-ups, goals pulse, not-today list. Writes DoDate/PlannedSlot to the planned rows. |
| **Morning** (Phase 1) | Say "plan my day". | Same brief, in chat. |
| **New work arrives** | "Add: …" or forward the email/message to the chat. | Dedupes, searches mail/calendar/files/Teams (≤4 queries), links context, scores it, tells you where it ranks. |
| **Switching tasks** | "What now?" | Re-ranks open items, states the tradeoff. |
| **Before a meeting** | "Prep me for the 2pm." | One-screen prep: purpose, your outcome, who, open items with them, docs, 3 talking points. |
| **After a meeting** | "Debrief the Contoso meeting." | Decisions, your actions → items, their actions → waiting-on, follow-up draft. Writes only after you say OK. |
| **Inbox piling up** | "Triage" or "triage quick". | Tiered list with drafts. Nothing sent without "Send N". |
| **Something's done** | "Done with the pricing prep." (or tap **Mark complete** on the card) | Writes the completion record, proposes goal progress, offers follow-ups. |
| **Friday 15:00** (Phase 3) | Approve or reject proposals on the weekly card. | Week summary + up to 3 skill proposals, patches, retirements. |

## Phrase cheat sheet

| Say | Skill | Notes |
|-----|-------|-------|
| "plan my day", "morning brief", "re-plan" | daily-brief | "Re-plan" after a meeting moves or something blows up |
| "add …", "remind me to …", "look into …", "track …" | intake | Include a deadline if you know it; otherwise it proposes one and labels it |
| "what now?", "rank my list", "what should I drop?" | prioritize | Ask "why is X above Y?" to see the score breakdown |
| "done with …", "finished …", "close out …" | reconcile | Mention minutes spent if you know them ("took about an hour") |
| "triage", "triage quick", "what needs me?" | triage | Then "Send 2", "Draft 3", "Track 4", "Edit 1: shorter" |
| "prep me for …", "brief me on the 2pm" | meeting-prep | Works best 15–30 min before the meeting |
| "debrief …", "capture actions from …" | meeting-debrief | Needs a Teams recap/transcript, or paste 3 bullets |
| "review my week", "what should be a skill?" | skill-miner | Then "approve 1", "reject 2", "approve patch 3" |
| "explore" / "just thinking out loud" | — | Turns off pushback; thinking-partner mode |

## Giving feedback (this is how it learns)

- **Correct it in plain words**, the way you'd correct a person: "Stop ranking internal syncs above customer asks." It logs your exact words to the Feedback sheet.
- **Same correction twice → it proposes a fix** (≤10 lines) to the relevant skill or its instructions. Nothing changes until you approve.
- **Edit drafts before sending** rather than re-asking; your edits are logged as tone/length feedback.
- **Mark repeated work done properly.** Each completion's Steps and Signature are what the weekly review mines for new skills. Sloppy closes = no skill proposals.

## Editing the sheet yourself

- Fine any time in **Excel for the web**: change Status, DueDate, notes, delete an item.
- Keep **Open** in sync (No when Status is done/dropped). The agent does this; if you edit Status by hand, flip Open too.
- Don't rename headers or add columns by hand; change `schema/workbook.yaml` and rebuild.
- Avoid editing in desktop Excel while a flow might be running (07:00, every 2h 9–5, Fri 15:00); the connector can lock the file for a few minutes.
- Something looks off? Download it and run `python3 m365/scripts/lint_workbook.py ChiefOfStaff.xlsx`.

## What it will never do

- Send, post, accept, decline, or delete anything without your explicit "Send"/"Y".
- Propose meeting times without checking your calendar, or ask others "when works for you?".
- Write summaries of confidential topics (fundraising, M&A, termination, PIP, restructuring, legal) — titles and links only.
- Activate a new skill, change its own instructions, or retire a skill without your approval.
- Invent links, dates, or people. If it can't find context it says so.

## Weekly 10-minute upkeep

1. Glance at the weekly review: approve useful proposals, reject noise.
2. Update goal progress if the agent's proposals missed something (Goals sheet).
3. Add one line to the iteration log in [05-roadmap.md](05-roadmap.md): what worked, what annoyed you.
4. Quarterly: refresh goals (`--goals` rebuild or edit the Goals sheet) and your profile (`render_instructions.py`).
