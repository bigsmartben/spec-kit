#!/usr/bin/env bash
# update-agent-context.sh
#
# Refresh the managed Spec Kit section in the coding agent's context file(s)
# (e.g. CLAUDE.md, .github/copilot-instructions.md, AGENTS.md).
#
# Reads `context_files` or `context_file`, plus `context_markers.{start,end}`, from the
# agent-context extension config:
#   .specify/extensions/agent-context/agent-context-config.yml
#
# Usage: update-agent-context.sh [feature_directory]
#
# When `feature_directory` is omitted, the script derives it from
# `.specify/feature.json` (written by /speckit-specify). It safely discovers the
# most recently modified specs/**/spec.md when the recorded feature is absent.

set -euo pipefail

PROJECT_ROOT="$(pwd)"
EXT_CONFIG="$PROJECT_ROOT/.specify/extensions/agent-context/agent-context-config.yml"
DEFAULT_START="<!-- SPECKIT START -->"
DEFAULT_END="<!-- SPECKIT END -->"

if [[ ! -f "$EXT_CONFIG" ]]; then
  echo "agent-context: $EXT_CONFIG not found; nothing to do." >&2
  exit 0
fi

# Locate a Python 3 interpreter with PyYAML available.
_python=""
_python_candidates=()
[[ -n "${SPECKIT_PYTHON:-}" ]] && _python_candidates+=("$SPECKIT_PYTHON")
_python_candidates+=("python3" "python")
for _candidate in "${_python_candidates[@]}"; do
  if command -v "$_candidate" >/dev/null 2>&1 \
    && "$_candidate" - <<'PY' >/dev/null 2>&1
import sys
try:
    import yaml  # noqa: F401
except ImportError:
    sys.exit(1)
sys.exit(0 if sys.version_info[0] == 3 else 1)
PY
  then
    _python="$_candidate"
    break
  fi
done
unset _candidate _python_candidates

if [[ -z "$_python" ]]; then
  echo "agent-context: Python 3 with PyYAML not found on PATH; skipping update." >&2
  echo "  To resolve: pip install pyyaml (or install it into the environment used by python3)." >&2
  exit 0
fi
_case_insensitive_context_files=0
case "$(uname -s 2>/dev/null || true)" in
  MINGW*|MSYS*|CYGWIN*) _case_insensitive_context_files=1 ;;
esac

# Parse extension config once; emit context files as JSON, followed by marker strings.
#
# NOTE (bash 3.2 / macOS portability): the embedded Python heredocs below run
# inside $(...) command substitution. bash 3.2 (the system /bin/bash on macOS)
# mis-parses a single-quote/apostrophe in a heredoc body nested in $(...),
# failing with "unexpected EOF while looking for matching `''". Keep these
# $(...)-nested heredoc bodies free of apostrophes (use double quotes in Python
# string literals and avoid contractions in comments).
if ! _raw_opts="$("$_python" - "$EXT_CONFIG" "$_case_insensitive_context_files" "$PROJECT_ROOT" <<'PY'
import json
import sys
try:
    import yaml
except ImportError:
    print(
        "agent-context: PyYAML is required to parse extension config but is not available "
        "in the current Python environment.\n"
        "  To resolve: pip install pyyaml (or install it into the environment used by python3).\n"
        "  Context file will not be updated until PyYAML is importable.",
        file=sys.stderr,
    )
    sys.exit(2)
try:
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
except Exception as exc:
    print(
        f"agent-context: unable to parse {sys.argv[1]} ({exc}); cannot update context.",
        file=sys.stderr,
    )
    sys.exit(2)
if not isinstance(data, dict):
    data = {}
def get_str(obj, *keys):
    node = obj
    for k in keys:
        if isinstance(node, dict) and k in node:
            node = node[k]
        else:
            return ""
    return node if isinstance(node, str) else ""
context_files = []
seen_context_files = set()
case_insensitive = sys.argv[2] == "1" or sys.platform.startswith(("win32", "cygwin"))
def add_context_file(value):
    if not isinstance(value, str):
        return
    candidate = value.strip()
    if not candidate:
        return
    key = candidate.casefold() if case_insensitive else candidate
    if key in seen_context_files:
        return
    context_files.append(candidate)
    seen_context_files.add(key)
