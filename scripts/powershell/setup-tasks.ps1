#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$Help,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

$ErrorActionPreference = 'Stop'

# Help wins over unknown-argument validation to match the Bash/Python
# variants, which stop at --help and exit 0.
if ($Help) {
    Write-Output "Usage: setup-tasks.ps1 [-Json] [-Help]"
    exit 0
}

if ($RemainingArgs.Count -gt 0) {
    [Console]::Error.WriteLine("ERROR: Unknown option '$($RemainingArgs[0])'")
    exit 1
}

# Source common functions
. "$PSScriptRoot/common.ps1"

# Get feature paths
$paths = Get-FeaturePathsEnv -ReturnNullOnError
if (-not $paths) {
    [Console]::Error.WriteLine("ERROR: Failed to resolve feature paths")
    exit 1
}

function Assert-NonEmptyFile {
    param(
        [string]$Path,
        [string]$Name
    )
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        [Console]::Error.WriteLine("ERROR: $Name not found in $($paths.FEATURE_DIR)")
        $specifyCommand = Format-SpecKitCommand -CommandName 'specify' -RepoRoot $paths.REPO_ROOT
        [Console]::Error.WriteLine("Run $specifyCommand first to create the frozen requirement contract.")
        return $false
    }
    if ((Get-Item -LiteralPath $Path).Length -eq 0) {
        [Console]::Error.WriteLine("ERROR: $Name is empty in $($paths.FEATURE_DIR)")
        $specifyCommand = Format-SpecKitCommand -CommandName 'specify' -RepoRoot $paths.REPO_ROOT
        [Console]::Error.WriteLine("Rerun $specifyCommand to regenerate $Name.")
        return $false
    }
    return $true
}

if (-not (Assert-NonEmptyFile -Path $paths.FEATURE_SPEC -Name 'spec.md') -or
    -not (Assert-NonEmptyFile -Path $paths.PROTOTYPE -Name 'prototype.html') -or
    -not (Assert-NonEmptyFile -Path $paths.QUICKSTART -Name 'quickstart.md')) {
    exit 1
}

$docs = @('spec.md', 'prototype.html', 'quickstart.md')

# Resolve tasks template through override stack
$tasksTemplate = Resolve-Template -TemplateName 'tasks-template' -RepoRoot $paths.REPO_ROOT
$tasksTemplateContent = Resolve-TemplateContent -TemplateName 'tasks-template' -RepoRoot $paths.REPO_ROOT
if ($null -eq $tasksTemplateContent) {
    [Console]::Error.WriteLine("ERROR: Could not resolve required tasks-template from the template override stack for $($paths.REPO_ROOT)")
    [Console]::Error.WriteLine("Template 'tasks-template' was not found in any supported location (overrides, presets, extensions, or shared core). Add an override at .specify/templates/overrides/tasks-template.md, or run 'specify init' / reinstall shared infra to restore the core .specify/templates/tasks-template.md template.")
    exit 1
}
if ($tasksTemplate -and (Test-Path -LiteralPath $tasksTemplate -PathType Leaf)) {
    $tasksTemplate = (Resolve-Path -LiteralPath $tasksTemplate).Path
} else {
    $tasksTemplate = ''
}

# Output results
if ($Json) {
    [PSCustomObject]@{
        FEATURE_DIR            = $paths.FEATURE_DIR
        FEATURE_SPEC           = $paths.FEATURE_SPEC
        PROTOTYPE              = $paths.PROTOTYPE
        QUICKSTART             = $paths.QUICKSTART
        AVAILABLE_DOCS         = $docs
        TASKS_TEMPLATE         = $tasksTemplate
        TASKS_TEMPLATE_CONTENT = $tasksTemplateContent
    } | ConvertTo-AsciiJson
} else {
    Write-Output "FEATURE_DIR: $($paths.FEATURE_DIR)"
    Write-Output "TASKS_TEMPLATE: $(if ($tasksTemplate) { $tasksTemplate } else { 'not found' })"
    Write-Output "AVAILABLE_DOCS:"
    # These helpers report their line with Write-Output and ALSO return a
    # bool, both on the Success stream, so 'Out-Null' discarded the report
    # line along with the return value and left AVAILABLE_DOCS empty. Drop
    # only the boolean so the per-document lines reach stdout like the
    # bash and Python twins.
    Test-FileExists -Path $paths.FEATURE_SPEC -Description 'spec.md' | Where-Object { $_ -isnot [bool] }
    Test-FileExists -Path $paths.PROTOTYPE -Description 'prototype.html' | Where-Object { $_ -isnot [bool] }
    Test-FileExists -Path $paths.QUICKSTART -Description 'quickstart.md' | Where-Object { $_ -isnot [bool] }
}
