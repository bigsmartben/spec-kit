#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

if ($Help) {
    Write-Output "Usage: ./validate-arch-artifacts.ps1 [-Json] [-Help]"
    Write-Output "  -Json     Output planning readiness result as JSON"
    Write-Output "  -Help     Show this help message"
    exit 0
}

function Find-SpecifyRoot {
    param([string]$StartDir = (Get-Location).Path)

    $resolved = Resolve-Path -LiteralPath $StartDir -ErrorAction SilentlyContinue
    $current = if ($resolved) { $resolved.Path } else { $null }
    if (-not $current) { return $null }

    while ($true) {
        if (Test-Path -LiteralPath (Join-Path $current ".specify") -PathType Container) {
            return $current
        }
        $parent = Split-Path $current -Parent
        if ([string]::IsNullOrEmpty($parent) -or $parent -eq $current) {
            return $null
        }
        $current = $parent
    }
}

function Get-RepoRoot {
    $specifyRoot = Find-SpecifyRoot
    if ($specifyRoot) {
        return $specifyRoot
    }

    try {
        $result = git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $result
        }
    } catch {
    }

    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "../../../../..")).Path
}

function Convert-ToPlainPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ($Path -like 'Microsoft.PowerShell.Core\FileSystem::*') {
        return $Path.Substring('Microsoft.PowerShell.Core\FileSystem::'.Length)
    }
    return $Path
}

function Add-Blocker {
    param(
        [Parameter(Mandatory = $true)][string]$Code,
        [Parameter(Mandatory = $true)][string]$Artifact,
        [string]$SectionId = "",
        [Parameter(Mandatory = $true)][string]$Message
    )

    $script:blockers += [PSCustomObject]@{
        code = $Code
        artifact = $Artifact
        sectionId = $SectionId
        message = $Message
    }
}

function Test-SectionExists {
    param(
        [AllowEmptyCollection()][AllowEmptyString()][string[]]$Lines,
        [Parameter(Mandatory = $true)][string]$Heading
    )

    $pattern = '^##\s+' + [regex]::Escape($Heading) + '\s*$'
    return [bool]($Lines | Where-Object { $_ -match $pattern } | Select-Object -First 1)
}

function Test-SectionHasContent {
    param(
        [AllowEmptyCollection()][AllowEmptyString()][string[]]$Lines,
        [Parameter(Mandatory = $true)][string]$Heading
    )

    $pattern = '^##\s+' + [regex]::Escape($Heading) + '\s*$'
    $inSection = $false
    foreach ($line in $Lines) {
        if ($line -match $pattern) {
            $inSection = $true
            continue
        }
        if ($inSection -and $line -match '^##\s+') {
            break
        }
        if (-not $inSection) {
            continue
        }

        $trimmed = $line.Trim()
        if (-not $trimmed) { continue }
        if ($trimmed -match 'NEEDS ARCH UPDATE|NEEDS REPO FACTS UPDATE') { continue }
        if ($trimmed -match '^[-|:\s]+$') { continue }
        if ($trimmed -match '^\|\s*[-:]') { continue }
        return $true
    }

    return $false
}

function Test-InvalidSourceValue {
    param([AllowEmptyString()][string]$Value)

    $normalized = ($Value -replace '`', '').Trim()
    return [string]::IsNullOrWhiteSpace($normalized) -or $normalized -match '^(tbd|n/a|na|none|unknown|guess|guessed|todo|needs arch update|needs repo facts update)$'
}

function Test-SectionHasMissingSource {
    param(
        [AllowEmptyCollection()][AllowEmptyString()][string[]]$Lines,
        [Parameter(Mandatory = $true)][string]$Heading
    )

    $pattern = '^##\s+' + [regex]::Escape($Heading) + '\s*$'
    $inSection = $false
    foreach ($line in $Lines) {
        if ($line -match $pattern) {
            $inSection = $true
            continue
        }
        if ($inSection -and $line -match '^##\s+') {
            break
        }
        if (-not $inSection) {
            continue
        }

        $trimmed = $line.Trim()
        if ($trimmed -notmatch '^\|.*\|$') { continue }
        if ($trimmed -match '\|\s*[-:]+\s*\|') { continue }
        if ($trimmed -match 'Source\s*/\s*Basis') { continue }

        $cells = $trimmed -split '\|'
        if ($cells.Count -lt 3) { return $true }
        $source = $cells[$cells.Count - 2]
        if (Test-InvalidSourceValue -Value $source) { return $true }
    }

    return $false
}