raw_files = data.get("context_files")
if isinstance(raw_files, list):
    for value in raw_files:
        add_context_file(value)
if not context_files:
    add_context_file(get_str(data, "context_file"))
if not context_files:
    # Self-seed: the agent-context extension manages its own lifecycle, so when
    # its config declares no target, it derives one from the active integration
    # recorded in init-options.json, mapped through the bundled
    # agent-context-defaults.json file. This is independent of the Specify CLI
    # by design; nothing here imports specify_cli.
    project_root = sys.argv[3] if len(sys.argv) > 3 else "."
    integration_key = ""
    try:
        with open(
            f"{project_root}/.specify/init-options.json", "r", encoding="utf-8"
        ) as fh:
            opts = json.load(fh)
        if isinstance(opts, dict):
            value = opts.get("integration") or opts.get("ai") or ""
            integration_key = value if isinstance(value, str) else ""
    except Exception:
        integration_key = ""
    if integration_key:
        defaults_path = (
            f"{project_root}/.specify/extensions/agent-context/"
            "agent-context-defaults.json"
        )
        mapping = {}
        try:
            with open(defaults_path, "r", encoding="utf-8") as fh:
                loaded = json.load(fh)
            agents = loaded.get("agents", {}) if isinstance(loaded, dict) else {}
            mapping = agents if isinstance(agents, dict) else {}
        except Exception:
            print(
                "agent-context: unable to read %s; cannot self-seed the context "
                "file. Set context_file in the extension config." % defaults_path,
                file=sys.stderr,
            )
            mapping = {}
        add_context_file(mapping.get(integration_key, "") or "")
        if not context_files:
            print(
                "agent-context: no default context file is known for integration "
                "%s. Set context_file in the extension config to choose one."
                % integration_key,
                file=sys.stderr,
            )
print(json.dumps(context_files))
print(get_str(data, "context_markers", "start"))
print(get_str(data, "context_markers", "end"))
PY
)"; then
  echo "agent-context: skipping update (see above for details)." >&2
  exit 0
fi

_opts_lines=()
while IFS= read -r _line || [[ -n "$_line" ]]; do
  _opts_lines+=("$_line")
