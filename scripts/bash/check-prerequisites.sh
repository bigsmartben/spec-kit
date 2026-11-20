#!/usr/bin/env bash

# Consolidated prerequisite checking script
#
# This script provides unified prerequisite checking for Spec-Driven Development workflow.
# It replaces the functionality previously spread across multiple scripts.
#
# Usage: ./check-prerequisites.sh [OPTIONS]
#
# OPTIONS:
#   --json              Output in JSON format
#   --require-spec      Require spec.md to exist (for analysis phase)
#   --require-contract  Require spec.md, prototype.html, and quickstart.md
#   --require-tasks     Require tasks.md to exist (for implementation phase)
#   --include-tasks     Include tasks.md in AVAILABLE_DOCS list
#   --paths-only        Only output path variables (no validation)
#   --template NAME     Include composed template content in JSON output
#   --help, -h          Show help message
#
# OUTPUTS:
#   JSON mode: {"FEATURE_DIR":"...", "AVAILABLE_DOCS":["..."]}
#   Text mode: FEATURE_DIR:... \n AVAILABLE_DOCS: \n ✓/✗ file.md
#   Paths only: REPO_ROOT: ... \n BRANCH: ... \n FEATURE_DIR: ... etc.

set -e

# Parse command line arguments
JSON_MODE=false
REQUIRE_SPEC=false
REQUIRE_CONTRACT=false
REQUIRE_TASKS=false
INCLUDE_TASKS=false
PATHS_ONLY=false
TEMPLATE_NAME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json)
            JSON_MODE=true
            ;;
        --require-spec)
            REQUIRE_SPEC=true
            ;;
        --require-contract)
            REQUIRE_CONTRACT=true
            ;;
        --require-tasks)
            REQUIRE_TASKS=true
            ;;
        --include-tasks)
            INCLUDE_TASKS=true
            ;;
        --paths-only)
            PATHS_ONLY=true
            ;;
        --template)
            shift
            if [[ $# -eq 0 ]]; then
                echo "ERROR: --template requires a template name" >&2
                exit 1
            fi
            TEMPLATE_NAME="$1"
            ;;
        --help|-h)
            cat << 'EOF'
Usage: check-prerequisites.sh [OPTIONS]

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
  ./check-prerequisites.sh --json --require-contract

  # Check implementation prerequisites
  ./check-prerequisites.sh --json --require-contract --require-tasks --include-tasks

  # Get feature paths only (no validation)
  ./check-prerequisites.sh --paths-only

EOF
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option '$1'. Use --help for usage information." >&2
            exit 1
            ;;
    esac
    shift
done

# Source common functions
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Get feature paths.
# In --paths-only mode this is pure resolution, so pass --no-persist to opt out
# of the feature.json write side effect (issue #3025).
if $PATHS_ONLY; then
    _paths_output=$(get_feature_paths --no-persist) || { echo "ERROR: Failed to resolve feature paths" >&2; exit 1; }
else
    _paths_output=$(get_feature_paths) || { echo "ERROR: Failed to resolve feature paths" >&2; exit 1; }
fi
eval "$_paths_output"
unset _paths_output

# If paths-only mode, output paths and exit (no validation)
if $PATHS_ONLY; then
    if $JSON_MODE; then
        # Minimal JSON paths payload (no validation performed)
        if has_jq; then
            jq -cn \
                --arg repo_root "$REPO_ROOT" \
                --arg branch "$CURRENT_BRANCH" \
                --arg feature_dir "$FEATURE_DIR" \
                --arg feature_spec "$FEATURE_SPEC" \
                --arg prototype "$PROTOTYPE" \
                --arg quickstart "$QUICKSTART" \
                --arg tasks "$TASKS" \
                '{REPO_ROOT:$repo_root,BRANCH:$branch,FEATURE_DIR:$feature_dir,FEATURE_SPEC:$feature_spec,PROTOTYPE:$prototype,QUICKSTART:$quickstart,TASKS:$tasks}'
        else
            printf '{"REPO_ROOT":"%s","BRANCH":"%s","FEATURE_DIR":"%s","FEATURE_SPEC":"%s","PROTOTYPE":"%s","QUICKSTART":"%s","TASKS":"%s"}\n' \
                "$(json_escape "$REPO_ROOT")" "$(json_escape "$CURRENT_BRANCH")" "$(json_escape "$FEATURE_DIR")" "$(json_escape "$FEATURE_SPEC")" "$(json_escape "$PROTOTYPE")" "$(json_escape "$QUICKSTART")" "$(json_escape "$TASKS")"
        fi
    else
        echo "REPO_ROOT: $REPO_ROOT"
        echo "BRANCH: $CURRENT_BRANCH"
        echo "FEATURE_DIR: $FEATURE_DIR"
        echo "FEATURE_SPEC: $FEATURE_SPEC"
        echo "PROTOTYPE: $PROTOTYPE"
        echo "QUICKSTART: $QUICKSTART"
        echo "TASKS: $TASKS"
    fi
    exit 0
fi

# Validate required directories and files
if [[ ! -d "$FEATURE_DIR" ]]; then
    echo "ERROR: Feature directory not found: $FEATURE_DIR" >&2
    echo "Run $(format_speckit_command specify "$REPO_ROOT") first to create the feature structure." >&2
    exit 1
fi

# Check for spec.md if required
if $REQUIRE_SPEC && [[ ! -f "$FEATURE_SPEC" ]]; then
    echo "ERROR: spec.md not found in $FEATURE_DIR" >&2
    echo "Run $(format_speckit_command specify "$REPO_ROOT") first to create the feature specification." >&2
    exit 1
fi

if $REQUIRE_CONTRACT; then
    require_contract_file() {
        local path="$1"
        local name="$2"
        if [[ ! -f "$path" ]]; then
            echo "ERROR: $name not found in $FEATURE_DIR" >&2
            echo "Run $(format_speckit_command specify "$REPO_ROOT") first to create the frozen requirement contract." >&2
            exit 1
        fi
        if [[ ! -s "$path" ]]; then
            echo "ERROR: $name is empty in $FEATURE_DIR" >&2
            echo "Rerun $(format_speckit_command specify "$REPO_ROOT") to regenerate $name." >&2
            exit 1
        fi
    }
    require_contract_file "$FEATURE_SPEC" "spec.md"
    require_contract_file "$PROTOTYPE" "prototype.html"
    require_contract_file "$QUICKSTART" "quickstart.md"
fi

# Check for tasks.md if required
if $REQUIRE_TASKS && [[ ! -f "$TASKS" ]]; then
    echo "ERROR: tasks.md not found in $FEATURE_DIR" >&2
    echo "Run $(format_speckit_command tasks "$REPO_ROOT") first to create the task list." >&2
    exit 1
fi

# Build list of available documents
docs=()
[[ -f "$FEATURE_SPEC" ]] && docs+=("spec.md")
[[ -f "$PROTOTYPE" ]] && docs+=("prototype.html")
[[ -f "$QUICKSTART" ]] && docs+=("quickstart.md")

# Include tasks.md if requested and it exists
if $INCLUDE_TASKS && [[ -f "$TASKS" ]]; then
    docs+=("tasks.md")
fi

TEMPLATE_CONTENT=""
if [[ -n "$TEMPLATE_NAME" ]]; then
    if TEMPLATE_CONTENT=$(resolve_template_content "$TEMPLATE_NAME" "$REPO_ROOT"; status=$?; printf x; exit "$status"); then
        TEMPLATE_CONTENT="${TEMPLATE_CONTENT%x}"
    else
        echo "ERROR: Could not resolve required $TEMPLATE_NAME from the template override stack for $REPO_ROOT" >&2
        exit 1
    fi
fi

# Output results
if $JSON_MODE; then
    # Build JSON array of documents
    if has_jq; then
        if [[ ${#docs[@]} -eq 0 ]]; then
            json_docs="[]"
        else
            json_docs=$(printf '%s\n' "${docs[@]}" | jq -R . | jq -s .)
        fi
        if [[ -n "$TEMPLATE_NAME" ]]; then
            jq -cn \
                --arg feature_dir "$FEATURE_DIR" \
                --argjson docs "$json_docs" \
                --arg template_content "$TEMPLATE_CONTENT" \
                '{FEATURE_DIR:$feature_dir,AVAILABLE_DOCS:$docs,TEMPLATE_CONTENT:$template_content}'
        else
            jq -cn \
                --arg feature_dir "$FEATURE_DIR" \
                --argjson docs "$json_docs" \
                '{FEATURE_DIR:$feature_dir,AVAILABLE_DOCS:$docs}'
        fi
    else
        if [[ ${#docs[@]} -eq 0 ]]; then
            json_docs="[]"
        else
            json_docs=$(for d in "${docs[@]}"; do printf '"%s",' "$(json_escape "$d")"; done)
            json_docs="[${json_docs%,}]"
        fi
        if [[ -n "$TEMPLATE_NAME" ]]; then
            printf '{"FEATURE_DIR":"%s","AVAILABLE_DOCS":%s,"TEMPLATE_CONTENT":"%s"}\n' \
                "$(json_escape "$FEATURE_DIR")" "$json_docs" "$(json_escape "$TEMPLATE_CONTENT")"
        else
            printf '{"FEATURE_DIR":"%s","AVAILABLE_DOCS":%s}\n' "$(json_escape "$FEATURE_DIR")" "$json_docs"
        fi
    fi
else
    # Text output
    echo "FEATURE_DIR:$FEATURE_DIR"
    echo "AVAILABLE_DOCS:"

    # Show status of each contract document.
    check_file "$FEATURE_SPEC" "spec.md"
    check_file "$PROTOTYPE" "prototype.html"
    check_file "$QUICKSTART" "quickstart.md"

    if $INCLUDE_TASKS; then
        check_file "$TASKS" "tasks.md"
    fi
fi
