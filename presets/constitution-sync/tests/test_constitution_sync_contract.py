"""Contract tests for the constitution-sync preset package."""

from pathlib import Path

import yaml


PRESET_DIR = Path(__file__).resolve().parents[1]


def test_constitution_sync_wrap_is_platform_neutral():
    manifest = yaml.safe_load(
        (PRESET_DIR / "preset.yml").read_text(encoding="utf-8")
    )
    template = manifest["provides"]["templates"][0]
    assert template["name"] == "speckit.constitution"
    assert template["strategy"] == "wrap"

    command = (PRESET_DIR / template["file"]).read_text(encoding="utf-8")
    for forbidden in (
        ".claude/skills",
        ".github/agents",
        ".github/skills",
        "SKILL.md",
    ):
        assert forbidden not in command
    assert ".specify/integrations/" in command
