#!/usr/bin/env pwsh

# Consolidated prerequisite checking script (PowerShell)
#
# This script provides unified prerequisite checking for Spec-Driven Development workflow.
# It replaces the functionality previously spread across multiple scripts.
#
# Usage: ./check-prerequisites.ps1 [OPTIONS]
#
# OPTIONS:
#   -Json               Output in JSON format
#   -RequireSpec        Require spec.md to exist (for analysis phase)
#   -RequireContract    Require spec.md, prototype.html, and quickstart.md
#   -RequireTasks       Require tasks.md to exist (for implementation phase)
#   -IncludeTasks       Include tasks.md in AVAILABLE_DOCS list
#   -PathsOnly          Only output path variables (no validation)
#   -Template NAME      Include composed template content in JSON output
#   -Help, -h           Show help message

[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$RequireSpec,
    [switch]$RequireContract,
    [switch]$RequireTasks,
    [switch]$IncludeTasks,
    [switch]$PathsOnly,
    [string]$Template,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

# Show help if requested
if ($Help) {
    Write-Output @"
Usage: check-prerequisites.ps1 [OPTIONS]

Consolidated prerequisite checking for Spec-Driven Development workflow.

OPTIONS:
  -Json               Output in JSON format
  -RequireSpec        Require spec.md to exist (for analysis phase)
  -RequireContract    Require spec.md, prototype.html, and quickstart.md
  -RequireTasks       Require tasks.md to exist (for implementation phase)
  -IncludeTasks       Include tasks.md in AVAILABLE_DOCS list
  -PathsOnly          Only output path variables (no prerequisite validation)
  -Template NAME      Include composed template content in JSON output
  -Help, -h           Show this help message

EXAMPLES:
  # Check the frozen Specify contract
  .\check-prerequisites.ps1 -Json -RequireContract

  # Check implementation prerequisites
  .\check-prerequisites.ps1 -Json -RequireContract -RequireTasks -IncludeTasks

  # Get feature paths only (no validation)
  .\check-prerequisites.ps1 -PathsOnly

"@
    exit 0
}

# Source common functions
. "$PSScriptRoot/common.ps1"

# Get feature paths.
# In -PathsOnly mode this is pure resolution, so pass -NoPersist to opt out of
# the feature.json write side effect (issue #3025).
if ($PathsOnly) {
    $paths = Get-FeaturePathsEnv -NoPersist
} else {
    $paths = Get-FeaturePathsEnv
}

# If paths-only mode, output paths and exit (no validation)
if ($PathsOnly) {
    if ($Json) {
        [PSCustomObject]@{
            REPO_ROOT    = $paths.REPO_ROOT
            BRANCH       = $paths.CURRENT_BRANCH
            FEATURE_DIR  = $paths.FEATURE_DIR
            FEATURE_SPEC = $paths.FEATURE_SPEC
            PROTOTYPE    = $paths.PROTOTYPE
            QUICKSTART   = $paths.QUICKSTART
            TASKS        = $paths.TASKS
        } | ConvertTo-AsciiJson
    } else {
        Write-Output "REPO_ROOT: $($paths.REPO_ROOT)"
        Write-Output "BRANCH: $($paths.CURRENT_BRANCH)"
        Write-Output "FEATURE_DIR: $($paths.FEATURE_DIR)"
        Write-Output "FEATURE_SPEC: $($paths.FEATURE_SPEC)"
        Write-Output "PROTOTYPE: $($paths.PROTOTYPE)"
        Write-Output "QUICKSTART: $($paths.QUICKSTART)"
        Write-Output "TASKS: $($paths.TASKS)"
    }
    exit 0
}

# Validate required directories and files
if (-not (Test-Path -LiteralPath $paths.FEATURE_DIR -PathType Container)) {
    [Console]::Error.WriteLine("ERROR: Feature directory not found: $($paths.FEATURE_DIR)")
    $specifyCommand = Format-SpecKitCommand -CommandName 'specify' -RepoRoot $paths.REPO_ROOT
    [Console]::Error.WriteLine("Run $specifyCommand first to create the feature structure.")
    exit 1
}

# Check for spec.md if required
if ($RequireSpec -and -not (Test-Path -LiteralPath $paths.FEATURE_SPEC -PathType Leaf)) {
    [Console]::Error.WriteLine("ERROR: spec.md not found in $($paths.FEATURE_DIR)")
    $specifyCommand = Format-SpecKitCommand -CommandName 'specify' -RepoRoot $paths.REPO_ROOT
    [Console]::Error.WriteLine("Run $specifyCommand first to create the feature specification.")
    exit 1
}

if ($RequireContract) {
    foreach ($contract in @(
        @{ Path = $paths.FEATURE_SPEC; Name = 'spec.md' },
        @{ Path = $paths.PROTOTYPE; Name = 'prototype.html' },
        @{ Path = $paths.QUICKSTART; Name = 'quickstart.md' }
    )) {
        if (-not (Test-Path -LiteralPath $contract.Path -PathType Leaf)) {
            [Console]::Error.WriteLine("ERROR: $($contract.Name) not found in $($paths.FEATURE_DIR)")
            $specifyCommand = Format-SpecKitCommand -CommandName 'specify' -RepoRoot $paths.REPO_ROOT
            [Console]::Error.WriteLine("Run $specifyCommand first to create the frozen requirement contract.")
            exit 1
        }
        if ((Get-Item -LiteralPath $contract.Path).Length -eq 0) {
            [Console]::Error.WriteLine("ERROR: $($contract.Name) is empty in $($paths.FEATURE_DIR)")
            $specifyCommand = Format-SpecKitCommand -CommandName 'specify' -RepoRoot $paths.REPO_ROOT
            [Console]::Error.WriteLine("Rerun $specifyCommand to regenerate $($contract.Name).")
            exit 1
        }
    }
}

# Check for tasks.md if required
if ($RequireTasks -and -not (Test-Path -LiteralPath $paths.TASKS -PathType Leaf)) {
    [Console]::Error.WriteLine("ERROR: tasks.md not found in $($paths.FEATURE_DIR)")
    $tasksCommand = Format-SpecKitCommand -CommandName 'tasks' -RepoRoot $paths.REPO_ROOT
    [Console]::Error.WriteLine("Run $tasksCommand first to create the task list.")
    exit 1
}

# Build list of available documents
$docs = @()

if (Test-Path -LiteralPath $paths.FEATURE_SPEC) { $docs += 'spec.md' }
if (Test-Path -LiteralPath $paths.PROTOTYPE) { $docs += 'prototype.html' }
if (Test-Path -LiteralPath $paths.QUICKSTART) { $docs += 'quickstart.md' }

# Include tasks.md if requested and it exists
if ($IncludeTasks -and (Test-Path -LiteralPath $paths.TASKS)) {
    $docs += 'tasks.md'
}

$templateContent = $null
if ($Template) {
    $templateContent = Resolve-TemplateContent -TemplateName $Template -RepoRoot $paths.REPO_ROOT
    if ($null -eq $templateContent) {
        [Console]::Error.WriteLine("ERROR: Could not resolve required $Template from the template override stack for $($paths.REPO_ROOT)")
        exit 1
    }
}

# Output results
if ($Json) {
    # JSON output
    $result = [ordered]@{
        FEATURE_DIR = $paths.FEATURE_DIR
        AVAILABLE_DOCS = $docs
    }
    if ($Template) {
        $result.TEMPLATE_CONTENT = $templateContent
    }
    [PSCustomObject]$result | ConvertTo-AsciiJson
} else {
    # Text output
    Write-Output "FEATURE_DIR:$($paths.FEATURE_DIR)"
    Write-Output "AVAILABLE_DOCS:"

    # Show status of each contract document.
    # These helpers report their line with Write-Output and ALSO return a
    # bool, both on the Success stream, so 'Out-Null' discarded the report
    # line along with the return value and left AVAILABLE_DOCS empty. Drop
    # only the boolean so the per-document lines reach stdout like the
    # bash and Python twins.
    Test-FileExists -Path $paths.FEATURE_SPEC -Description 'spec.md' | Where-Object { $_ -isnot [bool] }
    Test-FileExists -Path $paths.PROTOTYPE -Description 'prototype.html' | Where-Object { $_ -isnot [bool] }
    Test-FileExists -Path $paths.QUICKSTART -Description 'quickstart.md' | Where-Object { $_ -isnot [bool] }

    if ($IncludeTasks) {
        Test-FileExists -Path $paths.TASKS -Description 'tasks.md' | Where-Object { $_ -isnot [bool] }
    }
}
