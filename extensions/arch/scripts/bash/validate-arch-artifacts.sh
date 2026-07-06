#!/usr/bin/env bash

set -euo pipefail

JSON_MODE=false

for arg in "$@"; do
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --help|-h)
            echo "Usage: $0 [--json]"
            echo "  --json    Output planning readiness result as JSON"
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

json_escape() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\t'/\\t}"
    s="${s//$'\r'/\\r}"
    printf '%s' "$s"
}

blockers=()

add_blocker() {
    local code="$1"
    local artifact="$2"
    local section="$3"
    local message="$4"
    blockers+=("$(printf '{"code":"%s","artifact":"%s","sectionId":"%s","message":"%s"}' \
        "$(json_escape "$code")" \
        "$(json_escape "$artifact")" \
        "$(json_escape "$section")" \
        "$(json_escape "$message")")")
}

section_heading() {
    case "$1" in
        architecture-intent) echo "Architecture Intent" ;;
        planning-scope-rules) echo "Planning Scope Rules" ;;
        capability-boundaries) echo "Capability Boundaries" ;;
        required-constraints) echo "Required Constraints" ;;
        architecture-decisions-already-made) echo "Architecture Decisions Already Made" ;;
        allowed-extension-points) echo "Allowed Extension Points" ;;
        prohibited-plan-directions) echo "Prohibited Plan Directions" ;;
        open-architecture-questions) echo "Open Architecture Questions" ;;
        plan-review-checklist) echo "Plan Review Checklist" ;;
        *) return 1 ;;
    esac
}

section_exists() {
    local file="$1"
    local section_id="$2"
    local heading
    heading="$(section_heading "$section_id")"
    grep -Eq "^##[[:space:]]+$heading[[:space:]]*$" "$file"
}

section_has_content() {
    local file="$1"
    local section_id="$2"
    local heading
    heading="$(section_heading "$section_id")"
    awk -v heading="$heading" '
        $0 ~ "^##[[:space:]]+" heading "[[:space:]]*$" { in_section = 1; next }
        in_section && /^##[[:space:]]+/ { exit }
        in_section {
            line = $0
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)
            if (line == "") next
            if (line ~ /^[-|:[:space:]]+$/) next
            if (line ~ /NEEDS ARCH UPDATE|NEEDS REPO FACTS UPDATE/) next
            if (line ~ /^\|[[:space:]]*[-:]/) next
            if (line ~ /^\|.*\|$/ && line !~ /NEEDS ARCH UPDATE|NEEDS REPO FACTS UPDATE/) {
                found = 1
                exit
            }
            if (line !~ /^\|/) {
                found = 1
                exit
            }
        }
        END { exit(found ? 0 : 1) }
    ' "$file"
}

invalid_source_value() {
    local value="$1"
    value="$(printf '%s' "$value" | tr -d '`' | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')"
    [ -z "$value" ] && return 0
    printf '%s' "$value" | grep -Eiq '^(tbd|n/a|na|none|unknown|guess|guessed|todo|needs arch update|needs repo facts update)$'
}

section_has_missing_source() {
    local file="$1"
    local section_id="$2"
    local heading
    heading="$(section_heading "$section_id")"
    awk -v heading="$heading" '
        function trim(s) {
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", s)
            return s
        }
        $0 ~ "^##[[:space:]]+" heading "[[:space:]]*$" { in_section = 1; next }
        in_section && /^##[[:space:]]+/ { exit }
        in_section && /^\|.*\|[[:space:]]*$/ {
            line = $0
            if (line ~ /\|[[:space:]]*[-:]+[[:space:]]*\|/) next
            if (line ~ /Source[[:space:]]*\/[[:space:]]*Basis/) next
            n = split(line, cells, "|")
            source = trim(cells[n - 1])
            lower = tolower(source)
            if (source == "" || lower ~ /^(tbd|n\/a|na|none|unknown|guess|guessed|todo|needs arch update|needs repo facts update)$/) {
                found = 1
                exit
            }
        }
        END { exit(found ? 0 : 1) }
    ' "$file"
}

intent_has_missing_source() {
    local file="$1"
    awk '
        function trim(s) {
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", s)
            return s
        }
        /^##[[:space:]]+Architecture Intent[[:space:]]*$/ { in_section = 1; next }
        in_section && /^##[[:space:]]+/ { exit }
        in_section && /^\*\*Source[[:space:]]*\/[[:space:]]*Basis\*\*:/ {
            value = $0
            sub(/^\*\*Source[[:space:]]*\/[[:space:]]*Basis\*\*:[[:space:]]*/, "", value)
            value = trim(value)
            lower = tolower(value)
            if (value == "" || lower ~ /^(tbd|n\/a|na|none|unknown|guess|guessed|todo|needs arch update|needs repo facts update)$/) {
                found = 1
            }
            seen = 1
            exit
        }
        END {
            if (!seen) found = 1
            exit(found ? 0 : 1)
        }
    ' "$file"
}

open_questions_have_invalid_status() {
    local file="$1"
    local heading
    heading="$(section_heading "open-architecture-questions")"
    awk -v heading="$heading" '
        function trim(s) {
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", s)
            return s
        }
        $0 ~ "^##[[:space:]]+" heading "[[:space:]]*$" { in_section = 1; next }
        in_section && /^##[[:space:]]+/ { exit }
        in_section && /^\|.*\|[[:space:]]*$/ {
            line = $0
            if (line ~ /\|[[:space:]]*[-:]+[[:space:]]*\|/) next
            if (line ~ /Planning Status/) next
            n = split(line, cells, "|")
            status = trim(cells[n - 2])
            if (status != "BLOCKS_PLAN" && status != "CAN_PROCEED_WITH_GUARDRAIL") {
                found = 1
                exit
            }
        }
        END { exit(found ? 0 : 1) }
    ' "$file"
}

