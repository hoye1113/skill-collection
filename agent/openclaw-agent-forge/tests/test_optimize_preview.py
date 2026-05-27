from __future__ import annotations

import unittest

from test_support import SkillFixture


class OptimizePreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def run_optimize_fixture(
        self,
        workspace_fixture: str,
        *,
        preview_name: str,
        spec_name: str = "independent-flowyclaw.json",
        check: bool = True,
    ):
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path(workspace_fixture),
            self.fixture.output_path(f"{workspace_fixture}-workspace"),
        )
        preview_dir = self.fixture.output_path(preview_name)
        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path(spec_name)),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
            check=check,
        )
        return workspace_dir, preview_dir, completed

    def validate_preview_bundle(self, spec_name: str, preview_dir, workspace_dir, *, check: bool = True):
        return self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(self.fixture.fixture_path(spec_name)),
            "--mode",
            "optimize",
            "--preview-out",
            str(preview_dir),
            "--workspace",
            str(workspace_dir),
            check=check,
        )

    def render_hardened_workspace(self, name: str):
        workspace_dir = self.fixture.output_path(name)
        completed = self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw-hardened.json")),
            "--out",
            str(workspace_dir),
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("PASS: rendered IDENTITY.md, SOUL.md, AGENTS.md, TOOLS.md", completed.stdout)
        return workspace_dir

    def seed_hardened_workspace(self, name: str):
        workspace_dir = self.render_hardened_workspace(name)

        self.fixture.write_text(
            workspace_dir / "slides" / "demo" / "index.html",
            (
                "<!doctype html>\n"
                "<html>\n"
                "<body>\n"
                "  <img src=\"assets/hero.png\" alt=\"hero\">\n"
                "  <script>window.__WORKFLOW_HARDENING_EXPORT__ = { version: '1.0' };</script>\n"
                "</body>\n"
                "</html>\n"
            ),
        )
        self.fixture.write_text(workspace_dir / "slides" / "demo" / "assets" / "hero.png", "asset\n")
        self.fixture.write_text(workspace_dir / "state" / "demo.md", "preview_approved: false\n")
        self.fixture.write_text(workspace_dir / "slide-previews" / "demo-preview.html", "<html>preview</html>\n")
        self.fixture.write_text(
            workspace_dir / "dev" / ".openclaw-agent-install.json",
            '{\n  "setup": "uv run setup-demo",\n  "verify": "uv run verify-demo"\n}\n',
        )
        self.fixture.write_text(
            workspace_dir / "scripts" / "open_preview.py",
            "print('open preview')\n",
        )
        self.fixture.write_text(
            workspace_dir / "scripts" / "html_to_pptx.py",
            "print('export pptx')\n",
        )
        self.fixture.write_text(
            workspace_dir / "skills" / "frontend-slides" / "SKILL.md",
            "# Frontend Slides\n\nKeep canonical deck creation inside slides/demo.\n",
        )
        self.fixture.write_text(
            workspace_dir / "skills" / "deck-audit" / "SKILL.md",
            "# Deck Audit\n\nAudit findings and keep canonical source untouched.\n",
        )

        return workspace_dir

    def test_optimize_generates_report_preview_and_diffs_without_mutating_workspace(self) -> None:
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("broken-agent"),
            self.fixture.output_path("broken-agent-workspace"),
        )
        original_identity = (workspace_dir / "IDENTITY.md").read_text(encoding="utf-8")
        original_agents = (workspace_dir / "AGENTS.md").read_text(encoding="utf-8")
        original_tools = (workspace_dir / "TOOLS.md").read_text(encoding="utf-8")
        preview_dir = self.fixture.output_path("optimize-preview")
        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIn("PASS: optimization preview written", completed.stdout)
        self.assertIn("aligned=0", completed.stdout)
        self.assertIn("needs_update=3", completed.stdout)
        self.assertIn("missing=1", completed.stdout)

        report = (preview_dir / "optimize-report.md").read_text(encoding="utf-8")
        self.assertIn("## Summary", report)
        self.assertIn("## Workspace Warnings", report)
        self.assertIn("## Diagnostic Findings", report)
        self.assertIn("## Workflow Contract Findings", report)
        self.assertIn("## Skill Review Signals", report)
        self.assertIn("## Suggested Preview Artifacts", report)
        self.assertIn("## Apply Boundary", report)
        self.assertIn("- aligned: 0", report)
        self.assertIn("- needs_update: 3", report)
        self.assertIn("- missing: 1", report)
        self.assertIn("- workflow_contract_findings: 0", report)
        self.assertIn("- skill_review_signals: 0", report)
        self.assertIn("Forbidden governance file present:", report)
        self.assertIn("missing heading: ## Public Identity", report)
        self.assertIn("missing heading: ## Red Lines", report)
        self.assertIn("missing heading: ## Skill Resources", report)
        self.assertIn("## Workflow Contract Findings\n\n- none", report)
        self.assertIn("## Skill Review Signals\n\n- none", report)

        for filename in ("IDENTITY.md", "SOUL.md", "AGENTS.md", "TOOLS.md"):
            self.assertTrue((preview_dir / "preview" / filename).exists())
            self.assertTrue((preview_dir / "diffs" / f"{filename}.diff").exists())

        self.assertEqual((workspace_dir / "IDENTITY.md").read_text(encoding="utf-8"), original_identity)
        self.assertEqual((workspace_dir / "AGENTS.md").read_text(encoding="utf-8"), original_agents)
        self.assertEqual((workspace_dir / "TOOLS.md").read_text(encoding="utf-8"), original_tools)
        self.assertFalse((workspace_dir / "SOUL.md").exists())

        validation = self.validate_preview_bundle("independent-flowyclaw.json", preview_dir, workspace_dir)
        self.assertEqual(validation.returncode, 0)
        self.assertIn("PASS: optimize validation succeeded", validation.stdout)

    def test_optimize_rejects_non_agent_specs(self) -> None:
        _, preview_dir, completed = self.run_optimize_fixture(
            "broken-agent",
            preview_name="optimize-preview-non-agent",
            spec_name="non-agent.json",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("V1.3 optimize only supports specs whose judgment_result is '独立 agent'.", completed.stdout)
        self.assertFalse((preview_dir / "optimize-report.md").exists())

    def test_optimize_validator_detects_missing_report(self) -> None:
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("missing-red-lines-agent"),
            self.fixture.output_path("missing-report-workspace"),
        )
        preview_dir = self.fixture.output_path("missing-report-preview")
        (preview_dir / "preview").mkdir(parents=True, exist_ok=True)
        (preview_dir / "diffs").mkdir(parents=True, exist_ok=True)

        completed = self.validate_preview_bundle(
            "independent-flowyclaw.json",
            preview_dir,
            workspace_dir,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Missing optimize report:", completed.stdout)

    def test_optimize_validator_detects_missing_workflow_sections(self) -> None:
        workspace_dir, preview_dir, optimize = self.run_optimize_fixture(
            "missing-red-lines-agent",
            preview_name="missing-workflow-sections-preview",
        )
        self.assertEqual(optimize.returncode, 0)

        report_path = preview_dir / "optimize-report.md"
        broken_report = report_path.read_text(encoding="utf-8").replace("## Skill Review Signals", "## Missing Signals")
        report_path.write_text(broken_report, encoding="utf-8")

        completed = self.validate_preview_bundle(
            "independent-flowyclaw.json",
            preview_dir,
            workspace_dir,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Optimize report is missing section: ## Skill Review Signals", completed.stdout)

    def test_optimize_validator_detects_aligned_artifact(self) -> None:
        workspace_dir = self.fixture.copy_tree(
            self.fixture.golden_path("independent-flowyclaw"),
            self.fixture.output_path("aligned-workspace"),
        )
        preview_dir = self.fixture.output_path("aligned-preview")

        optimize = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
        )
        self.assertEqual(optimize.returncode, 0)
        self.assertIn("aligned=4", optimize.stdout)
        self.assertIn("needs_update=0", optimize.stdout)
        self.assertIn("missing=0", optimize.stdout)

        self.fixture.write_text(preview_dir / "preview" / "AGENTS.md", "# stray\n")
        self.fixture.write_text(preview_dir / "diffs" / "AGENTS.md.diff", "diff\n")

        completed = self.validate_preview_bundle(
            "independent-flowyclaw.json",
            preview_dir,
            workspace_dir,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("AGENTS.md is aligned but a preview artifact was generated", completed.stdout)
        self.assertIn("AGENTS.md is aligned but a diff artifact was generated", completed.stdout)

    def test_optimize_does_not_flag_structure_safe_text_drift(self) -> None:
        workspace_dir = self.fixture.copy_tree(
            self.fixture.golden_path("independent-flowyclaw"),
            self.fixture.output_path("text-drift-workspace"),
        )
        agents_path = workspace_dir / "AGENTS.md"
        agents_text = agents_path.read_text(encoding="utf-8").replace(
            "This workspace exists to design and scaffold OpenClaw agent workspaces from structured briefs.",
            "This workspace focuses on reusable OpenClaw agent scaffolds from structured briefs.",
        )
        agents_path.write_text(agents_text, encoding="utf-8")
        preview_dir = self.fixture.output_path("text-drift-preview")

        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("aligned=4", completed.stdout)
        self.assertNotIn("needs_update=1", completed.stdout)
        self.assertFalse((preview_dir / "preview" / "AGENTS.md").exists())
        self.assertFalse((preview_dir / "diffs" / "AGENTS.md.diff").exists())

    def test_optimize_detects_missing_red_lines_fixture(self) -> None:
        _, preview_dir, completed = self.run_optimize_fixture(
            "missing-red-lines-agent",
            preview_name="missing-red-lines-preview",
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("aligned=3", completed.stdout)
        self.assertIn("needs_update=1", completed.stdout)
        report = (preview_dir / "optimize-report.md").read_text(encoding="utf-8")
        self.assertIn("missing heading: ## Red Lines", report)

    def test_optimize_can_rerun_on_the_same_preview_directory(self) -> None:
        workspace_dir, preview_dir, first_run = self.run_optimize_fixture(
            "missing-red-lines-agent",
            preview_name="repeat-preview",
        )
        self.assertEqual(first_run.returncode, 0)

        second_run = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
        )
        self.assertEqual(second_run.returncode, 0)
        self.assertIn("aligned=3", second_run.stdout)
        self.assertIn("needs_update=1", second_run.stdout)

        validation = self.validate_preview_bundle("independent-flowyclaw.json", preview_dir, workspace_dir)
        self.assertEqual(validation.returncode, 0)
        self.assertIn("PASS: optimize validation succeeded", validation.stdout)

    def test_optimize_rejects_preview_directory_with_unexpected_top_level_entries(self) -> None:
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("missing-red-lines-agent"),
            self.fixture.output_path("unexpected-preview-workspace"),
        )
        preview_dir = self.fixture.output_path("unexpected-preview-dir")
        preview_dir.mkdir(parents=True, exist_ok=True)
        self.fixture.write_text(preview_dir / "notes.txt", "unexpected\n")

        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "Preview output directory must be empty or contain only optimize-report.md, preview, and diffs",
            completed.stdout,
        )

    def test_optimize_detects_bloat_fixture(self) -> None:
        _, preview_dir, completed = self.run_optimize_fixture(
            "bloated-agent",
            preview_name="bloated-preview",
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("aligned=3", completed.stdout)
        self.assertIn("needs_update=1", completed.stdout)
        report = (preview_dir / "optimize-report.md").read_text(encoding="utf-8")
        self.assertIn("bloat risk:", report)

    def test_optimize_detects_role_drift_fixture(self) -> None:
        _, preview_dir, completed = self.run_optimize_fixture(
            "role-drift-agent",
            preview_name="role-drift-preview",
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("aligned=2", completed.stdout)
        self.assertIn("needs_update=2", completed.stdout)
        report = (preview_dir / "optimize-report.md").read_text(encoding="utf-8")
        self.assertIn("out-of-scope heading: ## Public Identity", report)
        self.assertIn("duplicate root-file heading: ## Public Identity also appears in IDENTITY.md", report)

    def test_hardened_optimize_reports_workspace_contract_findings_without_root_previews(self) -> None:
        workspace_dir = self.seed_hardened_workspace("workflow-hardening-contract-gaps")
        preview_dir = self.fixture.output_path("workflow-hardening-contract-gaps-preview")

        agents_path = workspace_dir / "AGENTS.md"
        agents_text = agents_path.read_text(encoding="utf-8").replace("Preview Approval Gate", "User Preview Approval")
        agents_path.write_text(agents_text, encoding="utf-8")
        (workspace_dir / "dev" / ".openclaw-agent-install.json").unlink()
        (workspace_dir / "scripts" / "open_preview.py").unlink()
        (workspace_dir / "scripts" / "html_to_pptx.py").unlink()
        (workspace_dir / "slides" / "demo" / "assets" / "hero.png").unlink()
        (workspace_dir / "slides" / "demo" / "assets").rmdir()
        self.fixture.write_text(
            workspace_dir / "slides" / "demo" / "index.html",
            "<img src=\"D:\\\\assets\\\\hero.png\" alt=\"hero\">\n",
        )
        self.fixture.write_text(workspace_dir / "slides" / "demo" / "demo.pptx", "derived-inside-canonical\n")
        (workspace_dir / "skills" / "deck-audit" / "SKILL.md").unlink()

        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw-hardened.json")),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("aligned=4", completed.stdout)
        self.assertIn("needs_update=0", completed.stdout)
        report = (preview_dir / "optimize-report.md").read_text(encoding="utf-8")
        self.assertIn("- workflow_contract_findings: 8", report)
        self.assertIn("- skill_review_signals: 0", report)
        self.assertIn("approval gate missing from AGENTS.md: Preview Approval Gate", report)
        self.assertIn("conditional-runtime contract missing for Derived PPTX handoff: dev/.openclaw-agent-install.json", report)
        self.assertIn("prompt-only workflow gap: missing deterministic helper for Open canonical preview: scripts/open_preview.py", report)
        self.assertIn("prompt-only workflow gap: missing deterministic helper for Run derived PPTX export: scripts/html_to_pptx.py", report)
        self.assertIn("asset staging root is missing: slides/demo/assets", report)
        self.assertIn("portability finding: Windows drive path leaked into canonical source file slides\\demo\\index.html", report.replace("/", "\\"))
        self.assertIn("derived artifact confusion: found .pptx file inside canonical source root: slides\\demo\\demo.pptx", report.replace("/", "\\"))
        self.assertIn("sidecar owner is missing SKILL.md: skills/deck-audit", report)
        self.assertIn("## Skill Review Signals\n\n- none", report)
        self.assertFalse((preview_dir / "preview" / "AGENTS.md").exists())
        self.assertFalse((preview_dir / "diffs" / "AGENTS.md.diff").exists())

        validation = self.validate_preview_bundle("independent-flowyclaw-hardened.json", preview_dir, workspace_dir)
        self.assertEqual(validation.returncode, 0)
        self.assertIn("PASS: optimize validation succeeded", validation.stdout)

    def test_hardened_optimize_reports_skill_review_signals_without_blocking(self) -> None:
        workspace_dir = self.seed_hardened_workspace("workflow-hardening-signal-agent")
        preview_dir = self.fixture.output_path("workflow-hardening-signal-preview")

        self.fixture.write_text(
            workspace_dir / "skills" / "frontend-slides" / "SKILL.md",
            (
                "# Frontend Slides\n\n"
                "Attempt to open a preview when possible.\n"
                "Try to use relative paths and wait a bit before export.\n"
                "If supported, continue with the handoff.\n"
            ),
        )

        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw-hardened.json")),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("aligned=4", completed.stdout)
        self.assertIn("needs_update=0", completed.stdout)

        report = (preview_dir / "optimize-report.md").read_text(encoding="utf-8")
        self.assertIn("- workflow_contract_findings: 0", report)
        self.assertIn("- skill_review_signals: 1", report)
        self.assertIn("prompt-only workflow signal in skills\\frontend-slides\\SKILL.md", report.replace("/", "\\"))
        self.assertFalse((preview_dir / "preview" / "AGENTS.md").exists())
        self.assertFalse((preview_dir / "diffs" / "AGENTS.md.diff").exists())

        validation = self.validate_preview_bundle("independent-flowyclaw-hardened.json", preview_dir, workspace_dir)
        self.assertEqual(validation.returncode, 0)
        self.assertIn("PASS: optimize validation succeeded", validation.stdout)

    def test_hardened_optimize_can_report_root_and_contract_findings_together(self) -> None:
        workspace_dir = self.seed_hardened_workspace("workflow-hardening-root-and-contract-agent")
        preview_dir = self.fixture.output_path("workflow-hardening-root-and-contract-preview")

        agents_path = workspace_dir / "AGENTS.md"
        agents_text = agents_path.read_text(encoding="utf-8")
        agents_text = agents_text.replace("## Red Lines", "## Broken Red Lines")
        agents_text = agents_text.replace("Preview Approval Gate", "Preview Approval")
        agents_path.write_text(agents_text, encoding="utf-8")
        (workspace_dir / "dev" / ".openclaw-agent-install.json").unlink()

        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw-hardened.json")),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("aligned=3", completed.stdout)
        self.assertIn("needs_update=1", completed.stdout)

        report = (preview_dir / "optimize-report.md").read_text(encoding="utf-8")
        self.assertIn("missing heading: ## Red Lines", report)
        self.assertIn("approval gate missing from AGENTS.md: Preview Approval Gate", report)
        self.assertIn("conditional-runtime contract missing for Derived PPTX handoff: dev/.openclaw-agent-install.json", report)
        self.assertTrue((preview_dir / "preview" / "AGENTS.md").exists())
        self.assertTrue((preview_dir / "diffs" / "AGENTS.md.diff").exists())

    def test_optimize_detects_compaction_rule_misplacement(self) -> None:
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("missing-red-lines-agent"),
            self.fixture.output_path("compaction-misplacement-workspace"),
        )
        agents_path = workspace_dir / "AGENTS.md"
        agents_text = agents_path.read_text(encoding="utf-8")
        # Replace "Do not" with "Never" in Boundaries (critical keyword not in Session Startup/Red Lines)
        agents_text = agents_text.replace(
            "- Do not overwrite existing root files in V1.3.",
            "- Never overwrite existing root files in V1.3.",
        )
        agents_path.write_text(agents_text, encoding="utf-8")

        preview_dir = self.fixture.output_path("compaction-misplacement-preview")
        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
        )
        self.assertEqual(completed.returncode, 0)
        report = (preview_dir / "optimize-report.md").read_text(encoding="utf-8")
        self.assertIn(
            "compaction risk: critical keyword 'never' found in Boundaries but not in Session Startup or Red Lines",
            report,
        )

    def test_optimize_detects_unc_path_leakage(self) -> None:
        workspace_dir = self.seed_hardened_workspace("unc-leakage-workspace")
        preview_dir = self.fixture.output_path("unc-leakage-preview")

        self.fixture.write_text(
            workspace_dir / "slides" / "demo" / "index.html",
            '<img src="\\\\server\\share\\assets\\hero.png" alt="hero">\n',
        )

        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw-hardened.json")),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            str(preview_dir),
        )
        self.assertEqual(completed.returncode, 0)
        report = (preview_dir / "optimize-report.md").read_text(encoding="utf-8")
        self.assertIn("UNC path leaked into canonical source file", report.replace("/", "\\"))

    def test_optimize_rejects_empty_workspace_path(self) -> None:
        preview_dir = self.fixture.output_path("empty-workspace-preview")
        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--workspace",
            "",
            "--preview-out",
            str(preview_dir),
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--workspace is required and cannot be empty", completed.stdout)

    def test_optimize_rejects_empty_preview_out_path(self) -> None:
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("broken-agent"),
            self.fixture.output_path("empty-preview-workspace"),
        )
        completed = self.fixture.run_script(
            "optimize_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--workspace",
            str(workspace_dir),
            "--preview-out",
            "",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--preview-out is required and cannot be empty", completed.stdout)


if __name__ == "__main__":
    unittest.main()