function Test-IntentHasMissingSource {
    param([AllowEmptyCollection()][AllowEmptyString()][string[]]$Lines)

    $inSection = $false
    foreach ($line in $Lines) {
        if ($line -match '^##\s+Architecture Intent\s*$') {
            $inSection = $true
            continue
        }
        if ($inSection -and $line -match '^##\s+') {
            break
        }
        if (-not $inSection) {
            continue
        }
        if ($line -match '^\*\*Source\s*/\s*Basis\*\*:') {
            $value = $line -replace '^\*\*Source\s*/\s*Basis\*\*:\s*', ''
            return (Test-InvalidSourceValue -Value $value)
        }
    }

    return $true
}

function Test-OpenQuestionsHaveInvalidStatus {
    param(
        [AllowEmptyCollection()][AllowEmptyString()][string[]]$Lines,
        [Parameter(Mandatory = $true)][string]$Heading
    )

    $pattern = '^##\s+' + [regex]::Escape($Heading) + '\s*$'
    $inSection = $false
    foreach ($line in $Lines) {
        if ($line -match $pattern) {
            $inSection = $true
            continue
        }
        if ($inSection -and $line -match '^##\s+') {
            break
        }
        if (-not $inSection) {
            continue
        }

        $trimmed = $line.Trim()
        if ($trimmed -notmatch '^\|.*\|$') { continue }
        if ($trimmed -match '\|\s*[-:]+\s*\|') { continue }
        if ($trimmed -match 'Planning Status') { continue }

        $cells = $trimmed -split '\|'
        if ($cells.Count -lt 4) { return $true }
        $status = $cells[$cells.Count - 3].Trim()
        if ($status -ne "BLOCKS_PLAN" -and $status -ne "CAN_PROCEED_WITH_GUARDRAIL") {
            return $true
        }
    }

    return $false
}

function Test-UnsupportedConclusion {
    param([Parameter(Mandatory = $true)][string]$Content)

    if ($Content -match '(^|[^A-Za-z0-9_])(src|app|lib|packages|cmd|internal)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+([^A-Za-z0-9_]|$)') {
        return $true
    }
    if ($Content -match '\b[A-Za-z_][A-Za-z0-9_]*(Controller|Service|Repository|Manager)\b') {
        return $true
    }
    if ($Content -match '\b(add|create|edit|modify|write|implement|generate)\b.*\b(endpoint|endpoints|api schema|openapi|database schema|db table|db tables|migration|migrations|task list|tasks|test strategy|runbook|deployment manifest)\b') {
        return $true
    }

    return $false
}

$repoRoot = Convert-ToPlainPath (Get-RepoRoot)
$archFile = Join-Path $repoRoot ".specify/memory/architecture.md"
$artifact = "architecture-planning-contract"
$blockers = @()

$sectionHeadings = @{
    "architecture-intent" = "Architecture Intent"
    "planning-scope-rules" = "Planning Scope Rules"
    "capability-boundaries" = "Capability Boundaries"
    "required-constraints" = "Required Constraints"
    "architecture-decisions-already-made" = "Architecture Decisions Already Made"
    "allowed-extension-points" = "Allowed Extension Points"
    "prohibited-plan-directions" = "Prohibited Plan Directions"
    "open-architecture-questions" = "Open Architecture Questions"
    "plan-review-checklist" = "Plan Review Checklist"
}

$requiredSections = @(
    "architecture-intent",
    "planning-scope-rules",
    "capability-boundaries",
    "required-constraints",
    "architecture-decisions-already-made",
    "allowed-extension-points",
    "prohibited-plan-directions",
    "open-architecture-questions",
    "plan-review-checklist"
)

