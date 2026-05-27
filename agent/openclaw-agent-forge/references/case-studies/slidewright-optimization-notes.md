# Slidewright Optimization Notes

Use this reference when optimizing an existing OpenClaw / FlowyClaw agent workspace, or when extracting reusable patterns from a real agent hardening pass.

## Table of Contents

- [What Made This Agent Worth Optimizing](#what-made-this-agent-worth-optimizing)
- [Reusable Optimization Patterns](#reusable-optimization-patterns)
  - [1. Prefer Contract-Backed Workflows Over Prompt-Only Rules](#1-prefer-contract-backed-workflows-over-prompt-only-rules)
  - [2. Keep Root Files High-Level, But Put Compaction-Critical Rules in Session Startup or Red Lines](#2-keep-root-files-high-level-but-put-compaction-critical-rules-in-session-startup-or-red-lines)
  - [3. Separate Canonical Source From Derived Artifacts](#3-separate-canonical-source-from-derived-artifacts)
  - [4. Use Confirmation Gates for Non-Obvious Workflow Decisions](#4-use-confirmation-gates-for-non-obvious-workflow-decisions)
  - [5. Derived Exporters Should Consume a Strict Interface, Not Infer Structure](#5-derived-exporters-should-consume-a-strict-interface-not-infer-structure)
  - [6. Conditional Runtimes Need a Host-Level Install Contract](#6-conditional-runtimes-need-a-host-level-install-contract)
  - [7. For File-Based Artifacts, Stable Relative Paths Beat "Smart" Prompting](#7-for-file-based-artifacts-stable-relative-paths-beat-smart-prompting)
  - [8. Sidecar Skills Work Best When Their Write Responsibilities Are Clear](#8-sidecar-skills-work-best-when-their-write-responsibilities-are-clear)
  - [9. Design Quality Rules Need Both Philosophy and Workflow Placement](#9-design-quality-rules-need-both-philosophy-and-workflow-placement)
  - [10. Routing vs Locked Sidecar](#10-routing-vs-locked-sidecar)
  - [11. Preview HTML Parity With Runtime](#11-preview-html-parity-with-runtime)
  - [12. Preview Opening vs Export Subsystem](#12-preview-opening-vs-export-subsystem)
  - [13. Agent Write Hygiene](#13-agent-write-hygiene)
  - [14. Runtime State Contract File](#14-runtime-state-contract-file)
  - [15. Machine-Parseable Validator Error Messages](#15-machine-parseable-validator-error-messages)
  - [16. Large-File Truncation Detection](#16-large-file-truncation-detection)
  - [17. Automated Sync Scripts for Multi-File Consistency](#17-automated-sync-scripts-for-multi-file-consistency)
- [High-Value Failure Patterns To Watch For](#high-value-failure-patterns-to-watch-for)
- [Practical Suggestions For openclaw-agent-forge](#practical-suggestions-for-openclaw-agent-forge)
  - [Promotion Analysis Heuristics](#promotion-analysis-heuristics)
  - [Root-File Optimization Heuristics](#root-file-optimization-heuristics)
  - [Skill Review Heuristics](#skill-review-heuristics)
  - [Export / Delivery Heuristics](#export--delivery-heuristics)
  - [Asset Handling Heuristics](#asset-handling-heuristics)
- [What Should Be Reused As Patterns, Not Copied Blindly](#what-should-be-reused-as-patterns-not-copied-blindly)
- [Compact Reusable Checklist](#compact-reusable-checklist)
- [Suggested Use](#suggested-use)

This document summarizes the high-value changes made while iterating on `workspace-frontend-slides` (`Slidewright`). The goal is not to preserve a changelog. The goal is to capture reusable agent-generation rules, workflow contracts, and failure patterns that should inform future agent scaffolds and optimization passes.

## What Made This Agent Worth Optimizing

`Slidewright` is a good example of an agent that needed more than root-file cleanup. Its behavior depended on:

- canonical deliverables vs derived exports
- resume-safe workflow state
- a strict preview gate before delivery
- conditional runtimes for PPTX handoff
- deterministic scripts instead of prompt-only instructions
- deck-specific design rules that must survive compaction

That makes it a strong reference case for `openclaw-agent-forge`: many failures came from the gap between "document says so" and "workspace can actually do it."

## Reusable Optimization Patterns

### 1. Prefer Contract-Backed Workflows Over Prompt-Only Rules

The biggest improvements came from turning soft instructions into explicit contracts.

Examples:

- HTML preview was originally described as "should open for the user" but had no stable opener. The correct fix was to add a deterministic preview opener script and then reference it in workflow docs.
- HTML-to-PPTX export originally depended on "wait and screenshot." The correct fix was to define an export contract (`window.__SLIDEWRIGHT_EXPORT__`) and require the exporter to consume that contract.
- Local image handling originally said "use relative paths," but there was no staging step. The correct fix was to add a dedicated asset-staging script and forbid direct absolute file references in final deck content.

**Reusable rule**:

- If an agent says it can reliably perform a repeated action, that action should usually be backed by a script, runtime contract, or machine-checkable file convention.

### 2. Keep Root Files High-Level, But Put Compaction-Critical Rules in `Session Startup` or `Red Lines`

One recurring failure mode was that important workflow constraints were written in places that were easy to lose during long sessions.

The fix was not "move everything into `AGENTS.md`." The fix was:

- keep root files focused on governance and boundaries
- move skill detail back into `SKILL.md`
- but ensure compaction-critical rules live in `Session Startup` or `Red Lines`

For `Slidewright`, examples of compaction-critical rules were:

- HTML-first confirmation gate
- do not export before user preview approval
- do not reopen a locked design system during resume
- treat HTML as canonical and PPTX as derived
- forbid OS absolute file paths in final deck content

**Reusable rule**:

- If losing a rule after compaction would cause wrong routing, wrong deliverables, or destructive behavior, that rule belongs in `Session Startup` or `Red Lines`.

### 3. Separate Canonical Source From Derived Artifacts

One of the highest-value structural improvements was making deliverable classes explicit.

For `Slidewright`:

- canonical source: HTML deck in `slides/`
- workflow state: `state/{deck-name}.md`
- scratch / previews: `slide-previews/`
- derived exports: `exports/`

This distinction solved multiple downstream issues:

- resume logic became safer
- PPTX export stopped competing with HTML generation
- preview files stopped being treated as final deliverables
- auditing gained a stable target

**Reusable rule**:

- Every non-trivial agent should explicitly define `final / state / preview / export / skill-resources`.
- Never let derived exports drift into the same semantic bucket as canonical outputs.

### 4. Use Confirmation Gates for Non-Obvious Workflow Decisions

The original presentation workflow treated "PPT" as ambiguous. That caused bad routing and premature exports.

The fix was to add a real `Deliverable Confirmation Gate`:

- explain why HTML is preferred
- ask whether HTML is acceptable as the primary generation path
- distinguish `ppt handoff` from `editable/template/native PPTX`

Later, a second blocking gate became necessary:

- preview and user approval must happen before any PPTX export

**Reusable rule**:

- Add explicit confirmation gates whenever a request commonly arrives in ambiguous shorthand.
- Route only after the ambiguity is resolved.

### 5. Derived Exporters Should Consume a Strict Interface, Not Infer Structure

The HTML-to-PPTX exporter originally tried to infer slide boundaries and screenshot timing. That failed in multiple ways:

- blank slides because animation had not finished
- repeated cover slides because the runtime never truly advanced
- wrong captures because viewport slicing was not equivalent to slide selection

The durable fix was to make the exporter consume a strict export interface:

- `window.__SLIDEWRIGHT_EXPORT__.version`
- `getSlideCount()`
- `prepareSlide(index)`

And then enforce:

- final static state, not transient animation frames
- element-level capture, not blind viewport cropping
- fail-fast when the contract is missing or invalid

**Reusable rule**:

- For export or delivery skills, prefer "strict interface + fail-fast" over "best effort + silent fallback."

**Export capture detail**:

When the export pipeline uses headless browser screenshots, element-level capture methods (e.g., `element.screenshot()`) can produce misaligned results in non-standard layouts (horizontal scrolling, custom viewport units like `100dvh`). Prefer page-level capture with explicit clip coordinates:

- Use `page.screenshot({ clip: { x, y, width, height } })` instead of `element.screenshot()`
- Calculate clip coordinates from `getBoundingClientRect()` + `window.scrollX/scrollY`
- Eliminate viewport unit ambiguity with CSS forced pixel dimensions in export mode (e.g., `width: 1920px !important`)
- When scroll positioning may be unreliable, use CSS `transform: translateX()` as a fallback positioning strategy

### 6. Conditional Runtimes Need a Host-Level Install Contract

`Slidewright` needed extra runtime preparation for `html-to-pptx`. The right place for that was not scattered prose in skill docs. It was the dev-level install contract:

- `dev/.openclaw-agent-install.json`
- `dev/setup.py` script
- `dev/verify.py` script

This made the capability boundary honest:

- the skill exists
- the runtime may be conditional
- the host has a standard way to set it up and verify it
- the install contract lives in `dev/` (not shipped) because no runtime consumer reads it

**Reusable rule**:

- If a workspace needs environment prep, prefer `dev/.openclaw-agent-install.json` plus `dev/setup.py` and `dev/verify.py`.
- Keep `TOOLS.md` as the explanation layer, not the installation mechanism.
- Place the install contract in `dev/` — it is a deployment declaration, not an agent runtime dependency.

### 7. For File-Based Artifacts, Stable Relative Paths Beat "Smart" Prompting

One late-stage failure in `Slidewright` was that user-provided local images were ending up in final HTML as `D:\...` absolute paths.

The fix was not "tell the model to remember relative paths better." The fix was:

- define a deck-local asset root
- add a staging script
- require the workflow to stage local images before writing HTML
- audit absolute-path leakage as a delivery failure

The durable pattern became:

- if local images exist, switch to a multi-file output pattern
- copy those images into a deck-local `assets/` folder
- write only returned relative refs into final HTML/CSS

**Reusable rule**:

- When a workspace produces portable deliverables, never trust the model to hand-author file references reliably at scale.
- Add a staging tool and make the final content consume its output.

### 8. Sidecar Skills Work Best When Their Write Responsibilities Are Clear

The agent improved when responsibilities were narrowed:

- `frontend-slides` owns canonical deck creation/editing and asset staging
- `slide-asset-curation` owns selection and mapping, not file copying
- `html-to-pptx` owns derived PPTX handoff only
- `deck-audit` owns findings and severity

This avoided skill overlap and reduced "who is allowed to mutate what?" confusion.

**Reusable rule**:

- Sidecar skills should either:
  - analyze and recommend, or
  - perform bounded deterministic mutations
- Avoid giving multiple skills overlapping write authority over the same artifact root.

### 9. Design Quality Rules Need Both Philosophy and Workflow Placement

Borrowing design guidance from a stronger web-design prompt only worked when it was split by responsibility:

- root files got enduring quality bars
- `frontend-slides` got design-context and v0-direction workflow gates
- `slide-visual-builder` got anti-slop visual rules
- `deck-audit` got content-honesty and system-consistency checks

Copying a long prompt directly into `AGENTS.md` would have been wrong.

**Reusable rule**:

- Design philosophy belongs in multiple layers:
  - long-lived values in `SOUL.md`
  - workflow gates in the primary skill
  - anti-patterns in specialized sidecars
  - delivery enforcement in audit

### 10. Routing vs Locked Sidecar

Documentation sometimes lists **multiple candidates** (parallel stacks, alternate recipes, optional themes). That is fine for discovery.

Failure mode: prose implies that **before any confirmation**, one visual stack or sidecar is already the default — so routing jumps to half-loaded behavior while another recipe stays dormant.

**Reusable rule**:

- Separate **routing language** ("here are options") from **locked configuration** ("after gate X, load recipe Y / sidecar Z").
- After a design system or export path is locked, subsequent docs should load **that** contract explicitly — not a blend of option A's wording with option B's file paths.

### 11. Preview HTML Parity With Runtime

If docs promise keyboard navigation, overview modes, horizontal snapping, or a named controller (`#deck`, export hooks), the **preview shell must ship the same runtime story** as the canonical deliverable — or the docs must **narrow** the claim.

Anti-pattern: the specification describes `#deck` and a controller bundle, but the preview template omits those scripts; the page "scrolls" natively while shortcuts and contracts silently fail.

**Reusable rule**:

- Treat preview HTML as part of the **same contract** as shipped HTML when UX parity is advertised.

### 12. Preview Opening vs Export Subsystem

**Opening a local HTML file** in a browser (or host-equivalent) for human review is one transport story.

**Export or capture pipelines** (headless screenshot, PDF, packaged capture) may require a **different channel** — for example a short-lived HTTP server so automation can load assets with stable origins.

Failure mode: documentation or tooling hints blur the two; contributors assume "a server must always be up" before **any** preview, or conversely that export-time networking quirks apply to daily local review.

**Reusable rule**:

- Name **preview entry** vs **export/capture transport** explicitly in workflow docs so neither path is mistaken for the other.

### 13. Agent Write Hygiene

Tooling that writes files must receive **path plus full body**. Half-supplied writes fail predictably across hosts.

Large generations hit **single-invocation payload limits** in some environments (often stricter on Windows-class hosts). When content truncates mid-file, **incremental edits**, **chunked writes**, or **stdin / small helper scripts** beat one giant patch.

**Reusable rule**:

- Prefer targeted edits over wholesale replacement; scale up write strategy before blaming the model.

**Complementary read-side detection**:

Write-side defense (incremental edits, chunked writes) reduces truncation risk but does not eliminate it. Add a post-write validation step that checks document closure (closing tags present) and structural integrity (balanced braces). This catches the failure mode where a large write silently truncates mid-function — a common issue on Windows hosts with stricter tool payload limits.

### 14. Runtime State Contract File

Long-lived workspace docs should distinguish:

- **Human-facing contract** in a stable, indexed location (often `contracts/STATE.md` or similar): how final outputs, state, previews, and exports relate — **not** necessarily co-located with the OpenClaw root quartet; `AGENTS.md` / `TOOLS.md` should name the path.
- **`state/` (or equivalent)**: machine-oriented resume bullets — gate status, pointers, short checkpoints — **not** copies of canonical bodies.

Collaboration and audit should anchor on **canonical deliverables** plus the host's review process — not on treating ephemeral working trees as shared truth unless your deployment says so.

**Reusable rule**:

- Keep runtime state **light**; never use it as a dumpster for generated chapters or full duplicate decks.

### 15. Machine-Parseable Validator Error Messages

Validators that only report "what is wrong" force human interpretation before repair can begin. Adding a structured remediation instruction to each error message enables automated or semi-automated repair loops.

Example convention: suffix every error with `— fix: <actionable instruction>`. Downstream tools can split on the delimiter to extract both the diagnosis and the prescribed repair step.

This is a deeper layer than "contract-backed workflows" (Pattern 1). Pattern 1 says "use a validator." Pattern 15 says "make the validator's output machine-consumable so repair can be scripted."

**Reusable rule**:

- When a validator is part of a repeated workflow, structure error messages with a parseable delimiter separating diagnosis from remediation.
- Do not rely on the model to interpret free-text error descriptions reliably across sessions.

### 16. Large-File Truncation Detection

Pattern 13 addresses write-side defense (chunked writes, incremental edits). But when write-side defense fails — for example, a Windows tool size limit silently truncates a large HTML file — the corruption may go undetected until runtime.

The complementary read-side defense checks:

- **Document closure**: verify closing tags (e.g., `</script>`, `</body>`, `</html>`) are present
- **Structural completeness**: verify balanced braces in script blocks (no mid-function truncation)
- **Instantiation presence**: verify expected entry points exist after the script block

These checks are cheap to run as a post-write validation step and catch a class of silent corruption that content-level validators miss.

**Reusable rule**:

- Write-side defense (chunked writes) + read-side detection (closure tags, structural completeness) = complete truncation tolerance.
- Treat a truncated file as a hard validation failure, not a cosmetic issue.

### 17. Automated Sync Scripts for Multi-File Consistency

When a canonical implementation must be copied into multiple template or shell files, manual copying is error-prone: versions drift, patches are missed, and the agent may silently hand-write a "simpler" replacement.

A dedicated sync script can:

- Locate the canonical source and all target files
- Replace embedded copies (e.g., script blocks) with the current source
- Auto-increment a version constant in all locations
- Create backups before modification
- Support `--dry-run` for previewing changes
- Run a post-sync validation to confirm consistency

This pattern transforms a fragile agent behavior ("remember to copy the controller") into a deterministic mechanical action.

**Reusable rule**:

- When multiple files must stay in sync with a canonical source, prefer a sync script over agent-managed copying.
- The script should own: version bumping, backup, dry-run preview, and post-sync validation.

## High-Value Failure Patterns To Watch For

These failures showed up during optimization and are worth treating as recurring review prompts.

### Root-File Drift

- `AGENTS.md` starts carrying detailed workflow prose that belongs in skills
- `TOOLS.md` starts mixing host facts with workspace-private rules
- `Session Startup` stops containing the rules that actually matter during resume

### Capability Inflation

- a script exists, so the capability gets mislabeled as native
- docs imply support for image generation, deployment, or browser automation without a verified path
- "can probably work" gets documented like "is guaranteed"

### Derived-Artifact Confusion

- preview outputs treated as final deliverables
- exports treated as canonical source
- PPTX handoff described as editable/template-grade output when it is only a derived export

### Prompt-Only Workflow Drift

- docs say "open preview", "use relative paths", or "wait for readiness", but no deterministic mechanism exists
- the agent appears smart in writing but fails under repetition

### Audit Too Late, Not Early Enough

- absolute asset paths are only discovered after export
- content honesty issues are caught as polish instead of delivery blockers
- unresolved direction checkpoints still allow downstream export

## Practical Suggestions For `openclaw-agent-forge`

When generating or optimizing future agents, bake these heuristics into the skill's reasoning:

### Promotion Analysis Heuristics

Explicitly ask:

- Does this workspace need canonical vs derived artifact separation?
- Does this workflow require preview or approval gates?
- Are any capabilities conditional on runtime install contracts?
- Are there repeated actions that should be backed by scripts instead of prose?
- Will compaction lose any non-negotiable workflow state unless it is elevated?

### Root-File Optimization Heuristics

During optimize/review mode, specifically check:

- Are compaction-critical rules located in `Session Startup` or `Red Lines`?
- Are `Native / Conditional / Unsupported` boundaries honest?
- Are final/state/preview/export paths separated?
- Is there any rule in root files that should really be moved back into a skill?

### Skill Review Heuristics

Look for cases where a skill says:

- "attempt to"
- "try to"
- "if supported"
- "use relative paths"
- "wait a bit"

These phrases are often signs that the workspace still needs a deterministic helper script or contract.

### Export / Delivery Heuristics

For any export skill, ask:

- What is the canonical source?
- What exact contract does the exporter consume?
- What must be true before export is allowed?
- What failures should block export instead of producing a bad artifact?

### Asset Handling Heuristics

For any agent that references user-provided local files, ask:

- Is there a staging step?
- Is the final output portable if moved to another directory?
- Are absolute path leaks treated as delivery failures?

## What Should Be Reused As Patterns, Not Copied Blindly

These are good patterns from `Slidewright`, but should be adapted instead of copied verbatim:

- HTML-first confirmation gate
- canonical-vs-derived output semantics
- preview approval before downstream export
- strict exporter contract
- install-contract verification through `dev/.openclaw-agent-install.json`
- relative-path staging for local assets
- design-context and direction-checkpoint gates
- severity-based audit with explicit honesty checks
- explicit routing vs locked sidecar after confirmation gates
- preview/runtime parity when UX claims match production behavior
- distinguishing preview open from export-pipeline transport
- disciplined multi-step writes for large artifacts
- `contracts/` (or equivalent) for long-lived workspace contracts plus lightweight `state/` checkpoints; root `AGENTS`/`TOOLS` index the path

These should **not** be copied blindly into unrelated agents:

- presentation-specific wording
- slide-count thresholds
- PPTX-specific contract names
- deck-specific directory names such as `slide-previews/`
- animation/export assumptions tied to browser-native slides

## Compact Reusable Checklist

Use this when reviewing whether an existing agent needs the same kind of hardening:

- [ ] Canonical outputs are separated from derived exports
- [ ] Workflow state has an explicit resume entry
- [ ] Compaction-critical rules live in `Session Startup` or `Red Lines`
- [ ] Ambiguous user requests go through a real confirmation gate
- [ ] Repeated actions are backed by scripts or explicit contracts
- [ ] Conditional runtimes use `dev/.openclaw-agent-install.json` instead of prose-only setup instructions
- [ ] Exporters consume strict interfaces and fail fast on invalid input
- [ ] Local file references are staged and rewritten to relative paths
- [ ] Specialized sidecar skills have non-overlapping write responsibility
- [ ] Audit treats structural portability failures as real findings, not polish
- [ ] Routing docs do not imply a default stack before confirmation; locked recipes load explicitly after gates
- [ ] Preview HTML includes the same runtime contract as claimed (or docs narrow the claim)
- [ ] Human preview entry is documented separately from export/capture transport requirements
- [ ] Large writes use incremental or chunked strategies when single-shot payloads would exceed limits
- [ ] Runtime state stays light and does not duplicate canonical bodies; long-lived contract lives under an indexed path (e.g. `contracts/STATE.md`) and `AGENTS`/`TOOLS` point to it
- [ ] Validator error messages include machine-parseable remediation instructions (not just diagnosis)
- [ ] Large file writes are followed by closure-tag and structural-completeness checks
- [ ] Multi-file sync uses a dedicated script with version bumping, dry-run, and post-sync validation
- [ ] "Verbatim copy" rules are enforced by content-level comparison (not just feature-name checks) in the post-write validator

## Suggested Use

Use this note as:

- a review aid when optimizing an existing agent
- a pattern source when improving `openclaw-agent-forge`
- a checklist when deciding whether a workflow needs new scripts, stricter contracts, or better root-file placement

Do not use it as a template to mechanically copy wording into future agents. Reuse the reasoning, not the surface form.
