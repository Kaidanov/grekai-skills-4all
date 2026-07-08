---
name: exam-creator
description: >
  Generate single-file, self-contained HTML exam / study / quiz apps for kids and general
  study — gamified (XP, levels, badges), with localStorage progress, immediate feedback, and
  optional Hebrew TTS. USE THIS whenever the user wants to "create an exam app", "build a study
  app", "make a quiz", "build a practice app", asks for a "מבחן", "תרגול", "בוחן", "אפליקציית
  לימוד", "exam for grade X / לכיתה X", or names a subject to study — math / מתמטיקה, chemistry /
  כימיה, physics / פיזיקה, biology, first aid / עזרה ראשונה / מד״א, history / היסטוריה /
  השכלה / נאורות, English / אנגלית vocab or tenses, Bible / תנ״ך, literature / ספרות, Arabic,
  psychology / פסיכולוגיה — or says "add it to the exam hub". Triggers even on casual / partial
  requests like "quiz my kid on grade 8 math" or "תכין לי תרגול לכימיה". Output is one HTML file
  that runs offline by double-click or Netlify Drop, Hebrew RTL by default (other languages / LTR
  supported), mobile-first and accessible. Never fabricates graded answers without flagging them.
---

# exam-creator — single-file gamified exam & study apps

Turn a subject + grade level into a **single self-contained HTML file** the user's kids can open
by double-clicking or by dropping on [Netlify Drop](https://app.netlify.com/drop). It is the
packaged version of the one-off exam apps already in the hub
([exam-hub-grekai.netlify.app](https://exam-hub-grekai.netlify.app/)) — Hebrew math (grades 8–9),
grade-8 chemistry/מדע on the מטח textbook, physics (energy / braking distance), MDA first-aid,
Enlightenment history, English vocab & tenses, psychology, Bible, literature, Arabic.

Every app this skill produces obeys the **hard requirements** below. Don't relax them.

## Hard requirements (every output)

- **Single file, zero dependencies.** All CSS + JS inline. **No CDN, no MathJax/KaTeX, no build
  step, no network.** Runs by double-click or Netlify Drop, fully offline.
- **Hebrew RTL by default** (`dir="rtl" lang="he"`); switch to LTR / other languages when the
  subject calls for it (e.g. English vocab) via `meta.lang` / `meta.dir`.
- **Gamification:** XP points, levels (100 XP each), and badges for milestones. Progress is
  always visible (sticky XP bar + level + streak).
- **localStorage persistence:** XP, badges, answers, best score, and "continue where I left off"
  all survive refresh. Keys are namespaced `examcreator:<meta.id>` so multiple apps never collide.
- **Four question types:** multiple choice, true/false, numeric (with tolerance), short fill-in.
  Per-question immediate feedback + explanation; end-of-exam score summary + answer review.
- **Mobile-first, accessible:** large tap targets (≥48px), readable contrast, light/dark, keyboard
  navigable (number keys pick choices, Enter advances), works offline.
- **Formulas without libraries:** sub/superscripts, fractions, √ via inline HTML/CSS/unicode (see
  the `.frac` / `sub` / `sup` / `.sqrt` helpers in the template). Never pull MathJax/KaTeX.
- **Optional Hebrew TTS:** browser `SpeechSynthesis`, prefers a Hebrew voice, reads `tts` text
  with nikud when supplied. **Degrades silently** — the read button only shows if a matching voice
  exists; TTS failure never blocks the app. (Mirrors the MDA first-aid pattern.)

The bundled **[`references/template.html`](references/template.html)** already implements all of
the above. Generating an app = filling in one `EXAM` object; never re-author the engine.

## Anti-fabrication rule (read before generating questions)

This produces **graded academic content**. Wrong answer keys teach kids wrong facts.

1. **If the user supplies source material** (textbook pages, מטח chapter, notes, a PDF, a topic
   list with facts) — draw questions and answers **only** from it. Quote/paraphrase faithfully.
2. **If you must generate questions yourself** — keep them to standard, verifiable curriculum
   facts, and set `meta.generatedNote` to a Hebrew/English flag (e.g. "שאלות שנוצרו אוטומטית —
   ההורה מתבקש לאמת לפני שימוש"). The app shows this banner on the first question.
3. **Never invent** dates, formulas, dosages (first-aid!), citations, or numeric answers you are
   not sure of. When unsure, ask the user or mark the item for review — do not bluff.
4. **Answer keys must be internally consistent:** the `answer` must actually be among `choices`
   (for MC), the explanation must match the keyed answer, numeric `tolerance` must be sane.
   Sanity-check every key before delivering.

## Workflow

### 1 — Gather the spec
Ask only for what's missing (infer sensible defaults; keep it short):

- **Subject** (math, chemistry, physics, first-aid, history, English, psychology, …)
- **Grade level / audience** (e.g. כיתה ח׳, adult study)
- **Language & direction** (Hebrew RTL default; English/LTR for vocab, etc.)
- **Topics** to cover (a list, or "everything in chapter X")
- **Source material** — textbook (e.g. מטח), pasted notes, a file? *(decides fabrication path)*
- **Number of questions** (default ~10) and **question mix** (MC / TF / numeric / fill)
- **App title** and a short subtitle

### 2 — Generate the question set
Follow the **anti-fabrication rule**. Produce questions as `EXAM.questions` entries matching
**[`references/question-schema.md`](references/question-schema.md)**. Pick the type that fits each
fact: numeric for calculations (with a tolerance), fill for terms/vocab, TF for misconceptions, MC
for the rest. Add a one-line `explanation` to every question. For Hebrew readout add `tts` with
nikud. For formulas use the inline helpers, not a library.

### 3 — Build the single file
Copy `references/template.html`, replace **only** the `EXAM` object (`meta` + `questions`), and
leave the engine untouched. Set a **unique `meta.id`** (e.g. `math8-fractions-he`) so localStorage
won't collide with the user's other apps. Save as `<meta.id>.html` (or a name the user gives).

### 4 — Validate before delivering
- Confirm every `answer` is consistent (in-range MC index, explanation matches the key).
- Open it / sanity-check (in this repo: a quick Chromium/Playwright run answering each question and
  checking score + persistence — see how the sample was validated). At minimum, eyeball the
  rendered questions and re-check the keys.
- Deliver the file ready for **Netlify Drop**.

### 5 — Register on the exam hub
Tell the user how to add the new app to **exam-hub-grekai.netlify.app** — see
**[`references/exam-hub.md`](references/exam-hub.md)** for the card snippet and the subject
categories already in the hub.

## Quick reference — the `EXAM` object

```js
const EXAM = {
  meta: {
    id: "math8-fractions-he",   // unique → localStorage namespace
    title: "שברים — כיתה ח׳",
    subtitle: "מתמטיקה · תרגול",
    lang: "he", dir: "rtl",
    passingScore: 60,
    shuffleQuestions: false, shuffleChoices: false,
    tts: true,
    generatedNote: ""           // set a flag string if questions were AI-generated
  },
  questions: [ /* see references/question-schema.md */ ]
};
```

Full field list, every question type, tolerance, fill-in synonyms, and formula examples are in
**[`references/question-schema.md`](references/question-schema.md)**.

## Files

- `references/template.html` — the complete single-file engine (XP/levels/badges, localStorage,
  TTS fallback, all 4 question types, formula CSS, sample questions). **Edit only the `EXAM` object.**
- `references/question-schema.md` — the question structure the generator fills in.
- `references/exam-hub.md` — the hub's subjects + how to register a new app.
- `examples/grade8-math-he.html` — a validated 5-question grade-8 Hebrew math sample built from the template.
