from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from workspace_invariants import (
    check_memory_baseline_present,
    check_red_lines_monotonic,
    check_role_consistency,
    check_session_startup_references,
    check_skill_resources_paths,
    check_workspace_invariants,
)
from test_support import SkillFixture


class RedLinesMonotonicTests(unittest.TestCase):
    def test_pass_when_all_spec_rules_present(self) -> None:
        agents = "# AGENTS.md\n\n## Red Lines\n\n- Rule A\n- Rule B\n- Rule C\n"
        issues = check_red_lines_monotonic(["Rule A", "Rule B"], agents)
        self.assertEqual(issues, [])

    def test_fail_when_rule_deleted(self) -> None:
        agents = "# AGENTS.md\n\n## Red Lines\n\n- Rule A\n"
        issues = check_red_lines_monotonic(["Rule A", "Rule B"], agents)
        self.assertTrue(any("shrinkage" in i and "Rule B" in i for i in issues))

    def test_pass_when_spec_empty(self) -> None:
        agents = "# AGENTS.md\n\n## Red Lines\n\n- Rule A\n"
        issues = check_red_lines_monotonic([], agents)
        self.assertEqual(issues, [])

    def test_pass_when_agents_empty(self) -> None:
        issues = check_red_lines_monotonic(["Rule A"], "")
        self.assertEqual(issues, [])

    def test_pass_when_workspace_has_extra_rules(self) -> None:
        """Adding rules is allowed (monotonic growth)."""
        agents = "# AGENTS.md\n\n## Red Lines\n\n- Rule A\n- Rule B\n- Rule C\n"
        issues = check_red_lines_monotonic(["Rule A"], agents)
        self.assertEqual(issues, [])


class SessionStartupReferencesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_pass_when_referenced_file_exists(self) -> None:
        workspace = self.fixture.output_path("startup-ref")
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "AGENTS.md").write_text(
            "# AGENTS.md\n\n## Session Startup\n\n- Read AGENTS.md\n- Check SOUL.md\n",
            encoding="utf-8",
        )
        (workspace / "SOUL.md").write_text("# SOUL.md\n", encoding="utf-8")
        agents_text = (workspace / "AGENTS.md").read_text(encoding="utf-8")
        issues = check_session_startup_references(workspace, agents_text)
        self.assertEqual(issues, [])

    def test_fail_when_referenced_file_missing(self) -> None:
        workspace = self.fixture.output_path("startup-missing")
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "AGENTS.md").write_text(
            "# AGENTS.md\n\n## Session Startup\n\n- Read AGENTS.md\n- Check USER.md\n",
            encoding="utf-8",
        )
        agents_text = (workspace / "AGENTS.md").read_text(encoding="utf-8")
        issues = check_session_startup_references(workspace, agents_text)
        self.assertTrue(any("USER.md" in i for i in issues))

    def test_pass_when_no_references(self) -> None:
        workspace = self.fixture.output_path("startup-none")
        workspace.mkdir(parents=True, exist_ok=True)
        issues = check_session_startup_references(workspace, "# AGENTS.md\n\n## Session Startup\n\n- Check logs\n")
        self.assertEqual(issues, [])


class RoleConsistencyTests(unittest.TestCase):
    def test_pass_when_keywords_overlap(self) -> None:
        identity = "# IDENTITY.md\n\n- Role: ETL pipeline manager\n"
        agents = "# AGENTS.md\n\n## Workspace Positioning\n\nThis workspace manages ETL pipelines.\n"
        issues = check_role_consistency(identity, agents)
        self.assertEqual(issues, [])

    def test_fail_when_few_keywords_shared(self) -> None:
        identity = "# IDENTITY.md\n\n- Role: ETL pipeline manager\n"
        agents = "# AGENTS.md\n\n## Workspace Positioning\n\nCustomer support chatbot for help desk.\n"
        issues = check_role_consistency(identity, agents)
        self.assertTrue(any("drift" in i for i in issues))

    def test_pass_when_empty(self) -> None:
        self.assertEqual(check_role_consistency("", ""), [])
        self.assertEqual(check_role_consistency("- Role: X", ""), [])
        self.assertEqual(check_role_consistency("", "## Workspace Positioning\n\nText\n"), [])


class SkillResourcesPathsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_pass_when_path_exists(self) -> None:
        workspace = self.fixture.output_path("resources-ok")
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "skills").mkdir()
        (workspace / "skills" / "SKILL.md").write_text("# SKILL.md\n", encoding="utf-8")
        tools = "# TOOLS.md\n\n## Skill Resources\n\n- skills/SKILL.md\n"
        issues = check_skill_resources_paths(workspace, tools)
        self.assertEqual(issues, [])

    def test_fail_when_path_missing(self) -> None:
        workspace = self.fixture.output_path("resources-missing")
        workspace.mkdir(parents=True, exist_ok=True)
        tools = "# TOOLS.md\n\n## Skill Resources\n\n- skills/missing/SKILL.md\n"
        issues = check_skill_resources_paths(workspace, tools)
        self.assertTrue(any("missing" in i for i in issues))


class MemoryBaselinePresentTests(unittest.TestCase):
    def test_pass_when_memory_section_exists(self) -> None:
        agents = "# AGENTS.md\n\n## Session Startup\n\n- Read files\n\n## Memory\n\nNotes here.\n\n## Red Lines\n\n- Rule A\n"
        issues = check_memory_baseline_present(agents)
        self.assertEqual(issues, [])

    def test_fail_when_memory_section_missing(self) -> None:
        agents = "# AGENTS.md\n\n## Session Startup\n\n- Read files\n\n## Red Lines\n\n- Rule A\n"
        issues = check_memory_baseline_present(agents)
        self.assertTrue(any("## Memory" in i for i in issues))

    def test_fail_when_agents_empty(self) -> None:
        issues = check_memory_baseline_present("")
        self.assertTrue(any("empty" in i or "missing" in i for i in issues))

    def test_pass_when_only_baseline_text(self) -> None:
        """Baseline (no full config) still satisfies the invariant."""
        agents = (
            "# AGENTS.md\n\n## Memory\n\n"
            "You have memory capabilities available. "
            "Full memory configuration is not enabled for this workspace.\n"
        )
        issues = check_memory_baseline_present(agents)
        self.assertEqual(issues, [])


class WorkspaceInvariantsIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_full_invariant_check_on_shrinkage_fixture(self) -> None:
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("shrinkage-agent"),
            self.fixture.output_path("shrinkage-workspace"),
        )
        existing_contents = {
            f: (workspace_dir / f).read_text(encoding="utf-8")
            for f in ["AGENTS.md", "IDENTITY.md", "SOUL.md", "TOOLS.md"]
            if (workspace_dir / f).exists()
        }
        results = check_workspace_invariants(
            workspace_dir,
            existing_contents,
            spec_red_lines=["Never modify production schemas without approval", "Do not skip validation steps"],
        )
        by_name = {r["name"]: r for r in results}
        # "Do not skip validation steps" is missing from workspace → FAIL
        self.assertEqual(by_name["red_lines_monotonic"]["status"], "FAIL")
        self.assertIn("Do not skip validation steps", by_name["red_lines_monotonic"]["detail"])
        # No ## Memory section → FAIL
        self.assertEqual(by_name["memory_baseline_present"]["status"], "FAIL")
        # Other invariants should pass
        self.assertEqual(by_name["session_startup_references_valid"]["status"], "PASS")
        self.assertEqual(by_name["role_consistency"]["status"], "PASS")

    def test_full_invariant_check_on_external_fixture(self) -> None:
        workspace_dir = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("external-agent"),
            self.fixture.output_path("external-workspace"),
        )
        existing_contents = {
            f: (workspace_dir / f).read_text(encoding="utf-8")
            for f in ["AGENTS.md", "IDENTITY.md", "SOUL.md", "TOOLS.md"]
            if (workspace_dir / f).exists()
        }
        results = check_workspace_invariants(
            workspace_dir,
            existing_contents,
            spec_red_lines=["Never modify production schemas without approval", "Do not skip validation steps"],
        )
        by_name = {r["name"]: r for r in results}
        # Both rules present in fixture → PASS
        self.assertEqual(by_name["red_lines_monotonic"]["status"], "PASS")
        # No ## Memory section → FAIL
        self.assertEqual(by_name["memory_baseline_present"]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
