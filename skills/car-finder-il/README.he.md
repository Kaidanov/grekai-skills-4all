<div dir="rtl">

# car-finder-il 🚗

מציאת רכב יד שנייה טוב בישראל — עם **התראה לטלפון רק כשבאמת מופיע משהו ששווה.**

ההתראות של יד2 חינמיות, אבל הן קופצות על *כל* התאמה גסה. הסקיל הזה מושך את אותן
מודעות, ואז **נותן ציון לכל רכב מול קבוצת ההשוואה שלו** (מחיר מול מודעות דומות,
יד, סוג בעלות, ק"מ-לשנה, מספר תמונות) ושולח התראה רק כשרכב באמת טוב יותר מהשאר.
קריאה בלבד — מוצא ומדרג, לא מפרסם, לא מקפיץ ולא קונה.

> 🇬🇧 English: [README.md](README.md) · Guide: [docs/HOWTO.en.md](docs/HOWTO.en.md)

## ניסיון של 60 שניות (בלי טוקנים, בלי רשת)

<div dir="ltr">

```bash
python3 scripts/carfinder.py search examples/criteria.example.json --source mock --lang he
```

</div>

מקבלים רשימת רכבים מדורגת עם שורת נימוק לכל רכב. כל הערך בפקודה אחת.

## איך זה עובד

<div dir="ltr">

```
criteria.json ──▶ source (Apify read actor) ──▶ score (יחסי לקבוצה)
                                                      │
   התראה לטלפון ◀── notify ◀── רק חדש / ירידת מחיר ◀── store (דה-דופ)
```

</div>

- **קריאה, אף פעם לא כתיבה.** משתמש ב-actor של Apify מעל HTTPS — בלי התחברות,
  בלי דפדפן. אין API לפרסום באף לוח רכב בישראל, וזה במכוון.
- **תמחור כן.** אין API למחירון לוי יצחק, אז כל רכב נמדד מול **קבוצת ההשוואה
  שלו** (אותו יצרן+דגם, שנה ±1) מאותה שליפה.
- **התראות חכמות.** ריצה מתוזמנת (`run`) שולחת **רק התאמות חדשות וירידות מחיר
  אמיתיות**, עם דה-דופ ב-Supabase (או קובץ מקומי כשאין חיבור).
- **הטלפון שלך, הערוץ שלך.** wa-ai (וואטסאפ), טלגרם או ntfy.

## שתי דרכים להשתמש

| | פקודה | דורש |
|---|---|---|
| **חיפוש עכשיו** | `carfinder.py search criteria.json` | טוקן Apify + actor |
| **מעקב + התראה** | `carfinder.py run criteria.json` (ב-cron) | + Supabase + ערוץ דחיפה |

`search` לבדו שימושי לגמרי. מוסיפים `run` רק כשרוצים התראות אוטומטיות.

## התקנה

1. **Apify** — נרשמים, לוקחים טוקן, בוחרים actor של רכבי יד2 מ-
   [apify.com/store](https://apify.com/store) (חיפוש "yad2"), מעתיקים את ה-id.

<div dir="ltr">

```bash
export APIFY_TOKEN=apify_api_xxx
export APIFY_ACTOR_ID=some/yad2-actor
```

</div>

2. **קריטריונים** — מעתיקים את `examples/criteria.example.json` ועורכים.
3. **(רשות) מצב מעקב** — יוצרים את הטבלה ומגדירים ערוץ דחיפה:

<div dir="ltr">

```bash
python3 scripts/carfinder.py init-db | psql "$DATABASE_URL"
export SUPABASE_URL=https://<ref>.supabase.co
export SUPABASE_KEY=<service_role key>      # סודי, צד-שרת בלבד
export WAAI_WEBHOOK_URL=https://.../hook    # או TELEGRAM_* / NTFY_TOPIC
```

</div>

4. **(רשות) תזמון** — `.github/workflows/car-finder.yml` מריץ פעמיים ביום.
   מוסיפים את אותם שמות כ-Action secrets ועורכים את ה-cron.

מדריך מלא: [docs/HOWTO.he.md](docs/HOWTO.he.md).

## מה זה לא עושה (במכוון)

בלי פרסום, בלי הקפצה, בלי הודעות אוטומטיות למוכרים, בלי קנייה. אלה דורשים דפדפן
מחובר ושייכים לצד המכירה — בעיה נפרדת. דווקא ה"קריאה בלבד" הוא מה שהופך את זה
לבטוח להרצה אוטומטית.

פייתון ספריית-תקן בלבד. בלי תלויות. MIT.

</div>
