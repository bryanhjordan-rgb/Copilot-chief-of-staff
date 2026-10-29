# Adaptive Card templates

Cards the workflows post to your Teams chat with the agent. They use Adaptive Cards 1.5, which Teams supports. Each card is posted with **Microsoft Teams › Post adaptive card in a chat or channel and wait for a response**. The flow waits for your button press and gets back the button's `data` plus any text you typed.

## How to use a card in a flow

1. Add a **Compose** action and paste the card JSON in.
2. Replace each `"{{TOKEN}}"` string with dynamic content (keep the quotes). Compose escapes quotes and newlines for you. Never splice text in with `replace()`, because a quote in the brief would break the JSON.
3. Pass the Compose output to the Teams action's **Adaptive Card** field. Post as: Flow bot, Post in: Chat with Flow bot, Recipient: you.
4. Branch on `body/data/action` from the response (table below).

Tokens only ever appear as whole JSON string values, so every file is valid JSON as-is. CI checks this.

## Cards

### `daily-brief.card.json` — flow: [daily-brief.md](../daily-brief.md)

| Token | Value |
|-------|-------|
| `BRIEF_TITLE` | `Thursday, Oct 29 — 4 meetings, 3.5h free` (first line of the agent's brief) |
| `BRIEF_MARKDOWN` | The rest of the brief, in card-safe markdown (see below) |
| `BRIEF_DATE` | `yyyy-MM-dd` |

| `data.action` | Flow does |
|---------------|-----------|
| `accept` | Add a Feedback row: TargetType=brief, TargetRef=`briefDate`, Signal=accept |
| `edit` | Run the agent: `Edit today's brief: <editText>`. Add a Feedback row: Signal=edit, Detail=`editText` |
| `replan` | Run the agent: `Re-plan today. Reason: user requested.` Post the new brief as a new card |

### `weekly-review.card.json` — flow: [weekly-skill-review.md](../weekly-skill-review.md)

| Token | Value |
|-------|-------|
| `REVIEW_TITLE` | `Weekly review — Oct 23–29` |
| `REVIEW_MARKDOWN` | Week summary + numbered proposals, card-safe markdown |
| `REVIEW_DATE` | `yyyy-MM-dd` |

| `data.action` | Flow does |
|---------------|-----------|
| `decide` | Run the agent with `decisions` verbatim (e.g. `approve 1, reject 2`) |
| `approve_all` | Run the agent: `approve all` |
| `reject_all` | Run the agent: `reject all` |

### `completion-confirm.card.json` — flow: [completion-detector.md](../completion-detector.md)

One card per item with evidence.

| Token | Value |
|-------|-------|
| `ITEM_TITLE` | Items.Title |
| `EVIDENCE` | e.g. `Contoso renewal review ended at 12:00` |
| `ITEM_ID` | Items.ID |

| `data.action` | Flow does |
|---------------|-----------|
| `complete` | Run the agent: `Run reconcile for <itemId>. User confirmed. Minutes spent: <minutesSpent or unknown>.` |
| `not_yet` | Append `<now> flow completion_declined` to the item's History (suppresses re-asking for 24h, the same as `completion_asked`) |

## Card-safe markdown

Teams TextBlocks render a subset of markdown: `**bold**`, `_italic_`, `- ` bullets, `1. ` numbered lists, and `[text](url)` links. Headings, tables, and code fences show up as raw characters. The daily-brief and skill-miner skills return this subset when the invocation is `scheduled`.