if (-not (Test-Path -LiteralPath $archFile -PathType Leaf)) {
    Add-Blocker -Code "ARCH_ARTIFACT_MISSING" -Artifact $artifact -Message "Required architecture planning contract is missing: $archFile"
} else {
    $lines = Get-Content -LiteralPath $archFile
    $content = $lines -join "`n"
    if ($content -match 'NEEDS ARCH UPDATE|NEEDS REPO FACTS UPDATE') {
        Add-Blocker -Code "ARCH_PLACEHOLDER_PRESENT" -Artifact $artifact -Message "Planning contract still contains placeholder update markers."
    }

    if (Test-UnsupportedConclusion -Content $content) {
        Add-Blocker -Code "ARCH_UNSUPPORTED_CONCLUSION" -Artifact $artifact -Message "Planning contract contains implementation-level conclusions that belong to downstream planning or implementation."
    }

    foreach ($section in $requiredSections) {
        $heading = $sectionHeadings[$section]
        if (-not (Test-SectionExists -Lines $lines -Heading $heading)) {
            Add-Blocker -Code "ARCH_REQUIRED_SECTION_MISSING" -Artifact $artifact -SectionId $section -Message "Required planning contract section is missing."
            continue
        }

        if (-not (Test-SectionHasContent -Lines $lines -Heading $heading)) {
            if ($section -eq "planning-scope-rules") {
                Add-Blocker -Code "ARCH_PLANNING_SCOPE_RULES_MISSING" -Artifact $artifact -SectionId $section -Message "Planning Scope Rules has no supported records."
            } elseif ($section -eq "capability-boundaries") {
                Add-Blocker -Code "ARCH_CAPABILITY_BOUNDARIES_MISSING" -Artifact $artifact -SectionId $section -Message "Capability Boundaries has no supported records."
            } elseif ($section -eq "plan-review-checklist") {
                Add-Blocker -Code "ARCH_PLAN_REVIEW_CHECKLIST_MISSING" -Artifact $artifact -SectionId $section -Message "Plan Review Checklist has no supported records."
            } else {
                Add-Blocker -Code "ARCH_REQUIRED_SECTION_EMPTY" -Artifact $artifact -SectionId $section -Message "Required planning contract section has no supported records."
            }
        }
    }

    if (
        (Test-SectionExists -Lines $lines -Heading $sectionHeadings["architecture-intent"]) -and
        (Test-IntentHasMissingSource -Lines $lines)
    ) {
        Add-Blocker -Code "ARCH_SOURCE_MISSING" -Artifact $artifact -SectionId "architecture-intent" -Message "Architecture Intent is missing Source / Basis."
    }

    $sourceSections = @(
        "planning-scope-rules",
        "capability-boundaries",
        "required-constraints",
        "architecture-decisions-already-made",
        "allowed-extension-points",
        "prohibited-plan-directions",
        "open-architecture-questions",
        "plan-review-checklist"
    )

    foreach ($section in $sourceSections) {
        $heading = $sectionHeadings[$section]
        if (
            (Test-SectionExists -Lines $lines -Heading $heading) -and
            (Test-SectionHasMissingSource -Lines $lines -Heading $heading)
        ) {
            Add-Blocker -Code "ARCH_SOURCE_MISSING" -Artifact $artifact -SectionId $section -Message "Rule-bearing section has a row without supported Source / Basis."
        }
    }

    if (
        (Test-SectionExists -Lines $lines -Heading $sectionHeadings["open-architecture-questions"]) -and
        (Test-OpenQuestionsHaveInvalidStatus -Lines $lines -Heading $sectionHeadings["open-architecture-questions"])
    ) {
        Add-Blocker -Code "ARCH_OPEN_QUESTION_STATUS_INVALID" -Artifact $artifact -SectionId "open-architecture-questions" -Message "Open Architecture Questions must use BLOCKS_PLAN or CAN_PROCEED_WITH_GUARDRAIL."
    }

    if (
        (Test-SectionExists -Lines $lines -Heading $sectionHeadings["required-constraints"]) -and
        (Test-SectionExists -Lines $lines -Heading $sectionHeadings["architecture-decisions-already-made"]) -and
        -not (Test-SectionHasContent -Lines $lines -Heading $sectionHeadings["required-constraints"]) -and
        -not (Test-SectionHasContent -Lines $lines -Heading $sectionHeadings["architecture-decisions-already-made"])
    ) {
        Add-Blocker -Code "ARCH_CONSTRAINTS_OR_DECISIONS_MISSING" -Artifact $artifact -SectionId "required-constraints" -Message "Required Constraints and Architecture Decisions Already Made are both empty."
    }
}

$planningGate = if ($blockers.Count -eq 0) { "USABLE" } else { "BLOCKED" }
$readyGate = if ($blockers.Count -eq 0) { "PASS" } else { "BLOCKED" }
$result = [PSCustomObject]@{
    planning_gate = $planningGate
    ready_gate = $readyGate
    blockers = $blockers
}

if ($Json) {
    $result | ConvertTo-Json -Compress -Depth 5
} else {
    Write-Output "planning_gate: $planningGate"
    Write-Output "ready_gate: $readyGate"
    foreach ($blocker in $blockers) {
        Write-Output ($blocker | ConvertTo-Json -Compress)
    }
}

if ($blockers.Count -gt 0) {
    exit 1
}
