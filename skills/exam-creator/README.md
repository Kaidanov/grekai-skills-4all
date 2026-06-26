# exam-creator — single-file gamified exam & study apps

Generate **one self-contained HTML file** that turns a subject + grade level into a playable,
gamified study/exam app for kids (or anyone). It runs by **double-clicking the file** or by dropping
it on [Netlify Drop](https://app.netlify.com/drop) — **no CDN, no build step, no network**. This is
the reusable, packaged version of the one-off exam apps in
[exam-hub-grekai.netlify.app](https://exam-hub-grekai.netlify.app/) (Hebrew math, grade-8
chemistry/מדע on the מטח textbook, physics, MDA first-aid, Enlightenment history, English vocab &
tenses, psychology, Bible, literature, Arabic).

## What every generated app includes

- **Single file, zero dependencies** — all CSS + JS inline, fully offline.
- **Hebrew RTL by default**, with LTR / other languages when the subject needs it (English vocab).
- **Gamification** — XP, levels (100 XP each), and milestone badges, with a visible progress bar + streak.
- **localStorage persistence** — XP, badges, best score, and *continue-where-you-left-off* survive
  refresh; keys namespaced `examcreator:<id>` so apps never collide.
- **Four question types** — multiple choice, true/false, numeric (with tolerance), short fill-in —
  with immediate per-question feedback + explanation, a score summary, and an answer-review screen.
- **Mobile-first & accessible** — ≥48px tap targets, light/dark, good contrast, keyboard nav
  (number keys pick choices, Enter advances).
- **Formulas without libraries** — sub/superscripts, fractions and √ via inline HTML/CSS/unicode
  (no MathJax/KaTeX).
- **Optional Hebrew TTS** — `SpeechSynthesis` reads questions (with nikud) and **degrades silently**
  if no Hebrew voice is present.

## How it works

Generation = fill in one `EXAM` object (meta + questions) inside
[`references/template.html`](references/template.html); the XP/badge/persistence/TTS engine is
generic and stays untouched. The full field reference is in
[`references/question-schema.md`](references/question-schema.md).

## Use it

Just ask your assistant — in Hebrew or English:

- "create a grade-8 Hebrew math exam app on fractions"
- "תכין לי תרגול בכימיה לכיתה ח׳ על אטומים ומולקולות מהספר של מטח"
- "make an English tenses quiz for my kid"
- "build a first-aid study app with read-aloud"

The skill gathers the spec (subject, grade, language, topics, **source material**, question count
& mix), generates the questions (using your source material when provided, and **flagging
AI-generated content for review** otherwise), builds the single HTML file, and tells you how to
deploy it and add it to the exam hub.

## Install

```bash
npx degit Kaidanov/grekai-skills-4all/skills/exam-creator .claude/skills/exam-creator
```

No `npx`? Use git sparse-checkout:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/Kaidanov/grekai-skills-4all.git
cd grekai-skills-4all && git sparse-checkout set skills/exam-creator
cp -r skills/exam-creator <your-project>/.claude/skills/exam-creator
```

No dependencies to install — the generated apps are plain HTML.

## Files

- `SKILL.md` — the workflow (read this to run the skill).
- `references/template.html` — the complete single-file engine; edit only the `EXAM` object.
- `references/question-schema.md` — every question type and field.
- `references/exam-hub.md` — the hub's subjects + how to register a new app.
- `examples/grade8-math-he.html` — a validated 5-question grade-8 Hebrew math sample.

## Anti-fabrication

This builds **graded academic content**. The skill uses your supplied source material verbatim
where available, never invents facts/dates/dosages it isn't sure of, flags AI-generated question
sets with an on-screen review banner, and keeps answer keys internally consistent. First-aid,
chemistry and physics keys especially must be verified before kids use them.
