# The exam hub — subjects & how to register a new app

The kids' study apps are collected at **[exam-hub-grekai.netlify.app](https://exam-hub-grekai.netlify.app/)**
— a Hebrew, subject-categorized landing page that links out to each single-file app. Apps this
skill generates are deployed independently (Netlify Drop) and then **linked from the hub**.

## Subjects already in the hub (mirror these categories)

| Emoji / category | Apps in the hub | Notes |
|---|---|---|
| ➗ **מתמטיקה / Math** | `MATH 8` (כיתה ח׳ — נושאים, נוסחאון, בוחנים), `MATH 9` (כיתה ט׳ — חזרה לבחינה, תרגול, פתרונות) | Hebrew RTL; formulas via inline helpers. |
| 🔤 **אנגלית / English** | `eng-tet-grekai` (grammar, vocabulary, verbs), `tenses-english` (present/past/future + practice) | LTR — set `meta.lang:"en", dir:"ltr"`. |
| 📜 **היסטוריה / History** | `3 EXAMS` (תנועת ההשכלה, מהפכות, נאורות), `FULL` (סיכום נאורות + פילוסופים) | Hebrew; fill/MC about people, dates. |
| 🔬 **מדע / Science** | `MADA 8` (חומר מלא לכיתה ח׳), `MOLECULE` (אטומים ומולקולות + המחשה) | Chemistry formulas via `<sub>`/`<sup>`; מטח textbook. |
| ➕ **נושאים נוספים** | עזרה ראשונה / מד״א, פסיכולוגיה, פיזיקה (אנרגיה / מרחק בלימה), תנ״ך, ספרות, ערבית | First-aid uses the TTS readout pattern. |

When you build a new app, match an existing subject's language/direction and style so it feels at
home in the hub.

## Step 1 — Deploy the app

The file is fully self-contained, so any of these work:

- **Netlify Drop (no account needed):** open <https://app.netlify.com/drop> and drag the `.html`
  file in. You get a public URL instantly. (Rename the file to `index.html` first if you want a
  clean folder URL.)
- **Double-click / share the file** directly — it runs offline from disk.
- **Add to the hub's own repo** if the hub is deployed from git (drop the file into the hub's
  folder for that subject and commit).

## Step 2 — Link it from the hub

Add a card under the right subject section on the hub page. The hub uses simple linked cards;
a card looks like:

```html
<a class="exam-card" href="https://YOUR-NETLIFY-URL/" target="_blank" rel="noopener">
  <span class="exam-emoji">➗</span>
  <span class="exam-title">שברים — כיתה ח׳</span>
  <span class="exam-desc">תרגול שברים: חיבור, חיסור וצמצום · מטח</span>
</a>
```

Match the existing markup in the hub's `index.html` (class names, emoji, and the date/preview-image
convention the other cards use). If you don't have the hub source at hand, tell the user exactly:
the deployed URL, the subject category it belongs under, the title, and a one-line Hebrew
description — that's everything they need to paste a card in.

## Step 3 — Tell the user what you produced

Hand back:

1. The generated `.html` filename and its `meta.id` (the localStorage namespace).
2. A one-line "ready for Netlify Drop" instruction.
3. The suggested hub category + card snippet above, filled in.
