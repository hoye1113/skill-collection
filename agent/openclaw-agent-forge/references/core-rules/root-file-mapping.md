# Root File Mapping

Use this reference when converting the proposal into `IDENTITY.md`, `SOUL.md`, `AGENTS.md`, `TOOLS.md`, and optionally `BOOTSTRAP.md`, `USER.md`, `HEARTBEAT.md`.

## Table of Contents

- [Root File Roles](#root-file-roles)
- [What Stays in the Skill](#what-stays-in-the-skill)
- [What Moves to Root Files](#what-moves-to-root-files)
- [Required Headings for V1.3 Scaffold](#required-headings-for-v13-scaffold)
- [Resume Strategy Template](#resume-strategy-template)
- [Workspace Semantics Minimum](#workspace-semantics-minimum)
- [V1.3 Boundaries](#v13-boundaries)

## Root File Roles

| File | Owns | Keep out |
|------|------|----------|
| `IDENTITY.md` | name, role, public identity, durable mission | parameters, path tables, scripts, long workflow checklists |
| `SOUL.md` | lazy default, non-negotiables, enduring style, quality bar | scripts, paths, task-by-task instructions |
| `AGENTS.md` | workspace positioning, session startup, red lines, resume strategy, boundaries, layout | copied references, detailed script docs, parameter systems |
| `TOOLS.md` | output roots, local conventions, capability boundaries, skill resources | persona, philosophy, copied workflow bodies |
| `BOOTSTRAP.md` | first-run onboarding conversation flow | long-term rules, capability docs |
| `USER.md` | human user profile (name, pronouns, timezone) | agent persona, workflow details |
| `HEARTBEAT.md` | heartbeat polling task checklist | long-term rules, persona |
| `MEMORY.md` | curated long-term memory (loaded last, main session only) | workflow details, scripts |

## What Stays in the Skill

Keep these in `SKILL.md` or `references/`:

- trigger language
- workflow checklist
- confirmation gates
- parameter flags
- script invocation details
- detailed references
- pre-delivery checklist

## What Moves to Root Files

Move only long-lived contract into root files:

- durable identity
- durable quality bars
- resume entry rules
- overwrite and boundary rules
- workspace path semantics
- capability declarations

## Required Headings for V1.3 Scaffold

`IDENTITY.md`

- `# IDENTITY.md`
- `## Public Identity`

`SOUL.md`

- `# SOUL.md`
- `## Non-Negotiables`
- `## Enduring Style`

`AGENTS.md`

- `# AGENTS.md`
- `## Workspace Positioning`
- `## Session Startup`
- `## Red Lines`
- `## Default Behavior`
- `## Resume Strategy`
- `## Boundaries`
- `## Workspace Layout`

`TOOLS.md`

- `# TOOLS.md`
- `## Output Roots`
- `## Local Conventions`
- `## Capabilities`
- `## Skill Resources`

Optional files (generated when spec includes corresponding config):

`BOOTSTRAP.md`

- `# BOOTSTRAP.md`

`USER.md`

- `# USER.md`

`HEARTBEAT.md`

- `# HEARTBEAT.md`

## Resume Strategy Template

Use this contract in the scaffold spec:

```json
{
  "resume_strategy": {
    "global_resume_file": "",
    "task_topic_resume_file": "",
    "deliverable_inspection_path": "",
    "if_state_missing": "",
    "never_assume": ""
  }
}
```

## Workspace Semantics Minimum

Before scaffolding, the proposal must already distinguish:

- final deliverables
- workflow state
- scratch or preview
- export or package
- skill resources

Each entry must include a `shipped` field (`true` / `false`) to indicate whether the path is part of the delivered agent workspace or is a dev-only artifact.

Do not scaffold a workspace if those categories are still mixed together.

## V1.3 Boundaries

- Do not generate `PROMOTION_ANALYSIS.md`, `WORKSPACE_SEMANTICS.md`, or other extra governance files.
- Do not turn root files into a restatement of the full skill workflow.
- Do not overwrite existing root files in V1.3.
- Keep compaction-critical rules in `Session Startup` or `Red Lines`, not in side notes.
- Optional files (`BOOTSTRAP.md`, `USER.md`, `HEARTBEAT.md`) may be generated when the spec includes the corresponding config. They are not required.
- Character budget: 12,000 chars per file, 60,000 chars total.
