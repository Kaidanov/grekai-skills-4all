---
name: token-audit
description: Audit the active agent/Claude Code setup for token waste and produce a prioritized, quality-preserving reduction plan. Inventories and estimates the per-session token cost of CLAUDE.md files, MCP servers, hooks (especially SessionStart context injectors), skills, agents, plugins, and the memory index, then ranks the biggest sinks and proposes safe cuts. Use when the user types /token-audit or asks to "reduce token usage", "optimize context", "what can I trim/cut/disable", "why is my context so big", "token diet", "minimize tokens but keep quality", or to review skills/hooks/MCPs for cost.
---

# /token-audit — Cut token cost, keep quality

Goal: find what silently consumes context **every session** and recommend the smallest set of cuts that reclaim the most tokens with the least quality loss. Report only what is measurable; never fabricate token counts. **Read-only by default — propose, don't change.** Apply changes only when the user approves (or passes `--apply`), and never delete/disable anything without confirmation.

## Mental model — where per-session tokens go
Everything below loads into context at session start or every turn, before the user even speaks:
1. **MCP servers (usually the #1 sink).** Each *eagerly-loaded* server injects ALL its tool schemas. Locally-configured servers (`.mcp.json`, tool-specific paths like `.ai/mcp.json`, global config) are typically eager. Connectors and tools behind on-demand search/`ToolSearch` are **deferred** (cheap — name only until fetched) — don't flag those.
2. **SessionStart hooks that inject static context.** A hook that prints a large knowledge block (a platform "knowledge update", a long orientation dump) costs that many tokens *every* session. Big, easy win when the project doesn't use that platform.
3. **CLAUDE.md / AGENTS.md chain.** Global + workspace + project files all load every session. The global one is meant to stay lean.
4. **Skills & plugins.** Every skill's `name`+`description` loads into context (the body is lazy). Many installed skills = a long always-on list. Whole plugins pull in their skills + agents + MCPs.
5. **Agents.** Agent definitions (name + description) load so they can be dispatched.
6. **Memory.** The memory index (e.g. `MEMORY.md`) loads every session; recalled memory bodies add up per turn.
7. **The transcript itself.** Long/old sessions are the single biggest sink — flag this if relevant.

## Procedure

### 1. Inventory (read-only, fast)
Locate and size each source. Use `wc -c` / file size; estimate **tokens ≈ bytes ÷ 4**. Don't load giant data files — sizes only.
- **CLAUDE.md chain**: `~/.claude/CLAUDE.md`, each parent-dir `CLAUDE.md` up from the project, the project root `CLAUDE.md` (and any `AGENTS.md`). Record bytes each.
- **MCP servers**: parse the global config (`~/.claude.json` / `~/.claude/settings.json`) and project `.mcp.json` (or tool-specific paths). List each server, mark **eager vs deferred**, and (if discoverable) tool count. Eager + unused-in-this-project = prime cut.
- **Hooks**: global + project `settings.json`/`settings.local.json`. Flag every `SessionStart`/`UserPromptSubmit` hook and estimate its injected output size (check the script, or session-start output already in the transcript). Static knowledge dumps for unused platforms are top targets.
- **Skills**: count `~/.claude/skills/*/SKILL.md`, project `.claude/skills/*/SKILL.md`, and plugin skills. Sum description bytes. Flag rarely/never-used ones.
- **Agents**: count global + project agent dirs. Sum sizes.
- **Plugins**: list enabled plugins; note each pulls skills/agents/MCPs.
- **Memory**: index byte size + memory-file count; flag stale/duplicate entries.

### 2. Rank
One table sorted by estimated per-session cost, biggest first:

| Source | Item | ~Tokens/session (est) | Eager? | Used in this project? | Quality risk if cut | Recommended action |
|--------|------|----------------------:|--------|-----------------------|---------------------|--------------------|

Mark token numbers `(est)` — the bytes÷4 heuristic. The harness does not expose true per-source token counts; never present estimates as exact.

### 3. Recommend (quality-preserving, ordered by ROI)
Lead with **Top 3 quick wins** (biggest reclaim, lowest risk), then the full list. Typical moves, in rough ROI order:
- **Disable/uninstall eager MCP servers not used here**, or switch them to on-demand. Almost always the largest win.
- **Gate or trim large SessionStart hook injections** — make a platform/orientation dump fire only in repos that use it, or drop it. Quote the tokens/session reclaimed.
- **Uninstall or defer rarely-used skills/plugins** so their descriptions leave the always-on list.
- **Trim the CLAUDE.md chain** — dedup overlap across global/workspace/project; keep global lean; move long explanations into linked `.md` files.
- **Archive stale/duplicate memories** and tighten the memory index lines.
- **Behavioral, not config**: delegate broad search to subagents (return conclusions, not file dumps); reuse cached context; **start a fresh session for long transcripts** — and name what the new session should pick up.

### 4. Output
- The Top-3 quick wins with concrete commands/edits and est tokens reclaimed each.
- The full ranked table.
- A one-line **estimated total reclaim/session** vs current baseline.
- Then **ask before applying** anything. On approval (or `--apply`): make small, reversible config changes; never hard-delete user content — disable or move to an archive/backup first; show exactly what changed.

## Notes
- Estimates only — be explicit they are bytes÷4 heuristics, useful for *ranking*, not billing.
- Don't recommend cutting something genuinely in use just because it's big — note the quality risk and let the user decide.
- Pairs with the `tldr` skill (which reports actual spend per turn) — this skill targets the always-on baseline; `/tldr` targets the per-turn flow.
