"""Quality guards for the bundled Architecture migration extension."""

from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARCH_EXTENSION = PROJECT_ROOT / "extensions" / "arch"
COMMANDS = ARCH_EXTENSION / "commands"


def test_arch_snapshot_is_the_v3_migration_release():
    manifest = yaml.safe_load((ARCH_EXTENSION / "extension.yml").read_text(encoding="utf-8"))

    assert manifest["extension"]["id"] == "arch"
    assert manifest["extension"]["name"] == "Architecture Command Migration"
    assert manifest["extension"]["version"] == "3.0.1"
    assert [command["name"] for command in manifest["provides"]["commands"]] == [
        "speckit.arch.generate",
        "speckit.arch.reverse",
    ]


def test_arch_commands_are_write_free_compatibility_entrypoints():
    command_files = sorted(COMMANDS.glob("speckit.arch.*.md"))

    assert [path.name for path in command_files] == [
        "speckit.arch.generate.md",
        "speckit.arch.reverse.md",
    ]

    for command_file in command_files:
        content = command_file.read_text(encoding="utf-8")
        assert "ARCH_COMMAND_RETIRED" in content
        assert "__SPECKIT_COMMAND_CONSTITUTION__" in content
        assert "/speckit." not in content
        assert "Do not write `.specify/memory/architecture.md`" in content
        assert "scripts:" not in content
        assert "PoC" not in content


def test_arch_generation_assets_are_not_bundled():
    for retired_path in ("schemas", "scripts", "templates"):
        assert not (ARCH_EXTENSION / retired_path).exists()


def test_init_next_steps_do_not_list_arch_as_core_workflow():
    init_source = (PROJECT_ROOT / "src" / "specify_cli" / "commands" / "init.py").read_text(
        encoding="utf-8"
    )

    assert "_display_cmd('arch')" not in init_source
    assert "specify extension add arch" not in init_source
