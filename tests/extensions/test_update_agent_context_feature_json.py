"""Tests that agent-context prefers feature.json for the active contract."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from tests.conftest import requires_bash
from tests.extensions.test_extension_agent_context import (
    POWERSHELL,
    _bash_posix_path,
    _run_bash_agent_context_script,
    _run_powershell_agent_context_script,
)


def _setup_project(root: Path, context_file: str = "CLAUDE.md") -> None:
    """Write the extension config as JSON, which is valid YAML."""
    cfg_dir = root / ".specify" / "extensions" / "agent-context"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "agent-context-config.yml").write_text(
        json.dumps(
            {
                "context_file": context_file,
                "context_markers": {
                    "start": "<!-- SPECKIT START -->",
                    "end": "<!-- SPECKIT END -->",
                },
            }
        ),
        encoding="utf-8",
    )


def _write_feature_json(root: Path, feature_directory: str) -> None:
    specify_dir = root / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)
    (specify_dir / "feature.json").write_text(
        json.dumps({"feature_directory": feature_directory}),
        encoding="utf-8",
    )


def _make_artifacts(
    root: Path, feature_directory: str, *, tasks: bool = True
) -> Path:
    feature = root / feature_directory
    feature.mkdir(parents=True, exist_ok=True)
    (feature / "spec.md").write_text("# Specification\n", encoding="utf-8")
    (feature / "prototype.html").write_text("<!doctype html>\n", encoding="utf-8")
    (feature / "quickstart.md").write_text("# UAT\n", encoding="utf-8")
    if tasks:
        (feature / "tasks.md").write_text("- [ ] WP001\n", encoding="utf-8")
    return feature


def _assert_contract(context: str, feature: str, *, tasks: bool = True) -> None:
    for name in ("spec.md", "prototype.html", "quickstart.md"):
        assert f"{feature}/{name}" in context
    if tasks:
        assert f"{feature}/tasks.md" in context
    else:
        assert f"{feature}/tasks.md" not in context
    assert "plan.md" not in context


@requires_bash
def test_bash_uses_feature_json_for_all_available_artifacts(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    _make_artifacts(tmp_path, "specs/001-active")
    _write_feature_json(tmp_path, "specs/001-active")

    result = _run_bash_agent_context_script(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    _assert_contract(
        (tmp_path / "CLAUDE.md").read_text(encoding="utf-8"),
        "specs/001-active",
    )


@requires_bash
def test_bash_ignores_newer_stale_feature_when_feature_json_present(
    tmp_path: Path,
) -> None:
    _setup_project(tmp_path)
    active = _make_artifacts(tmp_path, "specs/001-active")
    stale = _make_artifacts(tmp_path, "specs/000-stale")
    now = time.time()
    os.utime(active / "spec.md", (now - 10, now - 10))
    os.utime(stale / "spec.md", (now, now))
    _write_feature_json(tmp_path, "specs/001-active")

    result = _run_bash_agent_context_script(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    context = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    _assert_contract(context, "specs/001-active")
    assert "specs/000-stale/" not in context


@requires_bash
def test_bash_falls_back_to_mtime_when_feature_json_absent(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    old = _make_artifacts(tmp_path, "specs/000-old")
    newer = _make_artifacts(tmp_path, "specs/001-newer")
    now = time.time()
    os.utime(old / "spec.md", (now - 10, now - 10))
    os.utime(newer / "spec.md", (now, now))

    result = _run_bash_agent_context_script(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    context = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    _assert_contract(context, "specs/001-newer")
    assert "specs/000-old/" not in context


@requires_bash
def test_bash_falls_back_when_recorded_feature_has_no_spec(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    _make_artifacts(tmp_path, "specs/000-active")
    historical = tmp_path / "specs" / "001-incomplete"
    historical.mkdir(parents=True)
    (historical / "plan.md").write_text("# Historical\n", encoding="utf-8")
    _write_feature_json(tmp_path, "specs/001-incomplete")

    result = _run_bash_agent_context_script(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    context = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    _assert_contract(context, "specs/000-active")
    assert "001-incomplete" not in context


@requires_bash
def test_bash_absolute_feature_dir_under_project_root_is_relative(
    tmp_path: Path,
) -> None:
    _setup_project(tmp_path)
    feature = _make_artifacts(tmp_path, "specs/001-active")
    _make_artifacts(tmp_path, "specs/000-stale")
    _write_feature_json(tmp_path, _bash_posix_path(feature))

    result = _run_bash_agent_context_script(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    context = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    _assert_contract(context, "specs/001-active")
    assert _bash_posix_path(tmp_path) not in context


@requires_bash
def test_bash_absolute_feature_dir_outside_project_root_is_preserved(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    external = tmp_path / "external" / "001-feature"
    project.mkdir()
    external.mkdir(parents=True)
    _make_artifacts(tmp_path, "external/001-feature")
    _setup_project(project)
    _write_feature_json(project, _bash_posix_path(external))

    result = _run_bash_agent_context_script(project)

    assert result.returncode == 0, result.stderr + result.stdout
    _assert_contract(
        (project / "CLAUDE.md").read_text(encoding="utf-8"),
        _bash_posix_path(external),
    )


@pytest.mark.skipif(not POWERSHELL, reason="no PowerShell available")
def test_powershell_uses_feature_json_for_all_available_artifacts(
    tmp_path: Path,
) -> None:
    _setup_project(tmp_path)
    _make_artifacts(tmp_path, "specs/001-active")
    _write_feature_json(tmp_path, str(tmp_path / "specs" / "001-active"))

    result = _run_powershell_agent_context_script(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    _assert_contract(
        (tmp_path / "CLAUDE.md").read_text(encoding="utf-8"),
        "specs/001-active",
    )


@pytest.mark.skipif(not POWERSHELL, reason="no PowerShell available")
def test_powershell_omits_tasks_until_task_stage(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    _make_artifacts(tmp_path, "specs/001-active", tasks=False)
    _write_feature_json(tmp_path, "specs/001-active")

    result = _run_powershell_agent_context_script(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    _assert_contract(
        (tmp_path / "CLAUDE.md").read_text(encoding="utf-8"),
        "specs/001-active",
        tasks=False,
    )


@pytest.mark.skipif(not POWERSHELL, reason="no PowerShell available")
def test_powershell_absolute_feature_dir_outside_project_root_is_preserved(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    external = tmp_path / "external" / "001-feature"
    project.mkdir()
    _make_artifacts(tmp_path, "external/001-feature")
    _setup_project(project)
    _write_feature_json(project, str(external))

    result = _run_powershell_agent_context_script(project)

    assert result.returncode == 0, result.stderr + result.stdout
    _assert_contract(
        (project / "CLAUDE.md").read_text(encoding="utf-8"),
        external.resolve().as_posix(),
    )
