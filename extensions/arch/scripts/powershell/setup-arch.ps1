#!/usr/bin/env pwsh
# Setup project-level architecture planning contract artifacts

[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

if ($Help) {
    Write-Output "Usage: ./setup-arch.ps1 [-Json] [-Help]"
    Write-Output "  -Json     Output results in JSON format"
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

function Resolve-ArchitectureTemplate {
    param(
        [Parameter(Mandatory = $true)][string]$TemplateName,
        [Parameter(Mandatory = $true)][string]$RepoRoot
    )

    $override = Join-Path $RepoRoot ".specify/templates/overrides/$TemplateName.md"
    if (Test-Path -LiteralPath $override -PathType Leaf) {
        return $override
    }

    $candidate = Join-Path $RepoRoot ".specify/extensions/arch/templates/$TemplateName.md"
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
        return $candidate
    }

    return $null
}

function Convert-ToPlainPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ($Path -like 'Microsoft.PowerShell.Core\FileSystem::*') {
        return $Path.Substring('Microsoft.PowerShell.Core\FileSystem::'.Length)
    }
    return $Path
}

$repoRoot = Convert-ToPlainPath (Get-RepoRoot)
$archDir = Join-Path $repoRoot ".specify/memory"
$schemaDir = Join-Path $repoRoot ".specify/extensions/arch/schemas"
$scriptDir = Join-Path $repoRoot ".specify/extensions/arch/scripts"
$archSchemaFile = Join-Path $schemaDir "architecture-artifacts.schema.json"
$archValidatorFile = Join-Path $scriptDir "bash/validate-arch-artifacts.sh"
$archValidatorPsFile = Join-Path $scriptDir "powershell/validate-arch-artifacts.ps1"
$archFile = Join-Path $archDir "architecture.md"

New-Item -ItemType Directory -Path $archDir -Force | Out-Null

function Copy-TemplateIfMissing {
    param(
        [Parameter(Mandatory = $true)][string]$TemplateName,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (Test-Path -LiteralPath $Destination -PathType Leaf) {
        return
    }

    $template = Resolve-ArchitectureTemplate -TemplateName $TemplateName -RepoRoot $repoRoot
    if ($template -and (Test-Path -LiteralPath $template -PathType Leaf)) {
        Copy-Item -LiteralPath $template -Destination $Destination -Force
        if ($Json) {
            [Console]::Error.WriteLine("Copied $TemplateName template to $Destination")
        } else {
            Write-Output "Copied $TemplateName template to $Destination"
        }
    } else {
        Write-Warning "$TemplateName template not found"
        New-Item -ItemType File -Path $Destination -Force | Out-Null
    }
}

Copy-TemplateIfMissing -TemplateName "architecture-template" -Destination $archFile

if ($Json) {
    [PSCustomObject]@{
        ARCH_FILE = $archFile
        ARCH_DIR = $archDir
        SCHEMA_DIR = $schemaDir
        ARCH_SCHEMA_FILE = $archSchemaFile
        ARCH_VALIDATOR_FILE = $archValidatorFile
        ARCH_VALIDATOR_PS_FILE = $archValidatorPsFile
    } | ConvertTo-Json -Compress
} else {
    Write-Output "ARCH_FILE: $archFile"
    Write-Output "ARCH_DIR: $archDir"
    Write-Output "SCHEMA_DIR: $schemaDir"
    Write-Output "ARCH_SCHEMA_FILE: $archSchemaFile"
    Write-Output "ARCH_VALIDATOR_FILE: $archValidatorFile"
    Write-Output "ARCH_VALIDATOR_PS_FILE: $archValidatorPsFile"
}
