# MCP server inventory (sanitized)

A distilled inventory of the MCP servers this toolkit configures, taken from a
canonical "edit once, sync to every tool" list (e.g. an `.ai/mcp.json`) plus the
Claude Desktop config. **All secrets are placeholders** — set each `${env:NAME}`
as a Windows User environment variable before launching; never hardcode a value.

> The server names, database names, and host placeholders below are **examples**.
> Replace them with your own. The point is the *shape* — generic transports,
> env-var-only secrets, read-only DB access — not these specific entries.

## Servers (example shape)

| Name | Transport / command | Purpose | Env vars needed |
| --- | --- | --- | --- |
| `sequential_thinking` | `npx @modelcontextprotocol/server-sequential-thinking` | Step-by-step reasoning scratchpad. | — |
| `memory` | `npx @modelcontextprotocol/server-memory` | Generic key/value memory. | — |
| `knowledge-graph` | `npx mcp-knowledge-graph --memory-path <repo>\.aim` | Project knowledge graph (entities/relations/observations). | — (path arg) |
| `filesystem` | `npx @modelcontextprotocol/server-filesystem <roots…>` | Scoped FS access to your source roots. | — (path args) |
| `context7` | http `https://mcp.context7.com/mcp` | Up-to-date library/docs lookup. | — |
| `nx-mcp` | http `http://localhost:9523/mcp` | Nx monorepo introspection (local). | — |
| `github-mcp` | http `https://api.githubcopilot.com/mcp` | GitHub via Copilot MCP. | (GitHub auth via host) |
| `playwright` | `npx @playwright/mcp@latest` | Browser automation / screenshots. | — |
| `db_local_a` | stdio `node …\MssqlMcp\Node\dist\index.js` | Read-only MSSQL: a local database. | `LOCAL_SQL_USER`, `LOCAL_SQL_PASSWORD` |
| `db_local_b` | stdio (same node MSSQL server) | Read-only MSSQL: another local database. | `LOCAL_SQL_USER`, `LOCAL_SQL_PASSWORD` |
| `db_remote_a` | stdio (same) | Read-only MSSQL: a remote database. | `REMOTE_SQL_HOST`, `REMOTE_SQL_USER`, `REMOTE_SQL_PASSWORD` |
| `db_remote_b` | stdio (same) | Read-only MSSQL: another remote database. | `REMOTE_SQL_HOST`, `REMOTE_SQL_USER`, `REMOTE_SQL_PASSWORD` |

All MSSQL servers run the same Node MSSQL MCP binary (e.g.
`<repo>\MssqlMcp\Node\dist\index.js`) with `READONLY=true` and
`TRUST_SERVER_CERTIFICATE=true`; only the connection env vars differ per
database. Keep DB MCP access read-only.

## Notes

- Keep the source list (e.g. `.ai/mcp.json`) **secret-clean** — env-var
  placeholders only. A single `sync` step can then push that one list to every
  tool's config.
- The Claude **Desktop** config (`%APPDATA%\Claude\claude_desktop_config.json`)
  may define no MCP servers at all — only UI preferences and trusted-folder
  paths. If so, there is nothing secret to import from it.
- **Never commit real values** behind `LOCAL_SQL_*`, `REMOTE_SQL_*`, host IPs,
  or DB names. If a host/password ever appears in a `settings.json` allow-list
  entry, do **not** copy that entry into a shared/public repo — recreate the
  permission locally instead.

## The real, filled config stays local

This file is a **public, sanitized template**. Your machine's actual MCP config
(real server names, database names, host IPs, and the env-var *values*) is
private — keep it out of any committed/public repo. Reconstruct servers from
this template and set every `${env:NAME}` locally.
