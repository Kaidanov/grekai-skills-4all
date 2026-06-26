# Natural-language logging → transaction rows

Turn a plain Hebrew/English message into clean Transactions rows. The family
types how they actually talk; this maps that to the ledger.

## Output contract

Always output rows in this exact column order (one row per line item):

`Date | Member | Account | Type | Group | Category | Description | Amount | ExcludeFromBudget | Notes`

- **Date** — ISO `YYYY-MM-DD`. Default to today if unstated. "אתמול"=yesterday,
  "ב-3" / "on the 3rd" = that day in the current/most recent month.
- **Member** — infer if named ("Maya's freelance" → Maya); else leave blank or
  use the primary member.
- **Account** — infer from cues ("on the Visa", "מהחשבון", "מזומן"); else blank.
- **Type** — one of `income | expense | transfer | investment`.
- **Group / Category** — from `references/categories.md`.
- **Amount** — positive number, no currency symbol, no thousands separators in
  the cell (parse "1,247" and "18.5k"/"18,500" → 18500).
- **ExcludeFromBudget** — `TRUE` for investment & transfer (and CC settlement),
  else `FALSE`. See budget-logic.
- **Notes** — anything extra worth keeping.

After the rows, give a one-line confirmation. Don't lecture.

## Amount & currency parsing

- Default currency = the household currency from Setup (₪ for Israel).
- Strip `₪`, `ש"ח`, `שח`, `NIS`, `$`, `€`. If a non-home currency is given,
  note it in Notes (don't silently convert unless asked).
- "k"/"אלף" → ×1000. "18.5k" → 18500. "וחצי" after a round number → +500 only if
  clearly meant; otherwise ask.
- Multiple items in one message → multiple rows ("250 בשופרסל ועוד 40 בארומה" →
  two rows).

## Type detection cues

- **income**: משכורת/salary, נכנס/נכנסה, התקבל, החזר מס, שכר דירה, freelance,
  דיבידנד, קצבה.
- **investment**: הפקדתי/העברתי ל… (קרן השתלמות, פנסיה, גמל), קניתי מניות,
  bought ETF, crypto.
- **transfer**: ביט, פייבוקס, העברה בנקאית, משכתי מהכספומט, moved to savings.
- **expense**: everything else (default).

## Israeli merchant → category map (high-confidence)

Supermarket → **food.supermarket**: שופרסל / Shufersal, רמי לוי / Rami Levy,
ויקטורי, יוחננוף, יינות ביתן, אושר עד, מגה, טיב טעם, סופר פארם (groceries side).
Pharmacy/health → **health.pharmacy**: סופר פארם (תרופות), Be / ניו פארם.
Cafes → **food.cafes**: ארומה / Aroma, קפה קפה, גרג, לנדוור, קפה גרג.
Restaurants/delivery → **food.delivery**: וולט / Wolt, תן ביס / 10bis, מישלוח.
Fuel → **transport.fuel**: פז / Paz, סונול / Sonol, דלק / Delek, דור אלון, ten.
Transit → **transport.public**: רב קו / Rav Kav, רכבת ישראל, אגד, דן, מטרופולין.
Taxi → **transport.taxis**: גט / Gett, יאנגו / Yango.
Parking/tolls → **transport.parking**: פנגו / Pango, סלופארק / Cellopark, פלאוטו;
**transport.toll**: כביש 6 / Kvish 6, דרך ארץ.
Fines → **transport.fines**: קנס, דוח חניה, משטרה (traffic).
HMO → **health.hmo**: מכבי / Maccabi, כללית / Clalit, מאוחדת / Meuhedet, לאומית.
Municipal → **housing.arnona**: ארנונה, עירייה, מועצה.
Utilities → **housing.electricity** חברת חשמל; **housing.water** מי…/תאגיד מים;
**housing.gas** סופרגז/אמישראגז/פזגז; **housing.internet** בזק/הוט/פרטנר/סלקום
(internet); **housing.phone** (mobile lines).
Streaming/subs → **entertainment.streaming** Netflix/Disney+/Apple TV;
**entertainment.music** Spotify; **subscriptions.software** SaaS.
Online → **shopping.online**: אמזון / Amazon, אלי אקספרס / AliExpress, KSP, איביי.
Electronics → **shopping.electronics**: KSP, באג / Bug, איוון, מחסני חשמל.
Transfers → **transfers.bit** ביט; **transfers.paybox** פייבוקס.
Investments → **savings.training** קרן השתלמות; **savings.pension** פנסיה;
**savings.provident** קופת גמל / גמל להשקעה; **savings.stocks** מניות/ETF/בלינק/
מיטב/IBI; **savings.crypto** ביטקוין/קריפטו.

When no pattern matches, set Category = `לא מסווג / Uncategorized` and add the
merchant name to Notes so the family can map it once and reuse.

## Worked examples

**Input:** "שילמתי 250 בשופרסל ו-40 בארומה, וקנס חניה 100"
**Output:**
```
2026-06-26 |  |  | expense | מזון וסופרמרקט | סופרמרקט | שופרסל | 250 | FALSE |
2026-06-26 |  |  | expense | מזון וסופרמרקט | קפה | ארומה | 40 | FALSE |
2026-06-26 |  |  | expense | תחבורה | קנסות תנועה | קנס חניה | 100 | FALSE |
```

**Input:** "salary 18,500 net came in, and I moved 2,000 to keren hishtalmut"
**Output:**
```
2026-06-26 |  |  | income | הכנסות | משכורת | Salary (net) | 18500 | FALSE |
2026-06-26 |  |  | investment | חיסכון והשקעות | קרן השתלמות | Transfer | 2000 | TRUE |
```

**Input:** "credit card bill Cal 7,430 came out"
**Output (ask if line items are also tracked; if just the bill):**
```
2026-06-26 |  | Cal | expense | הלוואות וחובות | כרטיס אשראי | חיוב חודשי Cal | 7430 | FALSE |
```
If the family *does* log Cal's individual purchases, instead mark this settlement
row `ExcludeFromBudget = TRUE` to avoid double-counting (see budget-logic §3).
