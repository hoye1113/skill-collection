# Agent Writes and Runtime State

Generic rules for OpenClaw / FlowyClaw workspaces. Load when designing or reviewing **tool-write discipline**, **runtime state files**, or **preview vs shipped runtime parity**.

Host-agnostic: no repository-layout specifics unless your workspace explicitly adopts them.

## Tool Writes

- Every **Write**-style tool invocation must include **both** a workspace-relative **path** and **complete body content**. Half-steps ("content only") fail hosts predictably.
- Prefer **small, targeted edits** (patch/replace flows) over replacing entire large artifacts when possible.
- Large payloads: some environments enforce strict **single-call size limits** (often tighter on Windows-class hosts). If generation truncates mid-file, switch strategy:

```text
Localized edit   → incremental patch
Medium rebuild   → skeleton first, then chunked edits
Very large dump   → stdin pipe or tiny helper script that writes from disk buffer — not a mega Write
```

- Never treat **runtime state** files as a bypass for "avoid writing canonical files": state stays **small and structured**.

## Read-Before-Write

Every edit or write operation must be preceded by a read of the target file.

Rules:

- Before calling any **Write** or **Edit** tool, the agent must have a current copy of the file in context.
- If the file was read earlier in the session, verify freshness before editing:
  - Re-read if the file may have changed since the last read.
  - If the file is large, read the specific section or line range that will be edited.
- Do not assume file content from memory alone when the edit would change existing text.

Anti-pattern:

- Editing a file based on a stale memory of its content, resulting in conflicts, lost changes, or validation errors.

## Path Parameter Validation

Every **Write** or **Edit** tool call must include a valid, absolute `path` parameter.

Rules:

- The `path` parameter is required. A tool call without it will fail with validation errors like `Validation failed for tool "write": path: must have required property 'path'`.
- Use absolute paths. Relative paths are acceptable only when the host environment explicitly guarantees resolution behavior.
- Validate the path exists (for edits) or the parent directory exists (for writes) before invoking the tool.
- Do not construct paths by string concatenation alone; use the workspace's path resolution conventions.

Anti-pattern:

- Calling a write tool with only `content` and no `path`.
- Assuming the host will infer the target path from context or previous operations.

## Runtime State vs Canonical

Distinguish clearly in `Workspace Semantics` and skills:

| Bucket | Holds |
|--------|--------|
| **Canonical** | Authoritative deliverables you ship, diff, and audit. |
| **Runtime state** | Resume checkpoints: gate status, short bullets, pointers — **not** copies of canonical bodies. |

Rules:

- If it reads like the main artifact (full HTML, giant JSON graph), it belongs under **canonical roots**, not state.
- Collaboration and review should anchor on **canonical outputs** plus whatever review process the host provides — do not assume everyone shares the same ephemeral working directory unless your deployment says so.

Recommended pattern: keep OpenClaw root to the standard quartet (`IDENTITY`, `SOUL`, `AGENTS`, `TOOLS`) and put long-lived workspace contracts under **`contracts/`** (for example `contracts/STATE.md`). Point to that path from `AGENTS.md` / `TOOLS.md` and from `Resume Strategy`. Per-deck files under `state/` remain **machine-oriented**.

## Preview vs Shipped Runtime

If documentation promises that **preview HTML** behaves like production (navigation, overview modes, export hooks), the preview shell must include the **same runtime contract** as shipped artifacts — or the docs must **narrow** the claim.

Anti-pattern:

- Spec requires `#deck`, horizontal snap, or controller hooks — template ships without loading them — preview "works" only by accident (native scroll) while shortcuts break.

Also separate:

- **Human preview entry**: opening local HTML in a browser (or host-equivalent) for review.
- **Export / capture pipelines**: may use a **different transport** (e.g. ephemeral HTTP for headless capture). Do not document those as if they were mandatory for ordinary preview.

## Related References

- `references/workflow-hardening/workflow-hardening.md` — when these concerns tie to gates and canonical-vs-derived separation.
- `references/case-studies/slidewright-optimization-notes.md` — concrete patterns (reuse reasoning, not surface paths).
