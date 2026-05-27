"""Cross-file workspace invariant checks.

Validates structural invariants that span multiple root files:
- Red Lines monotonicity (only grow, never shrink vs spec)
- Session Startup references point to existing files
- Role consistency between IDENTITY.md and AGENTS.md
- Skill Resources paths point to existing files
"""
from __future__ import annotations

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers (duplicated from infer_spec.py to avoid circular imports)
# ---------------------------------------------------------------------------

def _extract_section_content(text: str, heading: str) -> str:
    pattern = re.compile(r"^" + re.escape(heading) + r"\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def _extract_bullet_list(text: str, heading: str) -> list[str]:
    section = _extract_section_content(text, heading)
    return [
        m.group(1).strip()
        for m in re.finditer(r"^-\s+(.+)$", section, re.MULTILINE)
        if m.group(1).strip()
    ]


def _extract_labeled_value(text: str, label: str) -> str:
    match = re.search(r"^" + re.escape(label) + r"\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


# ---------------------------------------------------------------------------
# Individual invariant checks
# ---------------------------------------------------------------------------

def check_red_lines_monotonic(
    spec_red_lines: list[str],
    workspace_agents_text: str,
) -> list[str]:
    """Spec red_lines must not be deleted from workspace (only additions allowed)."""
    if not spec_red_lines or not workspace_agents_text:
        return []
    current_red = _extract_bullet_list(workspace_agents_text, "## Red Lines")
    issues: list[str] = []
    for rule in spec_red_lines:
        if rule not in current_red:
            issues.append(f"red_lines shrinkage: '{rule}' was in spec but missing from workspace")
    return issues


def check_session_startup_references(
    workspace_dir: Path,
    agents_text: str,
) -> list[str]:
    """Session Startup entries that reference .md files must point to existing files."""
    if not agents_text:
        return []
    startup_items = _extract_bullet_list(agents_text, "## Session Startup")
    issues: list[str] = []
    for item in startup_items:
        for filename in re.findall(r"([A-Z][A-Z_]*\.md)", item):
            if not (workspace_dir / filename).exists():
                issues.append(f"Session Startup references missing file: {filename}")
    return issues


def _normalize_words(text: str) -> set[str]:
    """Lowercase, split, strip punctuation, and apply naive stemming."""
    words = set()
    for w in text.lower().split():
        cleaned = w.strip(".,;:!?()[]{}\"'")
        if cleaned:
            words.add(cleaned)
            # Naive stemming: strip trailing 's'/'es'/'ed'/'ing'
            for suffix in ("ing", "ed", "es", "s"):
                if cleaned.endswith(suffix) and len(cleaned) > len(suffix) + 2:
                    words.add(cleaned[: -len(suffix)])
    return words


def check_role_consistency(
    identity_text: str,
    agents_text: str,
) -> list[str]:
    """IDENTITY.md role and AGENTS.md Workspace Positioning should share keywords."""
    if not identity_text or not agents_text:
        return []
    role = _extract_labeled_value(identity_text, "- Role:")
    positioning = _extract_section_content(agents_text, "## Workspace Positioning")
    if not role or not positioning:
        return []
    role_words = _normalize_words(role)
    pos_words = _normalize_words(positioning)
    stop_words = {"a", "an", "the", "and", "or", "of", "to", "in", "for", "is", "on", "with"}
    role_meaningful = role_words - stop_words
    pos_meaningful = pos_words - stop_words
    if not role_meaningful:
        return []
    overlap = role_meaningful & pos_meaningful
    if len(overlap) < 2:
        return [
            f"role drift: IDENTITY.md role '{role}' shares few keywords with Workspace Positioning"
        ]
    return []


def check_skill_resources_paths(
    workspace_dir: Path,
    tools_text: str,
) -> list[str]:
    """Skill Resources primary entrypoints should reference existing paths."""
    if not tools_text:
        return []
    section = _extract_section_content(tools_text, "## Skill Resources")
    if not section:
        return []
    issues: list[str] = []
    for m in re.finditer(r"^-\s+(.+)$", section, re.MULTILINE):
        path_str = m.group(1).strip()
        # Check if it looks like a file path (contains / or .)
        if "/" in path_str or "." in path_str:
            # Take first token as path, strip backticks
            candidate = path_str.split()[0].strip().strip("`")
            if candidate and not (workspace_dir / candidate).exists():
                issues.append(f"Skill Resources references missing path: {candidate}")
    return issues


def check_memory_baseline_present(
    agents_text: str,
) -> list[str]:
    """AGENTS.md must contain a ## Memory section (baseline or full)."""
    if not agents_text:
        return ["AGENTS.md is empty or missing"]
    if not re.search(r"^## Memory\s*$", agents_text, re.MULTILINE):
        return ["AGENTS.md missing ## Memory section (required baseline)"]
    return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

INVARIANT_CHECKS = [
    ("red_lines_monotonic", check_red_lines_monotonic),
    ("session_startup_references_valid", check_session_startup_references),
    ("role_consistency", check_role_consistency),
    ("skill_resources_paths_valid", check_skill_resources_paths),
    ("memory_baseline_present", check_memory_baseline_present),
]


def check_workspace_invariants(
    workspace_dir: Path,
    existing_contents: dict[str, str],
    spec_red_lines: list[str] | None = None,
) -> list[dict[str, str]]:
    """Run all cross-file invariant checks.

    Returns a list of dicts with keys ``name``, ``status`` (PASS/FAIL),
    and ``detail``.
    """
    agents_text = existing_contents.get("AGENTS.md", "")
    identity_text = existing_contents.get("IDENTITY.md", "")
    tools_text = existing_contents.get("TOOLS.md", "")

    results: list[dict[str, str]] = []

    for name, check_fn in INVARIANT_CHECKS:
        if name == "red_lines_monotonic":
            issues = check_fn(spec_red_lines or [], agents_text)
        elif name == "session_startup_references_valid":
            issues = check_fn(workspace_dir, agents_text)
        elif name == "role_consistency":
            issues = check_fn(identity_text, agents_text)
        elif name == "skill_resources_paths_valid":
            issues = check_fn(workspace_dir, tools_text)
        elif name == "memory_baseline_present":
            issues = check_fn(agents_text)
        else:
            issues = []

        if issues:
            for detail in issues:
                results.append({"name": name, "status": "FAIL", "detail": detail})
        else:
            results.append({"name": name, "status": "PASS", "detail": ""})

    return results
