#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import re
import shutil
import sys
from pathlib import Path

from content_analysis import analyze_content_quality
from root_file_renderer import render_all
from spec_contract import (
    ALL_POSSIBLE_ROOT_FILES,
    BLOAT_LINE_THRESHOLD,
    FORBIDDEN_FILENAMES,
    OPTIMIZE_ALLOWED_TOP_LEVEL,
    OPTIONAL_ROOT_FILENAMES,
    ROOT_FILE_REQUIREMENTS,
    ROOT_FILENAMES,
    load_json,
    require_independent_agent,
    validate_minimal_spec,
    validate_propose_spec,
)
from workflow_hardening_checks import run_workflow_hardening_diagnostics
from workspace_invariants import check_workspace_invariants


RESUME_LABELS = [
    "Global resume file",
    "Task/topic resume file",
    "Deliverable inspection path",
    "If state missing",
    "Never assume",
]


def suggest_version_bump(findings: list[dict[str, object]]) -> str:
    """Determine if this optimize run is structural or content-only."""
    for f in findings:
        if f["status"] == "missing":
            return "structural"
        file_sections = f.get("sections", {})
        if isinstance(file_sections, dict):
            for sec_info in file_sections.values():
                if isinstance(sec_info, dict) and sec_info.get("layer") == "structure":
                    return "structural"
    return "content"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def build_diff(filename: str, current_text: str, expected_text: str) -> str:
    diff_lines = difflib.unified_diff(
        current_text.splitlines(),
        expected_text.splitlines(),
        fromfile=f"current/{filename}",
        tofile=f"preview/{filename}",
        lineterm="",
    )
    return "\n".join(diff_lines).rstrip() + "\n"


def _extract_section_text(text: str, heading: str) -> str:
    """Return all text from *heading* to the next ## heading (inclusive of heading line)."""
    idx = text.find(heading)
    if idx == -1:
        return ""
    after = text[idx + len(heading):]
    next_heading = re.search(r"^##\s", after, re.MULTILINE)
    end = next_heading.start() if next_heading else len(after)
    return heading + after[:end]


def build_section_diff(
    filename: str,
    section_heading: str,
    current_section_text: str,
    expected_section_text: str,
) -> str:
    """Generate a unified diff for a single section."""
    if current_section_text == expected_section_text:
        return ""
    diff_lines = difflib.unified_diff(
        current_section_text.splitlines(),
        expected_section_text.splitlines(),
        fromfile=f"current/{filename}",
        tofile=f"preview/{filename}",
        lineterm="",
    )
    return "\n".join(diff_lines).rstrip() + "\n"


def prepare_preview_bundle(preview_dir: Path) -> tuple[Path, Path]:
    if preview_dir.exists():
        unexpected_top_level = sorted(path.name for path in preview_dir.iterdir() if path.name not in OPTIMIZE_ALLOWED_TOP_LEVEL)
        if unexpected_top_level:
            joined = ", ".join(unexpected_top_level)
            raise ValueError(
                "Preview output directory must be empty or contain only optimize-report.md, preview, and diffs: "
                + joined
            )
        report_path = preview_dir / "optimize-report.md"
        if report_path.exists():
            report_path.unlink()
        for directory in ("preview", "diffs"):
            path = preview_dir / directory
            if path.exists():
                shutil.rmtree(path)
    else:
        preview_dir.mkdir(parents=True, exist_ok=True)

    preview_files_dir = preview_dir / "preview"
    diff_files_dir = preview_dir / "diffs"
    preview_files_dir.mkdir(exist_ok=True)
    diff_files_dir.mkdir(exist_ok=True)

    return preview_files_dir, diff_files_dir


def extract_level_two_headings(text: str) -> set[str]:
    headings: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            headings.add(line)
    return headings


