#!/usr/bin/env python3
"""Consolidated prerequisite checking script."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from common import (
        FeaturePaths,
        TemplateResolutionError,
        format_speckit_command,
        get_feature_paths,
        resolve_template_content,
    )
except ImportError:  # pragma: no cover - direct execution from unusual cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import (
        FeaturePaths,
        TemplateResolutionError,
        format_speckit_command,
        get_feature_paths,
        resolve_template_content,
    )


def _json_line(payload: object) -> str:
    # ASCII escapes keep the JSON intact on a legacy Windows stdout code page.
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":")) + "\n"


HELP_TEXT = """Usage: check_prerequisites.py [OPTIONS]

Consolidated prerequisite checking for Spec-Driven Development workflow.

OPTIONS:
  --json              Output in JSON format
  --require-spec      Require spec.md to exist (for analysis phase)
  --require-contract  Require spec.md, prototype.html, and quickstart.md
  --require-tasks     Require tasks.md to exist (for implementation phase)
  --include-tasks     Include tasks.md in AVAILABLE_DOCS list
  --paths-only        Only output path variables (no prerequisite validation)
  --template NAME     Include composed template content in JSON output
  --help, -h          Show this help message

EXAMPLES:
  # Check the frozen Specify contract
  ./check_prerequisites.py --json --require-contract

  # Check implementation prerequisites
  ./check_prerequisites.py --json --require-contract --require-tasks --include-tasks

  # Get feature paths only (no validation)
  ./check_prerequisites.py --paths-only

