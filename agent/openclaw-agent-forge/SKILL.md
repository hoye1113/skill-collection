---
name: openclaw-agent-forge
description: "Generate, review, and optimize OpenClaw or FlowyClaw agent workspaces from a skill, workflow, or existing workspace brief. Use when the user asks to generate an agent, design an OpenClaw agent workspace, promote a skill into an agent, write agent root files, review an existing workspace, optimize current root files, check whether AGENTS SOUL IDENTITY TOOLS are complete, generate a preview patch, fix root-file responsibility drift, define canonical source vs derived export semantics, add a preview or approval gate, declare an install contract, stage local assets into portable relative paths, assign sidecar write ownership, draft Agent Promotion Analysis, define Workspace Semantics, design Resume Strategy, map IDENTITY SOUL AGENTS TOOLS, declare capability boundaries for an agent scaffold, configure agent memory system, set up heartbeat polling, design bootstrap onboarding, or define group chat behavior."
---

IRON LAW: Decide whether the input truly deserves an agent before generating any root files. Always produce `Agent Promotion Analysis` and `Workspace Semantics` first. Never turn root files into a compressed copy of `SKILL.md`.

# OpenClaw Agent Forge

Turn a skill, workflow, or agent brief into either:

1. a six-part OpenClaw agent proposal, or
2. a four-to-seven file root scaffold backed by that proposal (4 core + optional BOOTSTRAP.md, USER.md, HEARTBEAT.md), or
3. a preview-only optimization pass for an existing agent workspace.

V1.3 supports `--mode propose|scaffold|optimize`. `optimize` is diagnose-first and preview-only: it writes a diagnosis report, preview files, and diffs to a separate preview directory. It does not overwrite the target workspace.

## Parameters

Use these parameters when the caller already made a decision:

- `--mode propose|scaffold|optimize`
- `--host flowyclaw|generic-openclaw`
- `--control auto|step`

Defaults:

- `--mode propose`
- `--host flowyclaw`
- `--control step`

### `--control` Behavior

- `step` (default): Pause after Step 2 (`Agent Promotion Analysis`) and Step 3 (`Workspace Semantics`) for user confirmation before proceeding to Step 4 (root-file mapping). This follows the progressive generation pattern.
- `auto`: Proceed through all steps automatically. Confirmation gates at Step 6 still apply (propose always stops; scaffold/optimize follow their conditional rules).

## Reference Loading Map

Load only the reference needed for the current step:

- `references/core-rules/promotion-decision.md`
  Use when deciding `独立 agent / 附属 skill / 私有 skill / plugin / simpler workflow`.
- `references/core-rules/platform-constraints.md`
  Use when writing host assumptions, bootstrap rules, resume behavior, memory rules, and compaction-safe guidance.
- `references/core-rules/compaction-recovery.md`
  Use when designing which rules must survive session compaction and where to place them.
- `references/core-rules/root-file-mapping.md`
  Use when turning a proposal into `IDENTITY.md`, `SOUL.md`, `AGENTS.md`, and `TOOLS.md`.
- `references/core-rules/information-acquisition.md`
  Use when writing tool usage guidance or capability statements that involve fetching external information.
- `references/core-rules/capability-boundaries.md`
  Use when writing `Native / Conditional / Unsupported` capability statements or downgrading FlowyClaw-only assumptions for `generic-openclaw`.
- `references/openclaw-modules.md`
  Use when making promotion decisions involving OpenClaw runtime modules, or when classifying built-in vs plugin-level capabilities.
- `references/workflow-hardening/workflow-hardening.md`
  Use when the workflow depends on canonical-vs-derived outputs, preview or approval gates, local file staging, runtime prep, or sidecar ownership boundaries.
- `references/core-rules/agent-write-and-state.md`
  Use when designing or reviewing **runtime state vs canonical deliverables**, **large or chunked write strategies**, **preview vs shipped runtime parity** (same UX claims must share the same runtime contract), or **read-before-write discipline and path parameter validation**.
