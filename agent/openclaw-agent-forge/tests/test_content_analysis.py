from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from content_analysis import analyze_content_quality


class ContentAnalysisTests(unittest.TestCase):
    def _analyze(self, filename: str, content: str, **kwargs) -> list[dict[str, str]]:
        return analyze_content_quality(
            filename=filename,
            content=content,
            spec=kwargs.get("spec", {}),
            host_profile=kwargs.get("host_profile", "generic-openclaw"),
            all_file_sizes=kwargs.get("all_file_sizes"),
        )

    def _issue_texts(self, filename: str, content: str, **kwargs) -> list[str]:
        """Return just the issue strings for backward-compatible assertions."""
        return [item["issue"] for item in self._analyze(filename, content, **kwargs)]

    def test_detects_placeholders(self) -> None:
        content = (
            "# SOUL.md\n\n"
            "## Non-Negotiables\n\n"
            "- Be professional\n"
            "## Enduring Style\n\n"
            "- [TODO] Define style\n"
        )
        issues = self._issue_texts("SOUL.md", content)
        placeholder_issues = [i for i in issues if "placeholder" in i]
        self.assertTrue(placeholder_issues)

    def test_detects_empty_sections(self) -> None:
        content = (
            "# AGENTS.md\n\n"
            "## Workspace Positioning\n\n"
            "This workspace does X.\n\n"
            "## Red Lines\n\n"
            "## Default Behavior\n\n"
            "- Do things\n"
        )
        issues = self._issue_texts("AGENTS.md", content)
        empty_issues = [i for i in issues if "empty section" in i and "Red Lines" in i]
        self.assertTrue(empty_issues)

    def test_detects_vague_rules(self) -> None:
        content = (
            "# AGENTS.md\n\n"
            "## Red Lines\n\n"
            "- Try to be careful with data\n"
            "- Never delete without confirmation\n"
        )
        issues = self._issue_texts("AGENTS.md", content)
        vague_issues = [i for i in issues if "vague rule" in i]
        self.assertTrue(vague_issues)
        self.assertTrue(any("Try to be careful" in i for i in vague_issues))

    def test_detects_duplicate_rules(self) -> None:
        content = (
            "# AGENTS.md\n\n"
            "## Session Startup\n\n"
            "- Always validate before processing\n\n"
            "## Red Lines\n\n"
            "- Always validate before processing\n"
        )
        issues = self._issue_texts("AGENTS.md", content)
        dup_issues = [i for i in issues if "duplicate rule" in i]
        self.assertTrue(dup_issues)

    def test_detects_character_budget_violation(self) -> None:
        content = "# IDENTITY.md\n\n" + "x" * 15_000
        all_sizes = {"IDENTITY.md": len(content)}
        issues = self._issue_texts("IDENTITY.md", content, all_file_sizes=all_sizes)
        budget_issues = [i for i in issues if "character budget" in i and "limit" in i]
        self.assertTrue(budget_issues)
        self.assertTrue(any("IDENTITY.md" in i for i in budget_issues))

    def test_detects_total_budget_violation(self) -> None:
        content = "# IDENTITY.md\n\n" + "x" * 5_000
        all_sizes = {
            "IDENTITY.md": 5_000,
            "SOUL.md": 20_000,
            "AGENTS.md": 20_000,
            "TOOLS.md": 20_000,
        }
        issues = self._issue_texts("IDENTITY.md", content, all_file_sizes=all_sizes)
        budget_issues = [i for i in issues if "total across all files" in i]
        self.assertTrue(budget_issues)

    def test_host_profile_drift_detection(self) -> None:
        content = "# TOOLS.md\n\n## Output Roots\n\n- Run `uv run pipeline` to execute\n"
        issues = self._issue_texts("TOOLS.md", content, host_profile="generic-openclaw")
        drift_issues = [i for i in issues if "host profile drift" in i]
        self.assertTrue(drift_issues)

    def test_no_drift_when_host_matches(self) -> None:
        content = "# TOOLS.md\n\n## Output Roots\n\n- Run `uv run pipeline` to execute\n"
        issues = self._issue_texts("TOOLS.md", content, host_profile="flowyclaw")
        drift_issues = [i for i in issues if "host profile drift" in i]
        self.assertFalse(drift_issues)

    def test_clean_workspace_has_no_content_issues(self) -> None:
        content = (
            "# AGENTS.md\n\n"
            "## Workspace Positioning\n\n"
            "This workspace manages pipelines.\n\n"
            "## Session Startup\n\n"
            "- Read AGENTS.md\n\n"
            "## Red Lines\n\n"
            "- Never delete without confirmation\n\n"
            "## Default Behavior\n\n"
            "- Run diagnostics first\n\n"
            "## Resume Strategy\n\n"
            "- Global resume file: AGENTS.md\n\n"
            "## Boundaries\n\n"
            "- Stay within analytics namespace\n\n"
            "## Workspace Layout\n\n"
            "- pipelines/ - definitions\n"
        )
        issues = self._issue_texts("AGENTS.md", content)
        self.assertEqual(issues, [])

    def test_empty_content_returns_no_issues(self) -> None:
        issues = self._issue_texts("IDENTITY.md", "")
        self.assertEqual(issues, [])

    def test_non_agents_files_skip_vague_rule_check(self) -> None:
        """Only AGENTS.md gets vague-rule analysis."""
        content = (
            "# SOUL.md\n\n"
            "## Non-Negotiables\n\n"
            "- Try to be careful\n\n"
            "## Enduring Style\n\n"
            "- Professional\n"
        )
        issues = self._issue_texts("SOUL.md", content)
        vague_issues = [i for i in issues if "vague rule" in i]
        self.assertFalse(vague_issues)

    # --- Layered result format tests ---

    def test_layered_result_has_layer_section_issue_keys(self) -> None:
        content = (
            "# AGENTS.md\n\n"
            "## Red Lines\n\n"
            "- Try to be careful\n"
        )
        items = self._analyze("AGENTS.md", content)
        self.assertTrue(items)
        for item in items:
            self.assertIn("layer", item)
            self.assertIn("section", item)
            self.assertIn("issue", item)

    def test_placeholder_layer_is_content(self) -> None:
        content = "# SOUL.md\n\n## Non-Negotiables\n\n- [TODO] fill in\n"
        items = self._analyze("SOUL.md", content)
        placeholder_items = [i for i in items if "placeholder" in i["issue"]]
        self.assertTrue(placeholder_items)
        for item in placeholder_items:
            self.assertEqual(item["layer"], "content")

    def test_empty_section_layer_is_content(self) -> None:
        content = "# AGENTS.md\n\n## Red Lines\n\n## Default Behavior\n\n- Do things\n"
        items = self._analyze("AGENTS.md", content)
        empty_items = [i for i in items if "empty section" in i["issue"]]
        self.assertTrue(empty_items)
        for item in empty_items:
            self.assertEqual(item["layer"], "content")
            self.assertEqual(item["section"], "## Red Lines")

    def test_vague_rule_layer_is_quality(self) -> None:
        content = "# AGENTS.md\n\n## Red Lines\n\n- Try to be careful\n"
        items = self._analyze("AGENTS.md", content)
        vague_items = [i for i in items if "vague rule" in i["issue"]]
        self.assertTrue(vague_items)
        for item in vague_items:
            self.assertEqual(item["layer"], "quality")
            self.assertEqual(item["section"], "## Red Lines")

    def test_budget_layer_is_budget(self) -> None:
        content = "# IDENTITY.md\n\n" + "x" * 15_000
        all_sizes = {"IDENTITY.md": len(content)}
        items = self._analyze("IDENTITY.md", content, all_file_sizes=all_sizes)
        budget_items = [i for i in items if "character budget" in i["issue"]]
        self.assertTrue(budget_items)
        for item in budget_items:
            self.assertEqual(item["layer"], "budget")

    def test_drift_layer_is_drift(self) -> None:
        content = "# TOOLS.md\n\n## Output Roots\n\n- Run `uv run pipeline`\n"
        items = self._analyze("TOOLS.md", content, host_profile="generic-openclaw")
        drift_items = [i for i in items if "host profile drift" in i["issue"]]
        self.assertTrue(drift_items)
        for item in drift_items:
            self.assertEqual(item["layer"], "drift")


if __name__ == "__main__":
    unittest.main()
