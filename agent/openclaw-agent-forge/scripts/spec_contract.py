from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FORBIDDEN_FILENAMES = {
    "PROMOTION_ANALYSIS.md",
    "WORKSPACE_SEMANTICS.md",
    "AGENT_PROMOTION_ANALYSIS.md",
    "RESUME_STRATEGY.md",
}

ROOT_FILENAMES = ("IDENTITY.md", "SOUL.md", "AGENTS.md", "TOOLS.md")
OPTIONAL_ROOT_FILENAMES = ("BOOTSTRAP.md", "USER.md", "HEARTBEAT.md")
ALL_POSSIBLE_ROOT_FILES = ROOT_FILENAMES + OPTIONAL_ROOT_FILENAMES
OPTIMIZE_ALLOWED_TOP_LEVEL = {"optimize-report.md", "preview", "diffs"}
OPTIMIZE_STATUSES = {"aligned", "needs_update", "missing"}
BLOAT_LINE_THRESHOLD = 200
CHARACTER_BUDGET_SINGLE = 12_000
CHARACTER_BUDGET_TOTAL = 60_000

# Daily memory budget (enforced by OpenClaw runtime, not by this skill)
DAILY_MEMORY_MAX_CHARS = 1_200
DAILY_MEMORY_TOTAL_MAX_CHARS = 2_800
DAILY_MEMORY_DAYS = 2

REQUIRED_ANALYSIS_KEYS = [
    "skill_name",
    "host_profile",
    "promotion_decision",
    "core_role",
    "primary_value",
    "lazy_default_to_avoid",
    "non_negotiable_quality_bar",
    "canonical_deliverables",
    "workflow_state",
    "resume_entry_files",
    "native_capabilities",
    "conditional_capabilities",
    "non_capabilities",
    "what_stays_in_skill_md",
    "what_moves_to_root_files",
]

REQUIRED_ROOT_STRING_FIELDS = [
    "judgment_result",
    "host_profile",
    "preferred_control_pattern",
    "name",
    "role",
    "public_identity",
    "workspace_positioning",
]

REQUIRED_ROOT_LIST_FIELDS = [
    "non_negotiables",
    "enduring_style",
    "session_startup",
    "red_lines",
    "default_behavior",
    "boundaries",
    "workspace_layout",
    "output_roots",
    "local_conventions",
]

MINIMAL_SPEC_FIELDS = [
    "judgment_result",
    "host_profile",
    "name",
    "role",
    "public_identity",
]

REQUIRED_ROOT_FIELDS = [
    "judgment_result",
    "promotion_rationale",
    "host_profile",
    "preferred_control_pattern",
    "agent_promotion_analysis",
    "workspace_semantics",
    "name",
    "role",
    "public_identity",
    "non_negotiables",
    "enduring_style",
    "workspace_positioning",
    "session_startup",
    "red_lines",
    "default_behavior",
    "boundaries",
    "workspace_layout",
    "output_roots",
    "local_conventions",
    "capabilities",
    "skill_resources",
    "resume_strategy",
    "risks_and_non_capabilities",
]

REQUIRED_RESUME_KEYS = [
    "global_resume_file",
    "task_topic_resume_file",
    "deliverable_inspection_path",
    "if_state_missing",
    "never_assume",
]