- `references/core-rules/edit-boundaries.md`
  Use when **applying optimize recommendations** to check which sections may be modified and which are monotonic (Red Lines, Non-Negotiables, Boundaries).
- `references/checklists/self-review.md`
  Use before returning the final proposal or before calling any scaffold script.
- `references/case-studies/slidewright-optimization-notes.md`
  Use only when a concrete hardening case is useful; reuse its reasoning, not its presentation-specific wording.

## Workflow

Copy this checklist and check off items as you complete them:

```md
- [ ] Step 0: Read inputs and lock the host profile ⚠️ REQUIRED
  - [ ] 0.1 Read the skill brief, existing workspace notes, or source docs
  - [ ] 0.2 Decide whether the host profile is `flowyclaw` or `generic-openclaw`
  - [ ] 0.3 Load `references/core-rules/platform-constraints.md` before writing any platform claims
- [ ] Step 1: Make the promotion decision ⚠️ REQUIRED
  - [ ] 1.1 Load `references/core-rules/promotion-decision.md`
  - [ ] 1.2 Decide `独立 agent / 附属 skill / 私有 skill / plugin / simpler workflow`
  - [ ] 1.3 Pick the preferred control pattern
  - [ ] 1.4 If it should not be an independent agent, stop with an alternative plan
- [ ] Step 2: Build `Agent Promotion Analysis` ⚠️ REQUIRED
  - [ ] 2.1 Fill every required field
  - [ ] 2.2 Make the lazy default and quality bar explicit
  - [ ] 2.3 Separate native, conditional, and non-capabilities
  - [ ] 2.4 Classify each conditional capability as `runtime-conditional` / `dev-time-only` / `one-shot-setup`
  - [ ] 2.5 Decide whether `workflow_hardening` is required
- [ ] Step 3: Build `Workspace Semantics` ⚠️ REQUIRED
  - [ ] 3.1 Define final deliverables
  - [ ] 3.2 Define workflow state
  - [ ] 3.3 Define scratch or preview outputs
  - [ ] 3.4 Define export or package outputs
  - [ ] 3.5 Define skill resource roots
  - [ ] 3.6 Mark each path with `shipped: true/false` to distinguish delivered files from dev-only artifacts
  - [ ] 3.7 If applicable, distinguish canonical source from derived exports explicitly
- [ ] Step 4: Map the root files ⚠️ REQUIRED
  - [ ] 4.1 Load `references/core-rules/root-file-mapping.md`
  - [ ] 4.2 Write `IDENTITY.md` fields
  - [ ] 4.3 Write `SOUL.md` fields
  - [ ] 4.4 Write `AGENTS.md` fields, including `Session Startup`, `Red Lines`, and `Resume Strategy`
  - [ ] 4.5 Write `TOOLS.md` fields
  - [ ] 4.5b (Optional) Design memory and lifecycle: `memory_config`, `heartbeat_config`, `bootstrap_config`, `user_profile`, `group_chat_behavior`
  - [ ] 4.6 Validate write-readiness for all root files ⚠️ REQUIRED
    - [ ] Verify every file to be written or edited has been read or is new
    - [ ] Verify all write paths are absolute and include the required `path` parameter
    - [ ] Verify freshness: re-read any file that may have changed since last read
  - [ ] 4.7 Ground truth check ⚠️ REQUIRED
    - [ ] Verify that compaction-critical rules are placed in `Session Startup` or `Red Lines`
    - [ ] Verify host profile consistency (generic-openclaw mode must not contain flowyclaw-specific wording)
- [ ] Step 5: Write risks and non-promises ⚠️ REQUIRED
  - [ ] 5.1 Load `references/core-rules/capability-boundaries.md`
  - [ ] 5.2 State host-specific assumptions
  - [ ] 5.3 State unsupported or non-capability claims explicitly
  - [ ] 5.4 If applicable, classify approval gates, deterministic helpers, install contracts, asset staging, and sidecar write ownership
  - [ ] 5.5 Apply install contract decision: recommend `.openclaw-agent-install.json` only when both trigger conditions are met
- [ ] Step 6: Confirmation gate ⚠️ REQUIRED
  - [ ] 6.1 In `propose` mode, return the six-part proposal and stop
  - [ ] 6.2 In `scaffold` mode, continue only if `Promotion decision = 独立 agent`
  - [ ] 6.3 In `scaffold` mode, continue only if the user explicitly asked to write the root files
- [ ] Step 7: Render the scaffold (conditional)
  - [ ] 7.1 Prepare the structured JSON spec
  - [ ] 7.2 Run `python scripts/render_root_files.py --spec <spec.json> --out <workspace-dir>`
  - [ ] 7.3 Never overwrite existing root files in V1.3
  - [ ] 7.4 If memory/lifecycle fields are present, the renderer generates BOOTSTRAP.md, USER.md, and/or HEARTBEAT.md automatically
- [ ] Step 8: Optimize an existing workspace (conditional)
  - [ ] 8.1 Continue only if the user explicitly asked to improve an existing agent workspace
  - [ ] 8.2 If you have a complete spec: Run `python scripts/optimize_root_files.py --spec <spec.json> --workspace <workspace-dir> --preview-out <preview-dir>`
  - [ ] 8.3 If you do NOT have a spec (external workspace): Run `python scripts/infer_spec.py --workspace <workspace-dir> --out <spec.json> --host <profile>` to infer one
  - [ ] 8.4 Review the inferred spec, adjust host_profile and placeholder values
  - [ ] 8.5 Run optimize with `--lite`: `python scripts/optimize_root_files.py --spec <spec.json> --workspace <workspace-dir> --preview-out <preview-dir> --lite`
  - [ ] 8.6 Diagnose first, then generate preview files and diffs only for missing or structurally non-compliant contract files
  - [ ] 8.7 Treat the generated preview files and diffs as review artifacts, not as applied changes
  - [ ] 8.8 If `workflow_hardening` exists, run workspace-contract diagnostics before finalizing optimize output
- [ ] Step 9: Validate before delivery ⚠️ REQUIRED
  - [ ] 9.1 Load `references/checklists/self-review.md`
  - [ ] 9.2 Run `python scripts/validate_agent_output.py --spec <spec.json> --mode propose`
  - [ ] 9.3 If files were rendered, run `python scripts/validate_agent_output.py --spec <spec.json> --out <workspace-dir> --mode scaffold`
  - [ ] 9.4 If optimize preview was generated, run `python scripts/validate_agent_output.py --spec <spec.json> --mode optimize --preview-out <preview-dir> --workspace <workspace-dir>`
  - [ ] 9.5 If optimize used `--lite`, add `--lite` to the validate command as well
```

