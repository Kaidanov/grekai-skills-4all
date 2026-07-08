<div dir="rtl">

# מדריך — car-finder-il (עברית)

צעד-אחר-צעד, מאפס ועד "הטלפון מצלצל כשמופיע רכב טוב".

## 0. קודם לנסות אופליין (30 שניות)

בלי טוקנים — מוודאים שהציון הוא מה שרצית לפני שמחברים משהו:

<div dir="ltr">

```bash
python3 scripts/carfinder.py search examples/criteria.example.json --source mock --lang he
```

</div>

קוראים את שורת הנימוק מתחת לכל רכב. אם הנימוקים תואמים לאיך *שאתה* שופט רכב —
כל השאר זה רק חיבורים טכניים.

## 1. כותבים קריטריונים

מעתיקים את הדוגמה ועורכים:

<div dir="ltr">

```bash
cp examples/criteria.example.json my_criteria.json
```

```jsonc
{
  "id": "family-suv",          // מפתח דה-דופ — שמור אותו קבוע לכל חיפוש
  "label": "ג'יפון משפחתי < 90k",
  "lang": "he",
  "make": ["Kia", "Hyundai"],  // ריק = הכל
  "year_min": 2019,
  "price_max": 90000,
  "km_max": 120000,
  "hand_max": 2,               // יד ≤ 2
  "owner_type": ["private"],   // לפסול רכב חברה / ליסינג
  "min_score": 60,             // סף התראה
  "weights": { "price_value": 0.4, "hand": 0.15, "owner": 0.15,
               "km": 0.15, "photos": 0.05, "fresh": 0.1 }
}
```

</div>

ההתאמה של `make`/`model` גמישה, ואף פעם לא פוסלת רכב בגלל *מידע חסר* — רק בגלל
מידע שבאמת נכשל בכלל.

## 2. מחברים נתוני יד2 אמיתיים (Apify)

1. נרשמים ב-[apify.com](https://apify.com) ומעתיקים את ה-API token.
2. ב-[apify.com/store](https://apify.com/store) מחפשים **yad2**, פותחים actor
   של רכבים, ומעתיקים את ה-id (נראה כמו `user/actor-name`).
3. מייצאים ומריצים:

<div dir="ltr">

```bash
export APIFY_TOKEN=apify_api_xxx
export APIFY_ACTOR_ID=user/yad2-vehicles
python3 scripts/carfinder.py search my_criteria.json --lang he
```

</div>

אם ה-actor מצפה למבנה קלט אחר, מוסיפים בלוק `apify_input` לקריטריונים — הוא
מועבר כמו שהוא.

הערת עלות: Apify מחייב לפי ריצה/תוצאה. סריקה פעמיים ביום לחיפוש אחד = אגורות.

## 3. מפעילים התראות לטלפון (מסלול `run`)

`run` = שליפה → ציון → השוואה למה שכבר הוצג לך → דחיפה של החדשים בלבד. צריך
זיכרון וערוץ.

**זיכרון (Supabase):**

<div dir="ltr">

```bash
python3 scripts/carfinder.py init-db        # מדפיס את ה-SQL
python3 scripts/carfinder.py init-db | psql "$DATABASE_URL"
export SUPABASE_URL=https://<ref>.supabase.co
export SUPABASE_KEY=<service_role key>
```

</div>

אין Supabase? `run` עדיין עובד — נופל חזרה ל-`~/.car-finder-il/seen.json` כך
שהדה-דופ שורד בין ריצות על אותה מכונה.

**ערוץ (בוחרים אחד):**

<div dir="ltr">

```bash
export WAAI_WEBHOOK_URL=https://your-wa-ai/hook     # וואטסאפ דרך הסוכן שלך
export TELEGRAM_BOT_TOKEN=123:abc
export TELEGRAM_CHAT_ID=456
export NTFY_TOPIC=my-car-hunt-7f3a
```

</div>

בדיקה:

<div dir="ltr">

```bash
python3 scripts/carfinder.py run my_criteria.json
```

</div>

הריצה הראשונה דוחפת את כל ההתאמות; ריצות אחר כך דוחפות רק רכבים חדשים וירידות
מחיר.

## 4. שמים על תזמון

`.github/workflows/car-finder.yml` כבר מריץ `run` פעמיים ביום. כדי להשתמש:

1. דוחפים את הסקיל לריפו.
2. ריפו → **Settings → Secrets and variables → Actions** → מוסיפים
   `APIFY_TOKEN`, `APIFY_ACTOR_ID`, `SUPABASE_URL`, `SUPABASE_KEY` ואת סוד הערוץ.
3. עורכים את שורות ה-`cron:` ואת מטריצת ה-`criteria:` (שורה לכל חיפוש).
4. כפתור **Run workflow** להרצת בדיקה.

## פתרון תקלות

- **`APIFY_TOKEN not set`** ← אתה על המקור האמיתי בלי טוקן. הוסף אותו, או השתמש
  ב-`--source mock`.
- **תוצאות ריקות בנתונים אמיתיים** ← מפתחות הפלט של ה-actor שונים; בדוק פריט גולמי
  אחד ובמידת הצורך מפה דרך `apify_input`. הנרמול כבר מנסה הרבה שמות נפוצים.
- **אין דחיפה** ← לא הוגדר ערוץ, אז הודפס ל-stdout (לפי תכנון).
- **התראה חוזרת על אותו רכב** ← מכונה אחרת / אין Supabase משותף. כוון את שתיהן
  לאותם `SUPABASE_*`.

## תזכורת

זה כלי מציאה. הוא לעולם לא יפרסם, יקפיץ, ישלח הודעה למוכר או יקנה. זה צד המכירה,
ודורש דפדפן מחובר — כלי נפרד במכוון.

</div>
