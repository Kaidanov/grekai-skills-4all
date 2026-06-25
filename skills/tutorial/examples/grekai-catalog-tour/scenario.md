# Tutorial scenario: Browse & install from the GrekAI Skills catalog

- **slug:** `grekai-catalog-tour`
- **goal:** Show a first-time visitor how to find a skill in the GrekAI Skills catalog and copy its one-line install.
- **app route:** `http://localhost:4178/` (serve the repo root: `python -m http.server 4178`)
- **prerequisites:** none — the catalog is static and public.
- **audience:** new user evaluating the catalog.

## Steps

| # | Action (how to drive the UI) | What to show | Why it matters | Narration (spoken) |
|---|------------------------------|--------------|----------------|--------------------|
| 1 | Open `/` | Hero + skill cards | Orientation | "This is GrekAI Skills for All, a free and open catalog of agent skills you can drop straight into Claude Code." |
| 2 | Click the **Skills** category chip | Filtered list | Findability | "Filter by category to find what you need. Everything here is a ready to use, self contained skill." |
| 3 | Focus the **Tutorial** card | The card | Self-reference | "Here is the Tutorial skill. It records narrated walkthroughs of your own app, exactly like the one you are watching now." |
| 4 | Open `/skill.html?id=tutorial` | Detail page | Depth | "Open any skill for its own page: what it does, when to use it, and the full README." |
| 5 | Scroll to the Install panel | The `npx degit` command | The payoff | "Copy the one line install, and the skill lands in your Claude skills folder. Free to use, and open for your contributions." |

## Honesty notes

- The catalog is read from `skills.json` at load time; if you add a skill, its card appears with no build step.
- The README on the detail page is rendered client-side via `marked` from a CDN; offline it falls back to plain text.

## Acceptance criteria

- [ ] **AC1** — `/` loads and renders at least one `.card`.
- [ ] **AC2** — the **Tutorial** skill card is present in the catalog.
- [ ] **AC3** — clicking the **Skills** category keeps the list non-empty.
- [ ] **AC4** — `/skill.html?id=tutorial` opens and the title contains "Tutorial".
- [ ] **AC5** — the install panel shows `npx degit … skills/tutorial`.
- [ ] Narrated MP3s exist for every step and the player advances in sync; captions match the steps.

> These map 1:1 to the `expect()` assertions in [`grekai-catalog-tour.spec.ts`](./grekai-catalog-tour.spec.ts).