## Step 0: Read Inputs and Lock the Host Profile

Always start by determining what kind of input you actually have:

- a packaged skill directory
- a workflow brief
- a stack of method documents
- an existing workspace that needs analysis only

Then lock the host profile:

- `flowyclaw`: treat FlowyClaw as the default host and use its declared host baseline
- `generic-openclaw`: strip or downgrade any promise that depends on FlowyClaw-specific presets or guarantees

Do not write any host claim before reading `references/core-rules/platform-constraints.md`.

## Step 1: Make the Promotion Decision

Load `references/core-rules/promotion-decision.md`.

Answer these questions before writing anything else:

- Does this input have a long-lived identity, not just a one-off task?
- Does its value depend on workspace contract, resume strategy, state boundaries, or durable deliverables?
- Would `single-shot`, `workflow`, or `skill + scripts` already solve it cleanly?
- Does it require plugin-level runtime changes instead of an agent workspace?

If the answer is not `独立 agent`, stop with the correct alternative and do not scaffold files.

## Step 2: Build `Agent Promotion Analysis`

The analysis must exist before any root file mapping.

Use this machine-readable contract in the JSON spec:

```json
{
  "agent_promotion_analysis": {
    "skill_name": "",
    "host_profile": "flowyclaw",
    "promotion_decision": "独立 agent",
    "core_role": "",
    "primary_value": "",
    "lazy_default_to_avoid": "",
    "non_negotiable_quality_bar": "",
    "canonical_deliverables": [],
    "workflow_state": [],
    "resume_entry_files": [],
    "native_capabilities": [],
    "conditional_capabilities": [
      {
        "name": "",
        "classification": "runtime-conditional",
        "reason": ""
      }
    ],
    "non_capabilities": [],
    "what_stays_in_skill_md": [],
    "what_moves_to_root_files": []
  }
}
```

