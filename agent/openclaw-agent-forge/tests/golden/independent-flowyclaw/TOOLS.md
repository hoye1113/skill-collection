# TOOLS.md

## Output Roots

- workspace/ - canonical root-file scaffold
- exports/ - replaceable package outputs

## Local Conventions

- Treat flowyclaw as the default host profile.
- Keep resume rules inside AGENTS.md.

## Capabilities

### Native capability

- Read and write local Markdown root files
- Maintain structured proposal specs

### Conditional capability

- Host guarantees that depend on flowyclaw defaults

### Unsupported / non-capability

- Plugin-level runtime extensions
- Direct in-place optimization of existing agents in V1.3

## Skill Resources

### Primary skill entrypoints

- skills-main/openclaw-agent-forge/SKILL.md

### High-priority references

- references/core-rules/promotion-decision.md
- references/core-rules/root-file-mapping.md

### Conditional scripts

- scripts/render_root_files.py
- scripts/validate_agent_output.py
