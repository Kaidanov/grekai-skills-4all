# Skills

Each skill lives in its own folder under `skills/`.

## Add a new skill

1. Copy `skills/_template/` to `skills/<your-skill-id>/`.
2. Edit `skill.json` (id, title, description, tags, links).
3. Add a `README.md` documenting how to use it.
4. Register it: add an entry to the `items` array in the root [`skills.json`](../skills.json).

That's it — the dashboard at the site root reads `skills.json` and renders the card automatically. No build step.

## Entry shape

| Field | Required | Notes |
|-------|----------|-------|
| `id` | yes | Unique, kebab-case. |
| `category` | yes | One of the ids in `categories` (`skills`, `hooks`, `connectors`). |
| `title` | yes | Display name. |
| `description` | yes | 1–2 sentences. |
| `tags` | no | Array of strings, shown as chips. |
| `status` | no | `live`, `draft`, etc. |
| `links` | no | Map of label → URL (relative or absolute). |