has_unsupported_conclusion() {
    local file="$1"
    grep -Eiq '(^|[^A-Za-z0-9_])(src|app|lib|packages|cmd|internal)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+([^A-Za-z0-9_]|$)' "$file" && return 0
    grep -Eiq '\b[A-Za-z_][A-Za-z0-9_]*(Controller|Service|Repository|Manager)\b' "$file" && return 0
    grep -Eiq '\b(add|create|edit|modify|write|implement|generate)\b.*\b(endpoint|endpoints|api schema|openapi|database schema|db table|db tables|migration|migrations|task list|tasks|test strategy|runbook|deployment manifest)\b' "$file" && return 0
    return 1
}

REPO_ROOT="$(get_repo_root)"
ARCH_FILE="$REPO_ROOT/.specify/memory/architecture.md"
ARTIFACT="architecture-planning-contract"

if [ ! -f "$ARCH_FILE" ]; then
    add_blocker "ARCH_ARTIFACT_MISSING" "$ARTIFACT" "" "Required architecture planning contract is missing: $ARCH_FILE"
else
    if grep -Eq "NEEDS ARCH UPDATE|NEEDS REPO FACTS UPDATE" "$ARCH_FILE"; then
        add_blocker "ARCH_PLACEHOLDER_PRESENT" "$ARTIFACT" "" "Planning contract still contains placeholder update markers."
    fi

    if has_unsupported_conclusion "$ARCH_FILE"; then
        add_blocker "ARCH_UNSUPPORTED_CONCLUSION" "$ARTIFACT" "" "Planning contract contains implementation-level conclusions that belong to downstream planning or implementation."
    fi

    required_sections=(
        architecture-intent
        planning-scope-rules
        capability-boundaries
        required-constraints
        architecture-decisions-already-made
        allowed-extension-points
        prohibited-plan-directions
        open-architecture-questions
        plan-review-checklist
    )

    for section in "${required_sections[@]}"; do
        if ! section_exists "$ARCH_FILE" "$section"; then
            add_blocker "ARCH_REQUIRED_SECTION_MISSING" "$ARTIFACT" "$section" "Required planning contract section is missing."
            continue
        fi
        if ! section_has_content "$ARCH_FILE" "$section"; then
            case "$section" in
                planning-scope-rules)
                    add_blocker "ARCH_PLANNING_SCOPE_RULES_MISSING" "$ARTIFACT" "$section" "Planning Scope Rules has no supported records."
                    ;;
                capability-boundaries)
                    add_blocker "ARCH_CAPABILITY_BOUNDARIES_MISSING" "$ARTIFACT" "$section" "Capability Boundaries has no supported records."
                    ;;
                plan-review-checklist)
                    add_blocker "ARCH_PLAN_REVIEW_CHECKLIST_MISSING" "$ARTIFACT" "$section" "Plan Review Checklist has no supported records."
                    ;;
                *)
                    add_blocker "ARCH_REQUIRED_SECTION_EMPTY" "$ARTIFACT" "$section" "Required planning contract section has no supported records."
                    ;;
            esac
        fi
    done

    if section_exists "$ARCH_FILE" "architecture-intent" && intent_has_missing_source "$ARCH_FILE"; then
        add_blocker "ARCH_SOURCE_MISSING" "$ARTIFACT" "architecture-intent" "Architecture Intent is missing Source / Basis."
    fi

    source_sections=(
        planning-scope-rules
        capability-boundaries
        required-constraints
        architecture-decisions-already-made
        allowed-extension-points
        prohibited-plan-directions
        open-architecture-questions
        plan-review-checklist
    )

    for section in "${source_sections[@]}"; do
        if section_exists "$ARCH_FILE" "$section" && section_has_missing_source "$ARCH_FILE" "$section"; then
            add_blocker "ARCH_SOURCE_MISSING" "$ARTIFACT" "$section" "Rule-bearing section has a row without supported Source / Basis."
        fi
    done

    if section_exists "$ARCH_FILE" "open-architecture-questions" && open_questions_have_invalid_status "$ARCH_FILE"; then
        add_blocker "ARCH_OPEN_QUESTION_STATUS_INVALID" "$ARTIFACT" "open-architecture-questions" "Open Architecture Questions must use BLOCKS_PLAN or CAN_PROCEED_WITH_GUARDRAIL."
    fi

    if section_exists "$ARCH_FILE" "required-constraints" && section_exists "$ARCH_FILE" "architecture-decisions-already-made"; then
        if ! section_has_content "$ARCH_FILE" "required-constraints" && ! section_has_content "$ARCH_FILE" "architecture-decisions-already-made"; then
            add_blocker "ARCH_CONSTRAINTS_OR_DECISIONS_MISSING" "$ARTIFACT" "required-constraints" "Required Constraints and Architecture Decisions Already Made are both empty."
        fi
    fi
fi

if [ "${#blockers[@]}" -eq 0 ]; then
    if $JSON_MODE; then
        printf '{"planning_gate":"USABLE","ready_gate":"PASS","blockers":[]}\n'
    else
        echo "planning_gate: USABLE"
        echo "ready_gate: PASS"
    fi
    exit 0
fi

if $JSON_MODE; then
    printf '{"planning_gate":"BLOCKED","ready_gate":"BLOCKED","blockers":['
    local_prefix=""
    for blocker in "${blockers[@]}"; do
        printf '%s%s' "$local_prefix" "$blocker"
        local_prefix=","
    done
    printf ']}\n'
else
    echo "planning_gate: BLOCKED"
    echo "ready_gate: BLOCKED"
    for blocker in "${blockers[@]}"; do
        echo "$blocker"
    done
fi

exit 1