def find_duplicate_headings(contents: dict[str, str]) -> dict[str, list[str]]:
    heading_to_files: dict[str, list[str]] = {}
    for filename, text in contents.items():
        for heading in extract_level_two_headings(text):
            heading_to_files.setdefault(heading, []).append(filename)

    duplicates: dict[str, list[str]] = {}
    for heading, filenames in heading_to_files.items():
        if len(filenames) < 2:
            continue
        for filename in filenames:
            others = ", ".join(name for name in filenames if name != filename)
            duplicates.setdefault(filename, []).append(
                f"duplicate root-file heading: {heading} also appears in {others}"
            )
    return duplicates


def _try_relative(path: Path, base: Path | None = None) -> str:
    """Return a relative path if possible; otherwise return the original."""
    if base is None:
        base = Path.cwd()
    try:
        return str(path.relative_to(base)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def resolve_path(raw_path: str | Path, context: str = "path") -> Path:
    """Resolve a path to an absolute Path, validating it is not empty.

    Raises ValueError if the path is empty or resolves to something invalid.
    """
    if not raw_path:
        raise ValueError(f"{context} is required and cannot be empty")
    path = Path(raw_path).resolve()
    return path


def diagnose_file(
    *,
    spec: dict,
    filename: str,
    workspace_dir: Path,
    duplicate_heading_issues: dict[str, list[str]],
) -> dict[str, object]:
    current_path = workspace_dir / filename
    sections: dict[str, dict[str, object]] = {}
    result: dict[str, object] = {
        "filename": filename,
        "current_path": _try_relative(current_path, workspace_dir),
        "preview_path": None,
        "diff_path": None,
        "status": "aligned",
        "issues": [],
        "sections": sections,
        "recommended_action": "No preview artifact generated. Keep the current file.",
    }

    if not current_path.exists():
        result["status"] = "missing"
        result["issues"] = ["file missing"]
        result["recommended_action"] = "Create this root file from the rendered recommendation."
        return result

    current_text = current_path.read_text(encoding="utf-8")
    issues: list[str] = []
    rules = ROOT_FILE_REQUIREMENTS[filename]

    for heading in rules["required"]:
        if heading not in current_text:
            issues.append(f"missing heading: {heading}")
            sections[heading] = {"status": "missing", "layer": "structure", "issues": [f"missing heading: {heading}"]}
        else:
            sections[heading] = {"status": "aligned", "layer": "", "issues": []}
    for heading in rules["forbidden"]:
        if heading in current_text:
            issues.append(f"out-of-scope heading: {heading}")

    issues.extend(duplicate_heading_issues.get(filename, []))

    host_profile = str(spec.get("host_profile", "")).strip()
    if host_profile == "generic-openclaw" and filename in {"AGENTS.md", "TOOLS.md"}:
        if "flowyclaw" in current_text.lower():
            issues.append("host profile drift: flowyclaw-specific wording present under generic-openclaw")

    if filename == "AGENTS.md":
        line_count = len(current_text.splitlines())
        if line_count > BLOAT_LINE_THRESHOLD:
            issues.append(f"bloat risk: {line_count} lines exceeds {BLOAT_LINE_THRESHOLD}")
        preferred = str(spec.get("preferred_control_pattern", "")).strip()
        if preferred and "## Preferred Control Pattern" not in current_text:
            issues.append("missing preferred control pattern section")
        if "## Resume Strategy" in current_text:
            for label in RESUME_LABELS:
                if f"- {label}:" not in current_text:
                    issues.append(f"resume strategy is missing line: {label}")

        # Compaction-critical rule placement check
        compaction_critical_keywords = ("never", "do not", "must not", "always", "required", "forbidden")
        session_startup_text = ""
        red_lines_text = ""
        boundaries_text = ""
        workspace_layout_text = ""
        current_section = ""
        for raw_line in current_text.splitlines():
            stripped = raw_line.strip()
            if stripped.startswith("## "):
                current_section = stripped[3:].strip().lower()
                continue
            if current_section == "session startup":
                session_startup_text += stripped.lower() + " "
            elif current_section == "red lines":
                red_lines_text += stripped.lower() + " "
            elif current_section == "boundaries":
                boundaries_text += stripped.lower() + " "
            elif current_section == "workspace layout":
                workspace_layout_text += stripped.lower() + " "

        for keyword in compaction_critical_keywords:
            if keyword in boundaries_text and keyword not in session_startup_text and keyword not in red_lines_text:
                issues.append(
                    f"compaction risk: critical keyword '{keyword}' found in Boundaries but not in Session Startup or Red Lines"
                )
            if keyword in workspace_layout_text and keyword not in session_startup_text and keyword not in red_lines_text:
                issues.append(
                    f"compaction risk: critical keyword '{keyword}' found in Workspace Layout but not in Session Startup or Red Lines"
                )

    result["issues"] = issues or ["none"]
    if issues:
        result["status"] = "needs_update"
        result["recommended_action"] = "Review the diagnosis and compare it with the rendered recommendation."

    return result


def build_report(
    spec: dict,
    workspace_dir: Path,
    preview_dir: Path,
    findings: list[dict[str, object]],
    forbidden_files: list[Path],
    workflow_contract_findings: list[str],
    skill_review_signals: list[str],
    invariant_findings: list[dict[str, str]] | None = None,
    version_impact: str = "content",
) -> str:
    aligned = sum(1 for item in findings if item["status"] == "aligned")
    needs_update = sum(1 for item in findings if item["status"] == "needs_update")
    missing = sum(1 for item in findings if item["status"] == "missing")

    lines = [
        "# Root File Optimization Preview",
        "",
        f"- Workspace: {_try_relative(workspace_dir)}",
        f"- Host profile: {spec['host_profile']}",
        f"- Judgment result: {spec['judgment_result']}",
        "- Mode: preview-only optimize",
        f"- Preview root: {_try_relative(preview_dir)}",
        "",
        "## Summary",
        "",
        f"- aligned: {aligned}",
        f"- needs_update: {needs_update}",
        f"- missing: {missing}",
        f"- forbidden_governance_files: {len(forbidden_files)}",
        f"- workflow_contract_findings: {len(workflow_contract_findings)}",
        f"- skill_review_signals: {len(skill_review_signals)}",
        "",
        "## Workspace Warnings",
        "",
    ]

    if forbidden_files:
        for path in forbidden_files:
            lines.append(f"- Forbidden governance file present: {_try_relative(path, workspace_dir)}")
    else:
        lines.append("- none")

    lines.extend(["", "## Diagnostic Findings", ""])
    for item in findings:
        lines.extend(
            [
                f"### {item['filename']}",
                "",
                f"- Status: {item['status']}",
                f"- Current path: {item['current_path']}",
                f"- Recommended action: {item['recommended_action']}",
            ]
        )
        if item["preview_path"]:
            lines.append(f"- Preview path: {item['preview_path']}")
        if item["diff_path"]:
            lines.append(f"- Diff path: {item['diff_path']}")
        lines.append("- Issues:")
        for issue in item["issues"]:
            lines.append(f"  - {issue}")

        # Section Details table
        file_sections: dict[str, dict[str, object]] = item.get("sections", {})  # type: ignore[assignment]
        if file_sections:
            lines.extend(["", "#### Section Details", ""])
            lines.append("| Section | Layer | Status | Issues |")
            lines.append("|---------|-------|--------|--------|")
            for sec_name, sec_info in file_sections.items():
                sec_status = str(sec_info.get("status", "aligned"))
                sec_layer = str(sec_info.get("layer", ""))
                sec_issues_list = sec_info.get("issues", [])
                if isinstance(sec_issues_list, list):
                    sec_issues_text = "; ".join(str(i) for i in sec_issues_list) if sec_issues_list else "—"
                else:
                    sec_issues_text = str(sec_issues_list) or "—"
                lines.append(f"| {sec_name} | {sec_layer or '—'} | {sec_status} | {sec_issues_text} |")

            # Section-level diffs
            for sec_name, sec_info in file_sections.items():
                if not isinstance(sec_info, dict):
                    continue
                sec_diff = sec_info.get("diff")
                if sec_diff and isinstance(sec_diff, str):
                    sec_layer = str(sec_info.get("layer", ""))
                    sec_status = str(sec_info.get("status", "aligned"))
                    layer_label = f" — {sec_layer}" if sec_layer else ""
                    lines.extend([
                        "",
                        f"##### {sec_name} ({sec_status}{layer_label})",
                        "",
                        "```diff",
                        sec_diff.rstrip(),
                        "```",
                    ])
        lines.append("")

    lines.extend(["## Workflow Contract Findings", ""])
    if workflow_contract_findings:
        for finding in workflow_contract_findings:
            lines.append(f"- {finding}")
    else:
        lines.append("- none")
    lines.append("")

    lines.extend(["## Skill Review Signals", ""])
    if skill_review_signals:
        for signal in skill_review_signals:
            lines.append(f"- {signal}")
    else:
        lines.append("- none")
    lines.append("")

    lines.extend(["## Workspace Invariants", ""])
    if invariant_findings:
        for inv in invariant_findings:
            status = inv["status"]
            name = inv["name"]
            detail = inv["detail"]
            if status == "PASS":
                lines.append(f"- PASS: {name}")
            else:
                lines.append(f"- FAIL: {name} — {detail}")
    else:
        lines.append("- none")
    lines.append("")

    lines.extend(["## Suggested Preview Artifacts", ""])
    for item in findings:
        if item["preview_path"] and item["diff_path"]:
            lines.append(
                f"- {item['filename']}: preview and diff generated for review."
            )
        else:
            lines.append(f"- {item['filename']}: no preview artifact generated.")

    lines.extend(
        [
            "",
            "## Version Impact",
            "",
            f"- Change type: {version_impact}",
            "- Recommended: bump root_file_version after applying changes" if version_impact == "structural" else "- Content-only change: no version bump required",
            "",
            "## Apply Boundary",
            "",
            "- This run does not modify the target workspace.",
            "- Review the diagnosis, preview files, and diffs before applying any change manually.",
            "- V1.3 optimize mode is diagnose-first and preview-only.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview-only optimization pass for existing OpenClaw agent root files.")
    parser.add_argument("--spec", required=True, help="Path to the proposal/scaffold JSON spec.")
    parser.add_argument("--workspace", required=True, help="Existing workspace directory to inspect.")
    parser.add_argument("--preview-out", required=True, help="Separate preview directory for report, preview files, and diffs.")
    parser.add_argument("--lite", action="store_true", help="Accept a minimal spec (skip full propose validation).")
    args = parser.parse_args()

    try:
        spec = load_json(args.spec)
        if args.lite:
            errors = validate_minimal_spec(spec)
        else:
            errors = validate_propose_spec(spec)
        if errors:
            print("FAIL")
            for item in errors:
                print(f"- {item}")
            return 1
        require_independent_agent(spec, operation="optimize", allow_minimal=args.lite)

        workspace_dir = resolve_path(args.workspace, context="--workspace")
        if not workspace_dir.exists() or not workspace_dir.is_dir():
            raise ValueError(f"Workspace directory does not exist: {workspace_dir}")

        preview_dir = resolve_path(args.preview_out, context="--preview-out")
        if preview_dir == workspace_dir or workspace_dir in preview_dir.parents:
            raise ValueError("Preview output must live outside the target workspace in V1.3 optimize mode.")

        preview_files_dir, diff_files_dir = prepare_preview_bundle(preview_dir)
        expected_files = render_all(spec)

        existing_contents = {
            filename: (workspace_dir / filename).read_text(encoding="utf-8")
            for filename in ALL_POSSIBLE_ROOT_FILES
            if (workspace_dir / filename).exists()
        }
        duplicate_heading_issues = find_duplicate_headings(existing_contents)
        workflow_contract_findings, skill_review_signals = run_workflow_hardening_diagnostics(spec, workspace_dir)

        # Determine which optional files to diagnose: those in workspace OR generated by spec
        optional_to_diagnose = [
            f for f in OPTIONAL_ROOT_FILENAMES
            if (workspace_dir / f).exists() or f in expected_files
        ]

        # Build file-size map for budget checks
        all_file_sizes = {name: len(text) for name, text in existing_contents.items()}
        host_profile = str(spec.get("host_profile", "generic-openclaw"))

        findings: list[dict[str, object]] = []
        for filename in list(ROOT_FILENAMES) + optional_to_diagnose:
            finding = diagnose_file(
                spec=spec,
                filename=filename,
                workspace_dir=workspace_dir,
                duplicate_heading_issues=duplicate_heading_issues,
            )

            # Content-level analysis (layered results)
            current_text = existing_contents.get(filename, "")
            if current_text:
                layered_issues = analyze_content_quality(
                    filename=filename,
                    content=current_text,
                    spec=spec,
                    host_profile=host_profile,
                    all_file_sizes=all_file_sizes,
                )
                if layered_issues:
                    existing_issues = finding["issues"] if finding["issues"] != ["none"] else []
                    finding["issues"] = existing_issues + [item["issue"] for item in layered_issues]
                    if finding["status"] == "aligned":
                        finding["status"] = "needs_update"
                    # Merge content issues into sections
                    file_sections: dict[str, dict[str, object]] = finding["sections"]  # type: ignore[assignment]
                    for item in layered_issues:
                        sec = item["section"]
                        if not sec:
                            continue
                        if sec not in file_sections:
                            file_sections[sec] = {"status": "needs_update", "layer": item["layer"], "issues": []}
                        sec_entry = file_sections[sec]
                        sec_entry["issues"] = sec_entry["issues"] + [item["issue"]]  # type: ignore[operator]
                        if sec_entry["status"] == "aligned":
                            sec_entry["status"] = "needs_update"

            if finding["status"] in {"needs_update", "missing"} and filename in expected_files:
                preview_path = preview_files_dir / filename
                diff_path = diff_files_dir / f"{filename}.diff"
                current_text = ""
                current_file = workspace_dir / filename
                if current_file.exists():
                    current_text = current_file.read_text(encoding="utf-8")
                expected_text = expected_files[filename]
                write_text(preview_path, expected_text)
                write_text(diff_path, build_diff(filename, current_text, expected_text))
                finding["preview_path"] = _try_relative(preview_path, preview_dir)
                finding["diff_path"] = _try_relative(diff_path, preview_dir)

                # Generate section-level diffs for needs_update sections
                file_sections = finding.get("sections", {})
                if isinstance(file_sections, dict):
                    for sec_name, sec_info in file_sections.items():
                        if not isinstance(sec_info, dict):
                            continue
                        if sec_info.get("status") != "needs_update":
                            continue
                        current_sec = _extract_section_text(current_text, sec_name)
                        expected_sec = _extract_section_text(expected_text, sec_name)
                        if current_sec and expected_sec:
                            sec_diff = build_section_diff(filename, sec_name, current_sec, expected_sec)
                            if sec_diff:
                                sec_info["diff"] = sec_diff
            findings.append(finding)

        forbidden_files = [workspace_dir / name for name in FORBIDDEN_FILENAMES if (workspace_dir / name).exists()]
        invariant_findings = check_workspace_invariants(
            workspace_dir,
            existing_contents,
            spec_red_lines=spec.get("red_lines"),
        )
        version_impact = suggest_version_bump(findings)
        report_text = build_report(
            spec,
            workspace_dir,
            preview_dir,
            findings,
            forbidden_files,
            workflow_contract_findings,
            skill_review_signals,
            invariant_findings=invariant_findings,
            version_impact=version_impact,
        )
        write_text(preview_dir / "optimize-report.md", report_text)

        aligned = sum(1 for item in findings if item["status"] == "aligned")
        needs_update = sum(1 for item in findings if item["status"] == "needs_update")
        missing = sum(1 for item in findings if item["status"] == "missing")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}")
        return 1

    print(
        "PASS: optimization preview written "
        f"(aligned={aligned}, needs_update={needs_update}, missing={missing}) -> {preview_dir}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