Each `conditional_capabilities` entry must include a `classification` field:

- `runtime-conditional`: the agent needs this environment at task execution time (e.g., html-to-pptx needs python-pptx on every PPTX export). Requires an install contract.
- `dev-time-only`: verification or testing that runs during development or CI, not at agent runtime (e.g., integration tests, roundtrip checks). Does not require an install contract.
- `one-shot-setup`: a one-time preparation step handled by deployment, not the agent runtime (e.g., downloading a model file). Does not require an install contract.

## Step 3: Build `Workspace Semantics`

The proposal must distinguish these five path classes:

- final deliverables
- workflow state
- scratch or preview
- export or package
- skill resources

Use this contract in the JSON spec:

```json
{
  "workspace_semantics": [
    {
      "type": "Final deliverables",
      "path": "",
      "purpose": "",
      "persistent": "Yes",
      "overwrite_rule": "Ask first",
      "shipped": true
    }
  ]
}
```

The `shipped` field determines whether the file or directory is part of the delivered agent workspace:

- `true`: shipped to end users (root files, skills, runtime scripts)
- `false`: dev-only artifact (verification scripts, test fixtures, CI tooling, specs)
- Default to `true` if omitted. Set to `false` explicitly for `dev/` directory.
- All dev-only files MUST live under `dev/`. Do not scatter them across `scripts/` or the workspace root.

## Step 4: Map the Four Root Files

Load `references/core-rules/root-file-mapping.md`.

The JSON spec must include these root-file fields:

```json
{
  "name": "",
  "role": "",
  "public_identity": "",
  "non_negotiables": [],
  "enduring_style": [],
  "workspace_positioning": "",
  "session_startup": [],
  "red_lines": [],
  "default_behavior": [],
  "boundaries": [],
  "workspace_layout": [],
  "output_roots": [],
  "local_conventions": [],
  "capabilities": {
    "native": [],
    "conditional": [],
    "unsupported": []
  },
  "skill_resources": {
    "primary_skill_entrypoints": [],
    "high_priority_references": [],
    "conditional_scripts": []
  },
  "resume_strategy": {
    "global_resume_file": "",
    "task_topic_resume_file": "",
    "deliverable_inspection_path": "",
    "if_state_missing": "",
    "never_assume": ""
  }
}
```

If available, also include:

- `preferred_control_pattern`
- `host_profile`
- `judgment_result`
- `promotion_rationale`
- `risks_and_non_capabilities`

If the workflow needs hardening, also include this optional contract:

```json
{
  "workflow_hardening": {
    "canonical_source": {
      "path": "",
      "reason": ""
    },
    "derived_exports": [
      {
        "path": "",
        "source_path": "",
        "reason": "",
        "approval_gate": ""
      }
    ],
    "approval_gates": [],
    "install_contracts": [],
    "deterministic_helpers": [],
    "asset_staging": {
      "asset_root": "",
      "rewrite_rule": "",
      "absolute_path_policy": ""
    },
    "sidecar_write_ownership": []
  }
}
```

Each entry in `workflow_hardening.install_contracts` must correspond to a `runtime-conditional` entry in `agent_promotion_analysis.conditional_capabilities`. Do not create install contracts for `dev-time-only` or `one-shot-setup` capabilities.

### Optional Spec Fields (Memory & Lifecycle)

