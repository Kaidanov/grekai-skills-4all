---
description: Re-record an existing tutorial and refresh its video + index card.
---

Invoke the **tutorial** skill in **UPDATE** mode.

Tutorial slug: $ARGUMENTS

Follow `SKILL.md` → update: re-run the Playwright spec for this slug, re-render the narrated MP4 +
captions, bump `recordedAt` in the catalog, and rebuild the themeable `index.html`. Show me the
refreshed video before finishing. If the slug is missing, list the available tutorials from the catalog.
