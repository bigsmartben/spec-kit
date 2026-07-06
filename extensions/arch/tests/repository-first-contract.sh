#!/usr/bin/env bash
set -euo pipefail
trap 'echo "repository-first-contract failed at line $LINENO: $BASH_COMMAND" >&2' ERR

if command -v rg >/dev/null 2>&1 && rg --version >/dev/null 2>&1; then
    search() {
        rg -n "$@"
    }
else
    search() {
        local pattern="$1"
        shift
        grep -R -n -E "$pattern" "$@"
    }
fi

search "name: speckit\\.arch\\.generate" extension.yml >/dev/null
search "file: commands/speckit\\.arch\\.generate\\.md" extension.yml >/dev/null
search "name: speckit\\.arch\\.reverse" extension.yml >/dev/null
search "file: commands/speckit\\.arch\\.reverse\\.md" extension.yml >/dev/null
test -f "commands/speckit.arch.generate.md"
test -f "commands/speckit.arch.reverse.md"

registered_count=$(search "name: speckit\\.arch\\." extension.yml | wc -l | tr -d '[:space:]')
test "$registered_count" = "2"

if search "name: speckit\\.arch\\.(full|scenario|logical|process|development|physical)-" extension.yml >/dev/null; then
    echo "legacy 4+1 commands must not be registered by default" >&2
    exit 1
fi

search "Architecture Planning Contract" README.md >/dev/null
search "Commands count: 2" CATALOG-SUBMISSION.md >/dev/null
search "Internal Reasoning Model" README.md >/dev/null
search "4\\+1 as an internal reasoning lens" README.md >/dev/null
search "speckit\\.arch\\.generate" README.md >/dev/null
search "speckit\\.arch\\.reverse" README.md >/dev/null
search "planning_gate: USABLE" README.md >/dev/null
search "only generated architecture artifact" CATALOG-SUBMISSION.md >/dev/null
search "Architecture Planning Contract" templates/architecture-template.md >/dev/null
search "## Planning Scope Rules" templates/architecture-template.md >/dev/null
search "## Capability Boundaries" templates/architecture-template.md >/dev/null
search "## Required Constraints" templates/architecture-template.md >/dev/null
search "## Architecture Decisions Already Made" templates/architecture-template.md >/dev/null
search "## Allowed Extension Points" templates/architecture-template.md >/dev/null
search "## Prohibited Plan Directions" templates/architecture-template.md >/dev/null
search "## Open Architecture Questions" templates/architecture-template.md >/dev/null
search "## Plan Review Checklist" templates/architecture-template.md >/dev/null
source_basis_count=$(search "Source / Basis" templates/architecture-template.md | wc -l | tr -d '[:space:]')
test "$source_basis_count" = "9"
search "Planning Status" templates/architecture-template.md >/dev/null

search '"architecture-planning-contract"' schemas/architecture-artifacts.schema.json >/dev/null
if search '"repo-facts"' schemas/architecture-artifacts.schema.json >/dev/null; then
    echo "schema must not expose secondary repo-facts artifacts" >&2
    exit 1
fi
search '"planningGate"' schemas/architecture-artifacts.schema.json >/dev/null
search '"ARCH_PLANNING_SCOPE_RULES_MISSING"' schemas/architecture-artifacts.schema.json >/dev/null
search '"ARCH_CAPABILITY_BOUNDARIES_MISSING"' schemas/architecture-artifacts.schema.json >/dev/null
search '"ARCH_CONSTRAINTS_OR_DECISIONS_MISSING"' schemas/architecture-artifacts.schema.json >/dev/null
search '"ARCH_PLAN_REVIEW_CHECKLIST_MISSING"' schemas/architecture-artifacts.schema.json >/dev/null
search '"ARCH_UNSUPPORTED_CONCLUSION"' schemas/architecture-artifacts.schema.json >/dev/null
search '"ARCH_SOURCE_MISSING"' schemas/architecture-artifacts.schema.json >/dev/null
search '"ARCH_OPEN_QUESTION_STATUS_INVALID"' schemas/architecture-artifacts.schema.json >/dev/null

