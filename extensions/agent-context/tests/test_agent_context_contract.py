"""Contract tests for the agent-context extension package."""

import json
from pathlib import Path

import yaml


EXTENSION_DIR = Path(__file__).resolve().parents[1]


def test_agent_context_assets_are_owned_by_the_extension():
    manifest = yaml.safe_load(
        (EXTENSION_DIR / "extension.yml").read_text(encoding="utf-8")
    )
    assert manifest["extension"]["id"] == "agent-context"
    assert manifest["provides"]["commands"] == [
        {
            "name": "speckit.agent-context.update",
            "file": "commands/speckit.agent-context.update.md",
            "description": "Refresh the managed Spec Kit section in the coding agent context file",
        }
    ]

    defaults = json.loads(
        (EXTENSION_DIR / "agent-context-defaults.json").read_text(encoding="utf-8")
    )
    assert defaults
    assert (EXTENSION_DIR / "scripts/bash/update-agent-context.sh").is_file()
    assert (EXTENSION_DIR / "scripts/powershell/update-agent-context.ps1").is_file()
    assert (EXTENSION_DIR / "scripts/python/update_agent_context.py").is_file()
