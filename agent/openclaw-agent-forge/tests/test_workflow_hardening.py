from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from workflow_hardening_checks import (
    ABSOLUTE_PATH_PATTERNS,
    PROMPT_ONLY_PHRASES,
    display_path,
    extract_section,
    gather_skill_review_targets,
    iter_text_files,
    resolve_workspace_path,
    run_workflow_hardening_diagnostics,
)
from test_support import SkillFixture


# ---------------------------------------------------------------------------
# resolve_workspace_path
# ---------------------------------------------------------------------------

class ResolveWorkspacePathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_resolves_relative_path(self) -> None:
        workspace = self.fixture.output_path("ws")
        workspace.mkdir()
        result = resolve_workspace_path(workspace, "slides/demo")
        self.assertEqual(result, workspace / "slides" / "demo")

    def test_resolves_nested_path(self) -> None:
        workspace = self.fixture.output_path("ws")
        workspace.mkdir()
        result = resolve_workspace_path(workspace, "skills/frontend/SKILL.md")
        self.assertEqual(result, workspace / "skills" / "frontend" / "SKILL.md")


# ---------------------------------------------------------------------------
# display_path
# ---------------------------------------------------------------------------

class DisplayPathTests(unittest.TestCase):
    def test_returns_relative_path(self) -> None:
        workspace = Path("/workspace")
        full = Path("/workspace/slides/demo/index.html")
        self.assertEqual(display_path(full, workspace), "slides/demo/index.html")

    def test_returns_absolute_when_not_relative(self) -> None:
        workspace = Path("/workspace")
        full = Path("/other/path/file.md")
        result = display_path(full, workspace)
        self.assertIn("other", result)


# ---------------------------------------------------------------------------
# extract_section
# ---------------------------------------------------------------------------

class ExtractSectionTests(unittest.TestCase):
    def test_extracts_section_content(self) -> None:
        text = "# Title\n\n## Session Startup\n\n- Read AGENTS.md\n- Check logs\n\n## Red Lines\n\n- Never delete\n"
        result = extract_section(text, "## Session Startup")
        self.assertIn("Read AGENTS.md", result)
        self.assertIn("Check logs", result)
        self.assertNotIn("Never delete", result)

    def test_returns_empty_for_missing_section(self) -> None:
        text = "# Title\n\n## Red Lines\n\n- Rule\n"
        result = extract_section(text, "## Session Startup")
        self.assertEqual(result, "")

    def test_stops_at_next_heading(self) -> None:
        text = "## A\n\ncontent A\n\n## B\n\ncontent B\n"
        result = extract_section(text, "## A")
        self.assertEqual(result, "content A")

    def test_extracts_to_end_when_no_next_heading(self) -> None:
        text = "## A\n\ncontent A\n\nmore content\n"
        result = extract_section(text, "## A")
        self.assertIn("content A", result)
        self.assertIn("more content", result)


# ---------------------------------------------------------------------------
# iter_text_files
# ---------------------------------------------------------------------------

class IterTextFilesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_returns_empty_for_missing_path(self) -> None:
        result = iter_text_files(Path("/nonexistent"))
        self.assertEqual(result, [])

    def test_returns_single_text_file(self) -> None:
        path = self.fixture.output_path("test.md")
        path.write_text("# Test\n", encoding="utf-8")
        result = iter_text_files(path)
        self.assertEqual(result, [path])

    def test_skips_non_text_files(self) -> None:
        path = self.fixture.output_path("test.png")
        path.write_bytes(b"\x89PNG")
        result = iter_text_files(path)
        self.assertEqual(result, [])

    def test_recognizes_all_text_suffixes(self) -> None:
        for suffix in (".html", ".htm", ".md", ".css", ".js", ".json", ".txt"):
            path = self.fixture.output_path(f"file{suffix}")
            path.write_text("content", encoding="utf-8")
        result = iter_text_files(self.fixture.output_root)
        self.assertEqual(len(result), 7)

    def test_recurses_into_subdirectories(self) -> None:
        sub = self.fixture.output_path("sub")
        sub.mkdir()
        (sub / "a.md").write_text("a", encoding="utf-8")
        (sub / "b.md").write_text("b", encoding="utf-8")
        (self.fixture.output_root / "c.md").write_text("c", encoding="utf-8")
        result = iter_text_files(self.fixture.output_root)
        self.assertEqual(len(result), 3)

    def test_returns_empty_for_empty_directory(self) -> None:
        empty = self.fixture.output_path("empty")
        empty.mkdir()
        result = iter_text_files(empty)
        self.assertEqual(result, [])


