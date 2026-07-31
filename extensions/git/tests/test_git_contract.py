"""Contract tests for the git extension package."""

import json
from pathlib import Path

import yaml


EXTENSION_DIR = Path(__file__).resolve().parents[1]


def test_git_config_template_matches_declared_schema_surface():
    manifest = yaml.safe_load(
        (EXTENSION_DIR / "extension.yml").read_text(encoding="utf-8")
    )
    config = manifest["provides"]["config"][0]
    assert config["template"] == "config-template.yml"
    assert config["schema"] == "config.schema.json"

    template = yaml.safe_load(
        (EXTENSION_DIR / config["template"]).read_text(encoding="utf-8")
    )
    schema = json.loads(
        (EXTENSION_DIR / config["schema"]).read_text(encoding="utf-8")
    )
    assert set(template) <= set(schema["properties"])
    assert template["branch_numbering"] in {"sequential", "timestamp"}
    assert template["commit_style"] in {"fixed", "conventional"}


def test_git_manifest_declares_existing_canonical_commands():
    manifest = yaml.safe_load(
        (EXTENSION_DIR / "extension.yml").read_text(encoding="utf-8")
    )
    commands = manifest["provides"]["commands"]
    for command in commands:
        path = EXTENSION_DIR / command["file"]
        assert path.name == f"{command['name']}.md"
        assert path.is_file()
