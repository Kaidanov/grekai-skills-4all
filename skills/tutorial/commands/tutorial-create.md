---
description: Draft & approve a tutorial scenario, record it with Playwright, render narrated video, and publish.
---

Invoke the **tutorial** skill in **CREATE** mode.

Scenario request: $ARGUMENTS

Follow `SKILL.md` exactly:
1. Draft a scenario from the request into the configured `scenariosDir`.
2. ⛔ Get my approval of the scenario **before** recording.
3. Generate/record the Playwright spec, then render the narrated MP4 + captions.
4. ⛔ Show me the output and get approval; fix issues in a loop.
5. Update the catalog and regenerate the themeable tutorials `index.html`.

Honor done = proven — show the real rendered video/screenshot, never claim success without the artifact.
