#!/usr/bin/env python3
"""Infer a minimal OpenClaw agent spec from existing workspace root files.

Usage:
    python infer_spec.py --workspace <dir> --out <spec.json> [--host flowyclaw|generic-openclaw]

Scans IDENTITY.md, SOUL.md, AGENTS.md, TOOLS.md (and optional BOOTSTRAP.md,
USER.md, HEARTBEAT.md) and produces a JSON spec suitable for --lite optimize.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from spec_contract import ALL_POSSIBLE_ROOT_FILES, ROOT_FILENAMES


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

def _extract_section_content(text: str, heading: str) -> str:
    """Return all text between *heading* and the next ## heading (exclusive)."""
    pattern = re.compile(r"^" + re.escape(heading) + r"\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def _extract_bullet_list(text: str, heading: str) -> list[str]:
    """Extract `- item` lines under *heading*."""
    section = _extract_section_content(text, heading)
    return [
        m.group(1).strip()
        for m in re.finditer(r"^-\s+(.+)$", section, re.MULTILINE)
        if m.group(1).strip()
    ]


def _extract_labeled_items(text: str, heading: str) -> dict[str, str]:
    """Extract `- Label: value` lines under *heading*."""
    section = _extract_section_content(text, heading)
    result: dict[str, str] = {}
    for m in re.finditer(r"^-\s+(.+?):\s*(.+)$", section, re.MULTILINE):
        key = m.group(1).strip().lower().replace(" ", "_").replace("/", "_")
        result[key] = m.group(2).strip()
    return result


def _extract_subsections(text: str, heading: str) -> dict[str, list[str]]:
    """Extract ### sub-headings and their bullet lists under *heading*."""
    section = _extract_section_content(text, heading)
    result: dict[str, list[str]] = {}
    current_title: str | None = None
    current_items: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("### "):
            if current_title and current_items:
                result[current_title] = current_items
            current_title = stripped[4:].strip()
            current_items = []
        elif stripped.startswith("- ") and current_title:
            item = stripped[2:].strip()
            if item:
                current_items.append(item)
    if current_title and current_items:
        result[current_title] = current_items
    return result


def _read_file(workspace_dir: Path, filename: str) -> str:
    path = workspace_dir / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


# ---------------------------------------------------------------------------
# Per-file inference
# ---------------------------------------------------------------------------

def _infer_from_identity(text: str) -> dict[str, Any]:
    spec: dict[str, Any] = {}
    name_match = re.search(r"^-\s+Name:\s*(.+)$", text, re.MULTILINE)
    if name_match:
        spec["name"] = name_match.group(1).strip()
    role_match = re.search(r"^-\s+Role:\s*(.+)$", text, re.MULTILINE)
    if role_match:
        spec["role"] = role_match.group(1).strip()
    public = _extract_section_content(text, "## Public Identity")
    if public:
        spec["public_identity"] = public
    else:
        # Fallback: use name + role as public identity
        parts = []
        if spec.get("name"):
            parts.append(spec["name"])
        if spec.get("role"):
            parts.append(spec["role"])
        if parts:
            spec["public_identity"] = ". ".join(parts)
    return spec


def _infer_from_soul(text: str) -> dict[str, Any]:
    spec: dict[str, Any] = {}
    non_neg = _extract_bullet_list(text, "## Non-Negotiables")
    if non_neg:
        spec["non_negotiables"] = non_neg
    style = _extract_bullet_list(text, "## Enduring Style")
    if style:
        spec["enduring_style"] = style
    lazy = _extract_section_content(text, "## Lazy Default to Avoid")
    if lazy:
        spec["lazy_default_to_avoid"] = lazy
    return spec


def _infer_from_agents(text: str) -> dict[str, Any]:
    spec: dict[str, Any] = {}

    positioning = _extract_section_content(text, "## Workspace Positioning")
    if positioning:
        spec["workspace_positioning"] = positioning

    session = _extract_bullet_list(text, "## Session Startup")
    if session:
        spec["session_startup"] = session

    red = _extract_bullet_list(text, "## Red Lines")
    if red:
        spec["red_lines"] = red

    default = _extract_bullet_list(text, "## Default Behavior")
    if default:
        spec["default_behavior"] = default

    boundaries = _extract_bullet_list(text, "## Boundaries")
    if boundaries:
        spec["boundaries"] = boundaries

    layout = _extract_bullet_list(text, "## Workspace Layout")
    if layout:
        spec["workspace_layout"] = layout

    # Resume Strategy
    resume_items = _extract_labeled_items(text, "## Resume Strategy")
    if resume_items:
        spec["resume_strategy"] = {
            "global_resume_file": resume_items.get("global_resume_file", ""),
            "task_topic_resume_file": resume_items.get("task_topic_resume_file", ""),
            "deliverable_inspection_path": resume_items.get("deliverable_inspection_path", ""),
            "if_state_missing": resume_items.get("if_state_missing", ""),
            "never_assume": resume_items.get("never_assume", ""),
        }

    # Preferred Control Pattern
    pattern_section = _extract_section_content(text, "## Preferred Control Pattern")
    if pattern_section:
        pattern_match = re.search(r"^-\s+(.+)$", pattern_section, re.MULTILINE)
        if pattern_match:
            spec["preferred_control_pattern"] = pattern_match.group(1).strip()

    return spec


_CAPABILITY_SUBSECTION_MAP = {
    "native capability": "native",
    "conditional capability": "conditional",
    "unsupported / non-capability": "unsupported",
}


def _infer_capabilities(text: str) -> dict[str, list[str]]:
    subsections = _extract_subsections(text, "## Capabilities")
    result: dict[str, list[str]] = {"native": [], "conditional": [], "unsupported": []}
    for title, items in subsections.items():
        key = _CAPABILITY_SUBSECTION_MAP.get(title.lower())
        if key and items:
            result[key] = items
    return result


_RESOURCE_SUBSECTION_MAP = {
    "primary skill entrypoints": "primary_skill_entrypoints",
    "high-priority references": "high_priority_references",
    "conditional scripts": "conditional_scripts",
}


def _infer_skill_resources(text: str) -> dict[str, list[str]]:
    subsections = _extract_subsections(text, "## Skill Resources")
    result: dict[str, list[str]] = {}
    for title, items in subsections.items():
        key = _RESOURCE_SUBSECTION_MAP.get(title.lower())
        if key and items:
            result[key] = items
    return result


def _infer_from_tools(text: str) -> dict[str, Any]:
    spec: dict[str, Any] = {}
    roots = _extract_bullet_list(text, "## Output Roots")
    if roots:
        spec["output_roots"] = roots
    conventions = _extract_bullet_list(text, "## Local Conventions")
    if conventions:
        spec["local_conventions"] = conventions
    caps = _infer_capabilities(text)
    if any(caps.values()):
        spec["capabilities"] = caps
    resources = _infer_skill_resources(text)
    if any(resources.values()):
        spec["skill_resources"] = resources
    return spec


def _infer_from_user(text: str) -> dict[str, str | None]:
    profile: dict[str, str | None] = {}
    name_match = re.search(r"^-\s+Name:\s*(.+)$", text, re.MULTILINE)
    if name_match:
        val = name_match.group(1).strip()
        if val and "your human" not in val.lower():
            profile["name"] = val
    pronouns_match = re.search(r"^-\s+Pronouns:\s*(.+)$", text, re.MULTILINE)
    if pronouns_match:
        val = pronouns_match.group(1).strip()
        if val and "pronouns" not in val.lower():
            profile["pronouns"] = val
    tz_match = re.search(r"^-\s+Timezone:\s*(.+)$", text, re.MULTILINE)
    if tz_match:
        val = tz_match.group(1).strip()
        if val and "timezone" not in val.lower():
            profile["timezone"] = val
    return {k: v for k, v in profile.items() if v}


# ---------------------------------------------------------------------------
# Workspace semantics inference
# ---------------------------------------------------------------------------

_KNOWN_SEMANTICS: list[tuple[str, str, str, str, str, bool]] = [
    ("Final deliverables", "workspace/", "Canonical agent workspace", "Yes", "Ask first", True),
    ("Workflow state", "state/", "Proposal and scaffold state", "Yes", "Controlled", True),
    ("Scratch / preview", "scratch/", "Preview notes", "No", "Regenerable", False),
    ("Export / package", "exports/", "Optional packaged artifacts", "Optional", "Regenerable", False),
    ("Skill resources", "skills/", "Packaged local skills", "Yes", "Ask first", True),
]


def _infer_workspace_semantics(workspace_dir: Path) -> list[dict[str, Any]]:
    semantics: list[dict[str, Any]] = []
    for type_, default_path, purpose, persistent, overwrite, shipped in _KNOWN_SEMANTICS:
        # Check if the directory exists in workspace
        actual_path = default_path
        if not (workspace_dir / default_path.rstrip("/")).exists():
            # Try to find a matching directory
            for candidate in workspace_dir.iterdir():
                if candidate.is_dir() and candidate.name in {
                    default_path.rstrip("/"),
                    type_.split("/")[0].strip().lower().replace(" ", "-"),
                }:
                    actual_path = candidate.name + "/"
                    break
        semantics.append({
            "type": type_,
            "path": actual_path,
            "purpose": purpose,
            "persistent": persistent,
            "overwrite_rule": overwrite,
            "shipped": shipped,
        })
    return semantics


# ---------------------------------------------------------------------------
# Main inference function
# ---------------------------------------------------------------------------

def infer_spec_from_workspace(workspace_dir: Path, *, host_profile: str = "generic-openclaw") -> dict[str, Any]:
    """Build a minimal spec by scanning existing workspace root files."""
    identity_text = _read_file(workspace_dir, "IDENTITY.md")
    soul_text = _read_file(workspace_dir, "SOUL.md")
    agents_text = _read_file(workspace_dir, "AGENTS.md")
    tools_text = _read_file(workspace_dir, "TOOLS.md")

    spec: dict[str, Any] = {}

    # Merge per-file inferences (later files don't overwrite earlier ones)
    for source in [
        _infer_from_identity(identity_text),
        _infer_from_soul(soul_text),
        _infer_from_agents(agents_text),
        _infer_from_tools(tools_text),
    ]:
        for key, value in source.items():
            if key not in spec:
                spec[key] = value

    # Fill non-inferable fields with defaults
    spec.setdefault("judgment_result", "独立 agent")
    spec.setdefault("promotion_rationale", ["Inferred from existing workspace root files."])
    spec.setdefault("host_profile", host_profile)
    spec.setdefault("preferred_control_pattern", "step")

    skill_name = workspace_dir.name
    spec.setdefault("agent_promotion_analysis", {
        "skill_name": skill_name,
        "host_profile": host_profile,
        "promotion_decision": "独立 agent",
        "core_role": spec.get("role", "General-purpose agent"),
        "primary_value": spec.get("public_identity", "Agent workspace"),
        "lazy_default_to_avoid": spec.get("lazy_default_to_avoid", "Unclear defaults."),
        "non_negotiable_quality_bar": "Root files must have required headings.",
        "canonical_deliverables": spec.get("output_roots", ["workspace/"]),
        "workflow_state": ["state/"],
        "resume_entry_files": ["AGENTS.md"],
        "native_capabilities": spec.get("capabilities", {}).get("native", ["General-purpose"]),
        "conditional_capabilities": [],
        "non_capabilities": spec.get("capabilities", {}).get("unsupported", []),
        "what_stays_in_skill_md": ["workflow checklist", "detailed references"],
        "what_moves_to_root_files": ["resume strategy", "capability boundaries"],
    })

    spec.setdefault("workspace_semantics", _infer_workspace_semantics(workspace_dir))
    spec.setdefault("risks_and_non_capabilities", "Inferred spec — risks not assessed.")
    spec.setdefault("lazy_default_to_avoid", "Unclear or missing defaults.")

    # Ensure required list fields have at least one item
    for field, default in [
        ("non_negotiables", ["Maintain quality standards."]),
        ("enduring_style", ["Professional and clear."]),
        ("session_startup", ["Read AGENTS.md and SOUL.md."]),
        ("red_lines", ["Do not overwrite existing files without confirmation."]),
        ("default_behavior", ["Follow workspace conventions."]),
        ("boundaries", ["Stay within declared capabilities."]),
        ("workspace_layout", ["skills/ - packaged skills", "state/ - workflow state"]),
        ("output_roots", ["workspace/"]),
        ("local_conventions", ["Follow OpenClaw conventions."]),
    ]:
        spec.setdefault(field, default)

    # Ensure resume_strategy exists
    spec.setdefault("resume_strategy", {
        "global_resume_file": "AGENTS.md",
        "task_topic_resume_file": "state/",
        "deliverable_inspection_path": "workspace/",
        "if_state_missing": "Inspect existing files and rebuild state.",
        "never_assume": "Never assume a promotion decision without re-checking artifacts.",
    })

    # Ensure capabilities exists
    spec.setdefault("capabilities", {
        "native": spec.get("capabilities", {}).get("native", ["General-purpose"]),
        "conditional": spec.get("capabilities", {}).get("conditional", []),
        "unsupported": spec.get("capabilities", {}).get("unsupported", ["Plugin runtime extension"]),
    })

    # Ensure skill_resources exists
    spec.setdefault("skill_resources", {
        "primary_skill_entrypoints": ["SKILL.md"],
        "high_priority_references": [],
        "conditional_scripts": [],
    })

    # Optional files
    bootstrap_text = _read_file(workspace_dir, "BOOTSTRAP.md")
    if bootstrap_text:
        spec.setdefault("bootstrap_config", {"enabled": True, "conversation_topics": ["identity", "user_profile"]})

    user_text = _read_file(workspace_dir, "USER.md")
    if user_text:
        profile = _infer_from_user(user_text)
        if profile:
            spec.setdefault("user_profile", profile)

    heartbeat_text = _read_file(workspace_dir, "HEARTBEAT.md")
    if heartbeat_text:
        spec.setdefault("heartbeat_config", {"enabled": True, "tasks": []})

    return spec


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Infer a minimal OpenClaw agent spec from existing workspace root files."
    )
    parser.add_argument("--workspace", required=True, help="Path to the existing workspace directory.")
    parser.add_argument("--out", required=True, help="Path for the inferred spec JSON output.")
    parser.add_argument(
        "--host",
        default="generic-openclaw",
        choices=["flowyclaw", "generic-openclaw"],
        help="Host profile to assign (default: generic-openclaw).",
    )
    args = parser.parse_args()

    workspace_dir = Path(args.workspace).resolve()
    if not workspace_dir.exists() or not workspace_dir.is_dir():
        print(f"FAIL: workspace directory does not exist: {workspace_dir}")
        return 1

    spec = infer_spec_from_workspace(workspace_dir, host_profile=args.host)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Summary
    found = [f for f in ALL_POSSIBLE_ROOT_FILES if (workspace_dir / f).exists()]
    inferred_fields = [k for k in spec if k not in ("agent_promotion_analysis", "workspace_semantics", "capabilities", "skill_resources", "resume_strategy")]
    print(f"PASS: inferred spec from {len(found)} root files ({', '.join(found)})")
    print(f"  Inferred fields: {len(inferred_fields)}")
    print(f"  Host profile: {args.host}")
    print(f"  Output: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
