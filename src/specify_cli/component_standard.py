"""Executable coding-standard checks for Preset and Extension packages.

The runtime manifest loaders answer whether a package can be installed.  This
module adds repository component checks that answer whether a touched package
follows the component coding standard.  It deliberately has no network access
and does not mutate the package being checked.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

import yaml
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from .extensions import ExtensionManifest, ValidationError
from .integrations import INTEGRATION_REGISTRY
from .presets import PresetManifest, PresetValidationError

_COMPONENT_PARENTS = {"extensions": "extension", "presets": "preset"}
_MANIFEST_NAMES = {"extension": "extension.yml", "preset": "preset.yml"}
_SCAFFOLD_ROOTS = {
    ("extension", "template"),
    ("preset", "scaffold"),
}
_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SEMVER_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
_EXTENSION_COMMAND_PATTERN = re.compile(
    r"^speckit\.([a-z0-9]+(?:-[a-z0-9]+)*)\.([a-z0-9]+(?:-[a-z0-9]+)*)$"
)
_CANONICAL_COMMAND_PATTERN = re.compile(
    r"^speckit\.[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)*$"
)


def _platform_tokens() -> dict[str, str]:
    owners_by_directory: dict[str, list[str]] = {}
    for key, integration in INTEGRATION_REGISTRY.items():
        directory = str(integration.registrar_config.get("dir", "")).rstrip("/")
        if directory:
            owners_by_directory.setdefault(directory, []).append(key)

    tokens = {
        directory: "agent output directory for " + ", ".join(sorted(owners))
        for directory, owners in owners_by_directory.items()
    }
    tokens[".github/prompts"] = "Copilot companion prompt output directory"
    tokens["SKILL.md"] = "agent-specific skill filename"
    return tokens


_PLATFORM_TOKENS = _platform_tokens()
_PROMPT_SECTION_ALIASES = {
    "goal": {"goal", "objective", "目标"},
    "boundaries": {
        "operating boundaries",
        "boundaries",
        "scope",
        "边界",
        "操作边界",
    },
    "validation": {"validation", "validate", "验证"},
    "report": {"report", "output", "result", "报告", "输出"},
}
_REQUIRED_PACKAGE_FILES = ("README.md", "CHANGELOG.md", "LICENSE")
_STRUCTURED_SUFFIXES = {".json", ".yaml", ".yml"}


@dataclass(frozen=True)
class ComponentTarget:
    """A repository component selected for validation."""

    kind: str
    root: Path

    @property
    def manifest_path(self) -> Path:
        return self.root / _MANIFEST_NAMES[self.kind]


@dataclass(frozen=True)
class StandardIssue:
    """One stable, machine-readable standard violation."""

    code: str
    severity: str
    path: str
    message: str
    hint: str = ""


@dataclass(frozen=True)
class ValidationReport:
    """Deterministic validation result for a set of component packages."""

    components: tuple[str, ...]
    issues: tuple[StandardIssue, ...]

    @property
    def errors(self) -> tuple[StandardIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "error")

    @property
    def warnings(self) -> tuple[StandardIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "warning")

    @property
    def status(self) -> str:
        return "BLOCKED" if self.errors else "PASS"

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "components": list(self.components),
            "summary": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
            },
            "issues": [asdict(issue) for issue in self.issues],
        }


def _repository_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _is_contained(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return False
    return True


def _issue(
    repo_root: Path,
    code: str,
    severity: str,
    path: Path,
    message: str,
    hint: str = "",
) -> StandardIssue:
    return StandardIssue(
        code=code,
        severity=severity,
        path=_repository_relative(path, repo_root),
        message=message,
        hint=hint,
    )


def discover_component_targets(
    repo_root: Path,
    changed_paths: Iterable[str | Path],
) -> tuple[ComponentTarget, ...]:
    """Map changed repository paths to their owning component roots."""

    targets: dict[tuple[str, str], ComponentTarget] = {}
    resolved_root = repo_root.resolve()

    for raw_path in changed_paths:
        candidate = Path(raw_path)
        if candidate.is_absolute():
            try:
                relative = candidate.resolve().relative_to(resolved_root)
            except ValueError:
                continue
        else:
            relative = candidate

        parts = relative.parts
        if len(parts) < 2 or parts[0] not in _COMPONENT_PARENTS:
            continue

        kind = _COMPONENT_PARENTS[parts[0]]
        component_root = repo_root / parts[0] / parts[1]
        if not component_root.is_dir():
            continue
        targets[(kind, parts[1])] = ComponentTarget(kind, component_root)

    return tuple(
        targets[key] for key in sorted(targets, key=lambda item: (item[0], item[1]))
    )


def discover_all_component_targets(repo_root: Path) -> tuple[ComponentTarget, ...]:
    """Discover every repository Preset and Extension package."""

    candidates: list[Path] = []
    for parent, kind in _COMPONENT_PARENTS.items():
        parent_dir = repo_root / parent
        if not parent_dir.is_dir():
            continue
        manifest_name = _MANIFEST_NAMES[kind]
        candidates.extend(
            child
            for child in parent_dir.iterdir()
            if child.is_dir() and (child / manifest_name).is_file()
        )
    return discover_component_targets(repo_root, candidates)


def _run_git(repo_root: Path, args: Sequence[str]) -> list[str]:
    process = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if process.returncode != 0:
        detail = process.stderr.strip() or process.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return [line for line in process.stdout.splitlines() if line]


def collect_changed_paths(
    repo_root: Path,
    base_ref: str | None = None,
) -> tuple[str, ...]:
    """Collect committed, staged, unstaged, and untracked changed paths."""

    paths: set[str] = set()
    if base_ref:
        paths.update(
            _run_git(
                repo_root,
                ["diff", "--name-only", "--diff-filter=ACMRD", f"{base_ref}...HEAD"],
            )
        )
    paths.update(
        _run_git(
            repo_root,
            ["diff", "--name-only", "--diff-filter=ACMRD", "HEAD"],
        )
    )

    paths.update(
        _run_git(
            repo_root,
            ["ls-files", "--others", "--exclude-standard"],
        )
    )
    return tuple(sorted(paths))


def _safe_declared_path(
    component_root: Path, raw_path: Any
) -> tuple[Path | None, str | None]:
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None, "must be a non-empty string"
    if "\\" in raw_path:
        return None, "must use '/' separators"

    posix_path = PurePosixPath(raw_path)
    windows_path = PureWindowsPath(raw_path)
    if posix_path.is_absolute() or windows_path.is_absolute() or windows_path.drive:
        return None, "must be relative to the component root"
    if ".." in posix_path.parts:
        return None, "must not contain '..' traversal"

    target = component_root.joinpath(*posix_path.parts)
    try:
        target.resolve(strict=False).relative_to(component_root.resolve())
    except ValueError:
        return None, "resolves outside the component root"
    return target, None


def _load_manifest(
    target: ComponentTarget,
    repo_root: Path,
) -> tuple[dict[str, Any] | None, list[StandardIssue]]:
    manifest_path = target.manifest_path
    if not manifest_path.is_file():
        return None, [
            _issue(
                repo_root,
                "STD001",
                "error",
                manifest_path,
                f"Missing {_MANIFEST_NAMES[target.kind]}.",
            )
        ]

    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return None, [
            _issue(
                repo_root,
                "STD002",
                "error",
                manifest_path,
                f"Manifest is not valid UTF-8 YAML: {exc}",
            )
        ]

    if not isinstance(data, dict):
        return None, [
            _issue(
                repo_root,
                "STD003",
                "error",
                manifest_path,
                "Manifest root must be a YAML mapping.",
            )
        ]

    runtime_issues: list[StandardIssue] = []
    try:
        if target.kind == "extension":
            ExtensionManifest(manifest_path)
        else:
            PresetManifest(manifest_path)
    except (
        ValidationError,
        PresetValidationError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        runtime_issues.append(
            _issue(
                repo_root,
                "STD004",
                "error",
                manifest_path,
                f"Runtime manifest validation failed: {exc}",
            )
        )
    return data, runtime_issues


def _validate_metadata(
    target: ComponentTarget,
    data: dict[str, Any],
    repo_root: Path,
) -> tuple[str | None, list[StandardIssue]]:
    issues: list[StandardIssue] = []
    manifest_path = target.manifest_path

    if data.get("schema_version") != "1.0":
        issues.append(
            _issue(
                repo_root,
                "STD010",
                "error",
                manifest_path,
                "schema_version must be '1.0'.",
            )
        )

    metadata = data.get(target.kind)
    if not isinstance(metadata, dict):
        issues.append(
            _issue(
                repo_root,
                "STD011",
                "error",
                manifest_path,
                f"{target.kind} must be a mapping.",
            )
        )
        return None, issues

    for field in ("id", "name", "version", "description"):
        if not isinstance(metadata.get(field), str) or not metadata[field].strip():
            issues.append(
                _issue(
                    repo_root,
                    "STD012",
                    "error",
                    manifest_path,
                    f"{target.kind}.{field} must be a non-empty string.",
                )
            )

    component_id = metadata.get("id")
    if isinstance(component_id, str) and not _ID_PATTERN.fullmatch(component_id):
        issues.append(
            _issue(
                repo_root,
                "STD013",
                "error",
                manifest_path,
                f"Invalid {target.kind} ID '{component_id}'.",
                "Use lowercase letters, numbers, and single hyphens.",
            )
        )

    if (
        isinstance(component_id, str)
        and (target.kind, target.root.name) not in _SCAFFOLD_ROOTS
        and component_id != target.root.name
    ):
        issues.append(
            _issue(
                repo_root,
                "STD014",
                "error",
                manifest_path,
                f"Manifest ID '{component_id}' does not match directory '{target.root.name}'.",
            )
        )

    version = metadata.get("version")
    if isinstance(version, str):
        try:
            Version(version)
        except InvalidVersion:
            issues.append(
                _issue(
                    repo_root,
                    "STD015",
                    "error",
                    manifest_path,
                    f"Invalid semantic version '{version}'.",
                )
            )
        else:
            if not _SEMVER_PATTERN.fullmatch(version):
                issues.append(
                    _issue(
                        repo_root,
                        "STD015",
                        "error",
                        manifest_path,
                        f"Version '{version}' must use Semantic Versioning X.Y.Z.",
                    )
                )

    requires = data.get("requires")
    if (
        not isinstance(requires, dict)
        or not isinstance(requires.get("speckit_version"), str)
        or not requires["speckit_version"].strip()
    ):
        issues.append(
            _issue(
                repo_root,
                "STD016",
                "error",
                manifest_path,
                "requires.speckit_version must be a non-empty string.",
            )
        )
    else:
        try:
            SpecifierSet(requires["speckit_version"])
        except InvalidSpecifier:
            issues.append(
                _issue(
                    repo_root,
                    "STD016",
                    "error",
                    manifest_path,
                    "requires.speckit_version must be a valid version constraint.",
                )
            )

    return component_id if isinstance(component_id, str) else None, issues


def _validate_package_evidence(
    target: ComponentTarget,
    repo_root: Path,
) -> list[StandardIssue]:
    issues: list[StandardIssue] = []
    for filename in _REQUIRED_PACKAGE_FILES:
        file_path = target.root / filename
        if not file_path.is_file() or not _is_contained(file_path, target.root):
            issues.append(
                _issue(
                    repo_root,
                    "STD020",
                    "error",
                    file_path,
                    f"Component package must include {filename}.",
                )
            )

    test_dir = target.root / "tests"
    has_focused_test = (
        test_dir.is_dir()
        and _is_contained(test_dir, target.root)
        and any(
            path.is_file() and _is_contained(path, target.root)
            for path in test_dir.rglob("test_*.py")
        )
    )
    if not has_focused_test:
        issues.append(
            _issue(
                repo_root,
                "STD021",
                "error",
                test_dir,
                "Component must include at least one focused test_*.py contract test.",
            )
        )
    return issues


def _frontmatter(
    path: Path,
) -> tuple[dict[str, Any] | None, str, str | None]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return None, "", str(exc)

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, content, "missing opening '---'"

    try:
        closing_index = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
    except StopIteration:
        return None, content, "missing closing '---'"

    try:
        data = yaml.safe_load("\n".join(lines[1:closing_index])) or {}
    except yaml.YAMLError as exc:
        return None, content, f"invalid YAML: {exc}"
    if not isinstance(data, dict):
        return None, content, "frontmatter must be a YAML mapping"
    return data, "\n".join(lines[closing_index + 1 :]), None


def _prompt_headings(body: str) -> set[str]:
    return {
        match.group(1).strip().lower()
        for match in re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", body)
    }


def _validate_command_source(
    path: Path,
    repo_root: Path,
) -> list[StandardIssue]:
    issues: list[StandardIssue] = []
    frontmatter, body, frontmatter_error = _frontmatter(path)
    if frontmatter_error:
        issues.append(
            _issue(
                repo_root,
                "STD040",
                "error",
                path,
                f"Command frontmatter is invalid: {frontmatter_error}.",
            )
        )
        return issues

    if (
        not isinstance(frontmatter.get("description"), str)
        or not frontmatter["description"].strip()
    ):
        issues.append(
            _issue(
                repo_root,
                "STD041",
                "error",
                path,
                "Command frontmatter requires a non-empty description.",
            )
        )
    if not body.strip():
        issues.append(
            _issue(
                repo_root,
                "STD042",
                "error",
                path,
                "Command body must not be empty.",
            )
        )
        return issues

    content = path.read_text(encoding="utf-8")
    for token, label in _PLATFORM_TOKENS.items():
        if token in content:
            issues.append(
                _issue(
                    repo_root,
                    "STD043",
                    "error",
                    path,
                    f"Agent-neutral command hard-codes {label}: '{token}'.",
                    "Keep the source platform-neutral and let Integration/Registrar render it.",
                )
            )

    if re.search(r"(?m)(?:^|\\s)(?:/speckit[-.]|\\$speckit-)", body):
        issues.append(
            _issue(
                repo_root,
                "STD044",
                "error",
                path,
                "Command body contains a platform-specific invocation form.",
                "Use __SPECKIT_COMMAND_<NAME>__ for command references.",
            )
        )

    headings = _prompt_headings(body)
    missing = [
        name
        for name, aliases in _PROMPT_SECTION_ALIASES.items()
        if not headings.intersection(aliases)
    ]
    if missing:
        issues.append(
            _issue(
                repo_root,
                "STD045",
                "warning",
                path,
                "Prompt does not expose standard contract sections: "
                + ", ".join(missing)
                + ".",
                "Small commands may merge sections, but must preserve equivalent information.",
            )
        )

    line_count = len(content.splitlines())
    if line_count > 150:
        issues.append(
            _issue(
                repo_root,
                "STD046",
                "warning",
                path,
                f"Prompt is {line_count} lines; prompts over 150 lines require extraction rationale.",
                "Move stable structure or rules into Contract, Template, Schema, or Validator assets.",
            )
        )
    return issues


def _validate_extension(
    target: ComponentTarget,
    data: dict[str, Any],
    component_id: str | None,
    repo_root: Path,
) -> tuple[list[Path], list[StandardIssue]]:
    issues: list[StandardIssue] = []
    command_paths: list[Path] = []
    provides = data.get("provides")
    if not isinstance(provides, dict):
        return command_paths, [
            _issue(
                repo_root,
                "STD030",
                "error",
                target.manifest_path,
                "provides must be a mapping.",
            )
        ]

    commands = provides.get("commands", [])
    if not isinstance(commands, list):
        issues.append(
            _issue(
                repo_root,
                "STD031",
                "error",
                target.manifest_path,
                "provides.commands must be a list.",
            )
        )
        commands = []

    seen_command_names: set[str] = set()
    for command in commands:
        if not isinstance(command, dict):
            issues.append(
                _issue(
                    repo_root,
                    "STD032",
                    "error",
                    target.manifest_path,
                    "Each provides.commands entry must be a mapping.",
                )
            )
            continue

        command_name = command.get("name")
        if isinstance(command_name, str):
            if command_name in seen_command_names:
                issues.append(
                    _issue(
                        repo_root,
                        "STD032",
                        "error",
                        target.manifest_path,
                        f"Duplicate command ID '{command_name}'.",
                    )
                )
            seen_command_names.add(command_name)
        match = (
            _EXTENSION_COMMAND_PATTERN.fullmatch(command_name)
            if isinstance(command_name, str)
            else None
        )
        if not match or (component_id and match.group(1) != component_id):
            issues.append(
                _issue(
                    repo_root,
                    "STD033",
                    "error",
                    target.manifest_path,
                    f"Extension command '{command_name}' must match "
                    f"'speckit.{component_id or '<extension-id>'}.<command>'.",
                )
            )

        if (
            not isinstance(command.get("description"), str)
            or not command["description"].strip()
        ):
            issues.append(
                _issue(
                    repo_root,
                    "STD039",
                    "error",
                    target.manifest_path,
                    f"Command '{command_name}' requires a non-empty description.",
                )
            )

        command_path, path_error = _safe_declared_path(target.root, command.get("file"))
        if path_error or command_path is None:
            issues.append(
                _issue(
                    repo_root,
                    "STD034",
                    "error",
                    target.manifest_path,
                    f"Invalid command file '{command.get('file')}': {path_error}.",
                )
            )
            continue
        if not command_path.is_file():
            issues.append(
                _issue(
                    repo_root,
                    "STD035",
                    "error",
                    command_path,
                    "Manifest-declared command file does not exist.",
                )
            )
            continue
        command_paths.append(command_path)

        expected_filename = (
            f"{command_name}.md" if isinstance(command_name, str) else None
        )
        if expected_filename and command_path.name != expected_filename:
            issues.append(
                _issue(
                    repo_root,
                    "STD036",
                    "error",
                    command_path,
                    f"Command filename must align with its canonical ID: {expected_filename}.",
                )
            )

        aliases = command.get("aliases", [])
        if not isinstance(aliases, list) or any(
            not isinstance(alias, str) for alias in aliases
        ):
            issues.append(
                _issue(
                    repo_root,
                    "STD037",
                    "error",
                    target.manifest_path,
                    f"Aliases for '{command_name}' must be a list of strings.",
                )
            )
        elif component_id:
            for alias in aliases:
                alias_match = _EXTENSION_COMMAND_PATTERN.fullmatch(alias)
                if not alias_match or alias_match.group(1) != component_id:
                    issues.append(
                        _issue(
                            repo_root,
                            "STD038",
                            "error",
                            target.manifest_path,
                            f"Alias '{alias}' must use the extension namespace "
                            f"'speckit.{component_id}.*'.",
                        )
                    )

    configs = provides.get("config", [])
    if configs is not None and not isinstance(configs, list):
        issues.append(
            _issue(
                repo_root,
                "STD039",
                "error",
                target.manifest_path,
                "provides.config must be a list.",
            )
        )
        configs = []
    for config in configs or []:
        if not isinstance(config, dict):
            continue
        template_value = config.get("template")
        if (
            isinstance(template_value, str)
            and Path(template_value).suffix.lower() in _STRUCTURED_SUFFIXES
            and "schema" not in config
        ):
            issues.append(
                _issue(
                    repo_root,
                    "STD039",
                    "error",
                    target.manifest_path,
                    f"Structured config template '{template_value}' requires a schema.",
                )
            )
        for field in ("template", "schema"):
            if field not in config:
                continue
            config_path, path_error = _safe_declared_path(
                target.root, config.get(field)
            )
            if path_error or config_path is None or not config_path.is_file():
                issues.append(
                    _issue(
                        repo_root,
                        "STD035",
                        "error",
                        config_path or target.manifest_path,
                        f"Manifest-declared config {field} is invalid or missing: "
                        f"{config.get(field)!r}.",
                    )
                )

    hooks = data.get("hooks", {})
    if hooks is not None and not isinstance(hooks, dict):
        issues.append(
            _issue(
                repo_root,
                "STD050",
                "error",
                target.manifest_path,
                "hooks must be a mapping.",
            )
        )
        hooks = {}
    for hook_name, raw_entries in (hooks or {}).items():
        entries = raw_entries if isinstance(raw_entries, list) else [raw_entries]
        for entry in entries:
            if not isinstance(entry, dict):
                issues.append(
                    _issue(
                        repo_root,
                        "STD051",
                        "error",
                        target.manifest_path,
                        f"Hook '{hook_name}' must contain mapping entries.",
                    )
                )
                continue
            command = entry.get("command")
            command_match = (
                _CANONICAL_COMMAND_PATTERN.fullmatch(command)
                if isinstance(command, str)
                else None
            )
            if not command_match:
                issues.append(
                    _issue(
                        repo_root,
                        "STD052",
                        "error",
                        target.manifest_path,
                        f"Hook '{hook_name}' must reference a canonical command ID.",
                    )
                )
            if not isinstance(entry.get("optional"), bool):
                issues.append(
                    _issue(
                        repo_root,
                        "STD053",
                        "error",
                        target.manifest_path,
                        f"Hook '{hook_name}' must declare boolean 'optional'.",
                    )
                )
            if (
                not isinstance(entry.get("description"), str)
                or not entry["description"].strip()
            ):
                issues.append(
                    _issue(
                        repo_root,
                        "STD054",
                        "error",
                        target.manifest_path,
                        f"Hook '{hook_name}' must describe its purpose.",
                    )
                )
            priority = entry.get("priority")
            if priority is not None and (
                not isinstance(priority, int)
                or isinstance(priority, bool)
                or priority < 1
            ):
                issues.append(
                    _issue(
                        repo_root,
                        "STD055",
                        "error",
                        target.manifest_path,
                        f"Hook '{hook_name}' priority must be a positive integer.",
                    )
                )

    return command_paths, issues


def _validate_preset(
    target: ComponentTarget,
    data: dict[str, Any],
    repo_root: Path,
) -> tuple[list[Path], list[StandardIssue]]:
    issues: list[StandardIssue] = []
    command_paths: list[Path] = []
    provides = data.get("provides")
    templates = provides.get("templates") if isinstance(provides, dict) else None
    if not isinstance(templates, list) or not templates:
        return command_paths, [
            _issue(
                repo_root,
                "STD060",
                "error",
                target.manifest_path,
                "provides.templates must be a non-empty list.",
            )
        ]

    seen_entries: set[tuple[str, str]] = set()
    for entry in templates:
        if not isinstance(entry, dict):
            issues.append(
                _issue(
                    repo_root,
                    "STD061",
                    "error",
                    target.manifest_path,
                    "Each provides.templates entry must be a mapping.",
                )
            )
            continue
        entry_type = entry.get("type")
        entry_key = (str(entry_type), str(entry.get("name")))
        if entry_key in seen_entries:
            issues.append(
                _issue(
                    repo_root,
                    "STD061",
                    "error",
                    target.manifest_path,
                    f"Duplicate preset entry '{entry_type}:{entry.get('name')}'.",
                )
            )
        seen_entries.add(entry_key)
        entry_type_is_valid = isinstance(entry_type, str) and entry_type in {
            "template",
            "command",
            "script",
        }
        if not entry_type_is_valid:
            issues.append(
                _issue(
                    repo_root,
                    "STD062",
                    "error",
                    target.manifest_path,
                    f"Invalid preset entry type '{entry_type}'.",
                )
            )
        name = entry.get("name")
        if entry_type == "command" and (
            not isinstance(name, str) or not _CANONICAL_COMMAND_PATTERN.fullmatch(name)
        ):
            issues.append(
                _issue(
                    repo_root,
                    "STD063",
                    "error",
                    target.manifest_path,
                    f"Preset command '{name}' must use a canonical speckit.* ID.",
                )
            )
        if (
            not isinstance(entry.get("description"), str)
            or not entry["description"].strip()
        ):
            issues.append(
                _issue(
                    repo_root,
                    "STD063",
                    "error",
                    target.manifest_path,
                    f"Preset entry '{name}' requires a non-empty description.",
                )
            )

        content_path, path_error = _safe_declared_path(target.root, entry.get("file"))
        if path_error or content_path is None:
            issues.append(
                _issue(
                    repo_root,
                    "STD064",
                    "error",
                    target.manifest_path,
                    f"Invalid preset file '{entry.get('file')}': {path_error}.",
                )
            )
            continue
        if not content_path.is_file():
            issues.append(
                _issue(
                    repo_root,
                    "STD065",
                    "error",
                    content_path,
                    "Manifest-declared preset file does not exist.",
                )
            )
            continue

        strategy = entry.get("strategy", "replace")
        valid_strategies = (
            {"replace", "wrap"}
            if entry_type == "script"
            else {"replace", "prepend", "append", "wrap"}
        )
        if not isinstance(strategy, str) or strategy not in valid_strategies:
            issues.append(
                _issue(
                    repo_root,
                    "STD066",
                    "error",
                    target.manifest_path,
                    f"Strategy '{strategy}' is not valid for type '{entry_type}'.",
                )
            )
        if strategy == "wrap":
            placeholder = (
                "$CORE_SCRIPT" if entry_type == "script" else "{CORE_TEMPLATE}"
            )
            try:
                content = content_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                issues.append(
                    _issue(
                        repo_root,
                        "STD065",
                        "error",
                        content_path,
                        f"Preset file is not readable UTF-8: {exc}",
                    )
                )
                continue
            if placeholder not in content:
                issues.append(
                    _issue(
                        repo_root,
                        "STD067",
                        "error",
                        content_path,
                        f"Wrap strategy requires the {placeholder} placeholder.",
                    )
                )

        if entry_type == "command":
            command_paths.append(content_path)
            expected_filename = f"{name}.md" if isinstance(name, str) else None
            if expected_filename and content_path.name != expected_filename:
                issues.append(
                    _issue(
                        repo_root,
                        "STD068",
                        "error",
                        content_path,
                        f"Command filename must align with its canonical ID: {expected_filename}.",
                    )
                )

    structured_outputs = [
        path
        for path in target.root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in _STRUCTURED_SUFFIXES
        and path.name != "preset.yml"
        and "schemas" not in path.parts
    ]
    schemas = (
        list((target.root / "schemas").rglob("*.json"))
        if (target.root / "schemas").is_dir()
        else []
    )
    if structured_outputs and not schemas:
        issues.append(
            _issue(
                repo_root,
                "STD069",
                "warning",
                structured_outputs[0],
                "Structured artifact templates exist without a top-level schemas/ contract.",
            )
        )

    return command_paths, issues


def _validate_schema_files(
    target: ComponentTarget,
    repo_root: Path,
) -> list[StandardIssue]:
    issues: list[StandardIssue] = []
    schema_dirs = [
        target.root / "schemas",
        target.root / "templates" / "schemas",
    ]
    for schema_dir in schema_dirs:
        if not schema_dir.is_dir():
            continue
        for schema_path in sorted(schema_dir.rglob("*.json")):
            if not _is_contained(schema_path, target.root):
                issues.append(
                    _issue(
                        repo_root,
                        "STD074",
                        "error",
                        schema_path,
                        "Schema symlink resolves outside the component root.",
                    )
                )
                continue
            try:
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                issues.append(
                    _issue(
                        repo_root,
                        "STD070",
                        "error",
                        schema_path,
                        f"Schema is not valid UTF-8 JSON: {exc}",
                    )
                )
                continue
            if not isinstance(schema, dict):
                issues.append(
                    _issue(
                        repo_root,
                        "STD071",
                        "error",
                        schema_path,
                        "Schema root must be a JSON object.",
                    )
                )
                continue
            if not isinstance(schema.get("$id"), str) or not schema["$id"].strip():
                issues.append(
                    _issue(
                        repo_root,
                        "STD072",
                        "error",
                        schema_path,
                        "Schema requires a stable, non-empty $id.",
                    )
                )
            if "additionalProperties" not in schema:
                issues.append(
                    _issue(
                        repo_root,
                        "STD073",
                        "error",
                        schema_path,
                        "Schema must declare its additionalProperties policy.",
                    )
                )
    return issues


def validate_component(
    target: ComponentTarget,
    repo_root: Path,
) -> tuple[StandardIssue, ...]:
    """Validate one component package without network access or mutation."""

    data, issues = _load_manifest(target, repo_root)
    if data is None:
        return tuple(issues)

    component_id, metadata_issues = _validate_metadata(target, data, repo_root)
    issues.extend(metadata_issues)
    issues.extend(_validate_package_evidence(target, repo_root))

    if target.kind == "extension":
        command_paths, kind_issues = _validate_extension(
            target, data, component_id, repo_root
        )
    else:
        command_paths, kind_issues = _validate_preset(target, data, repo_root)
    issues.extend(kind_issues)

    for command_path in sorted(set(command_paths)):
        issues.extend(_validate_command_source(command_path, repo_root))
    issues.extend(_validate_schema_files(target, repo_root))

    return tuple(
        sorted(
            issues,
            key=lambda issue: (
                issue.path,
                0 if issue.severity == "error" else 1,
                issue.code,
                issue.message,
            ),
        )
    )


def validate_targets(
    targets: Iterable[ComponentTarget],
    repo_root: Path,
) -> ValidationReport:
    """Validate selected targets and return a deterministic aggregate report."""

    normalized_targets = tuple(
        sorted(
            set(targets),
            key=lambda target: (target.kind, target.root.as_posix()),
        )
    )
    issues = tuple(
        issue
        for target in normalized_targets
        for issue in validate_component(target, repo_root)
    )
    return ValidationReport(
        components=tuple(
            _repository_relative(target.root, repo_root)
            for target in normalized_targets
        ),
        issues=issues,
    )


def format_text_report(report: ValidationReport) -> str:
    """Render a concise report suitable for local terminals and CI logs."""

    lines = [
        f"Component standard: {report.status}",
        f"Components: {len(report.components)}",
        f"Errors: {len(report.errors)}; Warnings: {len(report.warnings)}",
    ]
    if not report.components:
        lines.append("No touched Preset or Extension components.")
        return "\n".join(lines)

    for issue in report.issues:
        lines.append(
            f"{issue.severity.upper()} {issue.code} {issue.path}: {issue.message}"
        )
        if issue.hint:
            lines.append(f"  Hint: {issue.hint}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate touched Preset/Extension packages against the coding standard."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Component roots or files. Defaults to working-tree changes.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: current directory).",
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--changed-from",
        metavar="GIT_REF",
        help="Validate components touched between GIT_REF and HEAD.",
    )
    selection.add_argument(
        "--all",
        action="store_true",
        help="Validate every repository Preset and Extension.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Report format.",
    )
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Return a failure exit code when warnings are present.",
    )
    return parser


def _print_selection_error(output_format: str, message: str) -> None:
    if output_format == "json":
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "components": [],
                    "summary": {"errors": 1, "warnings": 0},
                    "issues": [
                        {
                            "code": "STD000",
                            "severity": "error",
                            "path": "",
                            "message": message,
                            "hint": "",
                        }
                    ],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(f"Component standard: ERROR\n{message}", file=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    if args.all:
        targets = discover_all_component_targets(repo_root)
    else:
        try:
            paths = (
                tuple(args.paths)
                if args.paths
                else collect_changed_paths(repo_root, args.changed_from)
            )
        except RuntimeError as exc:
            _print_selection_error(args.format, str(exc))
            return 2
        targets = discover_component_targets(repo_root, paths)
        if args.paths and not targets:
            _print_selection_error(
                args.format,
                "No Preset or Extension component matched the supplied paths.",
            )
            return 2

    report = validate_targets(targets, repo_root)
    if args.format == "json":
        print(json.dumps(report.as_dict(), indent=2, ensure_ascii=False))
    else:
        print(format_text_report(report))
    return int(bool(report.errors or (args.warnings_as_errors and report.warnings)))


__all__ = [
    "ComponentTarget",
    "StandardIssue",
    "ValidationReport",
    "collect_changed_paths",
    "discover_all_component_targets",
    "discover_component_targets",
    "format_text_report",
    "main",
    "validate_component",
    "validate_targets",
]
