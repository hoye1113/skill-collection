from __future__ import annotations

import unittest
from pathlib import Path

from test_support import SkillFixture


class GoldenRenderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def assert_matches_golden(self, rendered_dir: Path, golden_dir: Path) -> None:
        for filename in ("IDENTITY.md", "SOUL.md", "AGENTS.md", "TOOLS.md"):
            actual = (rendered_dir / filename).read_text(encoding="utf-8")
            expected = (golden_dir / filename).read_text(encoding="utf-8")
            self.assertEqual(actual, expected, msg=f"Mismatch for {filename}")

    def test_render_matches_flowyclaw_golden(self) -> None:
        rendered_dir = self.fixture.output_path("rendered-flowyclaw")
        completed = self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--out",
            str(rendered_dir),
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("PASS: rendered IDENTITY.md, SOUL.md, AGENTS.md, TOOLS.md", completed.stdout)
        self.assert_matches_golden(rendered_dir, self.fixture.golden_path("independent-flowyclaw"))
        agents_text = (rendered_dir / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("## Red Lines", agents_text)

    def test_hardened_spec_still_renders_only_four_root_files(self) -> None:
        rendered_dir = self.fixture.output_path("rendered-hardened")
        completed = self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw-hardened.json")),
            "--out",
            str(rendered_dir),
        )
        self.assertEqual(completed.returncode, 0)
        actual_files = sorted(path.name for path in rendered_dir.iterdir() if path.is_file())
        self.assertEqual(actual_files, ["AGENTS.md", "IDENTITY.md", "SOUL.md", "TOOLS.md"])
        agents_text = (rendered_dir / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Preview Approval Gate", agents_text)

    def test_scaffold_validation_detects_forbidden_file_and_bad_heading(self) -> None:
        rendered_dir = self.fixture.output_path("broken-render")
        self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--out",
            str(rendered_dir),
        )

        self.fixture.write_text(rendered_dir / "PROMOTION_ANALYSIS.md", "# forbidden\n")
        tools_path = rendered_dir / "TOOLS.md"
        tools_text = tools_path.read_text(encoding="utf-8").replace("## Skill Resources", "## Wrong Heading")
        tools_path.write_text(tools_text, encoding="utf-8")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--out",
            str(rendered_dir),
            "--mode",
            "scaffold",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Forbidden governance file found:", completed.stdout)
        self.assertIn("TOOLS.md is missing heading: ## Skill Resources", completed.stdout)

    def test_render_refuses_to_overwrite_existing_root_files(self) -> None:
        rendered_dir = self.fixture.output_path("overwrite-guard")
        self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--out",
            str(rendered_dir),
        )

        completed = self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--out",
            str(rendered_dir),
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("V1.3 scaffold refuses to overwrite existing root files", completed.stdout)

    def test_render_rejects_invalid_root_contract_before_writing(self) -> None:
        bad_spec_path = self.fixture.output_path("render-invalid-spec.json")
        payload = self.fixture.fixture_path("independent-flowyclaw.json").read_text(encoding="utf-8").replace(
            "\"public_identity\": \"A reusable agent that turns agent briefs into structured OpenClaw proposals and safe root-file scaffolds.\"",
            "\"public_identity\": \"\"",
        )
        self.fixture.write_text(bad_spec_path, payload)

        rendered_dir = self.fixture.output_path("render-invalid-output")
        completed = self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(bad_spec_path),
            "--out",
            str(rendered_dir),
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Spec failed validation:", completed.stdout)
        self.assertIn("Missing non-empty field: public_identity", completed.stdout)

    def test_render_rejects_empty_out_path(self) -> None:
        completed = self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--out",
            "",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--out is required and cannot be empty", completed.stdout)


    def test_memory_spec_renders_seven_files(self) -> None:
        rendered_dir = self.fixture.output_path("rendered-memory")
        completed = self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw-with-memory.json")),
            "--out",
            str(rendered_dir),
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("BOOTSTRAP.md", completed.stdout)
        self.assertIn("USER.md", completed.stdout)
        self.assertIn("HEARTBEAT.md", completed.stdout)
        actual_files = sorted(path.name for path in rendered_dir.iterdir() if path.is_file())
        self.assertEqual(
            actual_files,
            ["AGENTS.md", "BOOTSTRAP.md", "HEARTBEAT.md", "IDENTITY.md", "SOUL.md", "TOOLS.md", "USER.md"],
        )

    def test_memory_spec_agents_md_contains_memory_section(self) -> None:
        rendered_dir = self.fixture.output_path("rendered-memory-agents")
        self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw-with-memory.json")),
            "--out",
            str(rendered_dir),
        )
        agents_text = (rendered_dir / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("## Memory", agents_text)
        self.assertIn("### MEMORY.md", agents_text)
        self.assertIn("### Write It Down", agents_text)
        self.assertIn("### Memory Maintenance", agents_text)
        self.assertIn("## Heartbeats", agents_text)
        self.assertIn("## Group Chats", agents_text)

    def test_memory_spec_matches_golden(self) -> None:
        rendered_dir = self.fixture.output_path("rendered-memory-golden")
        self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw-with-memory.json")),
            "--out",
            str(rendered_dir),
        )
        golden_dir = self.fixture.golden_path("independent-flowyclaw-with-memory")
        for filename in ("IDENTITY.md", "SOUL.md", "AGENTS.md", "TOOLS.md", "BOOTSTRAP.md", "USER.md", "HEARTBEAT.md"):
            actual = (rendered_dir / filename).read_text(encoding="utf-8")
            expected = (golden_dir / filename).read_text(encoding="utf-8")
            self.assertEqual(actual, expected, msg=f"Mismatch for {filename}")

    def test_backward_compatible_no_memory_config(self) -> None:
        rendered_dir = self.fixture.output_path("rendered-backward-compat")
        completed = self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--out",
            str(rendered_dir),
        )
        self.assertEqual(completed.returncode, 0)
        actual_files = sorted(path.name for path in rendered_dir.iterdir() if path.is_file())
        self.assertEqual(actual_files, ["AGENTS.md", "IDENTITY.md", "SOUL.md", "TOOLS.md"])
        agents_text = (rendered_dir / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("## Memory", agents_text)
        self.assertIn("Full memory configuration is not enabled", agents_text)
        self.assertNotIn("## Heartbeats", agents_text)
        self.assertNotIn("## Group Chats", agents_text)


if __name__ == "__main__":
    unittest.main()
