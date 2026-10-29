# Office Scripts

TypeScript that runs inside `ChiefOfStaff.xlsx` (Excel for the web › **Automate**). The flows call these with **Excel Online (Business) › Run script**. Deterministic work (counting, grouping, date math) happens here, so the agent spends Copilot Credits only on judgment.

| Script | Called by | Returns |
|--------|-----------|---------|
| `mine-signatures.ts` | [weekly-skill-review flow](../flows/weekly-skill-review.md) | JSON: skill candidates (signature, count, avg minutes, cadence, common steps, automation fit, score, est. minutes saved, evidence IDs) and signatures already covered by active skills |

## Install (once, ~3 min)

1. Open the workbook in Excel for the web › **Automate** › **New Script**.
2. Replace the editor contents with `mine-signatures.ts`. Skip `excelscript.d.ts`; Excel supplies those types.
3. Rename the script `mine-signatures` and save it. It's stored in OneDrive › Documents › Office Scripts.
4. Test it: **Run**. With no completed items it returns `{"itemsConsidered":0,"candidates":[],...}`.

## Keeping it honest

`m365/scripts/mine.py` is a line-for-line Python reference. `python3 -m unittest discover -s m365/tests` compiles the TypeScript with `tsc`, runs it under Node, and checks both produce identical JSON on the same rows. If you change one, change the other. Rounding is half-up (JavaScript `Math.round`) in both.

Run the reference against a downloaded workbook:

```bash
python3 m365/scripts/mine.py ~/Downloads/ChiefOfStaff.xlsx --as-of 2026-10-29
```
