#!/usr/bin/env bash

set -e

JSON_MODE=false

for arg in "$@"; do
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --help|-h)
            echo "Usage: $0 [--json]"
            echo "  --json    Output results in JSON format"
            echo "  --help    Show this help message"
            exit 0
            ;;
        *)
            ;;
    esac
done

find_specify_root() {
    local dir="${1:-$(pwd)}"
    dir="$(cd -- "$dir" 2>/dev/null && pwd)" || return 1
    local prev_dir=""
    while true; do
        if [ -d "$dir/.specify" ]; then
            echo "$dir"
            return 0
        fi
        if [ "$dir" = "/" ] || [ "$dir" = "$prev_dir" ]; then
            break
        fi
        prev_dir="$dir"
        dir="$(dirname "$dir")"
    done
    return 1
}

get_repo_root() {
    local specify_root
    if specify_root=$(find_specify_root); then
        echo "$specify_root"
        return
    fi

    if git rev-parse --show-toplevel >/dev/null 2>&1; then
        git rev-parse --show-toplevel
        return
    fi

    local script_dir
    script_dir="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    (cd "$script_dir/../../../../.." && pwd)
}

has_jq() {
    command -v jq >/dev/null 2>&1
}

json_escape() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\t'/\\t}"
    s="${s//$'\r'/\\r}"
    printf '%s' "$s"
}

resolve_architecture_template() {
    local template_name="$1"
    local repo_root="$2"
    local override="$repo_root/.specify/templates/overrides/${template_name}.md"
    local candidate="$repo_root/.specify/extensions/arch/templates/${template_name}.md"

    [ -f "$override" ] && echo "$override" && return 0
    [ -f "$candidate" ] && echo "$candidate" && return 0
    return 1
}

REPO_ROOT=$(get_repo_root)
ARCH_DIR="$REPO_ROOT/.specify/memory"
SCHEMA_DIR="$REPO_ROOT/.specify/extensions/arch/schemas"
SCRIPT_DIR="$REPO_ROOT/.specify/extensions/arch/scripts"
ARCH_SCHEMA_FILE="$SCHEMA_DIR/architecture-artifacts.schema.json"
ARCH_VALIDATOR_FILE="$SCRIPT_DIR/bash/validate-arch-artifacts.sh"
ARCH_VALIDATOR_PS_FILE="$SCRIPT_DIR/powershell/validate-arch-artifacts.ps1"
ARCH_FILE="$ARCH_DIR/architecture.md"

mkdir -p "$ARCH_DIR"

copy_template_if_missing() {
    local template_name="$1"
    local destination="$2"

    if [[ -f "$destination" ]]; then
        return 0
    fi

    local template
    template=$(resolve_architecture_template "$template_name" "$REPO_ROOT") || true
    if [[ -n "$template" ]] && [[ -f "$template" ]]; then
        cp "$template" "$destination"
        if $JSON_MODE; then
            echo "Copied $template_name template to $destination" >&2
        else
            echo "Copied $template_name template to $destination"
        fi
    else
        echo "Warning: $template_name template not found" >&2
        touch "$destination"
    fi
}

copy_template_if_missing "architecture-template" "$ARCH_FILE"

if $JSON_MODE; then
    if has_jq; then
        jq -cn \
            --arg arch_file "$ARCH_FILE" \
            --arg arch_dir "$ARCH_DIR" \
            --arg schema_dir "$SCHEMA_DIR" \
            --arg arch_schema_file "$ARCH_SCHEMA_FILE" \
            --arg arch_validator_file "$ARCH_VALIDATOR_FILE" \
            --arg arch_validator_ps_file "$ARCH_VALIDATOR_PS_FILE" \
            '{ARCH_FILE:$arch_file,ARCH_DIR:$arch_dir,SCHEMA_DIR:$schema_dir,ARCH_SCHEMA_FILE:$arch_schema_file,ARCH_VALIDATOR_FILE:$arch_validator_file,ARCH_VALIDATOR_PS_FILE:$arch_validator_ps_file}'
    else
        printf '{"ARCH_FILE":"%s","ARCH_DIR":"%s","SCHEMA_DIR":"%s","ARCH_SCHEMA_FILE":"%s","ARCH_VALIDATOR_FILE":"%s","ARCH_VALIDATOR_PS_FILE":"%s"}\n' \
            "$(json_escape "$ARCH_FILE")" \
            "$(json_escape "$ARCH_DIR")" \
            "$(json_escape "$SCHEMA_DIR")" \
            "$(json_escape "$ARCH_SCHEMA_FILE")" \
            "$(json_escape "$ARCH_VALIDATOR_FILE")" \
            "$(json_escape "$ARCH_VALIDATOR_PS_FILE")"
    fi
else
    echo "ARCH_FILE: $ARCH_FILE"
    echo "ARCH_DIR: $ARCH_DIR"
    echo "SCHEMA_DIR: $SCHEMA_DIR"
    echo "ARCH_SCHEMA_FILE: $ARCH_SCHEMA_FILE"
    echo "ARCH_VALIDATOR_FILE: $ARCH_VALIDATOR_FILE"
    echo "ARCH_VALIDATOR_PS_FILE: $ARCH_VALIDATOR_PS_FILE"
fi
