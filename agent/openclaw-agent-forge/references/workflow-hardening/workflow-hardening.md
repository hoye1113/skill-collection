# Workflow Hardening

Use this reference when an agent is more than a root-file cleanup problem.

## Table of Contents

- [1. Contract-Backed Repeated Actions](#1-contract-backed-repeated-actions)
- [2. Canonical Source vs Derived Exports](#2-canonical-source-vs-derived-exports)
- [3. Preview and Approval Gates](#3-preview-and-approval-gates)
- [4. Conditional Runtime Install Contracts](#4-conditional-runtime-install-contracts)
  - [Classification Requirement](#classification-requirement)
  - [Install Contract Trigger](#install-contract-trigger)
- [5. Asset Staging and Portability](#5-asset-staging-and-portability)
- [6. Sidecar Write Ownership](#6-sidecar-write-ownership)
- [7. Preview / Runtime Parity and Honest Preview Entry](#7-preview--runtime-parity-and-honest-preview-entry)
- [8. Output Path Portability](#8-output-path-portability)
- [9. Write Pre-Validation Gate](#9-write-pre-validation-gate)
- [10. Export Capture Determinism](#10-export-capture-determinism)
- [11. Verbatim Copy Enforcement](#11-verbatim-copy-enforcement)
- [12. Ship-Time File Set](#12-ship-time-file-set)
  - [The `dev/` Directory Convention](#the-dev-directory-convention)
  - [Default Classification](#default-classification)
  - [Smell Test](#smell-test)
- [Proposal Prompts](#proposal-prompts)
- [Optimize Prompts](#optimize-prompts)

This reference is the short-form rule set for workflows that depend on canonical outputs, derived exports, preview gates, runtime prep, asset staging, or multiple sidecar skills. Load it for proposal and optimize work. Use `slidewright-optimization-notes.md` only when you need a deeper case study.

## 1. Contract-Backed Repeated Actions

Repeated actions should not rely on prompt-only prose when failure would be expensive or hard to detect.

Prefer a script, strict interface, or machine-checkable convention when the agent claims it can reliably:

- open a preview
- stage local assets
- perform a derived export
- verify runtime readiness
- hand off work across sidecar skills

Common prompt-only smell phrases:

- `attempt to`
- `try to`
- `if supported`
- `use relative paths`
- `wait a bit`

If those phrases appear in a critical workflow, ask whether a deterministic helper should exist.

## 2. Canonical Source vs Derived Exports

Every non-trivial workspace should distinguish:

- canonical source
- workflow state
- scratch / preview
- derived exports
- skill resources

Rules:

- Canonical source is the authoritative artifact you edit and audit.
- Derived exports are downstream products of the canonical source.
- Do not let exports share the same semantic bucket as canonical source.
- Resume logic should inspect canonical source first, not derived exports.

## 3. Preview and Approval Gates

Add a real confirmation gate when:

- the user request is ambiguous shorthand
- a derived export would be expensive or misleading without preview
- approval must happen before delivery

Compaction-safe rule:

- If skipping the gate would cause wrong routing, wrong deliverables, or destructive behavior, elevate that rule into `Session Startup` or `Red Lines`.

## 4. Conditional Runtime Install Contracts

If a capability depends on environment prep, do not leave setup as scattered prose.

Prefer an install contract with:

- a contract file path
- a setup entry
- a verify entry

Rules:

- `TOOLS.md` explains the boundary.
- The install contract is the mechanism.
- If the contract is missing, the capability stays conditional or unsupported.

### Classification Requirement

Every conditional capability must be classified before an install contract is recommended:

- `runtime-conditional`: the agent needs this environment at task execution time. The capability degrades or fails without it. **Requires an install contract.**
- `dev-time-only`: verification or testing that runs during development or CI, not during agent task execution. **Does not require an install contract.** Keep as a dev tool with `shipped: false`.
- `one-shot-setup`: a one-time preparation handled by deployment or first-run provisioning. **Does not require an install contract.** Document in Workspace Layout.

### Install Contract Trigger

Only generate `.openclaw-agent-install.json` when both conditions are met:

1. At least one capability is classified as `runtime-conditional`
2. The agent cannot self-install the dependency at runtime

If any condition fails, the install contract should not exist. Scripts that only serve dev-time validation should be listed in Workspace Semantics with `shipped: false`.

When the install contract is generated, place it under `dev/` (not workspace root). No runtime consumer reads this file — it is a host-level deployment declaration. The host reads the contract and prepares the environment before the agent starts. The agent itself never references `dev/` files in AGENTS.md or Session Startup. The `contract_path` in the spec must be `dev/.openclaw-agent-install.json`.

## 5. Asset Staging and Portability

If the agent references user-provided local files, ask:

- Is there a staging step?
- Are final outputs portable if moved to another directory?
- Are OS absolute paths treated as delivery failures?

Rules:

- Stage local assets into a workspace-local root.
- Rewrite final content to use returned relative refs.
- Treat absolute path leakage as a real delivery failure, not polish.

## 6. Sidecar Write Ownership

Sidecar skills should have non-overlapping write responsibility.

Good ownership patterns:

- analysis-only sidecars that do not mutate final artifacts
- bounded mutation sidecars with explicit writable roots
- derived-export sidecars that must not rewrite canonical source

Bad ownership patterns:

- multiple sidecars sharing the same writable root without a clear owner
- sidecars that can both mutate and audit the same artifact root
- write boundaries documented only in prose, not in declared roots

## 7. Preview / Runtime Parity and Honest Preview Entry

If documentation promises that **preview HTML** behaves like production (navigation, overview modes, export hooks, named controllers), the preview artifact must include the **same runtime dependencies and contracts** as the shipped canonical output — or the docs must **narrow** what preview guarantees.

Rules:

- Do not describe `#deck`, keyboard routing, or exporter-facing hooks in the spec if the preview template does not load the bundles that implement them.
- Treat **human preview** (opening local HTML in a browser or host-equivalent) as a distinct story from **export or capture pipelines** that may use another transport (for example ephemeral HTTP for headless automation). Avoid implying that everyday review requires whatever server export needs.

Pointers:

- `references/core-rules/agent-write-and-state.md` for write discipline, state lightness, and preview vs shipped alignment.
- `references/case-studies/slidewright-optimization-notes.md` sections **10–14** for concrete failure patterns.

## Proposal Prompts

When hardening applies, explicitly answer:

- What is the canonical source?
- What artifacts are derived exports?
- What must be true before export is allowed?
- Which repeated actions need deterministic helpers?
- Which capabilities are `runtime-conditional` and therefore require install contracts?
- How are local assets staged and rewritten?
- Which sidecar owns which writable root?
- If preview is advertised as parity with shipped output, does preview load the same runtime contract?
- Is "open for review" documented separately from export/capture transport requirements?
- Is runtime state explicitly lightweight vs canonical, with no large generated bodies parked in state?
- Is every write path validated and absolute before the tool call is issued?

## 8. Output Path Portability

All generated artifacts (reports, previews, diffs, logs) must use relative paths when referencing workspace-internal locations.

Rules:
- Reports should reference files as `IDENTITY.md`, not `C:\Users\...\IDENTITY.md`
- Preview artifacts should reference paths relative to the preview root
- Absolute paths are acceptable only when referencing system-level resources outside the workspace
- Treat absolute path leakage in generated artifacts as a portability finding

## 9. Write Pre-Validation Gate

Before any tool writes to the workspace, verify three conditions:

1. **Read readiness**: The target file has been read in the current session, or is being created for the first time.
2. **Path validity**: The tool call includes a required `path` parameter with an absolute path.
3. **Freshness check**: If the file was read earlier, re-read when there is any chance the content changed since the last read.

Rules:

- Treat a missing `path` parameter as a hard failure, not a host quirk.
- Treat editing without a prior read as a contract violation in compaction-critical workflows.
- For scripts that perform writes, include a `resolve_path()` helper that enforces absolute paths and validates parent directory existence.

Pointers:

- `references/core-rules/agent-write-and-state.md` for read-before-write discipline and path parameter validation.

## 10. Export Capture Determinism

When an export pipeline captures visual output via headless browser, eliminate sources of non-determinism:

Rules:

- In headless contexts, force pixel dimensions via CSS overrides (e.g., `width: 1920px !important`) instead of relying on viewport units (`100vw`, `100dvh`) that may resolve differently in headless mode.
- Use page-level screenshot with explicit clip coordinates instead of element-level screenshot methods.
- When scroll-based positioning may be unreliable (horizontal scrolling, custom layouts), use CSS `transform` as a fallback positioning strategy.
- Apply a triple-positioning defense: scroll + CSS transform + CSS forced dimensions. Each layer covers a different failure mode of the other two.

Pointers:

- `references/case-studies/slidewright-optimization-notes.md` Pattern 5 (export capture detail) for concrete implementation.

## 11. Verbatim Copy Enforcement

When a workflow rule requires verbatim copying of a canonical file into a generated artifact (e.g., inlining a controller, embedding a template, pasting a license header), prose-only enforcement ("always copy verbatim") is not sufficient. Agents will rationalize simplification, compression, or "improvement."

Rules:

- A "copy verbatim" rule must have a machine-checkable enforcement mechanism, not just a Red Line in prose.
- The validator must compare the inlined content against the canonical source at the **content level** (normalized for whitespace), not just at the **feature level** (checking that method names or keywords exist). Feature-level checks pass hand-written implementations that contain the same identifiers but different logic.
- Place the enforcement in the same post-write validator that already runs after every generation step. Do not create a separate enforcement path that the agent can skip.
- The error message must include the canonical file path and an explicit "do NOT hand-write" instruction, because the agent that triggered the error is the same agent that will attempt the fix.

Detection smell:

- A validator that checks "does method X exist?" but not "is the implementation identical?" will pass hand-written controllers, simplified templates, and compressed headers — all of which violate the verbatim contract.
- If a Red Line says "verbatim copy" but the validator only checks structural completeness, the Red Line is unenforced.

Pointers:

- `skills/frontend-slides/scripts/validate-html-batch.js` `checkControllerExactMatch` for a concrete implementation: extract inlined `<script>`, normalize whitespace, compare against canonical `assets/slide-controller.js`.

## 12. Ship-Time File Set

Not every file in the agent workspace is part of the delivered agent. Distinguish shipped files from dev-only artifacts.

### The `dev/` Directory Convention

All dev-only files MUST live under a top-level `dev/` directory. This is the single boundary between shipped and not-shipped.

```
workspace/
├── AGENTS.md          # shipped
├── SOUL.md            # shipped
├── IDENTITY.md        # shipped
├── TOOLS.md           # shipped
├── USER.md            # shipped
├── skills/            # shipped
├── scripts/           # shipped (runtime helpers only)
├── state/             # shipped
├── data/              # shipped
├── output/            # shipped
├── memory/            # shipped
└── dev/               # NOT shipped — entire directory excluded
    ├── .openclaw-agent-install.json
    ├── setup.py
    ├── verify.py
    └── tests/
```

Rules:

- `scripts/` contains ONLY runtime helpers that the agent's AGENTS.md Session Startup or task execution actually calls.
- `dev/` contains ALL dev-only files: verification scripts, setup scripts, install contracts, test fixtures, CI tooling.
- The entire `dev/` directory is `shipped: false`. No per-file judgment needed.
- If a file's only consumer is a developer or CI pipeline, it belongs in `dev/`, not `scripts/`.

### Default Classification

| Path pattern | Default `shipped` | Rationale |
|---|---|---|
| `IDENTITY.md`, `SOUL.md`, `AGENTS.md`, `TOOLS.md` | `true` | Root contract files |
| `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md` | `true` | Agent runtime files |
| `skills/` | `true` | Agent needs skills at runtime |
| `scripts/` | `true` | Only if AGENTS.md Session Startup calls them |
| `dev/` | `false` | Entire directory is dev/CI only |
| `specs/`, `tests/`, `output/specs/` | `false` | Development and proposal artifacts |
| `state/`, `data/`, `output/briefings/` | `true` | Runtime state and deliverables |
| `memory/` | `true` | Agent runtime state |

### Smell Test

If a file's only consumer is a developer running it manually or a CI pipeline, it belongs in `dev/`. If the agent's Session Startup or task execution depends on it, it belongs in `scripts/` or the workspace root.

## Optimize Prompts

When reviewing an existing workspace, check:

- Are compaction-critical rules elevated into `Session Startup` or `Red Lines`?
- Are canonical source and derived exports separated?
- Is each conditional capability classified as `runtime-conditional` / `dev-time-only` / `one-shot-setup`?
- Does each `runtime-conditional` capability have an install contract, and are `dev-time-only` capabilities excluded from the install contract?
- Does the install contract exist only when AGENTS.md Session Startup actually calls it?
- Do repeated actions rely on helpers or just prose?
- Are local file refs portable?
- Do sidecars have overlapping write authority?
- Do generated reports and preview artifacts use relative paths for workspace-internal references?
- If UX docs promise preview parity with production, do preview templates include the same controllers and hooks — or are claims narrowed?
- Does the workspace distinguish daily preview entry from export-pipeline networking so neither is mistaken for the other?
- For large artifacts, is write strategy incremental or chunked — or does it rely on a single mega-patch with no fallback?
- Does any write or edit lack a preceding read, or use a relative / unvalidated path?
- Do validator outputs include machine-parseable repair instructions, or only free-text diagnosis?
- Are large file writes followed by closure and structural integrity checks?
- If multiple files must stay in sync, is there a dedicated sync script — or does the agent manage copies manually?
- If any rule says "verbatim copy," does the validator compare content (not just feature names) against the canonical source?
