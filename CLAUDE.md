# Project conventions — grekai-skills-4all

## Always merge and deploy (standing rule)
For every change in this repo:
1. Commit with a clear message.
2. Push to the working branch **and** fast-forward `main` to the same commit
   (`git push origin HEAD:main`). Pushing `main` triggers the Vercel auto-deploy.
3. Verify the deployment is green via the Vercel MCP connector
   (`web_fetch_vercel_url` against https://grekai-skills-4all.vercel.app/, and
   `get_deployment` / build logs if a check fails).

Do this automatically — do not ask for confirmation each time.

> Note: this container's network egress blocks Vercel hosts, so direct `vercel`
> CLI calls fail. Deploys happen via the GitHub→Vercel git integration on push to
> `main`; verification/observability go through the Vercel MCP connector (team
> `grekai`, project `grekai-skills-4all`).

## Project shape
- Static, manifest-driven catalog. Root `index.html` reads `skills.json` and renders
  one card per item; categories: `skills` (live), `hooks`, `connectors` (coming soon).
- Add an item: create a folder under `skills/` (copy `skills/_template/`) and add an
  entry to `items` in `skills.json`. No build step.
- Images live in `assets/images/` as committed SVGs; swap to real PNGs by matching the
  base name and flipping the extension in `README.md`.
- `vercel.json` enables clean URLs (no `.html`) and `no-cache` on `skills.json`.
