# Category taxonomy (Israel-first, bilingual)

This is the category tree the workbook seeds and that drives the Transactions
dropdowns. It mirrors the taxonomy from the user's FinanceOS project. 18 groups.
Format: **Group** → category (he / en). The machine slug is the english side,
lowercased with dots, e.g. `food.supermarket`.

For non-Israel setups, keep the structure but localize HMOs, ארנונה (municipal
tax), ביטוח לאומי (national insurance), and provident/pension names.

## Table of contents
Income · Food · Housing · Transport · Health · Insurance · Education · Children ·
Entertainment · Shopping · Travel · Subscriptions · Savings & Investments ·
Loans & Debt · Business · Transfers · Taxes & Fees · Uncategorized

---

## הכנסות / Income  *(type: income)*
- משכורת / Salary
- פרילנס / Freelance
- שכר דירה / Rental income
- דיבידנדים / Dividends
- החזר מס / Tax refund
- קצבאות / Government benefits (ביטוח לאומי, קצבת ילדים)
- מתנות שהתקבלו / Gifts received
- הכנסות אחרות / Other income

## מזון וסופרמרקט / Food & Groceries  *(expense)*
- סופרמרקט / Supermarket
- שוק / Market
- מסעדות / Restaurants
- קפה / Cafes
- משלוחים / Delivery (Wolt, 10bis)
- בר ואלכוהול / Bar & alcohol

## דיור / Housing  *(expense)*
- שכירות / Rent
- משכנתא / Mortgage
- ארנונה / Municipal tax (arnona)
- ועד בית / Building committee
- חשמל / Electricity
- גז / Gas
- מים / Water
- אינטרנט / Internet
- טלפון / Phone
- ביטוח דירה / Home insurance
- תחזוקת בית / Home maintenance & repairs

## תחבורה / Transportation  *(expense)*
- דלק / Fuel
- ביטוח רכב / Car insurance
- רישוי וטסט / Registration & licensing
- חנייה / Parking
- כביש 6 / Toll roads
- תחבורה ציבורית / Public transit (Rav Kav)
- מוניות / Taxis (Gett)
- תחזוקת רכב / Car maintenance
- קנסות תנועה / Traffic & parking fines

## בריאות / Health  *(expense)*
- קופת חולים / HMO (Maccabi, Clalit, Meuhedet, Leumit)
- ביטוח בריאות / Health insurance
- תרופות / Pharmacy
- רופאים / Doctors & specialists
- שיניים / Dental
- אופטיקה / Optometry

## ביטוחים / Insurance  *(expense)*
- ביטוח חיים / Life insurance
- ביטוח מנהלים / Executive insurance
- ביטוח נסיעות / Travel insurance
- ביטוח אחר / Other insurance

## חינוך / Education  *(expense)*
- שכר לימוד / Tuition
- קורסים / Courses & training
- ספרים וחומרי לימוד / Books & materials
- גן / מעון / Daycare / kindergarten
- חוגים / Extracurricular activities

## ילדים / Children  *(expense)*
- מזון לתינוקות / Baby & kids food
- ביגוד ילדים / Kids clothing
- צעצועים / Toys
- בייביסיטר / Babysitter & nanny

## בידור / Entertainment  *(expense)*
- סטרימינג / Streaming (Netflix, Disney+, Apple TV)
- מוזיקה / Music (Spotify)
- משחקים / Games
- קולנוע ואירועים / Cinema & events
- ספורט וחדר כושר / Sports & gym
- ספרים ומגזינים / Books & magazines

## קניות / Shopping  *(expense)*
- ביגוד והנעלה / Clothing & fashion
- אלקטרוניקה / Electronics
- ריהוט ובית / Furniture & home
- מתנות / Gifts
- קניות אונליין / Amazon & online shopping

## מסעות / Travel  *(expense)*
- טיסות / Flights
- מלונות / Hotels
- השכרת רכב / Car rental
- אטרקציות / Attractions & tours

## מנויים / Subscriptions  *(expense)*
- מנוי תוכן / Content subscription
- מנוי תוכנה / Software / SaaS
- מנוי חדר כושר / Gym membership
- מנוי אחר / Other recurring

## חיסכון והשקעות / Savings & Investments  *(type: investment — ExcludeFromBudget = TRUE)*
- קרן פנסיה / Pension fund
- קרן השתלמות / Training fund
- קופת גמל / Provident fund (כולל גמל להשקעה)
- מניות / Stocks & ETFs
- חיסכון / Savings transfer
- קריפטו / Crypto

## הלוואות וחובות / Loans & Debt  *(expense)*
- החזר הלוואה / Loan repayment
- כרטיס אשראי / Credit card payment *(reconciliation — see budget-logic)*
- ריבית / Interest charges

## עסק / Business *(if self-employed)*  *(expense)*
- הוצאות עסקיות / Business expenses
- ציוד משרדי / Office supplies
- שירותים מקצועיים / Professional services
- פרסום / Marketing & advertising

## העברות / Transfers  *(type: transfer — ExcludeFromBudget = TRUE)*
- ביט / Bit transfer
- פייבוקס / Paybox
- העברה בנקאית / Bank transfer
- משיכת מזומן / ATM cash withdrawal

## מיסים ועמלות / Taxes & Fees  *(expense)*
- מס הכנסה / Income tax
- ביטוח לאומי / National insurance
- עמלות בנק / Bank fees
- עמלות כרטיס / Card fees

## לא מסווג / Uncategorized
- ממתין לסיווג / Pending categorization
- אחר / Other

---

### Notes for the workbook builder
- The **Group** list seeds the budget-targets tab (one target row per group, with
  room to add per-category targets).
- The **Category** dropdown in Transactions should offer all leaf categories;
  pair it with the Group column for clean SUMIFS.
- Mark Savings & Investments and Transfers with `ExcludeFromBudget = TRUE` by
  default so the operating budget isn't distorted by asset moves.
