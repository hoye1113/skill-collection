# Self Review

Use this reference before returning the proposal or before running the scaffold scripts.

## Proposal Checks

- The output has exactly six sections in this order:
  1. 判断结果
  2. 升格理由
  3. `Agent Promotion Analysis`
  4. `Workspace Semantics`
  5. 四文件映射
  6. 风险与非承诺能力
- `judgment_result` is explicit.
- `promotion_rationale` explains why a simpler solution is or is not enough.
- `preferred_control_pattern` is explicit.
- `Agent Promotion Analysis` is complete.
- `Workspace Semantics` distinguishes `final / state / preview / export / skill resources`.
- Workspace semantics distinguish **runtime state** (resume checkpoints, pointers — lightweight) from **canonical deliverables**; state does not carry large duplicate bodies of final artifacts.
- Risk of **preview vs runtime documentation drift** is considered: if interaction promises match production, preview uses the same runtime story or claims are narrowed.
- If `workflow_hardening` exists, canonical source and derived exports are explicit.
- `Resume Strategy` is explicit.
- `Native / Conditional / Unsupported` capability classes are explicit.
- Each conditional capability has an explicit `classification` (`runtime-conditional` / `dev-time-only` / `one-shot-setup`).
- If install contract is recommended, all three trigger conditions are met (runtime-conditional exists, Session Startup calls it, host must pre-prepare).
- If install contract is not recommended, dev-only scripts are marked `shipped: false` in Workspace Semantics.
- Host assumptions are correct for the selected host profile.

## Scaffold Checks

- Only `IDENTITY.md`, `SOUL.md`, `AGENTS.md`, and `TOOLS.md` are written by the scaffold step.
- Existing root files are not overwritten in V1.3.
- Each root file contains the required headings and only its own responsibility.
- `AGENTS.md` includes `Session Startup`, `Red Lines`, and `Resume Strategy`.
- `TOOLS.md` includes capability boundaries and skill resources.
- No extra governance file was emitted.

## Optimize Checks

- `optimize` writes only preview artifacts outside the target workspace.
- The preview output includes `optimize-report.md`.
- The preview output uses only `preview/` and `diffs/` beside the report.
- Missing or drifted root files get both a preview file and a unified diff.
- Aligned root files are reported but not rewritten into the preview bundle.
- `Workflow Contract Findings` and `Skill Review Signals` sections are present.
- If `workflow_hardening` exists, workspace-level contract findings are reported separately from root-file preview artifacts.
- The target workspace remains unchanged after the preview run.
- Preview templates align with documented interaction behavior (controllers, hooks), or documentation explicitly limits preview guarantees.
- Write strategy does not depend solely on a single oversized patch where hosts may truncate payloads — incremental or chunked paths exist where needed.

## Failure Conditions

Fail the run if any of these are true:

- the promotion decision is not `独立 agent` but scaffold was attempted
- the promotion decision is not `独立 agent` but optimize was attempted
- `Workspace Semantics` still mixes final output, state, and preview
- host-specific guarantees were written as if they were generic facts
- required sections or headings are missing
- compaction-critical rules are missing from `Session Startup` or `Red Lines`
- candidate source discovery is conflated with final evidence acquisition
- `web_search` is treated as default primary content path
- known URL / batch scrape / render fallback are not mapped to `web_fetch` / `uv` / `browser`
- final conclusions rely on search summaries instead of retrievable source content
- a write or edit tool call is issued without a prior read of the target file
- a write or edit tool call is missing the required `path` parameter or uses a non-absolute path
- a file is edited based on stale content without re-reading after a potential change
- `dev/.openclaw-agent-install.json` exists but no `runtime-conditional` capability was declared (unnecessary install contract)
- `runtime-conditional` capability was declared but `dev/.openclaw-agent-install.json` is missing (missing install contract)
- AGENTS.md or Session Startup references `dev/` files (shipped files must not depend on not-shipped paths)
- `dev-time-only` or `one-shot-setup` capabilities are incorrectly treated as requiring an install contract
- Dev-only files (verify, setup, install contract, test fixtures) exist in `scripts/` or workspace root instead of `dev/`
- FlowyClaw preset boilerplate is duplicated in workspace `TOOLS.md`
- generated reports or preview artifacts use absolute paths for workspace-internal references
