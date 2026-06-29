# Skills

Each skill lives in its own folder under `skills/`.

## Add a new skill

1. Copy `skills/_template/` to `skills/<your-skill-id>/`.
2. Edit `skill.json` (id, title, description, tags, links).
3. Add a `README.md` documenting how to use it.
4. Register it: add an entry to the `items` array in the root [`skills.json`](../skills.json).

That's it — the dashboard at the site root reads `skills.json` and renders the card automatically. No build step.

## Installing a skill into Claude Code

Each skill's `install` command uses [`degit`](https://github.com/Rich-Harris/degit)
to copy the folder into a `.claude/skills/<name>/` directory, where Claude Code
discovers it from its `SKILL.md`.

- **Personal / global (all projects):** give an **absolute** destination —
  `~/.claude/skills/<name>` (macOS/Linux) or
  `"%USERPROFILE%\.claude\skills\<name>"` (Windows). A *relative* `.claude/...`
  path installs into the current folder, so a global folder can stay empty.
- **Project (one repo):** run the relative command from the project root.
- **Restart Claude Code** if `.claude/skills/` did not exist when the session
  started (existing skill folders update live; a new top-level one needs a
  restart). Then invoke with `/<name>` or just ask for it.

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
