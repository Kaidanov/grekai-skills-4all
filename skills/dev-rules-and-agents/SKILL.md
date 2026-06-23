---
name: dev-rules-and-agents
description: Portable engineering rules (coding, refactoring, working-style) plus a reusable 13-agent roster. Use when bootstrapping a project's CLAUDE.md / AGENTS.md / .cursor rules, or when you need a ready set of specialist subagents and a routing standard.
---

# Dev Rules & Agents

A self-contained, portable bundle of **general engineering rules** and a **reusable agent roster**,
extracted from a real production project (a Vite/React + .NET data-mapping tool) so they can be
dropped into any codebase. The agent roster is an **adaptable example** — see below.

## When to use
- Bootstrapping a new repo's `CLAUDE.md` / `AGENTS.md` / `.cursor/rules` from a known-good baseline.
- Standing up a set of specialist subagents (frontend, backend, refactor, qa, playwright, devops,
  security, ux, architecture, orchestration) plus a routing/activation standard.
- Aligning a refactor session to a durable, behavior-preserving dedup methodology.

## What's inside
```text
skills/dev-rules-and-agents/
  SKILL.md                    # this file
  README.md                   # overview + install
  rules/
    coding-rules.md           # general, project-agnostic coding rules
    refactoring-rules.md      # behavior-preserving dedup/consolidation methodology
    working-style.md          # session hygiene: done=proven, token economy, handoffs, commits
  agents/
    README.md                 # roster + how to use in Claude / Copilot / Cursor
    ARCHITECTURE_AND_STANDARDS.md   # routing order, activation, loops, token & pruning standards
    <13 agent definitions>.md       # Claude-style frontmatter, down-converts to other tools
```

## How an assistant should apply this
1. **Rules first.** Read `rules/coding-rules.md` and `rules/working-style.md` before editing; read
   `rules/refactoring-rules.md` before any dedup/consolidation work. Treat them as overriding defaults.
2. **Agents on demand.** Pick one primary agent from `agents/README.md`; only add a specialist after a
   real boundary is proven. Follow `agents/ARCHITECTURE_AND_STANDARDS.md` for routing order.
3. **Adapt the nouns.** The rules are generic; the agents are an **example roster** specialized for one
   product (a Vite/React + .NET XSLT data-mapping tool) — keep their structure and swap product-specific
   paths/stack/domain when reusing on another project.

## Install into a target project
```powershell
# Rules → fold the relevant lines into the project's CLAUDE.md / AGENTS.md, or reference this folder.
# Agents (Claude Code):
Copy-Item .\skills\dev-rules-and-agents\agents\*.md <target-repo>\.claude\agents\
# Agents (GitHub Copilot): transform each frontmatter into <name>.agent.md under .github/agents\
```
