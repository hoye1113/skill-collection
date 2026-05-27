"""Content-level quality analysis for OpenClaw agent root files.

Goes beyond structural heading checks to detect:
- Placeholder/template text left behind
- Empty sections
- Vague or non-actionable rules
- Duplicate rules across sections
- Character budget violations
- Host-profile-specific wording drift
"""
from __future__ import annotations

import re
from typing import Any

from spec_contract import CHARACTER_BUDGET_SINGLE, CHARACTER_BUDGET_TOTAL, ROOT_FILENAMES


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

PLACEHOLDER_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\[REQUIRED\]", re.IGNORECASE),
    re.compile(r"\[TODO\]", re.IGNORECASE),
    re.compile(r"\[FIXME\]", re.IGNORECASE),
    re.compile(r"\[PLACEHOLDER\]", re.IGNORECASE),
    re.compile(r"your human's name", re.IGNORECASE),
    re.compile(r"their pronouns", re.IGNORECASE),
    re.compile(r"their timezone", re.IGNORECASE),
    re.compile(r"inferred spec", re.IGNORECASE),
]

VAGUE_RULE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^-\s+(be careful|do your best|try to|when possible|if you can|as needed)\b", re.IGNORECASE | re.MULTILINE),
]

FLOWYCLAW_INDICATORS = re.compile(r"\b(uv run|node scripts/|flowyclaw|\.flowyclaw)\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_section_lines(text: str, heading: str) -> list[str]:
    """Return non-empty lines between *heading* and the next ## heading."""
    pattern = re.compile(r"^" + re.escape(heading) + r"\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return []
    start = match.end()
    next_heading = re.search(r"^##\s", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return [line.strip() for line in text[start:end].splitlines() if line.strip()]


def _extract_bullet_items(text: str, heading: str) -> list[str]:
    """Extract `- item` lines under *heading*."""
    lines = _extract_section_lines(text, heading)
    return [line[2:].strip() for line in lines if line.startswith("- ") and line[2:].strip()]


def _find_heading_for_position(content: str, pos: int) -> str:
    """Return the ## heading that contains position *pos* in *content*."""
    heading = ""
    for m in re.finditer(r"^(##\s+.+)$", content, re.MULTILINE):
        if m.start() <= pos:
            heading = m.group(1)
        else:
            break
    return heading


def _issue(layer: str, section: str, issue: str) -> dict[str, str]:
    return {"layer": layer, "section": section, "issue": issue}


# ---------------------------------------------------------------------------
# Per-file analysis
# ---------------------------------------------------------------------------

def _check_placeholders(content: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for pattern in PLACEHOLDER_PATTERNS:
        for match in pattern.finditer(content):
            context = content[max(0, match.start() - 20):match.end() + 20].replace("\n", " ").strip()
            section = _find_heading_for_position(content, match.start())
            issues.append(_issue("content", section, f"placeholder detected: '{context}'"))
    return issues


def _check_empty_sections(content: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for m in re.finditer(r"^(##\s+.+)$", content, re.MULTILINE):
        heading = m.group(1)
        after = content[m.end():]
        next_heading = re.search(r"^##\s", after, re.MULTILINE)
        section_text = after[:next_heading.start()] if next_heading else after
        lines = [line.strip() for line in section_text.splitlines() if line.strip()]
        if not lines:
            issues.append(_issue("content", heading, f"empty section: {heading} has no content"))
    return issues


def _check_vague_rules(content: str, section_heading: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    items = _extract_bullet_items(content, section_heading)
    for item in items:
        for pattern in VAGUE_RULE_PATTERNS:
            if pattern.match(f"- {item}"):
                issues.append(_issue("quality", section_heading, f"vague rule in {section_heading}: '- {item}' — consider making it specific and testable"))
    return issues


def _check_duplicate_rules(content: str) -> list[dict[str, str]]:
    """Check for identical bullet items across different sections."""
    issues: list[dict[str, str]] = []
    section_items: dict[str, list[str]] = {}
    current_heading: str | None = None
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            current_heading = stripped
            section_items[current_heading] = []
        elif stripped.startswith("- ") and current_heading:
            item = stripped[2:].strip()
            if item:
                section_items.setdefault(current_heading, []).append(item)

    seen: dict[str, str] = {}
    for heading, items in section_items.items():
        for item in items:
            normalized = item.lower()
            if normalized in seen and seen[normalized] != heading:
                issues.append(
                    _issue("quality", heading, f"duplicate rule: '- {item}' appears in both {seen[normalized]} and {heading}")
                )
            else:
                seen[normalized] = heading
    return issues


def _check_agents_specific(content: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if "## Red Lines" in content:
        issues.extend(_check_vague_rules(content, "## Red Lines"))
    if "## Boundaries" in content:
        issues.extend(_check_vague_rules(content, "## Boundaries"))
    issues.extend(_check_duplicate_rules(content))
    return issues


def _check_host_profile_drift(content: str, filename: str, host_profile: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if host_profile == "generic-openclaw" and filename in {"AGENTS.md", "TOOLS.md"}:
        if FLOWYCLAW_INDICATORS.search(content):
            issues.append(_issue("drift", "", f"host profile drift: flowyclaw-specific wording present under generic-openclaw"))
    return issues


def _check_character_budget(content: str, filename: str, all_file_sizes: dict[str, int]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    file_chars = len(content)
    if file_chars > CHARACTER_BUDGET_SINGLE:
        issues.append(
            _issue("budget", "", f"character budget: {filename} has {file_chars} chars (limit: {CHARACTER_BUDGET_SINGLE})")
        )
    total = sum(all_file_sizes.values())
    if total > CHARACTER_BUDGET_TOTAL:
        issues.append(
            _issue("budget", "", f"character budget: total across all files is {total} chars (limit: {CHARACTER_BUDGET_TOTAL})")
        )
    return issues


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_content_quality(
    *,
    filename: str,
    content: str,
    spec: dict[str, Any],
    host_profile: str,
    all_file_sizes: dict[str, int] | None = None,
) -> list[dict[str, str]]:
    """Analyze content quality for a single root file.

    Returns a list of dicts with keys ``layer``, ``section``, ``issue``.
    Each dict represents one detected issue (empty list if no issues found).
    """
    if not content:
        return []

    issues: list[dict[str, str]] = []

    # Placeholder detection (all files)
    issues.extend(_check_placeholders(content))

    # Empty section detection (all files)
    issues.extend(_check_empty_sections(content))

    # Character budget (all files)
    if all_file_sizes is not None:
        issues.extend(_check_character_budget(content, filename, all_file_sizes))

    # Host profile drift (AGENTS.md, TOOLS.md)
    issues.extend(_check_host_profile_drift(content, filename, host_profile))

    # AGENTS.md-specific checks
    if filename == "AGENTS.md":
        issues.extend(_check_agents_specific(content))

    return issues