These optional fields enable memory system, heartbeat, bootstrap, and group chat support. All are backward-compatible — omitting them produces the original 4-file scaffold.

| Field | Type | Description |
|-------|------|-------------|
| `memory_config` | object | Memory system (daily notes + MEMORY.md). When enabled, adds full `## Memory` section to AGENTS.md; when absent, a minimal baseline section is still rendered |
| `heartbeat_config` | object | Heartbeat polling tasks. When enabled, adds `## Heartbeats` to AGENTS.md and generates HEARTBEAT.md |
| `bootstrap_config` | object | First-run onboarding. When enabled, generates BOOTSTRAP.md |
| `user_profile` | object | Human user profile (name, pronouns, timezone). When present, generates USER.md |
| `group_chat_behavior` | object | Group chat participation rules. When enabled, adds `## Group Chats` to AGENTS.md |

Example:

```json
{
  "memory_config": {
    "enabled": true,
    "daily_notes": true,
    "long_term_memory": true,
    "security_boundary": "main_session_only",
    "curation_schedule": "heartbeat",
    "what_to_capture": ["decisions", "context", "lessons", "mistakes"]
  },
  "heartbeat_config": {
    "enabled": true,
    "tasks": ["review recent memory files", "update MEMORY.md", "check project status"],
    "quiet_hours": "23:00-08:00",
    "state_file": "memory/heartbeat-state.json"
  },
  "bootstrap_config": {
    "enabled": true,
    "conversation_topics": ["identity", "user_profile", "soul_principles"]
  },
  "user_profile": {
    "name": "Example User",
    "pronouns": "they/them",
    "timezone": "UTC+8"
  },
  "group_chat_behavior": {
    "enabled": true,
    "respond_when": ["mentioned", "can_add_value"],
    "stay_silent_when": ["casual_banter", "already_answered"]
  }
}
```

## Step 5: Write Risks and Non-Promises

Load `references/core-rules/capability-boundaries.md`.

Make these explicit:

- what is guaranteed only under `flowyclaw`
- what must be downgraded under `generic-openclaw`
- what the generated agent should explicitly treat as conditional or unsupported
- which conditional capabilities are `runtime-conditional` vs `dev-time-only` vs `one-shot-setup`

### Install Contract Decision

Only recommend creating `.openclaw-agent-install.json` when **both** conditions are true:

1. At least one conditional capability has `classification: "runtime-conditional"` in the Agent Promotion Analysis
2. The agent cannot self-install the dependency at runtime (the host must pre-prepare the environment)

If any condition fails:

- Do **not** generate `.openclaw-agent-install.json`
- Do **not** generate `scripts/setup.py` or `scripts/verify.py` as install-contract scripts
- If setup/verify scripts exist for dev-time validation, place them under `dev/` (not `scripts/`) and mark `dev/` as `shipped: false` in Workspace Semantics
- In `TOOLS.md` capabilities, mark these as `dev-time-only` with a note that they are developer verification tools, not runtime dependencies

If both conditions are met:

- Place `.openclaw-agent-install.json` under `dev/` (not workspace root). No runtime consumer reads this file — it is a host-level deployment declaration, not an agent runtime dependency. The host reads the contract and prepares the environment before the agent starts. The agent itself never references `dev/` files in AGENTS.md or Session Startup.
- The `contract_path` field in the spec must be `dev/.openclaw-agent-install.json`
- Mark `dev/` as `shipped: false` in Workspace Semantics

## Confirmation Gates

### `propose`

- Return the six-part proposal and stop.
- Do not write any root files.

### `scaffold`

Continue only if both are true:

1. `Promotion decision = 独立 agent`
2. the user explicitly asked to generate root files

If either condition fails, stop and return the alternative or the proposal only.

### `optimize`

Continue only if both are true:

1. `Promotion decision = 独立 agent`
2. the user explicitly asked to analyze or improve an existing agent workspace

Rules:

- `optimize` is preview-only in V1.3
- write the diagnosis report, preview files, and unified diffs to a separate preview directory
- never overwrite the target workspace directly