test -f scripts/bash/setup-arch.sh
test -x scripts/bash/setup-arch.sh
test -f scripts/bash/validate-arch-artifacts.sh
test -x scripts/bash/validate-arch-artifacts.sh
test -f scripts/powershell/setup-arch.ps1
test -f scripts/powershell/validate-arch-artifacts.ps1
search "SCENARIO_VIEW|LOGICAL_VIEW|PROCESS_VIEW|DEVELOPMENT_VIEW|PHYSICAL_VIEW|REPO_FACTS_FILE" scripts/bash/setup-arch.sh && {
    echo "setup output must not require secondary artifact paths" >&2
    exit 1
}
search "planning_gate" scripts/bash/validate-arch-artifacts.sh >/dev/null
search "ready_gate" scripts/bash/validate-arch-artifacts.sh >/dev/null
search "ARCH_UNSUPPORTED_CONCLUSION" scripts/bash/validate-arch-artifacts.sh >/dev/null
search "ARCH_SOURCE_MISSING" scripts/bash/validate-arch-artifacts.sh >/dev/null
search "ARCH_OPEN_QUESTION_STATUS_INVALID" scripts/bash/validate-arch-artifacts.sh >/dev/null
search "planning_gate" scripts/powershell/validate-arch-artifacts.ps1 >/dev/null
search "ready_gate" scripts/powershell/validate-arch-artifacts.ps1 >/dev/null
search "ARCH_UNSUPPORTED_CONCLUSION" scripts/powershell/validate-arch-artifacts.ps1 >/dev/null
search "ARCH_SOURCE_MISSING" scripts/powershell/validate-arch-artifacts.ps1 >/dev/null
search "ARCH_OPEN_QUESTION_STATUS_INVALID" scripts/powershell/validate-arch-artifacts.ps1 >/dev/null

search 'Write only `ARCH_FILE`' commands/speckit.arch.generate.md >/dev/null
search 'Write only `ARCH_FILE`' commands/speckit.arch.reverse.md >/dev/null
search 'Do not create, update, or require `.specify/memory/architecture-repo-facts.md`' commands/speckit.arch.reverse.md >/dev/null
search "Do not create, update, or require separate 4\\+1 view files" commands/speckit.arch.generate.md >/dev/null
search "Do not create, update, or require separate 4\\+1 view files" commands/speckit.arch.reverse.md >/dev/null
search "plan-facing architecture rules" commands/speckit.arch.generate.md >/dev/null
search "plan-facing architecture rules" commands/speckit.arch.reverse.md >/dev/null

if search "Evidence Rules|Prohibited Content|Move unsupported|One sentence|Identify the|List the|Record how|Do not treat|Record observable|projected into" templates >/dev/null; then
    echo "templates must not carry command execution rules" >&2
    exit 1
fi

