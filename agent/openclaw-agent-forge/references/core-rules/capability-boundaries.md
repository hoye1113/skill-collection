# Capability Boundaries

Use this reference when writing capability statements for the generated agent or when downgrading host assumptions.

## Capability Classes

### Native capability

Use only for abilities that belong to the workspace contract itself and do not depend on unverified external runtime claims.

Examples:

- reading and writing local Markdown, JSON, and text files
- maintaining canonical state in declared workspace paths
- routing through packaged local skills

### Conditional capability

Use when the behavior depends on:

- local scripts
- host tools
- runtime availability
- external services
- optional dependencies

If a script exists but still depends on runtime conditions, it is conditional until verified.

Each conditional capability must be classified:

- `runtime-conditional`: the agent needs this environment at task execution time. Requires an install contract.
- `dev-time-only`: verification or testing that runs during development or CI, not at agent runtime. No install contract needed.
- `one-shot-setup`: a one-time preparation handled by deployment. No install contract needed.

See `references/workflow-hardening/workflow-hardening.md` section 4 for install contract rules.

### Unsupported or non-capability

Use for claims the generated agent must not imply by default.

Examples:

- plugin-only features
- background automation that is not bundled
- host tools that are not guaranteed
- push delivery, browser automation, or office export when the design has not verified them

## Host-Specific Wording

Under `flowyclaw`:

- you may treat `uv` and `node` as host-profile baselines when the source docs say so
- do not restate host-preset boilerplate in the workspace files

Under `generic-openclaw`:

- do not inherit FlowyClaw-only host guarantees
- downgrade those claims to conditional unless the target agent verifies them independently

## Writing Rules

- Separate workspace-native abilities from script-assisted abilities.
- Separate host guarantees from design choices.
- If the generated agent depends on runtime preparation, say so directly.
- Do not promise "cross-environment portability" when the design only covers one host profile.

## Information Acquisition Layer

When classifying information-gathering capabilities:

| Tool | Classification | Rationale |
|------|----------------|-----------|
| `web_fetch` on known URL | Native-like | Direct, reproducible fetch |
| `web_search` | Fragile / discovery-only | Result quality depends on provider; summaries are not ground truth |
| `browser` | Conditional fallback | Requires rendering; use only when `web_fetch` fails or page is interactive |
| `uv`-driven scraping scripts | Conditional | Depends on script availability and runtime |

See `information-acquisition.md` for the full priority stack.

## Common Mistakes

- "There is a script, so it is native."
- "FlowyClaw can do it, so generic OpenClaw can do it too."
- "The user asked for it, so the capability must exist."
- "The workspace could support it later, so we can promise it now."
- "`web_search` is sufficient for final content acquisition."
- "Browser is the default primary path for reading web pages."

