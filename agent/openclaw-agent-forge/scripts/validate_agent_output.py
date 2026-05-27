#!/usr/bin/env python3
"""Validate an OpenClaw agent proposal spec and optional scaffold/optimize output.

Three modes:
- ``propose``: validate the spec JSON only
- ``scaffold``: validate spec + gate (judgment_result, promotion_decision) + output directory
- ``optimize``: validate spec + gate + preview bundle structure
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from spec_contract import (
    load_json,
    validate_minimal_spec,
    validate_optimize_output,
    validate_propose_spec,
    validate_scaffold_output,
)


def main() -> int:
    """Entry point for the validation CLI.

    Returns 0 on success, 1 on failure.  Prints PASS/FAIL to stdout.
    """
    parser = argparse.ArgumentParser(description="Validate an OpenClaw agent proposal spec and optional scaffold output.")
    parser.add_argument("--spec", required=True, help="Path to the proposal/scaffold JSON spec.")
    parser.add_argument("--mode", required=True, choices=["propose", "scaffold", "optimize"], help="Validation mode.")
    parser.add_argument("--out", help="Rendered workspace directory. Required in scaffold mode.")
    parser.add_argument("--preview-out", help="Optimize preview bundle directory. Required in optimize mode.")
    parser.add_argument("--workspace", help="Target workspace inspected by optimize mode.")
    parser.add_argument("--lite", action="store_true", help="Accept a minimal spec (skip full propose validation).")
    args = parser.parse_args()

    try:
        spec = load_json(args.spec)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}")
        return 1

    errors = validate_minimal_spec(spec) if args.lite else validate_propose_spec(spec)

    if args.mode == "scaffold":
        scaffold_gate_errors: list[str] = []
        if not args.out:
            scaffold_gate_errors.append("--out is required in scaffold mode")
        if str(spec.get("judgment_result", "")).strip() != "独立 agent":
            scaffold_gate_errors.append("scaffold mode requires judgment_result = 独立 agent")
        analysis = spec.get("agent_promotion_analysis")
        if not isinstance(analysis, dict) or str(analysis.get("promotion_decision", "")).strip() != "独立 agent":
            scaffold_gate_errors.append("scaffold mode requires agent_promotion_analysis.promotion_decision = 独立 agent")
        errors.extend(scaffold_gate_errors)
        if not scaffold_gate_errors and args.out:
            errors.extend(validate_scaffold_output(Path(args.out)))
    elif args.mode == "optimize":
        optimize_gate_errors: list[str] = []
        if not args.preview_out:
            optimize_gate_errors.append("--preview-out is required in optimize mode")
        if str(spec.get("judgment_result", "")).strip() != "独立 agent":
            optimize_gate_errors.append("optimize mode requires judgment_result = 独立 agent")
        if not args.lite:
            analysis = spec.get("agent_promotion_analysis")
            if not isinstance(analysis, dict) or str(analysis.get("promotion_decision", "")).strip() != "独立 agent":
                optimize_gate_errors.append("optimize mode requires agent_promotion_analysis.promotion_decision = 独立 agent")
        errors.extend(optimize_gate_errors)
        if not optimize_gate_errors and args.preview_out:
            workspace_path = Path(args.workspace) if args.workspace else None
            errors.extend(validate_optimize_output(Path(args.preview_out), workspace_path))

    if errors:
        print("FAIL")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"PASS: {args.mode} validation succeeded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