ROOT_FILE_REQUIREMENTS = {
    "IDENTITY.md": {
        "required": ["# IDENTITY.md", "## Public Identity"],
        "forbidden": ["## Capabilities", "## Output Roots", "## Session Startup"],
    },
    "SOUL.md": {
        "required": ["# SOUL.md", "## Non-Negotiables", "## Enduring Style"],
        "forbidden": ["## Output Roots", "## Skill Resources"],
    },
    "AGENTS.md": {
        "required": [
            "# AGENTS.md",
            "## Workspace Positioning",
            "## Session Startup",
            "## Red Lines",
            "## Default Behavior",
            "## Resume Strategy",
            "## Boundaries",
            "## Workspace Layout",
        ],
        "forbidden": ["## Capabilities", "## Public Identity"],
    },
    "TOOLS.md": {
        "required": ["# TOOLS.md", "## Output Roots", "## Local Conventions", "## Capabilities", "## Skill Resources"],
        "forbidden": ["## Public Identity", "## Session Startup"],
    },
    "BOOTSTRAP.md": {
        "required": ["# BOOTSTRAP.md"],
        "forbidden": ["## Capabilities", "## Output Roots"],
    },
    "USER.md": {
        "required": ["# USER.md"],
        "forbidden": ["## Capabilities", "## Session Startup"],
    },
    "HEARTBEAT.md": {
        "required": ["# HEARTBEAT.md"],
        "forbidden": ["## Capabilities", "## Public Identity"],
    },
}

REQUIRED_WORKSPACE_TYPES = {
    "final deliverables": False,
    "workflow state": False,
    "scratch / preview": False,
    "export / package": False,
    "skill resources": False,
}

REQUIRED_OPTIMIZE_REPORT_SECTIONS = [
    "# Root File Optimization Preview",
    "## Summary",
    "## Workspace Warnings",
    "## Diagnostic Findings",
    "## Workflow Contract Findings",
    "## Skill Review Signals",
    "## Workspace Invariants",
    "## Suggested Preview Artifacts",
    "## Version Impact",
    "## Apply Boundary",
]


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Spec must be a JSON object.")
    return payload


def ensure_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{field_name}' must be a non-empty string.")
    return value.strip()


def ensure_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"Field '{field_name}' must be a list of strings.")
    items = [str(item).strip() for item in value if str(item).strip()]
    if not items:
        raise ValueError(f"Field '{field_name}' must contain at least one non-empty item.")
    return items


VALID_CAPABILITY_CLASSIFICATIONS = {"runtime-conditional", "dev-time-only", "one-shot-setup"}


def validate_conditional_capabilities(value: Any, field_name: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, list) or not value:
        errors.append(f"{field_name} must be a non-empty list")
        return errors
    for index, item in enumerate(value):
        if isinstance(item, str):
            errors.append(
                f"{field_name}[{index}] uses legacy flat string format; "
                "expected object with 'name', 'classification', and 'reason'"
            )
            continue
        if not isinstance(item, dict) or not item:
            errors.append(f"{field_name}[{index}] must be an object")
            continue
        if not has_non_empty_string(item.get("name")):
            errors.append(f"{field_name}[{index}].name must be a non-empty string")
        classification = str(item.get("classification", "")).strip()
        if classification not in VALID_CAPABILITY_CLASSIFICATIONS:
            errors.append(
                f"{field_name}[{index}].classification must be one of: "
                + ", ".join(sorted(VALID_CAPABILITY_CLASSIFICATIONS))
            )
        if not has_non_empty_string(item.get("reason")):
            errors.append(f"{field_name}[{index}].reason must be a non-empty string")
    return errors


def validate_memory_config(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict) or not value:
        return ["memory_config must be a non-empty object"]
    if not isinstance(value.get("enabled"), bool):
        errors.append("memory_config.enabled must be a boolean")
    if not isinstance(value.get("daily_notes"), bool):
        errors.append("memory_config.daily_notes must be a boolean")
    if not isinstance(value.get("long_term_memory"), bool):
        errors.append("memory_config.long_term_memory must be a boolean")
    boundary = value.get("security_boundary")
    if boundary is not None and str(boundary).strip() not in {"main_session_only", "always"}:
        errors.append("memory_config.security_boundary must be 'main_session_only' or 'always'")
    curation = value.get("curation_schedule")
    if curation is not None and not isinstance(curation, str):
        errors.append("memory_config.curation_schedule must be a string")
    what = value.get("what_to_capture")
    if what is not None and (not isinstance(what, list) or not all(isinstance(i, str) for i in what)):
        errors.append("memory_config.what_to_capture must be a list of strings")
    return errors


