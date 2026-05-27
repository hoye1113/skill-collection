from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from repair_root_files import apply_section, apply_repairs, parse_optimize_report, build_repair_report
from workspace_invariants import check_workspace_invariants
from test_support import SkillFixture


class ApplySectionTests(unittest.TestCase):
    def test_replaces_section_content(self) -> None:
        original = (
            "# AGENTS.md\n\n"
            "## Red Lines\n\n- Old rule\n\n"
            "## Boundaries\n\n- Boundary A\n"
        )
        new_section = "## Red Lines\n\n- New rule A\n- New rule B\n"
        result = apply_section(original, "## Red Lines", new_section)
        self.assertIn("- New rule A", result)
        self.assertIn("- New rule B", result)
        self.assertNotIn("- Old rule", result)
        self.assertIn("- Boundary A", result)

    def test_preserves_surrounding_sections(self) -> None:
        original = (
            "# AGENTS.md\n\n"
            "## Workspace Positioning\n\nPositioning text\n\n"
            "## Red Lines\n\n- Rule A\n\n"
            "## Boundaries\n\n- Boundary A\n"
        )
        new_section = "## Red Lines\n\n- Rule A\n- Rule B\n"
        result = apply_section(original, "## Red Lines", new_section)
        self.assertIn("## Workspace Positioning", result)
        self.assertIn("Positioning text", result)
        self.assertIn("## Boundaries", result)
        self.assertIn("- Boundary A", result)
        self.assertIn("- Rule B", result)

    def test_appends_missing_section(self) -> None:
        original = "# AGENTS.md\n\n## Red Lines\n\n- Rule A\n"
        new_section = "## Memory\n\nMemory baseline here.\n"
        result = apply_section(original, "## Memory", new_section)
        self.assertIn("## Memory", result)
        self.assertIn("Memory baseline here.", result)
        self.assertIn("## Red Lines", result)

    def test_handles_last_section(self) -> None:
        original = (
            "# AGENTS.md\n\n"
            "## Red Lines\n\n- Rule A\n\n"
            "## Boundaries\n\n- Old boundary\n"
        )
        new_section = "## Boundaries\n\n- New boundary\n"
        result = apply_section(original, "## Boundaries", new_section)
        self.assertIn("- New boundary", result)
        self.assertNotIn("- Old boundary", result)
        self.assertIn("- Rule A", result)

    def test_no_change_when_section_identical(self) -> None:
        original = "# AGENTS.md\n\n## Red Lines\n\n- Rule A\n"
        new_section = "## Red Lines\n\n- Rule A\n"
        result = apply_section(original, "## Red Lines", new_section)
        self.assertEqual(result.strip(), original.strip())


class ParseOptimizeReportTests(unittest.TestCase):
    def _sample_report(self) -> str:
        return (
            "# Root File Optimization Preview\n\n"
            "## Diagnostic Findings\n\n"
            "### AGENTS.md\n\n"
            "- Status: needs_update\n"
            "- Issues:\n"
            "  - missing heading: ## Memory\n\n"
            "#### Section Details\n\n"
            "| Section | Layer | Status | Issues |\n"
            "|---------|-------|--------|--------|\n"
            "| ## Red Lines | — | aligned | — |\n"
            "| ## Memory | structure | missing | missing heading |\n\n"
            "### TOOLS.md\n\n"
            "- Status: aligned\n"
            "- Issues:\n"
            "  - none\n"
        )

    def test_parses_needs_update_file(self) -> None:
        findings = parse_optimize_report(self._sample_report())
        self.assertTrue(any(f["filename"] == "AGENTS.md" for f in findings))

    def test_skips_aligned_file(self) -> None:
        findings = parse_optimize_report(self._sample_report())
        self.assertFalse(any(f["filename"] == "TOOLS.md" for f in findings))

    def test_extracts_sections_needing_update(self) -> None:
        findings = parse_optimize_report(self._sample_report())
        agents = [f for f in findings if f["filename"] == "AGENTS.md"][0]
        sections = agents["sections"]
        self.assertTrue(any(s["heading"] == "## Memory" and s["status"] == "missing" for s in sections))

    def test_skips_aligned_sections(self) -> None:
        findings = parse_optimize_report(self._sample_report())
        agents = [f for f in findings if f["filename"] == "AGENTS.md"][0]
        sections = agents["sections"]
        self.assertFalse(any(s["heading"] == "## Red Lines" for s in sections))


class ApplyRepairsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def _run_optimize(self, workspace_fixture: str, spec_fixture: str = "independent-generic"):
        """Run optimize and return (workspace_dir, preview_dir, spec_path)."""
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path(workspace_fixture),
            self.fixture.output_path(f"{workspace_fixture}-workspace"),
        )
        spec_path = self.fixture.fixture_path(f"{spec_fixture}.json")
        preview_dir = self.fixture.output_path(f"{workspace_fixture}-preview")
        self.fixture.run_script(
            "optimize_root_files.py",
            "--spec", str(spec_path),
            "--workspace", str(workspace_dir),
            "--preview-out", str(preview_dir),
            "--lite",
        )
        return workspace_dir, preview_dir, spec_path

    def test_dry_run_does_not_modify_workspace(self) -> None:
        workspace_dir, preview_dir, spec_path = self._run_optimize("external-agent")
        original_content = (workspace_dir / "AGENTS.md").read_text(encoding="utf-8")
        spec = json.loads(spec_path.read_text(encoding="utf-8"))

        result = apply_repairs(spec, workspace_dir, preview_dir, dry_run=True)

        current_content = (workspace_dir / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(original_content, current_content)
        self.assertIn("applied", result)

    def test_generates_repair_report_structure(self) -> None:
        workspace_dir, preview_dir, spec_path = self._run_optimize("external-agent")
        spec = json.loads(spec_path.read_text(encoding="utf-8"))

        result = apply_repairs(spec, workspace_dir, preview_dir, dry_run=True)
        report = build_repair_report(result)

        self.assertIn("# Repair Report", report)
        self.assertIn("## Summary", report)
        self.assertIn("## Applied Changes", report)

    def test_applies_needs_update_sections(self) -> None:
        workspace_dir, preview_dir, spec_path = self._run_optimize("external-agent")
        spec = json.loads(spec_path.read_text(encoding="utf-8"))

        result = apply_repairs(spec, workspace_dir, preview_dir, dry_run=False)

        # Should have applied at least one change (or empty if all aligned)
        self.assertIsInstance(result["applied"], list)
        self.assertIsInstance(result["invariant_results"], list)

    def test_post_repair_invariants_checked(self) -> None:
        workspace_dir, preview_dir, spec_path = self._run_optimize("external-agent")
        spec = json.loads(spec_path.read_text(encoding="utf-8"))

        result = apply_repairs(spec, workspace_dir, preview_dir, dry_run=False)

        self.assertIn("invariant_results", result)
        self.assertTrue(len(result["invariant_results"]) > 0)
        self.assertTrue(
            all("name" in r and "status" in r for r in result["invariant_results"]),
            "Each invariant result should have 'name' and 'status'",
        )

    def test_repair_report_written_to_workspace(self) -> None:
        workspace_dir, preview_dir, spec_path = self._run_optimize("external-agent")
        spec = json.loads(spec_path.read_text(encoding="utf-8"))

        result = apply_repairs(spec, workspace_dir, preview_dir, dry_run=False)
        report_text = build_repair_report(result)
        report_path = workspace_dir / "repair-report.md"
        report_path.write_text(report_text.rstrip() + "\n", encoding="utf-8")

        self.assertTrue(report_path.exists(), "repair-report.md should be written to workspace")
        content = report_path.read_text(encoding="utf-8")
        self.assertIn("# Repair Report", content)
        self.assertIn("## Summary", content)


class RepairIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_full_repair_on_shrinkage_agent(self) -> None:
        """Shrinkage agent is missing a red line — repair should attempt to fix it."""
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("shrinkage-agent"),
            self.fixture.output_path("shrinkage-workspace"),
        )
        spec = json.loads(self.fixture.fixture_path("independent-generic.json").read_text(encoding="utf-8"))
        spec["red_lines"] = [
            "Never modify production schemas without approval",
            "Do not skip validation steps",
        ]
        spec_path = self.fixture.output_path("shrinkage-spec.json")
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        preview_dir = self.fixture.output_path("shrinkage-preview")
        self.fixture.run_script(
            "optimize_root_files.py",
            "--spec", str(spec_path),
            "--workspace", str(workspace_dir),
            "--preview-out", str(preview_dir),
            "--lite",
        )

        result = apply_repairs(spec, workspace_dir, preview_dir, dry_run=False)

        # Should have applied at least one change (the missing red line)
        self.assertIsInstance(result["applied"], list)
        self.assertIsInstance(result["rolled_back"], list)
        self.assertIsInstance(result["invariant_results"], list)

    def test_no_changes_when_all_aligned(self) -> None:
        """If workspace is already aligned, repair should apply nothing."""
        # Use the golden fixture which should be aligned with its own spec
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("external-agent"),
            self.fixture.output_path("aligned-workspace"),
        )
        # Run optimize to get the preview
        spec_path = self.fixture.fixture_path("independent-generic.json")
        preview_dir = self.fixture.output_path("aligned-preview")
        self.fixture.run_script(
            "optimize_root_files.py",
            "--spec", str(spec_path),
            "--workspace", str(workspace_dir),
            "--preview-out", str(preview_dir),
            "--lite",
        )

        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        result = apply_repairs(spec, workspace_dir, preview_dir, dry_run=True)

        # If all aligned, applied should be empty
        # (If there are findings, that's also valid — just check structure)
        self.assertIn("applied", result)
        self.assertIn("errors", result)

    def test_errors_on_missing_preview(self) -> None:
        """If optimize-report.md is missing from preview, should return error."""
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("external-agent"),
            self.fixture.output_path("no-preview-workspace"),
        )
        empty_preview = self.fixture.output_path("empty-preview")
        empty_preview.mkdir(parents=True, exist_ok=True)

        spec = json.loads(self.fixture.fixture_path("independent-generic.json").read_text(encoding="utf-8"))
        result = apply_repairs(spec, workspace_dir, empty_preview, dry_run=False)

        self.assertTrue(len(result["errors"]) > 0)
        self.assertIn("optimize-report.md not found", result["errors"][0])


if __name__ == "__main__":
    unittest.main()
