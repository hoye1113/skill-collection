from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from render_root_files import validate_required_fields, check_target_paths, resolve_path, write_file
from spec_contract import ALL_POSSIBLE_ROOT_FILES, FORBIDDEN_FILENAMES
from test_support import SkillFixture


class ValidateRequiredFieldsTests(unittest.TestCase):
    def test_passes_on_valid_spec(self) -> None:
        spec = json.loads(
            (SkillFixture().fixture_path("independent-flowyclaw.json")).read_text(encoding="utf-8")
        )
        # Should not raise
        validate_required_fields(spec)

    def test_raises_on_missing_field(self) -> None:
        spec = {"name": "Test", "role": "Tester"}
        # Missing many required fields
        with self.assertRaises(ValueError) as ctx:
            validate_required_fields(spec)
        self.assertIn("Spec failed validation", str(ctx.exception))

    def test_raises_on_empty_public_identity(self) -> None:
        spec = json.loads(
            (SkillFixture().fixture_path("independent-flowyclaw.json")).read_text(encoding="utf-8")
        )
        spec["public_identity"] = ""
        with self.assertRaises(ValueError) as ctx:
            validate_required_fields(spec)
        self.assertIn("public_identity", str(ctx.exception))


class CheckTargetPathsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_passes_on_empty_directory(self) -> None:
        output_dir = self.fixture.output_path("empty-target")
        output_dir.mkdir(parents=True, exist_ok=True)
        # Should not raise
        check_target_paths(output_dir)

    def test_raises_on_forbidden_file(self) -> None:
        output_dir = self.fixture.output_path("forbidden-target")
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "PROMOTION_ANALYSIS.md").write_text("# forbidden\n", encoding="utf-8")
        with self.assertRaises(ValueError) as ctx:
            check_target_paths(output_dir)
        self.assertIn("forbidden governance files", str(ctx.exception))

    def test_raises_on_existing_root_file(self) -> None:
        output_dir = self.fixture.output_path("existing-target")
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        with self.assertRaises(ValueError) as ctx:
            check_target_paths(output_dir)
        self.assertIn("refuses to overwrite", str(ctx.exception))


class ResolvePathTests(unittest.TestCase):
    def test_resolves_relative_path(self) -> None:
        result = resolve_path("some/path")
        self.assertTrue(result.is_absolute())

    def test_raises_on_empty_string(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            resolve_path("")
        self.assertIn("required and cannot be empty", str(ctx.exception))

    def test_accepts_path_object(self) -> None:
        result = resolve_path(Path("some/path"))
        self.assertTrue(result.is_absolute())


class WriteFileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SkillFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_writes_content_with_trailing_newline(self) -> None:
        parent = self.fixture.output_path("write-test")
        parent.mkdir(parents=True, exist_ok=True)
        path = parent / "test.md"
        write_file(path, "# Hello\n")
        content = path.read_text(encoding="utf-8")
        self.assertEqual(content, "# Hello\n")

    def test_strips_trailing_whitespace_and_adds_newline(self) -> None:
        parent = self.fixture.output_path("write-test2")
        parent.mkdir(parents=True, exist_ok=True)
        path = parent / "test.md"
        write_file(path, "# Hello   ")
        content = path.read_text(encoding="utf-8")
        self.assertEqual(content, "# Hello\n")


if __name__ == "__main__":
    unittest.main()
