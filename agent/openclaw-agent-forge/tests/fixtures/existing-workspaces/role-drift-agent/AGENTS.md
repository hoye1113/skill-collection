# AGENTS.md

## Workspace Positioning

This workspace exists to design and scaffold OpenClaw agent workspaces from structured briefs.

## Session Startup

- Read SOUL.md, IDENTITY.md, TOOLS.md, and USER.md if present.
- Inspect existing proposal artifacts before continuing.

## Red Lines

- Do not skip promotion analysis before changing root files.
- Keep compaction-critical rules in Session Startup or Red Lines.
- Do not overwrite an existing workspace in place during scaffold or optimize.

## Default Behavior

- Default to propose mode.
- Stop before writing files unless scaffold was explicitly requested.

## Preferred Control Pattern

- routing

## Resume Strategy

- Global resume file: AGENTS.md
- Task/topic resume file: state/current-proposal.json
- Deliverable inspection path: workspace/
- If state missing: Inspect the latest workspace draft and rebuild the proposal state from files.
- Never assume: Never assume a promotion decision without re-checking the proposal artifacts.

## Boundaries

- Do not overwrite existing root files in V1.3.
- Do not claim plugin capabilities from prompt logic alone.

## Workspace Layout

- skills/ - packaged local skills
- state/ - reusable proposal state
- exports/ - optional packaged artifacts
