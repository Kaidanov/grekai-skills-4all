# agents

User-authored subagent definitions **not** already covered by the
`dev-rules-and-agents` skill.

| Agent | Source | Purpose |
| --- | --- | --- |
| `qa-testing-agent.md` | a project's `.claude\agents\` | Comprehensive web-app QA: functional + accessibility + Lighthouse + code-quality (God-file/SOLID/`any`/secret scans) with screenshot/video reports. Drives a `qa-agent` Playwright MCP server. Distinct from the example roster's `qa-test-engineer`/`playwright-guardian`. |

## Referenced, not duplicated

The 13-agent example roster (`architect-overwatch`, `backend-dev`, `frontend-dev`,
`devops-engineer`, `qa-test-engineer`, `security-specialist`, `ui-ux-designer`,
`project-orchestrator`, `refactor-test-guardian`, `playwright-guardian`,
`mapper-refactor-test`, `mapper-competitor-ux-research`, `tutorial-test-recording`)
already lives in `skills/dev-rules-and-agents/agents/` in this repo — it is an
**adaptable example roster** (see that skill's README). Use that skill; do not
re-import here.

Per `USAGE.md`, the most-dispatched subagents are typically `Explore` (built-in)
and a project's refactor/test guardians.