def validate_heartbeat_config(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict) or not value:
        return ["heartbeat_config must be a non-empty object"]
    if not isinstance(value.get("enabled"), bool):
        errors.append("heartbeat_config.enabled must be a boolean")
    tasks = value.get("tasks")
    if tasks is not None:
        if not isinstance(tasks, list) or not all(isinstance(i, str) for i in tasks):
            errors.append("heartbeat_config.tasks must be a list of strings")
    quiet = value.get("quiet_hours")
    if quiet is not None and not isinstance(quiet, str):
        errors.append("heartbeat_config.quiet_hours must be a string")
    state = value.get("state_file")
    if state is not None and not isinstance(state, str):
        errors.append("heartbeat_config.state_file must be a string")
    return errors


def validate_bootstrap_config(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict) or not value:
        return ["bootstrap_config must be a non-empty object"]
    if not isinstance(value.get("enabled"), bool):
        errors.append("bootstrap_config.enabled must be a boolean")
    topics = value.get("conversation_topics")
    if topics is not None:
        if not isinstance(topics, list) or not all(isinstance(i, str) for i in topics):
            errors.append("bootstrap_config.conversation_topics must be a list of strings")
    return errors


def validate_group_chat_config(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict) or not value:
        return ["group_chat_behavior must be a non-empty object"]
    if not isinstance(value.get("enabled"), bool):
        errors.append("group_chat_behavior.enabled must be a boolean")
    for key in ("respond_when", "stay_silent_when"):
        val = value.get(key)
        if val is not None:
            if not isinstance(val, list) or not all(isinstance(i, str) for i in val):
                errors.append(f"group_chat_behavior.{key} must be a list of strings")
    return errors


def ensure_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Field '{field_name}' must be an object.")
    if not value:
        raise ValueError(f"Field '{field_name}' must not be empty.")
    return value


def has_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def has_non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and any(str(item).strip() for item in value)


def normalize_path_token(value: str) -> str:
    return value.strip().replace("\\", "/").rstrip("/").casefold()


def is_workspace_relative_path_token(value: str) -> bool:
    token = value.strip()
    if not token:
        return False
    if token.startswith("~"):
        return False
    path = Path(token)
    if path.is_absolute() or path.drive or path.root:
        return False
    return ".." not in path.parts


def validate_minimal_spec(spec: dict[str, Any]) -> list[str]:
    """Validate only MINIMAL_SPEC_FIELDS — used in --lite mode."""
    errors: list[str] = []
    for field in MINIMAL_SPEC_FIELDS:
        if not has_non_empty_string(spec.get(field)):
            errors.append(f"Missing non-empty field: {field}")
    return errors


def require_independent_agent(spec: dict[str, Any], operation: str = "scaffold", allow_minimal: bool = False) -> None:
    judgment = ensure_string(spec.get("judgment_result"), "judgment_result")
    if judgment != "独立 agent":
        raise ValueError(f"V1.3 {operation} only supports specs whose judgment_result is '独立 agent'.")

    if not allow_minimal:
        analysis = ensure_mapping(spec.get("agent_promotion_analysis"), "agent_promotion_analysis")
        decision = ensure_string(analysis.get("promotion_decision"), "agent_promotion_analysis.promotion_decision")
        if decision != "独立 agent":
            raise ValueError(
                f"V1.3 {operation} only supports specs whose agent_promotion_analysis.promotion_decision is '独立 agent'."
            )