## External Workspace Optimization

When optimizing a workspace that was **not** generated by this skill (no existing spec):

### Step 1: Infer the spec

```bash
python scripts/infer_spec.py --workspace <dir> --out <spec.json> --host <flowyclaw|generic-openclaw>
```

This scans root files and produces a minimal spec. Fields that cannot be inferred get placeholder values.

### Step 2: Review the inferred spec

- Check `host_profile` — the default is `generic-openclaw`
- Review `name`, `role`, `public_identity` — verify they match the workspace
- The `agent_promotion_analysis` will have generic placeholders — that's expected

### Step 3: Optimize with `--lite`

```bash
python scripts/optimize_root_files.py --spec <spec.json> --workspace <dir> --preview-out <preview> --lite
```

The `--lite` flag accepts a minimal spec with only 5 required fields:
- `judgment_result` (must be "独立 agent")
- `host_profile`
- `name`
- `role`
- `public_identity`

### Step 4: Validate with `--lite`

```bash
python scripts/validate_agent_output.py --spec <spec.json> --mode optimize --preview-out <preview> --workspace <dir> --lite
```

### Content-Level Diagnosis

The optimize pipeline now includes content-level analysis beyond structural heading checks:

- **Placeholder detection** — flags `[TODO]`, `[REQUIRED]`, template defaults left behind
- **Empty sections** — flags `## ` headings with no content
- **Vague rules** — flags non-actionable rules like "try to" or "be careful" in Red Lines/Boundaries
- **Duplicate rules** — flags identical bullet items appearing in multiple sections
- **Character budget** — checks 12K/file and 60K/total limits
- **Host profile drift** — flags flowyclaw-specific wording under generic-openclaw

### Section-Level Diagnosis

The optimize report now includes per-section diagnostics with layer classification:

| Layer | Meaning |
|-------|---------|
| `structure` | Missing required heading |
| `content` | Empty section or placeholder text |
| `quality` | Vague rules, duplicate rules |
| `budget` | Character budget violation |
| `drift` | Host profile wording mismatch |

Each file entry in the report includes a `#### Section Details` table showing
per-section status and layer. Use this to modify only the flagged sections.

### Workspace Invariants

The report includes a `## Workspace Invariants` section that checks cross-file
structural invariants:

- **red_lines_monotonic** — Red Lines in the workspace must not shrink compared to the spec
- **session_startup_references_valid** — Session Startup file references must point to existing files
- **role_consistency** — IDENTITY.md role must align with AGENTS.md Workspace Positioning
- **skill_resources_paths_valid** — Skill Resources paths must point to existing files
- **memory_baseline_present** — AGENTS.md must contain a `## Memory` section (baseline or full)

A FAIL on `red_lines_monotonic` means the workspace has lost rules that were in
the spec. This is a blocking issue — the agent must restore the missing rules.

### Version Impact

The report includes a `## Version Impact` section:

- **structural** — missing files or missing headings; bump `root_file_version` after applying
- **content-only** — quality/budget/drift issues only; no version bump required

### Edit Boundaries

When applying optimize recommendations:

1. Load `references/core-rules/edit-boundaries.md`
2. For each section flagged in the report, check the boundary table
3. **Red Lines**: only append, never delete existing rules
4. **Boundaries**: only add, never relax existing boundaries
5. **Non-Negotiables** (SOUL.md): only add stricter rules, never remove
6. **Resume Strategy**: preserve all 5 required labels
7. Modify only the flagged sections — do not rewrite entire files

### Section-Level Diff

The optimize report includes per-section diffs under each needs_update section.
Apply changes at the section level, not the file level. If only `## Red Lines`
is flagged, touch only that section in AGENTS.md.

### Repair Protocol（最小切片修复）

借鉴 `web-video-presentation` 的"检查→修复→汇报"铁律。

**流程**：

