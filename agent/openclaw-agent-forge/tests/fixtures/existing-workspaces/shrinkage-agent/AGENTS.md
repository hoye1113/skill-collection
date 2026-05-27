# AGENTS.md

## Workspace Positioning

This workspace manages ETL pipelines and data quality monitoring for the analytics team.

## Session Startup

- Read AGENTS.md and SOUL.md
- Check pipeline status dashboard
- Review recent failure logs

## Red Lines

- Never modify production schemas without approval

## Default Behavior

- Run diagnostics before any pipeline change
- Add retry logic for transient failures

## Resume Strategy

- Global resume file: AGENTS.md
- Task/topic resume file: state/current-pipeline.json
- Deliverable inspection path: pipelines/
- If state missing: Check pipeline status dashboard for last run
- Never assume: Never assume a pipeline succeeded without checking logs

## Boundaries

- Do not access databases outside the analytics namespace
- Do not deploy pipelines without running test suite first

## Workspace Layout

- pipelines/ - pipeline definitions
- state/ - run state and logs
- data/ - staging area
