# Compaction and Recovery

Use this reference when designing which rules must survive session compaction and how to structure `AGENTS.md` for long-session resilience.

## Platform Fact: Compaction Behavior

OpenClaw automatically compacts long sessions. After compaction:

- **`AGENTS.md` sections named `Session Startup` and `Red Lines` are re-injected** (up to ~3000 characters)
- Older fallback names: `Every Session` → `Session Startup`, `Safety` → `Red Lines`
- A `<workspace-critical-rules>` tag is also injected (up to ~2000 characters)
- **Other sections (`Workspace Layout`, `TOOLS.md` content, `Resume Strategy`) are NOT automatically re-injected**

## Design Consequence

If losing a rule after compaction would cause:
- Wrong routing
- Wrong deliverables
- Destructive behavior
- Security boundary violations

→ That rule **must** live in `Session Startup` or `Red Lines`.

## What Belongs Where

| Section | Purpose | Compaction Safe? |
|---------|---------|------------------|
| `Session Startup` | What to read first, boot order, host assumptions | Yes (re-injected) |
| `Red Lines` | Hard boundaries, never-do rules, safety constraints | Yes (re-injected) |
| `Resume Strategy` | How to continue existing work | No |
| `Workspace Layout` | Directory semantics | No |
| `Boundaries` | General boundaries (may reference SOUL.md) | No |

## Three Rule Layers

When writing any platform claim, you must distinguish:

| Layer | Meaning | Write As |
|-------|---------|----------|
| **Source Fact** | Guaranteed by OpenClaw source code | "The platform will..." |
| **Template Default** | Recommended by `workspace-template` | "The default template suggests..." |
| **Design Choice** | Chosen for this specific agent | "This agent uses..." |

Never write template defaults or design choices as if they were guaranteed platform facts.

## Common Mistakes

- Putting compaction-critical rules in `Workspace Layout` or `Boundaries` instead of `Session Startup`/`Red Lines`
- Treating `memory/YYYY-MM-DD.md` as automatically injected (it is not; must be explicitly read)
- Writing "OpenClaw automatically resumes from state files" (resume strategy is a design choice, not platform magic)

## Checklist

Before finalizing an agent design:

- [ ] All rules that must survive compaction are in `Session Startup` or `Red Lines`
- [ ] Source facts are separated from template defaults and design choices
- [ ] No platform claim is made without identifying which layer it belongs to
