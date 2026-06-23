# Agents

Canonical subagent definitions (one source → all tools). Each file uses Claude-style frontmatter
(the richest format, so it down-converts cleanly to Copilot `.agent.md` and others):

```markdown
---
name: refactor-test-guardian
description: When to use this agent (drives auto-routing).
tools: Read, Edit, Grep, Bash        # optional
model: sonnet                        # optional
---

System prompt / behavior for the agent goes here.
```

> **Heads-up — this is an ADAPTABLE EXAMPLE roster, specialized for one product.** The descriptions and
> system prompts name a concrete product (a Vite/React + .NET XSLT data-mapping tool, here called
> "MyApp"). They are included as a real, working reference roster — not a fixed standard. To reuse them
> on another project, keep the structure and methodology and swap the product-specific nouns (paths,
> stack, domain). The methodology in `../rules/` is already generic. No secrets or internal hosts appear
> in any agent file.

## How to use an agent in each environment
| Environment | Agents live in | Invoke it by |
|-------------|----------------|--------------|
| **Claude Code** | `.claude/agents/*.md` | Auto-routing on the agent's `description`, or explicitly via the Agent/Task tool (`subagent_type: <name>`). In chat: *"use the `backend-dev` agent to …"*. |
| **GitHub Copilot** (VS Code) | `.github/agents/*.agent.md` | Mention it in Copilot Chat — `@<Display Name>` — or pick it from the agent dropdown. |
| **Cursor** | — (no per-agent file) | Cursor runs on `.cursor/rules` + MCP. Reference the agent file in your prompt to get the same behavior. |

To wire these into a project, copy the relevant `*.md` files into that project's `.claude/agents/`
(verbatim) and, for Copilot, transform the frontmatter into `.github/agents/<name>.agent.md`.

## Roster (13)
| Agent | Use it for |
|-------|-----------|
| `mapper-refactor-test` | **primary router** for implementation + proof |
| `architect-overwatch` | cross-system design review, module boundaries, data flow |
| `backend-dev` | .NET API — endpoints, persistence, validation |
| `frontend-dev` | Vite React client — canvas, dialogs, hooks/state |
| `ui-ux-designer` | UI usability, design-system consistency, a11y |
| `refactor-test-guardian` | minimal refactors + targeted test proof |
| `qa-test-engineer` | xUnit / Vitest / Playwright validation strategy |
| `playwright-guardian` | browser tests + narrated video + step screenshots |
| `tutorial-test-recording` | deep narrated walkthroughs / training artifacts |
| `devops-engineer` | CI/CD, IIS deploy, legacy bridge hosting, monitoring |
| `security-specialist` | secrets, input validation, secure coding, audits |
| `mapper-competitor-ux-research` | Altova/MapForce UX benchmark, design-drift briefs |
| `project-orchestrator` | coordinate the agent set across a multi-step task |

See `ARCHITECTURE_AND_STANDARDS.md` for routing order, activation rules, agentic loops, autonomous-work
standards, token-usage standards, and the pruning standard for retiring agents.
