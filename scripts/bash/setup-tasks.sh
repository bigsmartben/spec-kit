#!/usr/bin/env bash

set -e

# Parse command line arguments
JSON_MODE=false

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --help|-h)
            echo "Usage: $0 [--json]"
            echo "  --json    Output results in JSON format"
            echo "  --help    Show this help message"
            exit 0
            ;;
        *) echo "ERROR: Unknown option '$arg'" >&2; exit 1 ;;
    esac
done

# Source common functions
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Get feature paths
_paths_output=$(get_feature_paths) || { echo "ERROR: Failed to resolve feature paths" >&2; exit 1; }
eval "$_paths_output"
unset _paths_output

# Validate the frozen Specify contract.
require_nonempty() {
    local path="$1"
    local name="$2"
    if [[ ! -f "$path" ]]; then
        echo "ERROR: $name not found in $FEATURE_DIR" >&2
        echo "Run $(format_speckit_command specify "$REPO_ROOT") first to create the frozen requirement contract." >&2
        return 1
    fi
    if [[ ! -s "$path" ]]; then
        echo "ERROR: $name is empty in $FEATURE_DIR" >&2
        echo "Rerun $(format_speckit_command specify "$REPO_ROOT") to regenerate $name." >&2
        return 1
    fi
}

require_nonempty "$FEATURE_SPEC" "spec.md"
require_nonempty "$PROTOTYPE" "prototype.html"
require_nonempty "$QUICKSTART" "quickstart.md"

# Build available docs list
docs=("spec.md" "prototype.html" "quickstart.md")

# Resolve tasks template through override stack
TASKS_TEMPLATE=$(resolve_template "tasks-template" "$REPO_ROOT") || true
if TASKS_TEMPLATE_CONTENT=$(resolve_template_content "tasks-template" "$REPO_ROOT"; status=$?; printf x; exit "$status"); then
    TASKS_TEMPLATE_CONTENT="${TASKS_TEMPLATE_CONTENT%x}"
else
    echo "ERROR: Could not resolve required tasks-template from the template override stack for $REPO_ROOT" >&2
    echo "Template 'tasks-template' was not found in any supported location (overrides, presets, extensions, or shared core). Add an override at .specify/templates/overrides/tasks-template.md, or run 'specify init' / reinstall shared infra to restore the core .specify/templates/tasks-template.md template." >&2
    exit 1
fi

# Output results
if $JSON_MODE; then
    if has_jq; then
        if [[ ${#docs[@]} -eq 0 ]]; then
            json_docs="[]"
        else
            json_docs=$(printf '%s\n' "${docs[@]}" | jq -R . | jq -s .)
        fi
        jq -cn \
            --arg feature_dir "$FEATURE_DIR" \
            --arg feature_spec "$FEATURE_SPEC" \
            --arg prototype "$PROTOTYPE" \
            --arg quickstart "$QUICKSTART" \
            --argjson docs "$json_docs" \
            --arg tasks_template "${TASKS_TEMPLATE:-}" \
            --arg tasks_template_content "$TASKS_TEMPLATE_CONTENT" \
            '{FEATURE_DIR:$feature_dir,FEATURE_SPEC:$feature_spec,PROTOTYPE:$prototype,QUICKSTART:$quickstart,AVAILABLE_DOCS:$docs,TASKS_TEMPLATE:$tasks_template,TASKS_TEMPLATE_CONTENT:$tasks_template_content}'
    else
        if [[ ${#docs[@]} -eq 0 ]]; then
            json_docs="[]"
        else
            json_docs=$(for d in "${docs[@]}"; do printf '"%s",' "$(json_escape "$d")"; done)
            json_docs="[${json_docs%,}]"
        fi
        printf '{"FEATURE_DIR":"%s","FEATURE_SPEC":"%s","PROTOTYPE":"%s","QUICKSTART":"%s","AVAILABLE_DOCS":%s,"TASKS_TEMPLATE":"%s","TASKS_TEMPLATE_CONTENT":"%s"}\n' \
            "$(json_escape "$FEATURE_DIR")" "$(json_escape "$FEATURE_SPEC")" "$(json_escape "$PROTOTYPE")" "$(json_escape "$QUICKSTART")" "$json_docs" "$(json_escape "${TASKS_TEMPLATE:-}")" "$(json_escape "$TASKS_TEMPLATE_CONTENT")"
    fi
else
    echo "FEATURE_DIR: $FEATURE_DIR"
    echo "TASKS_TEMPLATE: ${TASKS_TEMPLATE:-not found}"
    echo "AVAILABLE_DOCS:"
    check_file "$FEATURE_SPEC" "spec.md"
    check_file "$PROTOTYPE" "prototype.html"
    check_file "$QUICKSTART" "quickstart.md"
fi