# ---------------------------------------------------------------------------
# gather_skill_review_targets
# ---------------------------------------------------------------------------

class GatherSkillReviewTargetsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_returns_empty_when_no_resources(self) -> None:
        workspace = self.fixture.output_path("ws")
        workspace.mkdir()
        result = gather_skill_review_targets({}, workspace)
        self.assertEqual(result, [])

    def test_gathers_from_primary_skill_entrypoints(self) -> None:
        workspace = self.fixture.output_path("ws")
        skills = workspace / "skills" / "demo"
        skills.mkdir(parents=True)
        (skills / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
        spec = {"skill_resources": {"primary_skill_entrypoints": ["skills/demo/SKILL.md"]}}
        result = gather_skill_review_targets(spec, workspace)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "SKILL.md")

    def test_skips_missing_entrypoints(self) -> None:
        workspace = self.fixture.output_path("ws")
        workspace.mkdir()
        spec = {"skill_resources": {"primary_skill_entrypoints": ["skills/missing/SKILL.md"]}}
        result = gather_skill_review_targets(spec, workspace)
        self.assertEqual(result, [])

    def test_gathers_from_sidecar_write_ownership(self) -> None:
        workspace = self.fixture.output_path("ws")
        owner_dir = workspace / "skills" / "sidecar"
        owner_dir.mkdir(parents=True)
        (owner_dir / "SKILL.md").write_text("# Sidecar\n", encoding="utf-8")
        spec = {
            "workflow_hardening": {
                "sidecar_write_ownership": [
                    {"owner": "skills/sidecar", "writes_to": ["output/"], "must_not_write": []}
                ]
            }
        }
        result = gather_skill_review_targets(spec, workspace)
        self.assertEqual(len(result), 1)

    def test_deduplicates_targets(self) -> None:
        workspace = self.fixture.output_path("ws")
        skills = workspace / "skills" / "demo"
        skills.mkdir(parents=True)
        (skills / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
        spec = {
            "skill_resources": {"primary_skill_entrypoints": ["skills/demo/SKILL.md"]},
            "workflow_hardening": {
                "sidecar_write_ownership": [
                    {"owner": "skills/demo", "writes_to": [], "must_not_write": []}
                ]
            },
        }
        result = gather_skill_review_targets(spec, workspace)
        self.assertEqual(len(result), 1)

    def test_skips_empty_entrypoint_strings(self) -> None:
        workspace = self.fixture.output_path("ws")
        workspace.mkdir()
        spec = {"skill_resources": {"primary_skill_entrypoints": ["", "  "]}}
        result = gather_skill_review_targets(spec, workspace)
        self.assertEqual(result, [])


# ---------------------------------------------------------------------------
# run_workflow_hardening_diagnostics — no workflow_hardening
# ---------------------------------------------------------------------------

class NoWorkflowHardeningTests(unittest.TestCase):
    def test_returns_empty_when_no_workflow_hardening(self) -> None:
        fixture = SkillFixture()
        workspace = fixture.output_path("ws")
        workspace.mkdir()
        (workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        findings, signals = run_workflow_hardening_diagnostics({}, workspace)
        self.assertEqual(findings, [])
        self.assertEqual(signals, [])
        fixture.cleanup()

    def test_returns_empty_when_workflow_hardening_not_dict(self) -> None:
        fixture = SkillFixture()
        workspace = fixture.output_path("ws")
        workspace.mkdir()
        findings, signals = run_workflow_hardening_diagnostics({"workflow_hardening": "bad"}, workspace)
        self.assertEqual(findings, [])
        self.assertEqual(signals, [])
        fixture.cleanup()


# ---------------------------------------------------------------------------
# run_workflow_hardening_diagnostics — approval gates
# ---------------------------------------------------------------------------

class ApprovalGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()
        self.workspace = self.fixture.output_path("ws")
        self.workspace.mkdir()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_finds_missing_gate_in_agents(self) -> None:
        (self.workspace / "AGENTS.md").write_text(
            "# AGENTS.md\n\n## Session Startup\n\n- Read docs\n", encoding="utf-8"
        )
        spec = {"workflow_hardening": {"approval_gates": [{"name": "Preview Gate"}]}}
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertTrue(any("missing from AGENTS.md" in f for f in findings))

    def test_finds_gate_not_elevated(self) -> None:
        (self.workspace / "AGENTS.md").write_text(
            "# AGENTS.md\n\n## Default Behavior\n\n- Preview Gate is mentioned here\n"
            "## Session Startup\n\n- Read docs\n## Red Lines\n\n- Never skip\n",
            encoding="utf-8",
        )
        spec = {"workflow_hardening": {"approval_gates": [{"name": "Preview Gate"}]}}
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertTrue(any("not elevated" in f for f in findings))

    def test_passes_when_gate_in_session_startup(self) -> None:
        (self.workspace / "AGENTS.md").write_text(
            "# AGENTS.md\n\n## Session Startup\n\n- Check Preview Gate\n## Red Lines\n\n- Never\n",
            encoding="utf-8",
        )
        spec = {"workflow_hardening": {"approval_gates": [{"name": "Preview Gate"}]}}
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        gate_findings = [f for f in findings if "Preview Gate" in f]
        self.assertEqual(gate_findings, [])

    def test_passes_when_gate_in_red_lines(self) -> None:
        (self.workspace / "AGENTS.md").write_text(
            "# AGENTS.md\n\n## Session Startup\n\n- Read docs\n## Red Lines\n\n- Never skip Preview Gate\n",
            encoding="utf-8",
        )
        spec = {"workflow_hardening": {"approval_gates": [{"name": "Preview Gate"}]}}
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        gate_findings = [f for f in findings if "Preview Gate" in f]
        self.assertEqual(gate_findings, [])

    def test_skips_gate_without_name(self) -> None:
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        spec = {"workflow_hardening": {"approval_gates": [{"name": ""}]}}
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertEqual(findings, [])


# ---------------------------------------------------------------------------
# run_workflow_hardening_diagnostics — canonical source
# ---------------------------------------------------------------------------

class CanonicalSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()
        self.workspace = self.fixture.output_path("ws")
        self.workspace.mkdir()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_finds_missing_canonical_source(self) -> None:
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        spec = {"workflow_hardening": {"canonical_source": {"path": "slides/demo"}}}
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertTrue(any("canonical source path is missing" in f for f in findings))

    def test_passes_when_canonical_source_exists(self) -> None:
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        (self.workspace / "slides" / "demo").mkdir(parents=True)
        spec = {"workflow_hardening": {"canonical_source": {"path": "slides/demo"}}}
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        canonical_findings = [f for f in findings if "canonical source" in f]
        self.assertEqual(canonical_findings, [])


# ---------------------------------------------------------------------------
# run_workflow_hardening_diagnostics — derived exports
# ---------------------------------------------------------------------------

class DerivedExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()
        self.workspace = self.fixture.output_path("ws")
        self.workspace.mkdir()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_finds_export_resolving_to_canonical(self) -> None:
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        slides = self.workspace / "slides" / "demo"
        slides.mkdir(parents=True)
        spec = {
            "workflow_hardening": {
                "canonical_source": {"path": "slides/demo"},
                "derived_exports": [
                    {"path": "slides/demo", "source_path": "slides/demo", "reason": "test", "approval_gate": "G"}
                ],
            }
        }
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertTrue(any("resolves to canonical source" in f for f in findings))

    def test_finds_export_inside_canonical_root(self) -> None:
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        slides = self.workspace / "slides" / "demo"
        slides.mkdir(parents=True)
        spec = {
            "workflow_hardening": {
                "canonical_source": {"path": "slides/demo"},
                "derived_exports": [
                    {"path": "slides/demo/out.pptx", "source_path": "slides/demo", "reason": "test", "approval_gate": "G"}
                ],
            }
        }
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertTrue(any("inside canonical source root" in f for f in findings))


# ---------------------------------------------------------------------------
# run_workflow_hardening_diagnostics — install contracts
# ---------------------------------------------------------------------------

class InstallContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()
        self.workspace = self.fixture.output_path("ws")
        self.workspace.mkdir()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_finds_missing_contract(self) -> None:
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        spec = {
            "workflow_hardening": {
                "install_contracts": [
                    {"capability": "PPTX export", "contract_path": "dev/install.json", "setup_entry": "s", "verify_entry": "v"}
                ]
            }
        }
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertTrue(any("contract missing" in f for f in findings))

    def test_passes_when_contract_exists(self) -> None:
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        dev = self.workspace / "dev"
        dev.mkdir()
        (dev / "install.json").write_text("{}", encoding="utf-8")
        spec = {
            "workflow_hardening": {
                "install_contracts": [
                    {"capability": "PPTX export", "contract_path": "dev/install.json", "setup_entry": "s", "verify_entry": "v"}
                ]
            }
        }
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        contract_findings = [f for f in findings if "contract" in f.lower()]
        self.assertEqual(contract_findings, [])


# ---------------------------------------------------------------------------
# run_workflow_hardening_diagnostics — deterministic helpers
# ---------------------------------------------------------------------------

class DeterministicHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()
        self.workspace = self.fixture.output_path("ws")
        self.workspace.mkdir()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_finds_missing_helper(self) -> None:
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        spec = {
            "workflow_hardening": {
                "deterministic_helpers": [
                    {"action": "Open preview", "kind": "script", "entrypoint": "scripts/open_preview.py", "why_needed": "test"}
                ]
            }
        }
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertTrue(any("prompt-only workflow gap" in f for f in findings))

    def test_passes_when_helper_exists(self) -> None:
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        scripts = self.workspace / "scripts"
        scripts.mkdir()
        (scripts / "open_preview.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        spec = {
            "workflow_hardening": {
                "deterministic_helpers": [
                    {"action": "Open preview", "kind": "script", "entrypoint": "scripts/open_preview.py", "why_needed": "test"}
                ]
            }
        }
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        helper_findings = [f for f in findings if "prompt-only" in f]
        self.assertEqual(helper_findings, [])


# ---------------------------------------------------------------------------
# run_workflow_hardening_diagnostics — asset staging
# ---------------------------------------------------------------------------

class AssetStagingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()
        self.workspace = self.fixture.output_path("ws")
        self.workspace.mkdir()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_finds_missing_asset_root(self) -> None:
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        spec = {"workflow_hardening": {"asset_staging": {"asset_root": "slides/assets"}}}
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertTrue(any("asset staging root is missing" in f for f in findings))

    def test_passes_when_asset_root_exists(self) -> None:
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        (self.workspace / "slides" / "assets").mkdir(parents=True)
        spec = {"workflow_hardening": {"asset_staging": {"asset_root": "slides/assets"}}}
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        asset_findings = [f for f in findings if "asset staging" in f]
        self.assertEqual(asset_findings, [])


# ---------------------------------------------------------------------------
# run_workflow_hardening_diagnostics — absolute path patterns
# ---------------------------------------------------------------------------

class AbsolutePathPatternTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()
        self.workspace = self.fixture.output_path("ws")
        self.slides = self.workspace / "slides" / "demo"
        self.slides.mkdir(parents=True)
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def _run_with_content(self, content: str) -> list[str]:
        (self.slides / "index.html").write_text(content, encoding="utf-8")
        spec = {
            "workflow_hardening": {
                "canonical_source": {"path": "slides/demo"},
                "asset_staging": {"asset_root": "slides/demo"},
            }
        }
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        return [f for f in findings if "portability finding" in f]

    def test_detects_windows_drive_path(self) -> None:
        findings = self._run_with_content(r'<img src="C:\Users\test\img.png">')
        self.assertTrue(any("Windows drive path" in f for f in findings))

    def test_detects_unc_path(self) -> None:
        findings = self._run_with_content(r'<img src="\\server\share\img.png">')
        self.assertTrue(any("UNC path" in f for f in findings))

    def test_detects_file_uri(self) -> None:
        # Verify the file URI regex pattern works in isolation
        for label, pattern in ABSOLUTE_PATH_PATTERNS:
            if label == "file URI":
                self.assertIsNotNone(
                    pattern.search("file:///etc/hosts"),
                    "file URI pattern should match file:///etc/hosts",
                )
                break

    def test_detects_macos_home_path(self) -> None:
        findings = self._run_with_content('<img src="/Users/test/img.png">')
        self.assertTrue(any("macOS home path" in f for f in findings))

    def test_detects_linux_home_path(self) -> None:
        # Content that only matches Linux home (not macOS /Users)
        findings = self._run_with_content('<img src="/home/user/img.png">')
        self.assertTrue(any("Linux home path" in f for f in findings))

    def test_detects_windows_env_variable(self) -> None:
        findings = self._run_with_content(r'<img src="%USERPROFILE%\img.png">')
        self.assertTrue(any("Windows environment variable" in f for f in findings))

    def test_detects_unix_env_variable(self) -> None:
        findings = self._run_with_content('<img src="$HOME/img.png">')
        self.assertTrue(any("Unix environment variable" in f for f in findings))

    def test_detects_windows_program_files(self) -> None:
        # Content without drive letter — only matches Windows system folder pattern
        # Note: "C:\Program Files" matches "Windows drive path" first due to break,
        # so we test the regex directly here
        content = r'<img src="C:\Program Files\App\img.png">'
        for label, pattern in ABSOLUTE_PATH_PATTERNS:
            if label == "Windows system folder":
                self.assertIsNotNone(pattern.search(content), f"Pattern '{label}' should match {content}")
                break

    def test_no_finding_for_relative_paths(self) -> None:
        findings = self._run_with_content('<img src="assets/img.png">')
        self.assertEqual(findings, [])

    def test_all_8_pattern_types_in_tuple(self) -> None:
        self.assertEqual(len(ABSOLUTE_PATH_PATTERNS), 8)


# ---------------------------------------------------------------------------
# run_workflow_hardening_diagnostics — derived suffix inside canonical
# ---------------------------------------------------------------------------

class DerivedSuffixInCanonicalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()
        self.workspace = self.fixture.output_path("ws")
        self.workspace.mkdir()
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_finds_derived_suffix_inside_canonical(self) -> None:
        slides = self.workspace / "slides" / "demo"
        slides.mkdir(parents=True)
        (slides / "output.pptx").write_bytes(b"fake")
        spec = {
            "workflow_hardening": {
                "canonical_source": {"path": "slides/demo"},
                "derived_exports": [
                    {"path": "exports/out.pptx", "source_path": "slides/demo", "reason": "test", "approval_gate": "G"}
                ],
                "asset_staging": {"asset_root": "slides/demo"},
            }
        }
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertTrue(any(".pptx file inside canonical source root" in f for f in findings))


# ---------------------------------------------------------------------------
# run_workflow_hardening_diagnostics — sidecar write ownership
# ---------------------------------------------------------------------------

class SidecarWriteOwnershipTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()
        self.workspace = self.fixture.output_path("ws")
        self.workspace.mkdir()
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_finds_missing_owner_path(self) -> None:
        spec = {
            "workflow_hardening": {
                "sidecar_write_ownership": [
                    {"owner": "skills/missing", "writes_to": [], "must_not_write": []}
                ]
            }
        }
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertTrue(any("sidecar owner path is missing" in f for f in findings))

    def test_finds_owner_dir_without_skill_md(self) -> None:
        owner_dir = self.workspace / "skills" / "demo"
        owner_dir.mkdir(parents=True)
        spec = {
            "workflow_hardening": {
                "sidecar_write_ownership": [
                    {"owner": "skills/demo", "writes_to": [], "must_not_write": []}
                ]
            }
        }
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        self.assertTrue(any("missing SKILL.md" in f for f in findings))

    def test_passes_when_owner_has_skill_md(self) -> None:
        owner_dir = self.workspace / "skills" / "demo"
        owner_dir.mkdir(parents=True)
        (owner_dir / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
        spec = {
            "workflow_hardening": {
                "sidecar_write_ownership": [
                    {"owner": "skills/demo", "writes_to": [], "must_not_write": []}
                ]
            }
        }
        findings, _ = run_workflow_hardening_diagnostics(spec, self.workspace)
        sidecar_findings = [f for f in findings if "sidecar" in f.lower()]
        self.assertEqual(sidecar_findings, [])


# ---------------------------------------------------------------------------
# run_workflow_hardening_diagnostics — prompt-only phrases
# ---------------------------------------------------------------------------

class PromptOnlyPhraseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()
        self.workspace = self.fixture.output_path("ws")
        self.skills = self.workspace / "skills" / "demo"
        self.skills.mkdir(parents=True)
        (self.workspace / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def _run_with_skill_content(self, content: str) -> list[str]:
        (self.skills / "SKILL.md").write_text(content, encoding="utf-8")
        spec = {
            "skill_resources": {"primary_skill_entrypoints": ["skills/demo/SKILL.md"]},
            "workflow_hardening": {},
        }
        _, signals = run_workflow_hardening_diagnostics(spec, self.workspace)
        return signals

    def test_detects_attempt_to(self) -> None:
        signals = self._run_with_skill_content("# Skill\n\nAttempt to render the slide.\n")
        self.assertTrue(any("attempt to" in s for s in signals))

    def test_detects_try_to(self) -> None:
        signals = self._run_with_skill_content("# Skill\n\nTry to use relative paths.\n")
        self.assertTrue(any("try to" in s for s in signals))

    def test_detects_if_supported(self) -> None:
        signals = self._run_with_skill_content("# Skill\n\nExport to PPTX if supported.\n")
        self.assertTrue(any("if supported" in s for s in signals))

    def test_detects_use_relative_paths(self) -> None:
        signals = self._run_with_skill_content("# Skill\n\nAlways use relative paths.\n")
        self.assertTrue(any("use relative paths" in s for s in signals))

    def test_detects_wait_a_bit(self) -> None:
        signals = self._run_with_skill_content("# Skill\n\nWait a bit before retry.\n")
        self.assertTrue(any("wait a bit" in s for s in signals))

    def test_no_signal_for_clean_content(self) -> None:
        signals = self._run_with_skill_content("# Skill\n\nRender slides and export.\n")
        self.assertEqual(signals, [])

    def test_all_prompt_phrases_listed(self) -> None:
        self.assertEqual(len(PROMPT_ONLY_PHRASES), 5)


# ---------------------------------------------------------------------------
# Integration — full hardened spec
# ---------------------------------------------------------------------------

class FullHardenedSpecIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()
        self.workspace = self.fixture.copy_tree(
            self.fixture.workspace_fixture_path("external-agent"),
            self.fixture.output_path("hardened-workspace"),
        )

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_hardened_spec_produces_findings_and_signals(self) -> None:
        spec = {
            "workflow_hardening": {
                "canonical_source": {"path": "slides/demo"},
                "approval_gates": [{"name": "Preview Approval Gate"}],
                "install_contracts": [
                    {"capability": "PPTX", "contract_path": "dev/install.json", "setup_entry": "s", "verify_entry": "v"}
                ],
                "deterministic_helpers": [
                    {"action": "Open preview", "kind": "script", "entrypoint": "scripts/open_preview.py", "why_needed": "test"}
                ],
                "asset_staging": {"asset_root": "slides/assets"},
                "sidecar_write_ownership": [
                    {"owner": "skills/missing", "writes_to": [], "must_not_write": []}
                ],
            }
        }
        findings, signals = run_workflow_hardening_diagnostics(spec, self.workspace)
        # Should have multiple findings from various checks
        self.assertTrue(len(findings) >= 3, f"Expected >= 3 findings, got {len(findings)}")


if __name__ == "__main__":
    unittest.main()
