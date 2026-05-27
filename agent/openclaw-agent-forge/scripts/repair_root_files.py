#!/usr/bin/env python3
"""Minimal-slice repair script for OpenClaw agent workspaces.

Reads an optimize-report.md + preview directory, applies section-level fixes
to the workspace, then re-runs invariant checks.  Invariant failures trigger
per-section rollback.

CLI:
    python repair_root_files.py --spec spec.json --workspace ./ws --preview ./preview
    python repair_root_files.py --spec spec.json --workspace ./ws --preview ./preview --dry-run
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from spec_contract import load_json, require_independent_agent, validate_minimal_spec, validate_propose_spec
from workspace_invariants import check_workspace_invariants, _extract_section_content


# ---------------------------------------------------------------------------
# Section-level replacement
# ---------------------------------------------------------------------------

def apply_section(
    file_content: str,
    section_heading: str,
    new_section_text: str,
) -> str:
    """Replace the content of *section_heading* in *file_content*.

    The section spans from the heading line to the next ``##`` heading (or EOF).
    If the heading does not exist, *new_section_text* is appended at the end.

    Returns the full file content after replacement.
    """
    pattern = re.compile(
        r"^(?P<heading>" + re.escape(section_heading) + r")\s*$",
        re.MULTILINE,
    )
    match = pattern.search(file_content)

    if match is None:
        # Heading missing → append at end
        separator = "\n\n" if file_content and not file_content.endswith("\n\n") else ""
        return file_content + separator + new_section_text.rstrip() + "\n"

    # Find the end of this section (next ## heading or EOF)
    after_heading = file_content[match.end():]
    next_heading = re.search(r"^##\s", after_heading, re.MULTILINE)

    if next_heading is not None:
        end_offset = match.end() + next_heading.start()
        return file_content[: match.start()] + new_section_text.rstrip() + "\n" + file_content[end_offset:]
    else:
        # Last section in file
        return file_content[: match.start()] + new_section_text.rstrip() + "\n"


# ---------------------------------------------------------------------------
# Report parsing (lightweight — avoids coupling to spec_contract internals)
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^###\s+(.+?\.(?:md))\s*$", re.MULTILINE)
_STATUS_RE = re.compile(r"^- Status:\s*(\S+)", re.MULTILINE)
_SECTION_TABLE_ROW_RE = re.compile(
    r"^\|\s*(##[^|]+?)\s*\|\s*(\S*)\s*\|\s*(\S+)\s*\|\s*(.*?)\s*\|$",
    re.MULTILINE,
)


def parse_optimize_report(report_text: str) -> list[dict[str, object]]:
    """Extract per-file findings from an optimize-report.md.

    Returns a list of dicts:
        {"filename": str, "status": str, "sections": [
            {"heading": str, "layer": str, "status": str, "issues": str}
        ]}
    """
    findings: list[dict[str, object]] = []

    # Split by file headings (### AGENTS.md, etc.)
    parts = _HEADING_RE.split(report_text)
    # parts: [preamble, "AGENTS.md", body, "IDENTITY.md", body, ...]
    for i in range(1, len(parts), 2):
        filename = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""

        status_match = _STATUS_RE.search(body)
        status = status_match.group(1) if status_match else "aligned"

        sections: list[dict[str, str]] = []
        for row_match in _SECTION_TABLE_ROW_RE.finditer(body):
            heading = row_match.group(1).strip()
            layer = row_match.group(2).strip()
            sec_status = row_match.group(3).strip()
            issues = row_match.group(4).strip()
            if sec_status in ("needs_update", "missing"):
                sections.append({
                    "heading": heading,
                    "layer": layer,
                    "status": sec_status,
                    "issues": issues,
                })

        if status in ("needs_update", "missing") or sections:
            findings.append({
                "filename": filename,
                "status": status,
                "sections": sections,
            })

    return findings


# ---------------------------------------------------------------------------
# Preview section extraction
# ---------------------------------------------------------------------------

def extract_preview_section(preview_dir: Path, filename: str, heading: str) -> str:
    """Read the preview file and extract the section under *heading*."""
    preview_file = preview_dir / "preview" / filename
    if not preview_file.exists():
        return ""
    text = preview_file.read_text(encoding="utf-8")
    return _extract_section_content(text, heading)


# ---------------------------------------------------------------------------
# Core repair logic
# ---------------------------------------------------------------------------

def apply_repairs(
    spec: dict,
    workspace_dir: Path,
    preview_dir: Path,
    dry_run: bool = False,
) -> dict[str, object]:
    """Apply section-level repairs from an optimize preview bundle.

    Returns:
        {
            "applied": [{"filename", "section", "layer"}],
            "rolled_back": [{"filename", "section", "reason"}],
            "invariant_results": [{"name", "status", "detail"}],
            "errors": [str],
        }
    """
    report_path = preview_dir / "optimize-report.md"
    if not report_path.exists():
        return {"applied": [], "rolled_back": [], "invariant_results": [], "errors": [
            f"optimize-report.md not found at {report_path}"
        ]}

    report_text = report_path.read_text(encoding="utf-8")
    findings = parse_optimize_report(report_text)

    if not findings:
        return {"applied": [], "rolled_back": [], "invariant_results": [], "errors": []}

    # Load existing workspace contents for invariant checks
    def _read_workspace() -> dict[str, str]:
        contents: dict[str, str] = {}
        for name in ["AGENTS.md", "IDENTITY.md", "SOUL.md", "TOOLS.md"]:
            path = workspace_dir / name
            if path.exists():
                contents[name] = path.read_text(encoding="utf-8")
        return contents

    original_contents = _read_workspace()
    spec_red_lines = spec.get("red_lines", [])

    applied: list[dict[str, str]] = []
    rolled_back: list[dict[str, str]] = []
    errors: list[str] = []

    for finding in findings:
        filename = str(finding["filename"])
        file_status = str(finding["status"])
        sections = finding.get("sections", [])
        if not isinstance(sections, list):
            continue

        workspace_file = workspace_dir / filename

        # Handle whole-file missing
        if file_status == "missing":
            preview_file = preview_dir / "preview" / filename
            if not preview_file.exists():
                errors.append(f"Preview file missing for {filename}")
                continue
            preview_text = preview_file.read_text(encoding="utf-8")

            if not dry_run:
                workspace_file.parent.mkdir(parents=True, exist_ok=True)
                workspace_file.write_text(preview_text, encoding="utf-8")

                # Check invariants after writing the whole file
                current_contents = _read_workspace()
                inv = check_workspace_invariants(workspace_dir, current_contents, spec_red_lines)
                new_fails = [r for r in inv if r["status"] == "FAIL" and
                             not any(r2["name"] == r["name"] and r2["status"] == "FAIL"
                                     for r2 in check_workspace_invariants(
                                         workspace_dir, original_contents, spec_red_lines))]

                if new_fails:
                    # Rollback: restore original state
                    if filename in original_contents:
                        workspace_file.write_text(original_contents[filename], encoding="utf-8")
                    else:
                        workspace_file.unlink(missing_ok=True)
                    for fail in new_fails:
                        rolled_back.append({
                            "filename": filename,
                            "section": "(whole file)",
                            "reason": fail["detail"],
                        })
                else:
                    applied.append({"filename": filename, "section": "(whole file)", "layer": "structure"})
            else:
                applied.append({"filename": filename, "section": "(whole file)", "layer": "structure"})
            continue

        # Handle section-level repairs
        current_text = workspace_file.read_text(encoding="utf-8") if workspace_file.exists() else ""

        for sec in sections:
            heading = sec["heading"]
            layer = sec.get("layer", "")
            sec_status = sec["status"]

            if sec_status == "missing":
                # Structure layer: heading doesn't exist → append from preview
                preview_section = extract_preview_section(preview_dir, filename, heading)
                if not preview_section:
                    errors.append(f"No preview section for {filename} {heading}")
                    continue
                new_text = apply_section(current_text, heading, preview_section)
            elif sec_status == "needs_update":
                preview_section = extract_preview_section(preview_dir, filename, heading)
                if not preview_section:
                    errors.append(f"No preview section for {filename} {heading}")
                    continue
                new_text = apply_section(current_text, heading, preview_section)
            else:
                continue

            if dry_run:
                applied.append({"filename": filename, "section": heading, "layer": layer})
                continue

            # Apply the change
            workspace_file.write_text(new_text, encoding="utf-8")

            # Post-repair invariant check
            current_contents = _read_workspace()
            post_inv = check_workspace_invariants(workspace_dir, current_contents, spec_red_lines)
            pre_inv = check_workspace_invariants(workspace_dir, original_contents, spec_red_lines)
            pre_fails = {r["name"] for r in pre_inv if r["status"] == "FAIL"}
            new_fails = [r for r in post_inv if r["status"] == "FAIL" and r["name"] not in pre_fails]

            if new_fails:
                # Rollback this single section
                workspace_file.write_text(current_text, encoding="utf-8")
                for fail in new_fails:
                    rolled_back.append({
                        "filename": filename,
                        "section": heading,
                        "reason": fail["detail"],
                    })
            else:
                applied.append({"filename": filename, "section": heading, "layer": layer})
                # Update current_text for subsequent sections in the same file
                current_text = new_text

    # Final invariant check (only if not dry_run)
    if not dry_run:
        final_contents = _read_workspace()
        invariant_results = check_workspace_invariants(workspace_dir, final_contents, spec_red_lines)
    else:
        invariant_results = []

    return {
        "applied": applied,
        "rolled_back": rolled_back,
        "invariant_results": invariant_results,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_repair_report(result: dict[str, object]) -> str:
    """Generate a markdown repair report."""
    lines = ["# Repair Report\n"]

    applied = result.get("applied", [])
    rolled_back = result.get("rolled_back", [])
    invariant_results = result.get("invariant_results", [])
    errors = result.get("errors", [])

    # Summary
    lines.append("## Summary\n")
    lines.append(f"- Applied: {len(applied)}")
    lines.append(f"- Rolled back: {len(rolled_back)}")
    lines.append(f"- Errors: {len(errors)}")
    lines.append("")

    # Applied changes
    lines.append("## Applied Changes\n")
    if applied:
        for item in applied:
            lines.append(f"- **{item['filename']}** `{item['section']}` (layer: {item.get('layer', '—')})")
    else:
        lines.append("- none")
    lines.append("")

    # Rolled back changes
    if rolled_back:
        lines.append("## Rolled Back\n")
        for item in rolled_back:
            lines.append(f"- **{item['filename']}** `{item['section']}` — {item['reason']}")
        lines.append("")

    # Invariant results
    if invariant_results:
        lines.append("## Post-Repair Invariants\n")
        for inv in invariant_results:
            status = inv["status"]
            name = inv["name"]
            detail = inv.get("detail", "")
            if detail:
                lines.append(f"- {status}: {name} — {detail}")
            else:
                lines.append(f"- {status}: {name}")
        lines.append("")

    # Errors
    if errors:
        lines.append("## Errors\n")
        for err in errors:
            lines.append(f"- {err}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Apply minimal-slice repairs to an agent workspace.")
    parser.add_argument("--spec", required=True, help="Path to the agent spec JSON.")
    parser.add_argument("--workspace", required=True, help="Path to the workspace directory.")
    parser.add_argument("--preview", required=True, help="Path to the optimize preview directory.")
    parser.add_argument("--dry-run", action="store_true", help="Preview repairs without modifying workspace.")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    workspace_dir = Path(args.workspace)
    preview_dir = Path(args.preview)

    if not spec_path.exists():
        print(f"Error: spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)
    if not workspace_dir.is_dir():
        print(f"Error: workspace directory not found: {workspace_dir}", file=sys.stderr)
        sys.exit(1)
    if not preview_dir.is_dir():
        print(f"Error: preview directory not found: {preview_dir}", file=sys.stderr)
        sys.exit(1)

    spec = load_json(spec_path)
    require_independent_agent(spec)

    errors = validate_propose_spec(spec)
    if errors:
        # Full spec validation failed — try minimal (lite mode)
        minimal_errors = validate_minimal_spec(spec)
        if minimal_errors:
            print("FAIL: spec validation failed:", file=sys.stderr)
            for err in minimal_errors:
                print(f"- {err}", file=sys.stderr)
            sys.exit(1)

    result = apply_repairs(spec, workspace_dir, preview_dir, dry_run=args.dry_run)

    report = build_repair_report(result)

    if args.dry_run:
        print(report)
    else:
        report_path = workspace_dir / "repair-report.md"
        report_path.write_text(report.rstrip() + "\n", encoding="utf-8")
        print(f"Repair complete. Report: {report_path}")
        print(f"  Applied: {len(result['applied'])}")
        print(f"  Rolled back: {len(result['rolled_back'])}")
        print(f"  Errors: {len(result['errors'])}")


if __name__ == "__main__":
    main()