def validate_workflow_hardening_spec(payload: Any) -> list[str]:
    if not isinstance(payload, dict) or not payload:
        return ["workflow_hardening must be a non-empty object"]

    errors: list[str] = []
    populated_sections = 0

    canonical_source_path: str | None = None
    canonical_source = payload.get("canonical_source")
    if canonical_source is not None:
        populated_sections += 1
        if not isinstance(canonical_source, dict) or not canonical_source:
            errors.append("workflow_hardening.canonical_source must be a non-empty object")
        else:
            if not has_non_empty_string(canonical_source.get("path")):
                errors.append("workflow_hardening.canonical_source.path must be a non-empty string")
            else:
                canonical_source_path = str(canonical_source.get("path")).strip()
                if not is_workspace_relative_path_token(canonical_source_path):
                    errors.append("workflow_hardening.canonical_source.path must be a workspace-relative path")
            if not has_non_empty_string(canonical_source.get("reason")):
                errors.append("workflow_hardening.canonical_source.reason must be a non-empty string")

    def validate_object_list(section_name: str, required_keys: list[str]) -> list[dict[str, Any]]:
        nonlocal populated_sections
        items = payload.get(section_name)
        if items is None:
            return []
        populated_sections += 1
        if not isinstance(items, list) or not items:
            errors.append(f"workflow_hardening.{section_name} must be a non-empty list")
            return []

        validated_items: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict) or not item:
                errors.append(f"workflow_hardening.{section_name}[{index}] must be a non-empty object")
                continue
            for key in required_keys:
                value = item.get(key)
                if key in {"writes_to", "must_not_write"}:
                    if not has_non_empty_list(value):
                        errors.append(f"workflow_hardening.{section_name}[{index}].{key} must be a non-empty list")
                elif not has_non_empty_string(value):
                    errors.append(f"workflow_hardening.{section_name}[{index}].{key} must be a non-empty string")
            validated_items.append(item)
        return validated_items

    derived_exports = validate_object_list(
        "derived_exports",
        ["path", "source_path", "reason", "approval_gate"],
    )
    approval_gates = validate_object_list(
        "approval_gates",
        ["name", "blocks_until", "failure_if_skipped"],
    )
    install_contracts = validate_object_list(
        "install_contracts",
        ["capability", "contract_path", "setup_entry", "verify_entry"],
    )
    deterministic_helpers = validate_object_list(
        "deterministic_helpers",
        ["action", "kind", "entrypoint", "why_needed"],
    )
    sidecar_write_ownership = validate_object_list(
        "sidecar_write_ownership",
        ["owner", "writes_to", "must_not_write"],
    )

    asset_staging = payload.get("asset_staging")
    if asset_staging is not None:
        populated_sections += 1
        if not isinstance(asset_staging, dict) or not asset_staging:
            errors.append("workflow_hardening.asset_staging must be a non-empty object")
        else:
            for key in ("asset_root", "rewrite_rule", "absolute_path_policy"):
                if not has_non_empty_string(asset_staging.get(key)):
                    errors.append(f"workflow_hardening.asset_staging.{key} must be a non-empty string")

    if populated_sections == 0:
        errors.append("workflow_hardening must define at least one populated section")

    if derived_exports and not canonical_source_path:
        errors.append("workflow_hardening.derived_exports requires workflow_hardening.canonical_source")

    if canonical_source_path:
        canonical_norm = normalize_path_token(canonical_source_path)
        for index, item in enumerate(derived_exports):
            source_path = item.get("source_path")
            export_path = item.get("path")
            if has_non_empty_string(source_path) and not is_workspace_relative_path_token(str(source_path)):
                errors.append(
                    f"workflow_hardening.derived_exports[{index}].source_path must be a workspace-relative path"
                )
            if has_non_empty_string(export_path) and not is_workspace_relative_path_token(str(export_path)):
                errors.append(f"workflow_hardening.derived_exports[{index}].path must be a workspace-relative path")
            if has_non_empty_string(source_path) and normalize_path_token(str(source_path)) != canonical_norm:
                errors.append(
                    f"workflow_hardening.derived_exports[{index}].source_path must match workflow_hardening.canonical_source.path"
                )
            if has_non_empty_string(export_path) and normalize_path_token(str(export_path)) == canonical_norm:
                errors.append(
                    f"workflow_hardening.derived_exports[{index}].path must differ from workflow_hardening.canonical_source.path"
                )

    for index, item in enumerate(deterministic_helpers):
        kind = item.get("kind")
        if has_non_empty_string(kind) and str(kind).strip() not in {"script", "interface", "file_convention"}:
            errors.append(
                f"workflow_hardening.deterministic_helpers[{index}].kind must be one of: script, interface, file_convention"
            )
        entrypoint = item.get("entrypoint")
        if has_non_empty_string(entrypoint) and not is_workspace_relative_path_token(str(entrypoint)):
            errors.append(
                f"workflow_hardening.deterministic_helpers[{index}].entrypoint must be a workspace-relative path"
            )

    for index, item in enumerate(install_contracts):
        contract_path = item.get("contract_path")
        if has_non_empty_string(contract_path) and not is_workspace_relative_path_token(str(contract_path)):
            errors.append(
                f"workflow_hardening.install_contracts[{index}].contract_path must be a workspace-relative path"
            )

    writable_roots: dict[str, str] = {}
    for index, item in enumerate(sidecar_write_ownership):
        owner = item.get("owner")
        if has_non_empty_string(owner) and not is_workspace_relative_path_token(str(owner)):
            errors.append(f"workflow_hardening.sidecar_write_ownership[{index}].owner must be a workspace-relative path")
        writes_to = [normalize_path_token(str(entry)) for entry in item.get("writes_to", []) if str(entry).strip()]
        must_not_write = [normalize_path_token(str(entry)) for entry in item.get("must_not_write", []) if str(entry).strip()]
        for key in ("writes_to", "must_not_write"):
            for entry in item.get(key, []):
                if str(entry).strip() and not is_workspace_relative_path_token(str(entry)):
                    errors.append(
                        f"workflow_hardening.sidecar_write_ownership[{index}].{key} entries must be workspace-relative paths"
                    )
                    break
        overlap = sorted(set(writes_to) & set(must_not_write))
        if overlap:
            errors.append(
                f"workflow_hardening.sidecar_write_ownership[{index}] has overlapping writes_to and must_not_write: "
                + ", ".join(overlap)
            )

        owner_name = str(item.get("owner", "")).strip() or f"owner[{index}]"
        for path_token in writes_to:
            previous_owner = writable_roots.get(path_token)
            if previous_owner and previous_owner != owner_name:
                errors.append(
                    "workflow_hardening.sidecar_write_ownership declares overlapping writable root "
                    f"'{path_token}' for both {previous_owner} and {owner_name}"
                )
            else:
                writable_roots[path_token] = owner_name

    return errors