done < <(printf '%s\n' "$_raw_opts")
if (( ${#_opts_lines[@]} < 1 )); then
  echo "agent-context: malformed config parser output; expected at least the context_files line, got ${#_opts_lines[@]}; skipping update." >&2
  exit 0
fi
# The marker lines may be absent: the $(...) capture above strips trailing
# newlines, so blank markers (the config omitting context_markers and relying on
# defaults) collapse the 3-line output to fewer lines. Default them to empty here
# and let the DEFAULT_START/END substitution below fill them in, matching the
# Python and PowerShell ports.
CONTEXT_FILES_JSON="${_opts_lines[0]}"
MARKER_START="${_opts_lines[1]:-}"
MARKER_END="${_opts_lines[2]:-}"

if ! _context_files_raw="$("$_python" - "$CONTEXT_FILES_JSON" <<'PY'
import json
import sys
try:
    data = json.loads(sys.argv[1])
except Exception:
    data = []
if not isinstance(data, list):
    data = []
for value in data:
    if isinstance(value, str) and value:
        print(value)
PY
)"; then
  echo "agent-context: malformed context_files parser output; skipping update." >&2
  exit 0
fi

CONTEXT_FILES=()
while IFS= read -r _line || [[ -n "$_line" ]]; do
  [[ -n "$_line" ]] && CONTEXT_FILES+=("$_line")
done < <(printf '%s\n' "$_context_files_raw")

if (( ${#CONTEXT_FILES[@]} == 0 )); then
  echo "agent-context: context_files/context_file not set in extension config; nothing to do." >&2
  exit 0
fi

for CONTEXT_FILE in "${CONTEXT_FILES[@]}"; do
  # Reject absolute paths, backslash separators, and '..' path segments in context files
  if [[ "$CONTEXT_FILE" == /* ]] || [[ "$CONTEXT_FILE" =~ ^[A-Za-z]: ]]; then
    echo "agent-context: context files must be project-relative paths; got '$CONTEXT_FILE'." >&2
    exit 1
  fi
  if [[ "$CONTEXT_FILE" == *\\* ]]; then
    echo "agent-context: context files must not contain backslash separators; got '$CONTEXT_FILE'." >&2
    exit 1
  fi
  IFS='/' read -ra _cf_parts <<< "$CONTEXT_FILE"
  for _seg in "${_cf_parts[@]}"; do
    if [[ "$_seg" == ".." ]]; then
      echo "agent-context: context files must not contain '..' path segments; got '$CONTEXT_FILE'." >&2
      exit 1
    fi
  done
  if ! "$_python" - "$PROJECT_ROOT" "$CONTEXT_FILE" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
target = (root / sys.argv[2]).resolve(strict=False)
try:
    target.relative_to(root)
except ValueError:
    sys.exit(1)
PY
  then
    echo "agent-context: context file path resolves outside the project root; got '$CONTEXT_FILE'." >&2
    exit 1
  fi
done
unset _cf_parts _seg

[[ -z "$MARKER_START" ]] && MARKER_START="$DEFAULT_START"
[[ -z "$MARKER_END"   ]] && MARKER_END="$DEFAULT_END"

FEATURE_DIRECTORY="${1:-}"
ARTIFACT_PATHS_JSON="$("$_python" - "$PROJECT_ROOT" "$FEATURE_DIRECTORY" <<'PY'
import json
import re
import sys
from pathlib import Path
from stat import S_ISREG

project_root, explicit_feature = sys.argv[1:3]
artifact_names = ("spec.md", "prototype.html", "quickstart.md", "tasks.md")
root = Path(project_root).resolve()

def feature_dir_from_value(value):
    normalized = value.replace("\\", "/").rstrip("/")
    if not normalized:
        return None
    if sys.platform.startswith("win") and re.match(r"^/[A-Za-z]/", normalized):
        normalized = normalized[1].upper() + ":/" + normalized[3:]
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized):
        return Path(normalized)
    return Path(project_root) / normalized

def display_path(candidate, contained):
    resolved = candidate.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return "" if contained else resolved.as_posix()

def paths_for_feature(feature_dir, contained):
    paths = []
    for name in artifact_names:
        candidate = feature_dir / name
        try:
            if not candidate.is_file():
                continue
            displayed = display_path(candidate, contained)
        except (OSError, ValueError):
            continue
        if displayed:
            paths.append(displayed)
    return paths

feature_value = explicit_feature
if not feature_value:
    feature_json = root / ".specify" / "feature.json"
    if feature_json.is_file():
        try:
            with open(feature_json, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            value = data.get("feature_directory", "") if isinstance(data, dict) else ""
            feature_value = value if isinstance(value, str) else ""
        except Exception:
            feature_value = ""

feature_dir = feature_dir_from_value(feature_value)
if feature_dir is not None:
    paths = paths_for_feature(feature_dir, False)
    if any(Path(path).name == "spec.md" for path in paths):
        print(json.dumps(paths))
        raise SystemExit(0)

candidates = []
for candidate in (root / "specs").rglob("spec.md"):
    try:
        resolved = candidate.resolve()
        relative = resolved.relative_to(root)
    except (OSError, ValueError):
        continue
    try:
        mode = candidate.stat().st_mode
    except (FileNotFoundError, NotADirectoryError):
        continue
    if S_ISREG(mode):
        candidates.append((candidate, relative))
candidates.sort(key=lambda pair: pair[0].stat().st_mtime, reverse=True)
paths = []
if candidates:
    discovered, relative = candidates[0]
    paths = [relative.as_posix()]
    for name in artifact_names[1:]:
        companion = discovered.parent / name
        try:
            displayed = display_path(companion, True) if companion.is_file() else ""
        except (OSError, ValueError):
            displayed = ""
        if displayed:
            paths.append(displayed)
print(json.dumps(paths))
PY
)"

for CONTEXT_FILE in "${CONTEXT_FILES[@]}"; do
  CTX_PATH="$PROJECT_ROOT/$CONTEXT_FILE"
  mkdir -p "$(dirname "$CTX_PATH")"

  "$_python" - "$CTX_PATH" "$MARKER_START" "$MARKER_END" "$ARTIFACT_PATHS_JSON" <<'PY'
import json
import os
import re
import sys

ctx_path, start, end, artifact_paths_json = sys.argv[1:5]
try:
    artifact_paths = json.loads(artifact_paths_json)
except Exception:
    artifact_paths = []
if not isinstance(artifact_paths, list):
    artifact_paths = []
section_lines = [
    start,
    "Use the active Spec Kit feature artifacts as the product contract:",
]
section_lines.extend(
    f"- `{path}`" for path in artifact_paths if isinstance(path, str)
)
section_lines.append(end)
section = "\n".join(section_lines) + "\n"


def ensure_mdc_frontmatter(content):
    """Ensure ``.mdc`` content has YAML frontmatter with ``alwaysApply: true``.

    Cursor only auto-loads ``.mdc`` rule files that carry frontmatter with
    ``alwaysApply: true``. Prepend it when missing, or repair the value while
    preserving any existing frontmatter comments/formatting.
    """
    leading_ws = len(content) - len(content.lstrip())
    leading = content[:leading_ws]
    stripped = content[leading_ws:]

    if not stripped.startswith("---"):
        return "---\nalwaysApply: true\n---\n\n" + content

    match = re.match(
        r"^(---[ \t]*\r?\n)(.*?)(\r?\n---[ \t]*)(\r?\n|$)(.*)",
        stripped,
        re.DOTALL,
    )
    if not match:
        return "---\nalwaysApply: true\n---\n\n" + content

    opening, fm_text, closing, sep, rest = match.groups()
    newline = "\r\n" if "\r\n" in opening else "\n"

    if re.search(r"(?m)^[ \t]*alwaysApply[ \t]*:[ \t]*true[ \t]*(?:#.*)?$", fm_text):
        return content

    if re.search(r"(?m)^[ \t]*alwaysApply[ \t]*:", fm_text):
        fm_text = re.sub(
            r"(?m)^([ \t]*)alwaysApply[ \t]*:.*?([ \t]*(?:#.*)?)$",
            r"\1alwaysApply: true\2",
            fm_text,
            count=1,
        )
    elif fm_text.strip():
        fm_text = fm_text + newline + "alwaysApply: true"
    else:
        fm_text = "alwaysApply: true"

    return f"{leading}{opening}{fm_text}{closing}{sep}{rest}"


if os.path.exists(ctx_path):
    with open(ctx_path, "r", encoding="utf-8-sig") as fh:
        content = fh.read()
    s = content.find(start)
    e = content.find(end, s if s != -1 else 0)
    if s != -1 and e != -1 and e > s:
        end_of_marker = e + len(end)
        if end_of_marker < len(content) and content[end_of_marker] == "\r":
            end_of_marker += 1
        if end_of_marker < len(content) and content[end_of_marker] == "\n":
            end_of_marker += 1
        new_content = content[:s] + section + content[end_of_marker:]
    elif s != -1:
        new_content = content[:s] + section
    elif e != -1:
        end_of_marker = e + len(end)
        if end_of_marker < len(content) and content[end_of_marker] == "\r":
            end_of_marker += 1
        if end_of_marker < len(content) and content[end_of_marker] == "\n":
            end_of_marker += 1
        new_content = section + content[end_of_marker:]
    else:
        if content and not content.endswith("\n"):
            content += "\n"
        new_content = (content + "\n" + section) if content else section
else:
    new_content = section

new_content = new_content.replace("\r\n", "\n").replace("\r", "\n")
if ctx_path.casefold().endswith(".mdc"):
    new_content = ensure_mdc_frontmatter(new_content)
with open(ctx_path, "wb") as fh:
    fh.write(new_content.encode("utf-8"))
PY

  echo "agent-context: updated $CONTEXT_FILE"
done
