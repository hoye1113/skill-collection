from __future__ import annotations

import re
from pathlib import Path
from typing import Any


TEXT_FILE_SUFFIXES = {".html", ".htm", ".md", ".css", ".js", ".json", ".txt"}
PROMPT_ONLY_PHRASES = (
    "attempt to",
    "try to",
    "if supported",
    "use relative paths",
    "wait a bit",
)
_URL_SCHEME_RE = re.compile(r"https?://|ftp://", re.IGNORECASE)

ABSOLUTE_PATH_PATTERNS = (
    ("Windows drive path", re.compile(r"[A-Za-z]:[\\/][^\s\"'<>]+")),
    ("UNC path", re.compile(r"\\\\[^\s\"'<>]+")),
    ("file URI", re.compile(r"file://[^\s\"'<>]+", re.IGNORECASE)),
    ("macOS home path", re.compile(r"/Users/[^\s\"'<>]+")),
    ("Linux home path", re.compile(r"/home/[^\s\"'<>]+")),
    ("Windows environment variable", re.compile(r"%[A-Za-z_]+%[\\/][^\s\"'<>]+")),
    ("Unix environment variable", re.compile(r"\$[A-Za-z_]+[\\/][^\s\"'<>]+")),
    ("Windows system folder", re.compile(r"[A-Za-z]:[\\/]Program\s+Files[\\/][^\s\"'<>]+", re.IGNORECASE)),
)


def resolve_workspace_path(workspace_dir: Path, raw_path: str) -> Path:
    return (workspace_dir / Path(raw_path)).resolve()