def validate_propose_spec(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_ROOT_STRING_FIELDS:
        if not has_non_empty_string(spec.get(field)):
            errors.append(f"Missing non-empty field: {field}")

    for field in REQUIRED_ROOT_LIST_FIELDS:
        if not has_non_empty_list(spec.get(field)):
            errors.append(f"{field} must be a non-empty list")

    rationale = spec.get("promotion_rationale")
    if not (has_non_empty_string(rationale) or has_non_empty_list(rationale)):
        errors.append("Missing promotion_rationale content")

    analysis = spec.get("agent_promotion_analysis")
    if not isinstance(analysis, dict):
        errors.append("Missing object: agent_promotion_analysis")
    else:
        for key in REQUIRED_ANALYSIS_KEYS:
            value = analysis.get(key)
            if key == "conditional_capabilities":
                errors.extend(validate_conditional_capabilities(value, f"agent_promotion_analysis.{key}"))
            elif isinstance(value, list):
                if not has_non_empty_list(value):
                    errors.append(f"agent_promotion_analysis.{key} must be a non-empty list")
            elif not has_non_empty_string(value):
                errors.append(f"agent_promotion_analysis.{key} must be a non-empty string or list")
        if has_non_empty_string(spec.get("judgment_result")) and has_non_empty_string(analysis.get("promotion_decision")):
            if str(spec.get("judgment_result")).strip() != str(analysis.get("promotion_decision")).strip():
                errors.append("judgment_result and agent_promotion_analysis.promotion_decision must match")
        if has_non_empty_string(spec.get("host_profile")) and has_non_empty_string(analysis.get("host_profile")):
            if str(spec.get("host_profile")).strip() != str(analysis.get("host_profile")).strip():
                errors.append("host_profile and agent_promotion_analysis.host_profile must match")

    semantics = spec.get("workspace_semantics")
    if not isinstance(semantics, list) or not semantics:
        errors.append("workspace_semantics must be a non-empty list")
    else:
        required_types = dict(REQUIRED_WORKSPACE_TYPES)
        for index, item in enumerate(semantics):
            if not isinstance(item, dict):
                errors.append(f"workspace_semantics[{index}] must be an object")
                continue
            for key in ("type", "path", "purpose", "persistent", "overwrite_rule"):
                if not has_non_empty_string(item.get(key)):
                    errors.append(f"workspace_semantics[{index}].{key} must be a non-empty string")
            shipped = item.get("shipped")
            if shipped is not None and not isinstance(shipped, bool):
                errors.append(f"workspace_semantics[{index}].shipped must be a boolean if present")
            item_type = str(item.get("type", "")).strip().lower()
            if item_type in required_types:
                required_types[item_type] = True
        for key, seen in required_types.items():
            if not seen:
                errors.append(f"workspace_semantics is missing category: {key}")

    missing_root_fields = [field for field in REQUIRED_ROOT_FIELDS if field not in spec]
    if missing_root_fields:
        errors.append("Missing required root-file fields: " + ", ".join(missing_root_fields))

    resume = spec.get("resume_strategy")
    if not isinstance(resume, dict):
        errors.append("resume_strategy must be an object")
    else:
        for key in REQUIRED_RESUME_KEYS:
            if not has_non_empty_string(resume.get(key)):
                errors.append(f"resume_strategy.{key} must be a non-empty string")

    capabilities = spec.get("capabilities")
    if not isinstance(capabilities, dict):
        errors.append("capabilities must be an object")
    else:
        for key in ("native", "conditional", "unsupported"):
            if key not in capabilities or not has_non_empty_list(capabilities.get(key)):
                errors.append(f"capabilities.{key} must be a non-empty list")

    resources = spec.get("skill_resources")
    if not isinstance(resources, dict):
        errors.append("skill_resources must be an object")
    else:
        if not any(has_non_empty_list(resources.get(key)) for key in resources):
            errors.append("skill_resources must contain at least one non-empty resource list")

    risks = spec.get("risks_and_non_capabilities")
    if not (has_non_empty_string(risks) or has_non_empty_list(risks)):
        errors.append("Missing risks_and_non_capabilities content")

    lazy_default = spec.get("lazy_default_to_avoid")
    if not has_non_empty_string(lazy_default):
        errors.append("Missing lazy_default_to_avoid: every agent must declare its lazy default")

    if "workflow_hardening" in spec:
        errors.extend(validate_workflow_hardening_spec(spec.get("workflow_hardening")))

    if "memory_config" in spec:
        errors.extend(validate_memory_config(spec.get("memory_config")))
    if "heartbeat_config" in spec:
        errors.extend(validate_heartbeat_config(spec.get("heartbeat_config")))
    if "bootstrap_config" in spec:
        errors.extend(validate_bootstrap_config(spec.get("bootstrap_config")))
    if "group_chat_behavior" in spec:
        errors.extend(validate_group_chat_config(spec.get("group_chat_behavior")))

    return errors


def validate_scaffold_output(output_dir: Path) -> list[str]:
    errors: list[str] = []

    if not output_dir.exists():
        return [f"Output directory does not exist: {output_dir}"]

    for forbidden in FORBIDDEN_FILENAMES:
        if (output_dir / forbidden).exists():
            errors.append(f"Forbidden governance file found: {output_dir / forbidden}")

    total_chars = 0
    for filename in ROOT_FILENAMES:
        rules = ROOT_FILE_REQUIREMENTS[filename]
        file_path = output_dir / filename
        if not file_path.exists():
            errors.append(f"Missing scaffold file: {file_path}")
            continue
        content = file_path.read_text(encoding="utf-8")
        file_chars = len(content)
        total_chars += file_chars
        if file_chars > CHARACTER_BUDGET_SINGLE:
            errors.append(
                f"{filename} exceeds single-file character budget: {file_chars} > {CHARACTER_BUDGET_SINGLE}"
            )
        for heading in rules["required"]:
            if heading not in content:
                errors.append(f"{filename} is missing heading: {heading}")
        for heading in rules["forbidden"]:
            if heading in content:
                errors.append(f"{filename} contains out-of-scope heading: {heading}")

    for filename in OPTIONAL_ROOT_FILENAMES:
        file_path = output_dir / filename
        if not file_path.exists():
            continue
        rules = ROOT_FILE_REQUIREMENTS.get(filename)
        if rules is None:
            continue
        content = file_path.read_text(encoding="utf-8")
        file_chars = len(content)
        total_chars += file_chars
        if file_chars > CHARACTER_BUDGET_SINGLE:
            errors.append(
                f"{filename} exceeds single-file character budget: {file_chars} > {CHARACTER_BUDGET_SINGLE}"
            )
        for heading in rules["required"]:
            if heading not in content:
                errors.append(f"{filename} is missing heading: {heading}")
        for heading in rules["forbidden"]:
            if heading in content:
                errors.append(f"{filename} contains out-of-scope heading: {heading}")

    if total_chars > CHARACTER_BUDGET_TOTAL:
        errors.append(
            f"Total root-file character budget exceeded: {total_chars} > {CHARACTER_BUDGET_TOTAL}"
        )

    return errors


def parse_optimize_report(report_text: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    for section in REQUIRED_OPTIMIZE_REPORT_SECTIONS:
        if section not in report_text:
            errors.append(f"Optimize report is missing section: {section}")

    entries: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    current_name: str | None = None
    collecting_issues = False

    for raw_line in report_text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("### "):
            name = line[4:].strip()
            collecting_issues = False
            if name in ROOT_FILENAMES:
                current_name = name
                current = {"issues": []}
                entries[name] = current
            else:
                current_name = None
                current = None
            continue

        if current is None or current_name is None:
            continue

        if line == "- Issues:":
            collecting_issues = True
            continue

        if collecting_issues:
            if line.startswith("  - "):
                current["issues"].append(line[4:].strip())
                continue
            collecting_issues = False

        if line.startswith("- Status: "):
            current["status"] = line.removeprefix("- Status: ").strip()
        elif line.startswith("- Current path: "):
            current["current_path"] = line.removeprefix("- Current path: ").strip()
        elif line.startswith("- Recommended action: "):
            current["recommended_action"] = line.removeprefix("- Recommended action: ").strip()
        elif line.startswith("- Preview path: "):
            current["preview_path"] = line.removeprefix("- Preview path: ").strip()
        elif line.startswith("- Diff path: "):
            current["diff_path"] = line.removeprefix("- Diff path: ").strip()

    for filename in ROOT_FILENAMES:
        entry = entries.get(filename)
        if entry is None:
            errors.append(f"Optimize report is missing diagnostic entry: {filename}")
            continue
        status = entry.get("status")
        if status not in OPTIMIZE_STATUSES:
            errors.append(f"Optimize report has invalid status for {filename}: {status}")
        if not has_non_empty_string(entry.get("current_path")):
            errors.append(f"Optimize report is missing current path for {filename}")
        if not has_non_empty_string(entry.get("recommended_action")):
            errors.append(f"Optimize report is missing recommended action for {filename}")
        issues = entry.get("issues")
        if not isinstance(issues, list) or not issues:
            errors.append(f"Optimize report is missing issues list for {filename}")

    return entries, errors


def validate_optimize_output(preview_dir: Path, workspace_dir: Path | None = None) -> list[str]:
    errors: list[str] = []

    if workspace_dir is not None:
        workspace_dir = workspace_dir.resolve()

    if not preview_dir.exists():
        return [f"Preview directory does not exist: {preview_dir}"]

    preview_dir = preview_dir.resolve()

    if workspace_dir is not None and (preview_dir == workspace_dir or workspace_dir in preview_dir.parents):
        errors.append("Preview output must live outside the target workspace in V1.3 optimize mode.")

    top_level = {path.name for path in preview_dir.iterdir()}
    unexpected_top_level = sorted(top_level - OPTIMIZE_ALLOWED_TOP_LEVEL)
    if unexpected_top_level:
        errors.append(
            "Preview bundle contains unexpected top-level entries: " + ", ".join(unexpected_top_level)
        )

    report_path = preview_dir / "optimize-report.md"
    preview_files_dir = preview_dir / "preview"
    diff_files_dir = preview_dir / "diffs"

    if not report_path.exists():
        errors.append(f"Missing optimize report: {report_path}")
        return errors
    if not preview_files_dir.exists() or not preview_files_dir.is_dir():
        errors.append(f"Missing preview directory: {preview_files_dir}")
    if not diff_files_dir.exists() or not diff_files_dir.is_dir():
        errors.append(f"Missing diff directory: {diff_files_dir}")

    report_entries, report_errors = parse_optimize_report(report_path.read_text(encoding="utf-8"))
    errors.extend(report_errors)

    allowed_preview = set(ALL_POSSIBLE_ROOT_FILES)
    allowed_diffs = {f"{filename}.diff" for filename in ALL_POSSIBLE_ROOT_FILES}

    if preview_files_dir.exists():
        preview_extra = sorted(
            path.name for path in preview_files_dir.iterdir() if path.is_file() and path.name not in allowed_preview
        )
        if preview_extra:
            errors.append("Preview directory contains unexpected files: " + ", ".join(preview_extra))

    if diff_files_dir.exists():
        diff_extra = sorted(
            path.name for path in diff_files_dir.iterdir() if path.is_file() and path.name not in allowed_diffs
        )
        if diff_extra:
            errors.append("Diff directory contains unexpected files: " + ", ".join(diff_extra))

    for filename in ALL_POSSIBLE_ROOT_FILES:
        entry = report_entries.get(filename)
        if entry is None:
            continue
        status = entry.get("status")
        preview_path = preview_files_dir / filename
        diff_path = diff_files_dir / f"{filename}.diff"

        if status in {"needs_update", "missing"}:
            if not preview_path.exists():
                errors.append(f"{filename} requires a preview artifact but none was found")
            if not diff_path.exists():
                errors.append(f"{filename} requires a diff artifact but none was found")
            if not has_non_empty_string(entry.get("preview_path")):
                errors.append(f"Optimize report is missing preview path for {filename}")
            if not has_non_empty_string(entry.get("diff_path")):
                errors.append(f"Optimize report is missing diff path for {filename}")
        elif status == "aligned":
            if preview_path.exists():
                errors.append(f"{filename} is aligned but a preview artifact was generated")
            if diff_path.exists():
                errors.append(f"{filename} is aligned but a diff artifact was generated")
            if has_non_empty_string(entry.get("preview_path")):
                errors.append(f"{filename} is aligned but the report lists a preview path")
            if has_non_empty_string(entry.get("diff_path")):
                errors.append(f"{filename} is aligned but the report lists a diff path")

    return errors
