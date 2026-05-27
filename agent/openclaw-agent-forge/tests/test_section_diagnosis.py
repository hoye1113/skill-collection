from __future__ import annotations

import json
import unittest
from pathlib import Path

from test_support import SkillFixture


class SectionDiagnosisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def _run_optimize(self, workspace_fixture: str, spec_fixture: str = "independent-generic") -> str:
        """Run optimize on a workspace fixture and return the report text."""
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path(workspace_fixture),
            self.fixture.output_path(f"{workspace_fixture}-workspace"),
        )
        spec_path = self.fixture.fixture_path(f"{spec_fixture}.json")
        preview_dir = self.fixture.output_path(f"{workspace_fixture}-preview")
        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(spec_path),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
            "--lite",
        )
        self.assertEqual(completed.returncode, 0)
        report_path = preview_dir / "optimize-report.md"
        self.assertTrue(report_path.exists())
        return report_path.read_text(encoding="utf-8")

    def test_report_contains_section_details_table(self) -> None:
        report = self._run_optimize("external-agent")
        self.assertIn("#### Section Details", report)
        self.assertIn("| Section | Layer | Status | Issues |", report)

    def test_report_contains_workspace_invariants(self) -> None:
        report = self._run_optimize("external-agent")
        self.assertIn("## Workspace Invariants", report)

    def test_report_contains_version_impact(self) -> None:
        report = self._run_optimize("external-agent")
        self.assertIn("## Version Impact", report)
        self.assertIn("Change type:", report)

    def test_section_details_have_layer_info(self) -> None:
        report = self._run_optimize("external-agent")
        # At least one section should have a layer classification
        self.assertTrue(
            any(layer in report for layer in ["content", "quality", "structure", "budget", "drift"]),
            "Report should contain at least one layer classification",
        )

    def test_shrinkage_fixture_reports_invariant_failure(self) -> None:
        """The shrinkage-agent fixture should trigger red_lines_monotonic FAIL."""
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("shrinkage-agent"),
            self.fixture.output_path("shrinkage-workspace"),
        )
        # Load existing spec and add red_lines that the workspace is missing
        spec_path = self.fixture.fixture_path("independent-generic.json")
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        spec["red_lines"] = [
            "Never modify production schemas without approval",
            "Do not skip validation steps",
        ]
        shrinkage_spec_path = self.fixture.output_path("shrinkage-spec.json")
        shrinkage_spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        spec_path = shrinkage_spec_path

        preview_dir = self.fixture.output_path("shrinkage-preview")
        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(spec_path),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
            "--lite",
        )
        self.assertEqual(completed.returncode, 0)
        report = (preview_dir / "optimize-report.md").read_text(encoding="utf-8")
        self.assertIn("## Workspace Invariants", report)
        self.assertIn("FAIL: red_lines_monotonic", report)
        self.assertIn("Do not skip validation steps", report)

    def test_version_impact_structural_when_missing_file(self) -> None:
        """A missing file should produce structural version impact."""
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("external-agent"),
            self.fixture.output_path("external-no-tools"),
        )
        # Remove TOOLS.md to trigger a missing file
        tools_path = workspace_dir / "TOOLS.md"
        if tools_path.exists():
            tools_path.unlink()

        spec_path = self.fixture.fixture_path("independent-generic.json")
        preview_dir = self.fixture.output_path("external-no-tools-preview")
        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(spec_path),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
            "--lite",
        )
        self.assertEqual(completed.returncode, 0)
        report = (preview_dir / "optimize-report.md").read_text(encoding="utf-8")
        self.assertIn("Change type: structural", report)


if __name__ == "__main__":
    unittest.main()
