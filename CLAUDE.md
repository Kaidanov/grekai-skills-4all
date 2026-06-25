# Project conventions — grekai-skills-4all

## Always merge and deploy (standing rule)
`main` is a **protected branch** — no direct pushes. For every change in this repo:
1. Commit with a clear message on a working branch.
2. Push the working branch and open a PR into `main`.
3. Enable auto-merge on the PR (`enable_pr_auto_merge`, squash). Once the Vercel
   status check goes green the PR merges itself; the merge into `main` triggers the
   Vercel production auto-deploy.
4. Verify the deployment is green via the Vercel MCP connector
   (`web_fetch_vercel_url` against https://grekai-skills-4all.vercel.app/, and
   `get_deployment` / build logs if a check fails).

Do this automatically — do not ask for confirmation each time.

> Branch protection on `main`: require a PR before merging and require the Vercel
> status check to pass; do **not** require approving reviews (this is a solo repo, so
> requiring reviews would block auto-merge). Repo setting "Allow auto-merge" must be on.

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