command_count=$(find commands -maxdepth 1 -type f -name 'speckit.arch.*.md' | wc -l | tr -d '[:space:]')
test "$command_count" = "2"
template_count=$(find templates -maxdepth 1 -type f -name 'architecture-*.md' | wc -l | tr -d '[:space:]')
test "$template_count" = "1"

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT
git -C "$tmpdir" init >/dev/null
mkdir -p "$tmpdir/.specify/extensions/arch"
cp -R commands scripts templates schemas "$tmpdir/.specify/extensions/arch/"
(
    cd "$tmpdir"
    setup_json=$(.specify/extensions/arch/scripts/bash/setup-arch.sh --json)
    printf '%s\n' "$setup_json" | search '"ARCH_FILE"' - >/dev/null
    printf '%s\n' "$setup_json" | search '"ARCH_SCHEMA_FILE"' - >/dev/null
    printf '%s\n' "$setup_json" | search '"ARCH_VALIDATOR_FILE"' - >/dev/null
    printf '%s\n' "$setup_json" | search '"ARCH_VALIDATOR_PS_FILE"' - >/dev/null
    if printf '%s\n' "$setup_json" | search 'SCENARIO_VIEW|LOGICAL_VIEW|PROCESS_VIEW|DEVELOPMENT_VIEW|PHYSICAL_VIEW|REPO_FACTS_FILE' - >/dev/null; then
        echo "setup JSON must not include secondary artifact paths" >&2
        exit 1
    fi

    test -f .specify/memory/architecture.md
    test -f .specify/extensions/arch/schemas/architecture-artifacts.schema.json
    test -f .specify/extensions/arch/scripts/bash/validate-arch-artifacts.sh
    test -x .specify/extensions/arch/scripts/bash/validate-arch-artifacts.sh
    test -f .specify/extensions/arch/scripts/powershell/validate-arch-artifacts.ps1

    find .specify/memory -maxdepth 1 -type f | wc -l | search '^[[:space:]]*1[[:space:]]*$' - >/dev/null
    search "## Planning Scope Rules" .specify/memory/architecture.md >/dev/null

    if validator_json=$(.specify/extensions/arch/scripts/bash/validate-arch-artifacts.sh --json); then
        echo "placeholder planning contract must block planning readiness" >&2
        exit 1
    fi
    printf '%s\n' "$validator_json" | search '"planning_gate":"BLOCKED"' - >/dev/null
    printf '%s\n' "$validator_json" | search '"ready_gate":"BLOCKED"' - >/dev/null
    printf '%s\n' "$validator_json" | search '"ARCH_PLACEHOLDER_PRESENT"' - >/dev/null

    write_contract() {
        local intent="$1"
        local scope_do="$2"
        local scope_source="$3"
        local question_status="$4"

        cat > .specify/memory/architecture.md <<EOF
# Architecture Planning Contract: Demo

**Purpose**: Guide downstream Spec Kit \`/plan\` work.

**Consumer**: Feature planning agents and human reviewers.

## Architecture Intent

$intent

**Source / Basis**: README.md project description

## Planning Scope Rules

| Rule | Applies When | Plan Must Do | Plan Must Not Do | Source / Basis |
|------|--------------|--------------|------------------|----------------|
| Preserve product boundary | Any feature expands behavior | $scope_do | Move unrelated responsibilities across boundaries | $scope_source |

## Capability Boundaries

| Capability / Boundary | Owns | Does Not Own | Planning Implication | Source / Basis |
|-----------------------|------|--------------|----------------------|----------------|
| Planning contract | Architecture guidance | Implementation sequencing | Plans must cite the affected rule | README.md extension overview |

## Required Constraints

| Constraint | Applies To | Plan Enforcement | Source / Basis |
|------------|------------|------------------|----------------|
| Single architecture artifact | Architecture memory | Plans consume architecture.md only | README.md Files Written |

## Architecture Decisions Already Made

| Decision | Plan Consequence | Revisit Trigger | Source / Basis |
|----------|------------------|-----------------|----------------|
| Use a plan-facing contract | Plans check guardrails before design | Contract no longer guides planning | README.md Planning Contract |

## Allowed Extension Points

| Extension Point | Intended Use | Required Review If | Source / Basis |
|-----------------|--------------|--------------------|----------------|
| Open questions | Capture unsupported architecture gaps | A gap blocks planning | Template section list |

## Prohibited Plan Directions

| Anti-pattern | Why Forbidden | Safer Direction | Source / Basis |
|--------------|---------------|-----------------|----------------|
| Treat missing architecture as permission | It hides decision gaps | Record a blocking question | README.md readiness notes |

## Open Architecture Questions

| Question | Plan Impact | Required Clarification | Planning Status | Source / Basis |
|----------|-------------|------------------------|-----------------|----------------|
| Which boundary owns future integrations? | Plan may need review before expansion | Identify owning boundary | $question_status | README.md When You Need This |

## Plan Review Checklist

| Check | Pass Criteria | Blocking Failure | Source / Basis |
|-------|---------------|------------------|----------------|
| Boundary cited | Plan names the affected boundary | Plan changes behavior without boundary review | README.md Planning Contract |
EOF
    }

    write_contract \
        "Keep feature planning aligned to the existing product boundary." \
        "State which existing boundary is affected" \
        "README.md project description" \
        "CAN_PROCEED_WITH_GUARDRAIL"
    usable_json=$(.specify/extensions/arch/scripts/bash/validate-arch-artifacts.sh --json)
    printf '%s\n' "$usable_json" | search '"planning_gate":"USABLE"' - >/dev/null

    write_contract \
        "Create API schemas and edit src/controllers/UserController.ts." \
        "Add endpoints and DB tables" \
        "README.md project description" \
        "CAN_PROCEED_WITH_GUARDRAIL"
    if implementation_json=$(.specify/extensions/arch/scripts/bash/validate-arch-artifacts.sh --json); then
        echo "implementation-level contract must block planning readiness" >&2
        exit 1
    fi
    printf '%s\n' "$implementation_json" | search '"ARCH_UNSUPPORTED_CONCLUSION"' - >/dev/null

    write_contract \
        "Keep feature planning aligned to the existing product boundary." \
        "State which existing boundary is affected" \
        "unknown" \
        "CAN_PROCEED_WITH_GUARDRAIL"
    if missing_source_json=$(.specify/extensions/arch/scripts/bash/validate-arch-artifacts.sh --json); then
        echo "contract with unsupported Source / Basis must block planning readiness" >&2
        exit 1
    fi
    printf '%s\n' "$missing_source_json" | search '"ARCH_SOURCE_MISSING"' - >/dev/null

    write_contract \
        "Keep feature planning aligned to the existing product boundary." \
        "State which existing boundary is affected" \
        "README.md project description" \
        "MAYBE"
    if invalid_status_json=$(.specify/extensions/arch/scripts/bash/validate-arch-artifacts.sh --json); then
        echo "contract with invalid open question status must block planning readiness" >&2
        exit 1
    fi
    printf '%s\n' "$invalid_status_json" | search '"ARCH_OPEN_QUESTION_STATUS_INVALID"' - >/dev/null

    printf 'custom sentinel\n' > .specify/memory/architecture.md
    .specify/extensions/arch/scripts/bash/setup-arch.sh --json >/dev/null
    search "custom sentinel" .specify/memory/architecture.md >/dev/null
)
