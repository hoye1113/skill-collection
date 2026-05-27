#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Any
import sys
from pathlib import Path

from root_file_renderer import render_all
from spec_contract import (
    ALL_POSSIBLE_ROOT_FILES,
    FORBIDDEN_FILENAMES,
    load_json,
    require_independent_agent,
    validate_propose_spec,
)


def validate_required_fields(spec: dict[str, Any]) -> None:
    errors = validate_propose_spec(spec)
    if errors:
        joined = "\n- ".join(errors)
        raise ValueError("Spec failed validation:\n- " + joined)
    require_independent_agent(spec, operation="scaffold")


def check_target_paths(output_dir: Path) -> None:
    forbidden_paths = [output_dir / name for name in FORBIDDEN_FILENAMES if (output_dir / name).exists()]
    if forbidden_paths:
        joined = ", ".join(str(path) for path in forbidden_paths)
        raise ValueError(f"Output directory already contains forbidden governance files: {joined}")

    existing = [output_dir / name for name in ALL_POSSIBLE_ROOT_FILES if (output_dir / name).exists()]
    if existing:
        joined = ", ".join(str(path) for path in existing)
        raise ValueError(f"V1.3 scaffold refuses to overwrite existing root files: {joined}")


def write_file(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def resolve_path(raw_path: str | Path, context: str = "path") -> Path:
    """Resolve a path to an absolute Path, validating it is not empty.

    Raises ValueError if the path is empty or resolves to something invalid.
    """
    if not raw_path:
        raise ValueError(f"{context} is required and cannot be empty")
    path = Path(raw_path).resolve()
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render OpenClaw agent root files from a structured JSON spec.")
    parser.add_argument("--spec", required=True, help="Path to the proposal/scaffold JSON spec.")
    parser.add_argument("--out", required=True, help="Target workspace directory for the root files.")
    args = parser.parse_args()

    try:
        spec = load_json(args.spec)
        validate_required_fields(spec)
        output_dir = resolve_path(args.out, context="--out")
        output_dir.mkdir(parents=True, exist_ok=True)
        check_target_paths(output_dir)

        files = render_all(spec)

        for filename, content in files.items():
            write_file(output_dir / filename, content)

    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}")
        return 1

    file_list = ", ".join(files.keys())
    print(f"PASS: rendered {file_list}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