1. **Diagnose** — 运行 `optimize_root_files.py` 生成 preview 目录
2. **Repair** — 运行 `repair_root_files.py --spec <spec> --workspace <dir> --preview <preview_dir>`
   - 修复后自动重跑不变量检查
   - 不变量失败的修改会被回滚（单个回滚，不连坐）
3. **Report** — 查看 `repair-report.md`，确认所有修改通过

**铁律**：
- 不要跳过 repair 直接手动改 workspace
- 不要整文件重写——只改 report 中标记的 section
- 不变量 FAIL 的修改必须修复后才能继续
- 拿到结论后**先按 fail 项改完**，再向用户汇报

**层优先定位**（对应诊断的 5 个 layer）：

| Layer | 含义 | 修复方式 |
|-------|------|---------|
| `structure` | 缺少 required heading | 从 preview 追加新 section |
| `content` | section 内容为空或有占位符 | 用 preview 中对应 section 替换 |
| `quality` | 规则模糊或重复 | 用 preview 中更精确的版本替换 |
| `budget` | 字符超限 | 用 preview 中精简版本替换 |
| `drift` | host profile 措辞漂移 | 用 preview 中正确措辞替换 |

## Anti-Patterns

- Do not jump straight to templates before checking whether an agent is even the right abstraction.
- Do not paste long reference content into `AGENTS.md`.
- Do not turn checklist steps or parameter flags into root-file persona rules.
- Do not classify a capability as native only because a script exists.
- Do not leave `classification` blank or omit it on conditional capabilities.
- Do not generate `.openclaw-agent-install.json` for `dev-time-only` or `one-shot-setup` capabilities.
- Do not place dev-only files (verify, setup, install contract, test fixtures) in `scripts/` or the workspace root. Use `dev/`.
- Do not mix FlowyClaw defaults with workspace-private rules as if they were platform facts.
- Do not emit `PROMOTION_ANALYSIS.md`, `WORKSPACE_SEMANTICS.md`, or any other extra governance file in V1.3.
- Do not use `scaffold` mode to overwrite an existing agent workspace in V1.3.
- Do not use `optimize` mode to rewrite files in place. Preview only.

## Pre-Delivery Checklist

- [ ] The proposal uses this order exactly:
  1. 判断结果
  2. 升格理由
  3. `Agent Promotion Analysis`
  4. `Workspace Semantics`
  5. 四文件映射
  6. 风险与非承诺能力
- [ ] `Agent Promotion Analysis` is complete before any scaffold step
- [ ] `Workspace Semantics` distinguishes `final / state / preview / export / skill resources`
- [ ] If applicable, `workflow_hardening` distinguishes canonical source from derived exports
- [ ] `Preferred control pattern` is explicit
- [ ] `Native / Conditional / Unsupported` capability classes are explicit
- [ ] `Resume Strategy` is explicit and belongs in `AGENTS.md`
- [ ] `Red Lines` is explicit and belongs in `AGENTS.md`
- [ ] Compaction-critical rules live in `Session Startup` or `Red Lines`
- [ ] Repeated actions are backed by deterministic helpers or explicit contracts when needed
- [ ] Each conditional capability is classified as `runtime-conditional` / `dev-time-only` / `one-shot-setup`
- [ ] Install contract (`dev/.openclaw-agent-install.json`) exists only when `runtime-conditional` capabilities exist and agent cannot self-install
- [ ] Dev-only files are under `dev/` and marked `shipped: false` in Workspace Semantics
- [ ] Local asset handling uses a staging rule and portable relative-path policy when needed
- [ ] `scaffold` mode writes `IDENTITY.md`, `SOUL.md`, `AGENTS.md`, `TOOLS.md`, and optionally `BOOTSTRAP.md`, `USER.md`, `HEARTBEAT.md`
- [ ] Character budget: 12,000 chars per file, 60,000 chars total (aligned with OpenClaw source)
- [ ] Existing root files are not overwritten in V1.3
- [ ] `optimize` mode writes only preview artifacts outside the target workspace
- [ ] Host assumptions are correct for `flowyclaw` vs `generic-openclaw`
