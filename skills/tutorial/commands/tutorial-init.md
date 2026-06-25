---
description: Interactive setup — ask a few questions, then write tutorial.config.json and scaffold folders.
---

Invoke the **tutorial** skill in **INIT** mode.

Before doing anything else, **ask me these questions** (use the AskUserQuestion tool, in one batch):

1. **App** — product name + the base URL where the dev server runs (e.g. `http://127.0.0.1:5173`), and the dev command (e.g. `npm run dev`).
2. **Brand** — logo path (served by the app, e.g. `/logo.svg`), accent color, and default theme (dark or light).
3. **Narration** — voice (default `en-US-JennyNeural`) and the output folder for tutorials (default `public/tutorials`).
4. **First tutorial** — a one-line goal for the first walkthrough (or "skip" to only set up).

Then:
- Copy `config.example.json` → `tutorial.config.json` at the project root and fill it from my answers.
- Create the `scenariosDir` and `outputDir` folders.
- Confirm what was written.
- If I gave a first-tutorial goal, continue into **CREATE** mode and draft that scenario for my approval.

⛔ Never record anything until I approve a scenario.
