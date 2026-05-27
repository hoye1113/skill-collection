from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = SKILL_ROOT / "scripts"


class SkillFixture:
    def __init__(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory(prefix="openclaw-agent-forge-tests-")
        self.root = Path(self._tempdir.name)
        self.output_root = self.root / "output"
        self.output_root.mkdir(parents=True, exist_ok=True)

    def cleanup(self) -> None:
        self._tempdir.cleanup()

    def fixture_path(self, relative_name: str) -> Path:
        return SKILL_ROOT / "tests" / "fixtures" / relative_name

    def golden_path(self, *parts: str) -> Path:
        return SKILL_ROOT / "tests" / "golden" / Path(*parts)

    def workspace_fixture_path(self, *parts: str) -> Path:
        return SKILL_ROOT / "tests" / "fixtures" / "existing-workspaces" / Path(*parts)

    def output_path(self, *parts: str) -> Path:
        return self.output_root.joinpath(*parts)

    def run_script(self, script_name: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        script_path = SCRIPTS_ROOT / script_name
        env = os.environ.copy()
        env.setdefault("PYTHONUTF8", "1")
        env.setdefault("PYTHONIOENCODING", "utf-8")
        return subprocess.run(
            [sys.executable, str(script_path), *[str(arg) for arg in args]],
            cwd=str(SKILL_ROOT),
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

    def load_module(self, module_name: str):
        module_path = SCRIPTS_ROOT / module_name
        spec = importlib.util.spec_from_file_location(module_name.replace(".py", "_test"), module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def write_text(self, path: Path, content: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def copy_tree(self, source: Path, destination: Path) -> Path:
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        return destination