def display_path(path: Path, workspace_dir: Path) -> str:
    try:
        return str(path.relative_to(workspace_dir)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def extract_section(markdown_text: str, heading: str) -> str:
    lines = markdown_text.splitlines()
    capture = False
    collected: list[str] = []
    for line in lines:
        if line.strip() == heading:
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if capture:
            collected.append(line)
    return "\n".join(collected).strip()


def iter_text_files(root_path: Path) -> list[Path]:
    if not root_path.exists():
        return []
    if root_path.is_file():
        return [root_path] if root_path.suffix.lower() in TEXT_FILE_SUFFIXES else []
    return sorted(
        path for path in root_path.rglob("*") if path.is_file() and path.suffix.lower() in TEXT_FILE_SUFFIXES
    )


def gather_skill_review_targets(spec: dict[str, Any], workspace_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    seen: set[Path] = set()

    resources = spec.get("skill_resources")
    if isinstance(resources, dict):
        entrypoints = resources.get("primary_skill_entrypoints")
        if isinstance(entrypoints, list):
            for entry in entrypoints:
                entry_text = str(entry).strip()
                if not entry_text:
                    continue
                candidate = resolve_workspace_path(workspace_dir, entry_text)
                if candidate.exists() and candidate.is_file() and candidate not in seen:
                    seen.add(candidate)
                    candidates.append(candidate)

    workflow_hardening = spec.get("workflow_hardening")
    if isinstance(workflow_hardening, dict):
        owners = workflow_hardening.get("sidecar_write_ownership")
        if isinstance(owners, list):
            for item in owners:
                if not isinstance(item, dict):
                    continue
                owner_text = str(item.get("owner", "")).strip()
                if not owner_text:
                    continue
                owner_path = resolve_workspace_path(workspace_dir, owner_text)
                if owner_path.is_dir():
                    candidate = owner_path / "SKILL.md"
                else:
                    candidate = owner_path
                if candidate.exists() and candidate.is_file() and candidate not in seen:
                    seen.add(candidate)
                    candidates.append(candidate)

    return candidates


def run_workflow_hardening_diagnostics(spec: dict[str, Any], workspace_dir: Path) -> tuple[list[str], list[str]]:
    workflow_hardening = spec.get("workflow_hardening")
    if not isinstance(workflow_hardening, dict):
        return [], []

    workflow_contract_findings: list[str] = []
    skill_review_signals: list[str] = []

    agents_path = workspace_dir / "AGENTS.md"
    agents_text = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    session_startup = extract_section(agents_text, "## Session Startup")
    red_lines = extract_section(agents_text, "## Red Lines")

    approval_gates = workflow_hardening.get("approval_gates")
    if isinstance(approval_gates, list):
        for item in approval_gates:
            if not isinstance(item, dict):
                continue
            gate_name = str(item.get("name", "")).strip()
            if not gate_name:
                continue
            if gate_name not in agents_text:
                workflow_contract_findings.append(f"approval gate missing from AGENTS.md: {gate_name}")
            elif gate_name not in session_startup and gate_name not in red_lines:
                workflow_contract_findings.append(
                    f"approval gate is not elevated into Session Startup or Red Lines: {gate_name}"
                )

    canonical_source = workflow_hardening.get("canonical_source")
    canonical_path: Path | None = None
    if isinstance(canonical_source, dict):
        canonical_text = str(canonical_source.get("path", "")).strip()
        if canonical_text:
            canonical_path = resolve_workspace_path(workspace_dir, canonical_text)
            if not canonical_path.exists():
                workflow_contract_findings.append(f"canonical source path is missing: {canonical_text}")

    derived_export_suffixes: set[str] = set()
    derived_exports = workflow_hardening.get("derived_exports")
    if isinstance(derived_exports, list):
        for item in derived_exports:
            if not isinstance(item, dict):
                continue
            export_text = str(item.get("path", "")).strip()
            if not export_text:
                continue
            export_path = resolve_workspace_path(workspace_dir, export_text)
            if canonical_path is not None and canonical_path.exists():
                if export_path == canonical_path:
                    workflow_contract_findings.append(
                        f"derived artifact confusion: export path resolves to canonical source path: {export_text}"
                    )
                elif canonical_path.is_dir() and canonical_path in export_path.parents:
                    workflow_contract_findings.append(
                        f"derived artifact confusion: export path lives inside canonical source root: {export_text}"
                    )
            suffix = Path(export_text).suffix.lower()
            if suffix:
                derived_export_suffixes.add(suffix)

    install_contracts = workflow_hardening.get("install_contracts")
    if isinstance(install_contracts, list):
        for item in install_contracts:
            if not isinstance(item, dict):
                continue
            contract_text = str(item.get("contract_path", "")).strip()
            capability = str(item.get("capability", "")).strip() or contract_text
            if contract_text and not resolve_workspace_path(workspace_dir, contract_text).exists():
                workflow_contract_findings.append(
                    f"conditional-runtime contract missing for {capability}: {contract_text}"
                )

    deterministic_helpers = workflow_hardening.get("deterministic_helpers")
    if isinstance(deterministic_helpers, list):
        for item in deterministic_helpers:
            if not isinstance(item, dict):
                continue
            entry_text = str(item.get("entrypoint", "")).strip()
            action = str(item.get("action", "")).strip() or entry_text
            if entry_text and not resolve_workspace_path(workspace_dir, entry_text).exists():
                workflow_contract_findings.append(
                    f"prompt-only workflow gap: missing deterministic helper for {action}: {entry_text}"
                )

    asset_staging = workflow_hardening.get("asset_staging")
    if isinstance(asset_staging, dict):
        asset_root_text = str(asset_staging.get("asset_root", "")).strip()
        if asset_root_text:
            asset_root_path = resolve_workspace_path(workspace_dir, asset_root_text)
            if not asset_root_path.exists():
                workflow_contract_findings.append(f"asset staging root is missing: {asset_root_text}")

        if canonical_path is not None and canonical_path.exists():
            text_files = iter_text_files(canonical_path)
            for file_path in text_files:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                for label, pattern in ABSOLUTE_PATH_PATTERNS:
                    match = pattern.search(content)
                    if match:
                        # Skip URL schemes (https://, http://, ftp://)
                        prefix = content[max(0, match.start() - 10):match.start()]
                        if _URL_SCHEME_RE.search(prefix + match.group()[:10]):
                            continue
                        workflow_contract_findings.append(
                            f"portability finding: {label} leaked into canonical source file {display_path(file_path, workspace_dir)}"
                        )
                        break

            if canonical_path.is_dir() and derived_export_suffixes:
                for suffix in sorted(derived_export_suffixes):
                    for file_path in canonical_path.rglob(f"*{suffix}"):
                        if file_path.is_file():
                            workflow_contract_findings.append(
                                "derived artifact confusion: found "
                                f"{suffix} file inside canonical source root: {display_path(file_path, workspace_dir)}"
                            )

    sidecar_owners = workflow_hardening.get("sidecar_write_ownership")
    if isinstance(sidecar_owners, list):
        for item in sidecar_owners:
            if not isinstance(item, dict):
                continue
            owner_text = str(item.get("owner", "")).strip()
            if not owner_text:
                continue
            owner_path = resolve_workspace_path(workspace_dir, owner_text)
            if not owner_path.exists():
                workflow_contract_findings.append(f"sidecar owner path is missing: {owner_text}")
            elif owner_path.is_dir() and not (owner_path / "SKILL.md").exists():
                workflow_contract_findings.append(f"sidecar owner is missing SKILL.md: {owner_text}")

    for skill_path in gather_skill_review_targets(spec, workspace_dir):
        content = skill_path.read_text(encoding="utf-8", errors="replace").lower()
        matched = [phrase for phrase in PROMPT_ONLY_PHRASES if phrase in content]
        if matched:
            skill_review_signals.append(
                "prompt-only workflow signal in "
                f"{display_path(skill_path, workspace_dir)}: found {', '.join(matched)}; "
                "consider deterministic helper / install contract / staging"
            )

    return workflow_contract_findings, skill_review_signals
