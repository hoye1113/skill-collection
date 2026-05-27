from __future__ import annotations

import json
import unittest
from pathlib import Path

from test_support import SkillFixture


class InferSpecTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def _infer(self, workspace_fixture: str, *, host: str = "generic-openclaw") -> dict:
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path(workspace_fixture),
            self.fixture.output_path(f"{workspace_fixture}-workspace"),
        )
        out_path = self.fixture.output_path(f"{workspace_fixture}-inferred.json")
        completed = self.fixture.run_script(
            "infer_spec.py",
            "--workspace",
            str(workspace_dir),
            "--out",
            str(out_path),
            "--host",
            host,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("PASS: inferred spec", completed.stdout)
        return json.loads(out_path.read_text(encoding="utf-8"))

    def test_infers_name_role_from_identity(self) -> None:
        spec = self._infer("external-agent")
        self.assertEqual(spec["name"], "Data Pipeline Agent")
        self.assertEqual(spec["role"], "ETL pipeline manager and data quality guardian")

    def test_infers_public_identity(self) -> None:
        spec = self._infer("external-agent")
        self.assertIn("Manages data pipelines", spec["public_identity"])

    def test_infers_bullet_lists_from_soul(self) -> None:
        spec = self._infer("external-agent")
        self.assertIn("Always validate input schemas before processing", spec["non_negotiables"])
        self.assertIn("Systematic and methodical", spec["enduring_style"])
        self.assertIn("Running pipelines without validation checks", spec["lazy_default_to_avoid"])

    def test_infers_resume_strategy_from_agents(self) -> None:
        spec = self._infer("external-agent")
        resume = spec["resume_strategy"]
        self.assertEqual(resume["global_resume_file"], "AGENTS.md")
        self.assertIn("pipeline status dashboard", resume["if_state_missing"])

    def test_infers_capabilities_from_tools(self) -> None:
        spec = self._infer("external-agent")
        caps = spec["capabilities"]
        self.assertIn("Run and monitor ETL pipelines", caps["native"])
        self.assertIn("Real-time streaming", caps["unsupported"])

    def test_infers_skill_resources_from_tools(self) -> None:
        spec = self._infer("external-agent")
        resources = spec["skill_resources"]
        self.assertIn("skills/data-pipeline/SKILL.md", resources["primary_skill_entrypoints"])

    def test_infers_optional_files(self) -> None:
        spec = self._infer("external-agent")
        # USER.md exists but has placeholder values, so user_profile may be empty
        # But the inference should not crash
        self.assertIn("judgment_result", spec)

    def test_fills_uninferable_fields_with_defaults(self) -> None:
        spec = self._infer("external-agent")
        self.assertEqual(spec["judgment_result"], "独立 agent")
        self.assertIn("agent_promotion_analysis", spec)
        self.assertIn("workspace_semantics", spec)
        self.assertIn("risks_and_non_capabilities", spec)

    def test_host_profile_override(self) -> None:
        spec = self._infer("external-agent", host="flowyclaw")
        self.assertEqual(spec["host_profile"], "flowyclaw")
        self.assertEqual(spec["agent_promotion_analysis"]["host_profile"], "flowyclaw")

    def test_external_workspace_produces_valid_lite_spec(self) -> None:
        """The inferred spec should pass validate_minimal_spec."""
        spec = self._infer("external-agent")
        # Write spec and validate via CLI
        spec_path = self.fixture.output_path("external-agent-lite-spec.json")
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("external-agent"),
            self.fixture.output_path("external-agent-validate-workspace"),
        )
        # Run optimize with --lite
        preview_dir = self.fixture.output_path("external-agent-lite-preview")
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
        self.assertIn("PASS: optimization preview written", completed.stdout)

        # Validate with --lite
        validation = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(spec_path),
            "--mode",
            "optimize",
            "--preview-out",
            str(preview_dir),
            "--workspace",
            str(workspace_dir),
            "--lite",
        )
        self.assertEqual(validation.returncode, 0)
        self.assertIn("PASS: optimize validation succeeded", validation.stdout)

    def test_infers_red_lines_and_boundaries(self) -> None:
        spec = self._infer("external-agent")
        self.assertIn("Never modify production schemas without approval", spec["red_lines"])
        self.assertIn("Do not access databases outside the analytics namespace", spec["boundaries"])

    def test_infers_output_roots_and_conventions(self) -> None:
        spec = self._infer("external-agent")
        self.assertIn("pipelines/ - pipeline definitions", spec["output_roots"])
        self.assertIn("Use UTC timestamps in all logs", spec["local_conventions"])


if __name__ == "__main__":
    unittest.main()