"""


@dataclass(frozen=True)
class Args:
    json_mode: bool = False
    require_spec: bool = False
    require_contract: bool = False
    require_tasks: bool = False
    include_tasks: bool = False
    paths_only: bool = False
    template_name: str | None = None


def _parse_args(argv: list[str]) -> Args:
    json_mode = False
    require_spec = False
    require_contract = False
    require_tasks = False
    include_tasks = False
    paths_only = False
    template_name = None

    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--json":
            json_mode = True
        elif arg == "--require-spec":
            require_spec = True
        elif arg == "--require-contract":
            require_contract = True
        elif arg == "--require-tasks":
            require_tasks = True
        elif arg == "--include-tasks":
            include_tasks = True
        elif arg == "--paths-only":
            paths_only = True
        elif arg == "--template":
            index += 1
            if index >= len(argv):
                print(
                    "ERROR: --template requires a template name",
                    file=sys.stderr,
                )
                raise SystemExit(1)
            template_name = argv[index]
        elif arg in {"--help", "-h"}:
            sys.stdout.write(HELP_TEXT)
            raise SystemExit(0)
        else:
            print(
                f"ERROR: Unknown option '{arg}'. Use --help for usage information.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        index += 1

    return Args(
        json_mode=json_mode,
        require_spec=require_spec,
        require_contract=require_contract,
        require_tasks=require_tasks,
        include_tasks=include_tasks,
        paths_only=paths_only,
        template_name=template_name,
    )


def _available_docs(paths: FeaturePaths, include_tasks: bool) -> list[str]:
    docs: list[str] = []
    if paths.feature_spec.is_file():
        docs.append("spec.md")
    if paths.prototype.is_file():
        docs.append("prototype.html")
    if paths.quickstart.is_file():
        docs.append("quickstart.md")
    if include_tasks and paths.tasks.is_file():
        docs.append("tasks.md")
    return docs


def _print_paths_only(paths: FeaturePaths, json_mode: bool) -> None:
    if json_mode:
        sys.stdout.write(
            _json_line(
                {
                    "REPO_ROOT": str(paths.repo_root),
                    "BRANCH": paths.current_branch,
                    "FEATURE_DIR": str(paths.feature_dir),
                    "FEATURE_SPEC": str(paths.feature_spec),
                    "PROTOTYPE": str(paths.prototype),
                    "QUICKSTART": str(paths.quickstart),
                    "TASKS": str(paths.tasks),
                }
            )
        )
        return

    print(f"REPO_ROOT: {paths.repo_root}")
    print(f"BRANCH: {paths.current_branch}")
    print(f"FEATURE_DIR: {paths.feature_dir}")
    print(f"FEATURE_SPEC: {paths.feature_spec}")
    print(f"PROTOTYPE: {paths.prototype}")
    print(f"QUICKSTART: {paths.quickstart}")
    print(f"TASKS: {paths.tasks}")


def _status_marker(ok: bool) -> str:
    """Return the status glyph, downgraded to ASCII when stdout cannot encode it.

    On Windows sys.stdout falls back to the ANSI code page whenever it is not a
    console - a pipe or a file redirect, which is how agents and workflow steps
    invoke these scripts - and U+2713 is unencodable in cp1252, so printing it
    raised UnicodeEncodeError and aborted the report right after
    "AVAILABLE_DOCS:". "[OK]"/"[FAIL]" is the ASCII rendering these markers
    already have in-tree: see Test-FileExists in scripts/powershell/common.ps1
    and normalize_status_text in tests/parity_helpers.py.
    """
    glyph = "✓" if ok else "✗"
    try:
        glyph.encode(getattr(sys.stdout, "encoding", None) or "utf-8")
    except (LookupError, UnicodeEncodeError):
        return "[OK]" if ok else "[FAIL]"
    return glyph


def _check_file(path: Path, description: str) -> None:
    print(f"  {_status_marker(path.is_file())} {description}")


def _print_text_results(paths: FeaturePaths, include_tasks: bool) -> None:
    print(f"FEATURE_DIR:{paths.feature_dir}")
    print("AVAILABLE_DOCS:")
    _check_file(paths.feature_spec, "spec.md")
    _check_file(paths.prototype, "prototype.html")
    _check_file(paths.quickstart, "quickstart.md")
    if include_tasks:
        _check_file(paths.tasks, "tasks.md")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(list(argv if argv is not None else sys.argv[1:]))

    try:
        paths = get_feature_paths(
            no_persist=args.paths_only,
            script_file=Path(__file__),
        )
    except SystemExit as exc:
        if exc.code == 0:
            return 0
        print("ERROR: Failed to resolve feature paths", file=sys.stderr)
        return int(exc.code) if isinstance(exc.code, int) else 1

    if args.paths_only:
        _print_paths_only(paths, args.json_mode)
        return 0

    if not paths.feature_dir.is_dir():
        print(f"ERROR: Feature directory not found: {paths.feature_dir}", file=sys.stderr)
        print(
            f"Run {format_speckit_command('specify', paths.repo_root)} first to create the feature structure.",
            file=sys.stderr,
        )
        return 1

    if args.require_spec and not paths.feature_spec.is_file():
        print(f"ERROR: spec.md not found in {paths.feature_dir}", file=sys.stderr)
        print(
            f"Run {format_speckit_command('specify', paths.repo_root)} first to create the feature specification.",
            file=sys.stderr,
        )
        return 1

    if args.require_contract:
        required = (
            (paths.feature_spec, "spec.md"),
            (paths.prototype, "prototype.html"),
            (paths.quickstart, "quickstart.md"),
        )
        for path, name in required:
            if not path.is_file():
                print(f"ERROR: {name} not found in {paths.feature_dir}", file=sys.stderr)
                print(
                    f"Run {format_speckit_command('specify', paths.repo_root)} "
                    "first to create the frozen requirement contract.",
                    file=sys.stderr,
                )
                return 1
            if path.stat().st_size == 0:
                print(f"ERROR: {name} is empty in {paths.feature_dir}", file=sys.stderr)
                print(
                    f"Rerun {format_speckit_command('specify', paths.repo_root)} "
                    f"to regenerate {name}.",
                    file=sys.stderr,
                )
                return 1

    if args.require_tasks and not paths.tasks.is_file():
        print(f"ERROR: tasks.md not found in {paths.feature_dir}", file=sys.stderr)
        print(
            f"Run {format_speckit_command('tasks', paths.repo_root)} first to create the task list.",
            file=sys.stderr,
        )
        return 1

    docs = _available_docs(paths, args.include_tasks)
    template_content = None
    if args.template_name:
        try:
            template_content = resolve_template_content(
                args.template_name, paths.repo_root
            )
        except TemplateResolutionError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        if template_content is None:
            print(
                f"ERROR: Could not resolve required {args.template_name} from "
                f"the template override stack for {paths.repo_root}",
                file=sys.stderr,
            )
            return 1

    if args.json_mode:
        payload: dict[str, object] = {
            "FEATURE_DIR": str(paths.feature_dir),
            "AVAILABLE_DOCS": docs,
        }
        if args.template_name:
            payload["TEMPLATE_CONTENT"] = template_content
        sys.stdout.write(
            _json_line(payload)
        )
    else:
        _print_text_results(paths, args.include_tasks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
