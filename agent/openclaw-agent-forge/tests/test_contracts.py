from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from test_support import SkillFixture


class ContractValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_flowyclaw_fixture_passes_propose_validation(self) -> None:
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--mode",
            "propose",
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("PASS: propose validation succeeded", completed.stdout)

    def test_generic_fixture_passes_propose_validation(self) -> None:
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(self.fixture.fixture_path("independent-generic.json")),
            "--mode",
            "propose",
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("PASS: propose validation succeeded", completed.stdout)

    def test_hardened_fixture_passes_propose_validation(self) -> None:
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw-hardened.json")),
            "--mode",
            "propose",
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("PASS: propose validation succeeded", completed.stdout)

    def test_missing_red_lines_is_reported(self) -> None:
        bad_spec_path = self.fixture.output_path("bad-missing-red-lines.json")
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw.json").read_text(encoding="utf-8"))
        payload.pop("red_lines", None)
        self.fixture.write_text(bad_spec_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(bad_spec_path),
            "--mode",
            "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("red_lines must be a non-empty list", completed.stdout)

    def test_empty_root_contract_fields_are_reported(self) -> None:
        bad_spec_path = self.fixture.output_path("bad-empty-root-fields.json")
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw.json").read_text(encoding="utf-8"))
        payload["public_identity"] = "   "
        payload["non_negotiables"] = []
        self.fixture.write_text(bad_spec_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(bad_spec_path),
            "--mode",
            "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Missing non-empty field: public_identity", completed.stdout)
        self.assertIn("non_negotiables must be a non-empty list", completed.stdout)

    def test_hardened_spec_rejects_derived_exports_without_canonical_source(self) -> None:
        bad_spec_path = self.fixture.output_path("bad-workflow-hardening-missing-canonical.json")
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw-hardened.json").read_text(encoding="utf-8"))
        payload["workflow_hardening"].pop("canonical_source", None)
        self.fixture.write_text(bad_spec_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(bad_spec_path),
            "--mode",
            "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "workflow_hardening.derived_exports requires workflow_hardening.canonical_source",
            completed.stdout,
        )

    def test_hardened_spec_rejects_matching_derived_export_and_canonical_source(self) -> None:
        bad_spec_path = self.fixture.output_path("bad-workflow-hardening-derived-equals-canonical.json")
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw-hardened.json").read_text(encoding="utf-8"))
        payload["workflow_hardening"]["derived_exports"][0]["path"] = "slides/demo"
        self.fixture.write_text(bad_spec_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(bad_spec_path),
            "--mode",
            "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "workflow_hardening.derived_exports[0].path must differ from workflow_hardening.canonical_source.path",
            completed.stdout,
        )

    def test_hardened_spec_rejects_incomplete_asset_staging(self) -> None:
        bad_spec_path = self.fixture.output_path("bad-workflow-hardening-asset-staging.json")
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw-hardened.json").read_text(encoding="utf-8"))
        payload["workflow_hardening"]["asset_staging"]["absolute_path_policy"] = ""
        self.fixture.write_text(bad_spec_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(bad_spec_path),
            "--mode",
            "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "workflow_hardening.asset_staging.absolute_path_policy must be a non-empty string",
            completed.stdout,
        )

    def test_hardened_spec_rejects_sidecar_write_conflicts(self) -> None:
        bad_spec_path = self.fixture.output_path("bad-workflow-hardening-sidecar-conflicts.json")
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw-hardened.json").read_text(encoding="utf-8"))
        payload["workflow_hardening"]["sidecar_write_ownership"][0]["must_not_write"] = [
            "exports",
            "slides/demo",
        ]
        payload["workflow_hardening"]["sidecar_write_ownership"][1]["writes_to"] = [
            "slides/demo/assets",
        ]
        self.fixture.write_text(bad_spec_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(bad_spec_path),
            "--mode",
            "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "workflow_hardening.sidecar_write_ownership[0] has overlapping writes_to and must_not_write",
            completed.stdout,
        )
        self.assertIn(
            "workflow_hardening.sidecar_write_ownership declares overlapping writable root 'slides/demo/assets'",
            completed.stdout,
        )

    def test_hardened_spec_rejects_absolute_workflow_paths(self) -> None:
        bad_spec_path = self.fixture.output_path("bad-workflow-hardening-absolute-paths.json")
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw-hardened.json").read_text(encoding="utf-8"))
        payload["workflow_hardening"]["canonical_source"]["path"] = r"C:\temp\slides\demo"
        payload["workflow_hardening"]["derived_exports"][0]["source_path"] = r"C:\temp\slides\demo"
        payload["workflow_hardening"]["deterministic_helpers"][0]["entrypoint"] = r"..\scripts\open_preview.py"
        self.fixture.write_text(bad_spec_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(bad_spec_path),
            "--mode",
            "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "workflow_hardening.canonical_source.path must be a workspace-relative path",
            completed.stdout,
        )
        self.assertIn(
            "workflow_hardening.derived_exports[0].source_path must be a workspace-relative path",
            completed.stdout,
        )
        self.assertIn(
            "workflow_hardening.deterministic_helpers[0].entrypoint must be a workspace-relative path",
            completed.stdout,
        )

    def test_skill_markdown_reference_paths_exist(self) -> None:
        skill_md = Path(__file__).resolve().parents[1] / "SKILL.md"
        references = sorted(set(re.findall(r"references/[A-Za-z0-9._/-]+\.md", skill_md.read_text(encoding="utf-8"))))
        self.assertTrue(references)
        for reference in references:
            self.assertTrue((skill_md.parent / reference).exists(), msg=f"Missing referenced file: {reference}")

    def test_example_fixture_reference_paths_exist(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]
        for fixture_name in (
            "independent-flowyclaw.json",
            "independent-generic.json",
            "independent-flowyclaw-hardened.json",
        ):
            payload = json.loads(self.fixture.fixture_path(fixture_name).read_text(encoding="utf-8"))
            references = payload["skill_resources"].get("high_priority_references", [])
            self.assertTrue(references, msg=f"{fixture_name} is missing high_priority_references")
            for reference in references:
                self.assertTrue((skill_root / reference).exists(), msg=f"{fixture_name} points to missing reference: {reference}")

    def test_non_agent_fixture_is_rejected_in_scaffold_mode(self) -> None:
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(self.fixture.fixture_path("non-agent.json")),
            "--out",
            str(self.fixture.output_path("non-agent-render")),
            "--mode",
            "scaffold",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("scaffold mode requires judgment_result = 独立 agent", completed.stdout)
        self.assertIn("scaffold mode requires agent_promotion_analysis.promotion_decision = 独立 agent", completed.stdout)

    def test_scaffold_rejects_character_budget_violation(self) -> None:
        workspace_dir = self.fixture.output_path("budget-violation-workspace")
        completed = self.fixture.run_script(
            "render_root_files.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--out",
            str(workspace_dir),
        )
        self.assertEqual(completed.returncode, 0)

        # Make IDENTITY.md exceed the single-file budget (>12K chars)
        identity_path = workspace_dir / "IDENTITY.md"
        original = identity_path.read_text(encoding="utf-8")
        identity_path.write_text(original + "x" * 15_000, encoding="utf-8")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--out",
            str(workspace_dir),
            "--mode",
            "scaffold",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("exceeds single-file character budget", completed.stdout)

        # Also test total budget by making all 4 files large
        for filename in ("SOUL.md", "AGENTS.md", "TOOLS.md"):
            path = workspace_dir / filename
            path.write_text(path.read_text(encoding="utf-8") + "y" * 20_000, encoding="utf-8")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw.json")),
            "--out",
            str(workspace_dir),
            "--mode",
            "scaffold",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Total root-file character budget exceeded", completed.stdout)


    def test_memory_fixture_passes_propose_validation(self) -> None:
        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(self.fixture.fixture_path("independent-flowyclaw-with-memory.json")),
            "--mode",
            "propose",
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("PASS: propose validation succeeded", completed.stdout)

    def test_invalid_memory_config_rejected(self) -> None:
        bad_spec_path = self.fixture.output_path("bad-memory-config.json")
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw-with-memory.json").read_text(encoding="utf-8"))
        payload["memory_config"]["enabled"] = "not_a_bool"
        payload["memory_config"]["what_to_capture"] = "not_a_list"
        self.fixture.write_text(bad_spec_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(bad_spec_path),
            "--mode",
            "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("memory_config.enabled must be a boolean", completed.stdout)
        self.assertIn("memory_config.what_to_capture must be a list of strings", completed.stdout)

    def test_invalid_heartbeat_config_rejected(self) -> None:
        bad_spec_path = self.fixture.output_path("bad-heartbeat-config.json")
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw-with-memory.json").read_text(encoding="utf-8"))
        payload["heartbeat_config"]["enabled"] = 123
        payload["heartbeat_config"]["tasks"] = "not_a_list"
        self.fixture.write_text(bad_spec_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(bad_spec_path),
            "--mode",
            "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("heartbeat_config.enabled must be a boolean", completed.stdout)
        self.assertIn("heartbeat_config.tasks must be a list of strings", completed.stdout)

    def test_invalid_group_chat_config_rejected(self) -> None:
        bad_spec_path = self.fixture.output_path("bad-group-chat-config.json")
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw-with-memory.json").read_text(encoding="utf-8"))
        payload["group_chat_behavior"]["respond_when"] = [123, 456]
        self.fixture.write_text(bad_spec_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(bad_spec_path),
            "--mode",
            "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("group_chat_behavior.respond_when must be a list of strings", completed.stdout)

    def test_invalid_bootstrap_config_rejected(self) -> None:
        bad_spec_path = self.fixture.output_path("bad-bootstrap-config.json")
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw-with-memory.json").read_text(encoding="utf-8"))
        payload["bootstrap_config"]["enabled"] = "not_a_bool"
        payload["bootstrap_config"]["conversation_topics"] = [123]
        self.fixture.write_text(bad_spec_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        completed = self.fixture.run_script(
            "validate_agent_output.py",
            "--spec",
            str(bad_spec_path),
            "--mode",
            "propose",
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("bootstrap_config.enabled must be a boolean", completed.stdout)
        self.assertIn("bootstrap_config.conversation_topics must be a list of strings", completed.stdout)

    def test_memory_fixture_reference_paths_exist(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]
        payload = json.loads(self.fixture.fixture_path("independent-flowyclaw-with-memory.json").read_text(encoding="utf-8"))
        references = payload["skill_resources"].get("high_priority_references", [])
        self.assertTrue(references, msg="independent-flowyclaw-with-memory.json is missing high_priority_references")
        for reference in references:
            self.assertTrue((skill_root / reference).exists(), msg=f"independent-flowyclaw-with-memory.json points to missing reference: {reference}")


if __name__ == "__main__":
    unittest.main()
