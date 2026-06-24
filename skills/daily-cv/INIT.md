# daily-cv — INIT (per-person onboarding)

This is the **one-time setup** that makes the skill yours. The goal: produce a complete,
accurate `profile/PROFILE.json` (your single source of truth). After this, every daily run
reuses it. Nothing personal is ever committed — `profile/PROFILE.json` is gitignored.

> **Golden rule:** the assistant **gathers candidate facts from your sources, confirms every
> fact with you, and never fabricates.** Anything it cannot verify is left blank or marked as a
> gap — see the *Anti-Fabrication Rules* in `SKILL.md`. Numbers go only into `key_metrics`,
> which is the ground truth every CV/cover-letter number must trace back to.

## What you end up with

```
profile/PROFILE.json   <- your real, filled profile (gitignored)
```

Start by copying the template:

```powershell
# from skills/daily-cv/
Copy-Item .\profile\PROFILE.template.json .\profile\PROFILE.json
```

Then fill it using any combination of the sources below (automated first, manual fallback).
The assistant should **merge** what it finds, show you a draft, and ask you to confirm or
correct each section before writing `PROFILE.json`.

---

## Source 1 — LinkedIn (fastest for employment history)

Best for: job titles, employers, dates, location, headline, education.

Options, in order of convenience:

1. **Export your data** — LinkedIn → *Settings & Privacy → Data privacy → Get a copy of your
   data → "Profile"*. You receive a CSV/JSON archive. Hand the `Profile.csv` /
   `Positions.csv` / `Education.csv` files to the assistant.
2. **Save to PDF** — on your LinkedIn profile, *More → Save to PDF*. Give the assistant the
   PDF (it reads it like any document).
3. **Paste the public profile** — copy your public profile URL or the visible text and paste
   it into the chat.

The assistant maps these to:
`identity.headline`, `identity.location`, `experience[].{title,company,dates,city,bullets}`,
`education[]`, and seeds `summary` / `competencies`.

> Do **not** paste private connection lists or messages — only your own profile.

---

## Source 2 — Email scan (Gmail MCP)

Best for: recovering employers/titles/dates and skills from CVs you already sent, and finding
recruiter context. Requires the **Gmail MCP** connector to be enabled.

Suggested searches (the assistant runs these with `search_threads`, then `get_thread`):

- `has:attachment (filename:pdf OR filename:docx) (resume OR CV OR "cover letter")` — pull
  prior CV attachments to extract employers / titles / dates / skills.
- `subject:(application OR "thank you for applying" OR interview)` — past applications and the
  roles you targeted.
- `from:(recruiter OR talent OR "no-reply") (role OR position OR opportunity)` — recruiter
  threads that reveal target titles and companies.

The assistant extracts candidate facts, **shows you what it found**, and only writes confirmed
items. It must never invent a number or a title it cannot see in a source.

> Privacy: email contents stay in your session. Extracted facts go only into your local,
> gitignored `PROFILE.json`.

---

## Source 3 — AI chat history (voice + achievements)

Best for: achievements you've described before, and your **writing voice** for the summary and
cover-letter tone.

Sources the assistant can parse if you provide them:

- **ChatGPT export** — *Settings → Data controls → Export data* → `conversations.json`.
- **Claude export** — your account data export.
- **Local Claude Code transcripts** — `~/.claude` (or `%USERPROFILE%\.claude`) session
  transcripts on this machine.

The assistant scans for stated experience, achievements, and metrics, then proposes draft
`summary` and bullet phrasing in *your* voice — but every concrete claim still has to be
confirmed by you and backed by `key_metrics`.

---

## Source 4 — Manual questionnaire (always works, no integrations)

If you have no exports or MCP connectors, answer these and the assistant fills the profile:

**Identity & contact**
- [ ] Exact name as it should appear (and the exact word order).
- [ ] City, country / location line.
- [ ] Email, phone, LinkedIn URL, personal site (optional).
- [ ] Any clearance to mention, stated accurately (active vs. historical), or leave blank.
- [ ] One-line headline (e.g. "VP Engineering | SaaS Platform Leader").

**Experience** (repeat per role, most recent first)
- [ ] Title, company, dates (Mon YYYY - Present/YYYY), city.
- [ ] 2-4 achievement bullets with concrete, verifiable outcomes.

**Education / earlier career / volunteering**
- [ ] Degrees: name, institution, dates, optional note.
- [ ] One-liners for older roles.
- [ ] Volunteering / community lines.

**Ground-truth numbers (key_metrics)**
- [ ] Every metric you want usable in a CV: `metric`, `value`, `context`.
  *(If it isn't here, the assistant won't use it.)*

**Targets**
- [ ] Default target company/role and output folder (`target_defaults`).

---

## Finish the init

1. Assistant assembles a draft `PROFILE.json` from the sources above.
2. **You confirm each section** (the assistant reads it back; you correct anything wrong).
3. Assistant writes `profile/PROFILE.json` (gitignored — never committed).
4. Smoke-test the generators:

   ```powershell
   # from skills/daily-cv/scripts/
   python generate_cv.py  --company Acme --role "VP Engineering" --run-date 20260101 --output-dir ./out
   python generate_pdf.py --company Acme --role "VP Engineering" --run-date 20260101 --output-dir ./out
   ```

   No "Jane Doe" fallback warning means your `PROFILE.json` loaded correctly.

5. Configure sources/criteria/watchlist in `config/` (see `README.md` → How-To), then run the
   skill via `SKILL.md`.

See **[profile/README.md](profile/README.md)** for the profile model and loader order, and
**[SKILL.md](SKILL.md)** for the Anti-Fabrication Rules that govern every extraction.
