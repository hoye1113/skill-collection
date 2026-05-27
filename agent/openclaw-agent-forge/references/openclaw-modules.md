# OpenClaw Module Quick Reference

Use this reference when making promotion decisions or writing capability boundaries. It maps OpenClaw source modules to agent-relevant capability types.

## Plugin-Level Change Signals

If the user's request involves modifying or extending these modules, strongly consider a **plugin** rather than an agent workspace:

| Module Path | Change Type | Why |
|-------------|-------------|-----|
| `src/channels/` | New messaging channel | Channel implementations are behind the plugin boundary |
| `src/plugins/` | New host tool/provider | Plugin discovery, manifests, registry, loaders |
| `src/plugin-sdk/` | New SDK surface | Contracts exported to extensions |
| `extensions/` | New bundled extension | Workspace packages for channels, providers, tools |

> Rule: If the requirement changes the host capability surface (new tools, new providers, new channels), it is a plugin candidate. If it only changes workspace prompts and files, it is an agent concern.

## Native / Conditional Capability Modules

| Module Path | Capability Type | Notes |
|-------------|-----------------|-------|
| `src/web-fetch/` | Native-like | OpenClaw built-in fetch; preferred for known URLs |
| `src/web-search/` | Conditional | Depends on external search provider configuration |
| `src/mcp/` | Conditional | Requires MCP server setup |
| `src/browser/` | Conditional | Requires browser extension; fallback only |
| `src/media/` / `src/media-understanding/` | Conditional | Vision model / media pipeline dependencies |
| `src/gateway/` | Runtime | Gateway server, protocol, sessions; not agent-writable |

## Agent Runtime Modules

| Module Path | Relevant Capability |
|-------------|---------------------|
| `src/agents/` | Agent loop, tool use, model selection |
| `src/agents/tools/` | Tool availability and usage patterns |
| `src/sessions/` | Session store, compaction behavior |
| `src/cron/` | Scheduled jobs (no bootstrap injection) |
| `src/context-engine/` | Context assembly |
| `src/trajectory/` | Disk logs, export, redaction |

## User Runtime Data

| Location | OS | Purpose |
|----------|-----|---------|
| `~/.openclaw/` | macOS / Linux | Config, workspace, skills |
| `%USERPROFILE%\.openclaw\` | Windows | Same layout as Unix |

Agent workspaces live under `~/.openclaw/workspace/` (or `%USERPROFILE%\.openclaw\workspace\`).

## Reference Architecture

For deeper architecture docs, see:
- `docs/concepts/architecture.md` — Gateway + clients overview
- `docs/plugins/architecture.md` — Plugins overview
- `docs/gateway/protocol.md` — Gateway protocol

## How to Use This Reference

1. **Promotion Decision**: If the brief mentions `src/channels/`, `extensions/`, or `src/plugins/`, check the plugin column first
2. **Capability Boundaries**: If the agent claims web capabilities, use this table to classify them correctly (native vs conditional)
3. **Resume Design**: If designing session recovery, understand which modules handle compaction (`src/sessions/`)
