from __future__ import annotations

import json
import unittest
from pathlib import Path

from test_support import SkillFixture


class ProposeModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_passes_on_valid_spec(self) -> None:
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec", str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--mode", "propose",
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("PASS", completed.stdout)

    def test_fails_on_missing_field(self) -> None:
        bad_spec = self.fixture.output_path("bad-spec.json")
        bad_spec.write_text(json.dumps({"name": "Test"}), encoding="utf-8")
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec", str(bad_spec),
            "--mode", "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("FAIL", completed.stdout)

    def test_passes_with_lite_flag_on_minimal_spec(self) -> None:
        minimal = self.fixture.output_path("minimal-spec.json")
        minimal.write_text(json.dumps({
            "name": "Test",
            "role": "Tester",
            "judgment_result": "独立 agent",
            "host_profile": "generic-openclaw",
            "workspace_positioning": "Test workspace",
            "session_startup": ["Read files"],
            "red_lines": ["Rule A"],
            "default_behavior": ["Behavior A"],
            "resume_strategy": {
                "global_resume_file": "AGENTS.md",
                "task_topic_resume_file": "state/current.json",
                "deliverable_inspection_path": "workspace/",
                "if_state_missing": "Rebuild",
                "never_assume": "Never assume",
            },
            "boundaries": ["Boundary A"],
            "workspace_layout": ["workspace/ - files"],
            "public_identity": "A tester",
            "non_negotiables": ["Rule 1"],
            "enduring_style": ["Style 1"],
            "capabilities": {"native": ["testing"]},
            "output_roots": ["workspace/"],
            "local_conventions": ["Convention 1"],
            "skill_resources": {"primary_skill_entrypoints": ["SKILL.md"]},
        }), encoding="utf-8")
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec", str(minimal),
            "--mode", "propose",
            "--lite",
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("PASS", completed.stdout)


class ScaffoldModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_requires_out_path(self) -> None:
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec", str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--mode", "scaffold",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--out is required", completed.stdout)

    def test_requires_judgment_result(self) -> None:
        spec = json.loads(self.fixture.fixture_path("independent-flowyclaw.json").read_text(encoding="utf-8"))
        spec["judgment_result"] = "不生成"
        bad_spec = self.fixture.output_path("no-judgment.json")
        bad_spec.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")

        out_dir = self.fixture.output_path("scaffold-out")
        out_dir.mkdir(parents=True, exist_ok=True)

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec", str(bad_spec),
            "--mode", "scaffold",
            "--out", str(out_dir),
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("judgment_result", completed.stdout)

    def test_passes_on_valid_scaffold(self) -> None:
        # First render a valid scaffold
        rendered_dir = self.fixture.output_path("valid-scaffold")
        self.fixture.run_script(
            "render_root_files.py",
            "--spec", str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--out", str(rendered_dir),
        )
        # Then validate it
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec", str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--mode", "scaffold",
            "--out", str(rendered_dir),
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("PASS", completed.stdout)


class OptimizeModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_requires_preview_out(self) -> None:
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec", str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--mode", "optimize",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--preview-out is required", completed.stdout)

    def test_requires_judgment_result_in_optimize(self) -> None:
        spec = json.loads(self.fixture.fixture_path("independent-flowyclaw.json").read_text(encoding="utf-8"))
        spec["judgment_result"] = "不生成"
        bad_spec = self.fixture.output_path("no-judgment-opt.json")
        bad_spec.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")

        preview_dir = self.fixture.output_path("optimize-preview")
        preview_dir.mkdir(parents=True, exist_ok=True)

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec", str(bad_spec),
            "--mode", "optimize",
            "--preview-out", str(preview_dir),
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("judgment_result", completed.stdout)


class ErrorHandlingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_fails_on_missing_spec(self) -> None:
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec", str(self.fixture.output_path("nonexistent.json")),
            "--mode", "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)

    def test_fails_on_invalid_json(self) -> None:
        bad_json = self.fixture.output_path("invalid.json")
        bad_json.write_text("not json {", encoding="utf-8")
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec", str(bad_json),
            "--mode", "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("FAIL", completed.stdout)


if __name__ == "__main__":
    unittest.main()
