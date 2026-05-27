# Platform Constraints

Use this reference whenever you write platform claims, resume behavior, or host-specific guarantees.

## Table of Contents

- [Three Rule Layers](#three-rule-layers)
- [OpenClaw Bootstrap Reality](#openclaw-bootstrap-reality)
- [Resume and Compaction](#resume-and-compaction)
- [Memory Rules](#memory-rules)
- [Character Budget](#character-budget)
- [FlowyClaw Default Host Profile](#flowyclaw-default-host-profile)
- [Generic OpenClaw Downgrade](#generic-openclaw-downgrade)
- [Install Contracts](#install-contracts)
  - [When NOT to create an install contract](#when-not-to-create-an-install-contract)
- [Host Profile Preset Mechanism](#host-profile-preset-mechanism)
- [Design Consequences](#design-consequences)

## Three Rule Layers

- Source facts: runtime behavior guaranteed by OpenClaw itself
- Template defaults: recommended patterns from templates
- Design choices: workspace-specific rules chosen for this agent

Never write template defaults or design choices as if they were guaranteed platform facts.

## OpenClaw Bootstrap Reality

Main sessions load files in this order:

1. `AGENTS.md`
2. `SOUL.md`
3. `TOOLS.md`
4. `IDENTITY.md`
5. `USER.md`
6. `HEARTBEAT.md`
7. `BOOTSTRAP.md`
8. `MEMORY.md` (only if exact-case file exists; legacy `memory.md` is skipped)

Sub-agents only get: `AGENTS.md`, `TOOLS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md` (5 files). No HEARTBEAT, BOOTSTRAP, or MEMORY.

Cron sessions load all 8 files (same as main session).

Heartbeat sessions: HEARTBEAT.md is classified as a "dynamic context file" (placed below the cache boundary). In lightweight heartbeat mode, only HEARTBEAT.md is kept; other files are filtered out.

`workspace-state.json` tracks `bootstrapSeededAt` and `setupCompletedAt` timestamps. The bootstrap is considered pending when `setupCompletedAt` is not set AND BOOTSTRAP.md exists on disk.

## Resume and Compaction

- `Resume Strategy` is a design rule, not a platform magic feature.
- Keep compaction-critical guidance in `AGENTS.md` sections that survive recovery, especially `Session Startup` and `Red Lines`.
- If recovery depends on `memory/YYYY-MM-DD.md` or any custom state file, the read order must be explicit in `Session Startup` or `Resume Strategy`.

## Memory Rules

- Do not precreate empty `MEMORY.md`.
- If the design uses `memory/`, declare its meaning in `Workspace Layout`.
- Sensitive long-lived notes belong in `MEMORY.md`, not in files that sub-agents always inherit.

## Character Budget

- Single bootstrap file: **12,000 characters** max (`DEFAULT_BOOTSTRAP_MAX_CHARS`)
- All bootstrap files total: **60,000 characters** max (`DEFAULT_BOOTSTRAP_TOTAL_MAX_CHARS`)
- Truncation strategy: **75% head + 25% tail** with a truncation marker
- When truncation occurs, a warning is injected: `[Bootstrap truncation warning] Some workspace bootstrap files were truncated before injection.`
- Near-limit warning threshold: 85% of budget
- Daily memory (`memory/YYYY-MM-DD.md`) has a separate budget: 1,200 chars/file, 2,800 chars total for today + yesterday, loaded via `startup-context.ts` (independent from bootstrap budget)
- Root files are for long-lived contract, not for full workflow bodies or copied references.

## FlowyClaw Default Host Profile

Under `flowyclaw`, you may assume the default host profile described by the source documents:

- OpenClaw runtime is embedded by the host
- `uv` and `node` are host-level baselines
- host presets inject shared context outside the workspace-specific root files

Do not repeat host-preset boilerplate in workspace `TOOLS.md`.

## Generic OpenClaw Downgrade

Under `generic-openclaw`:

- do not assume FlowyClaw host presets exist
- do not promise `uv` or `node` unless the target agent explicitly verifies them
- write host-dependent claims as conditional, not native

## Install Contracts

When a capability depends on environment preparation at **agent runtime**, use `.openclaw-agent-install.json` instead of scattered prose.

Place the file under `dev/` (not workspace root). No runtime consumer reads this file — it is a host-level deployment declaration. The host reads the contract and prepares the environment before the agent starts. The agent itself never references `dev/` files.

Standard fields:
- `version`: contract version
- `pythonVersion`: target Python version
- `setup.script`: `dev/setup.py` (must be idempotent)
- `verify.script`: `dev/verify.py` (should read-only)

Setup scripts should consume `--python-executable` and `--uv-executable` from the host, not guess system PATH.

### When NOT to create an install contract

Do not create `.openclaw-agent-install.json` when:

- The capability is `dev-time-only` (verification scripts, integration tests, CI checks)
- The capability is `one-shot-setup` (handled by deployment, not agent runtime)
- The agent's AGENTS.md Session Startup does not call the setup or verify script
- The agent can self-install the dependency at task execution time

In these cases, keep setup/verify scripts under `dev/` (not `scripts/`) and mark `dev/` as `shipped: false` in Workspace Semantics.

## Host Profile Preset Mechanism

FlowyClaw injects shared context via `resources/context/AGENTS.preset.md` and `resources/context/TOOLS.preset.md`. Do not repeat host-preset boilerplate (e.g., `uv`, `browser`, brand notes) in workspace `TOOLS.md`.

## Design Consequences

- The generated agent must separate platform facts from workspace rules.
- `AGENTS.md` should state what to read first and how to resume safely.
- `TOOLS.md` should state path semantics and capability boundaries, not persona.
- Do not invent extra governance files to hold middle-layer analysis.

