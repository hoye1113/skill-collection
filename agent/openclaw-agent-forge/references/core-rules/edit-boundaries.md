# Edit Boundaries

Each root-file section has a modification contract. Agents MUST follow these
boundaries when applying optimize recommendations.

**Key principle**: Modify only the flagged sections — do not rewrite entire files.

## AGENTS.md

| Section | Allowed | Forbidden |
|---------|---------|-----------|
| ## Workspace Positioning | Refine wording | Remove entirely |
| ## Session Startup | Add/remove entries | Remove all entries, change structure |
| ## Red Lines | Add more specific rules | Delete existing rules (only refine) |
| ## Default Behavior | Add/remove entries | — |
| ## Resume Strategy | Update paths/strategy text | Delete any of the 5 required labels |
| ## Boundaries | Add new boundaries | Relax/remove existing boundaries |
| ## Workspace Layout | Add/update path descriptions | Delete existing paths |
| ## Preferred Control Pattern | Update pattern name | Remove section |

## IDENTITY.md

| Section | Allowed | Forbidden |
|---------|---------|-----------|
| ## Public Identity | Refine wording | Remove entirely |

## SOUL.md

| Section | Allowed | Forbidden |
|---------|---------|-----------|
| ## Non-Negotiables | Add stricter rules | Remove existing rules |
| ## Enduring Style | Add new traits | Remove existing traits |

## TOOLS.md

| Section | Allowed | Forbidden |
|---------|---------|-----------|
| ## Output Roots | Add/update path descriptions | Remove existing paths |
| ## Local Conventions | Add new conventions | Remove existing conventions |
| ## Capabilities | Add/reclassify | Remove native capabilities |
| ## Skill Resources | Add/update paths | Remove primary entrypoints |

## Monotonic Sections (Never Shrink)

The following sections are **monotonic** — they may only grow, never shrink:

- **Red Lines** in AGENTS.md
- **Non-Negotiables** in SOUL.md
- **Boundaries** in AGENTS.md

The optimize report's invariant checks will flag any shrinkage as a FAIL.
