"""Focused contract checks to keep when copying this Extension scaffold."""

import runpy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_declares_existing_command_files() -> None:
    manifest = yaml.safe_load((ROOT / "extension.yml").read_text(encoding="utf-8"))

    for command in manifest["provides"]["commands"]:
        assert command["name"].startswith(f"speckit.{manifest['extension']['id']}.")
        assert (ROOT / command["file"]).is_file()


def test_commands_expose_execution_contract() -> None:
    manifest = yaml.safe_load((ROOT / "extension.yml").read_text(encoding="utf-8"))

    for command in manifest["provides"]["commands"]:
        content = (ROOT / command["file"]).read_text(encoding="utf-8")
        for heading in (
            "## Goal",
            "## Operating Boundaries",
            "## Validation",
            "## Report",
        ):
            assert heading in content


def test_config_validator_covers_valid_and_invalid_examples() -> None:
    namespace = runpy.run_path(str(ROOT / "validators" / "config_contract.py"))
    validate_config = namespace["validate_config"]
    manifest = yaml.safe_load((ROOT / "extension.yml").read_text(encoding="utf-8"))

    valid = validate_config(manifest["defaults"])
    invalid = validate_config({"feature": {"enabled": "yes"}})

    assert valid == {"status": "PASS", "blockers": []}
    assert invalid["status"] == "BLOCKED"
    assert {blocker["code"] for blocker in invalid["blockers"]} == {
        "MY_EXTENSION_CONFIG_ENABLED_INVALID",
        "MY_EXTENSION_CONFIG_REPORT_MODE_INVALID",
    }
