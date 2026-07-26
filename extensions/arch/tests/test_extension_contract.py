from pathlib import Path


EXTENSION_DIR = Path(__file__).resolve().parents[1]


def test_retired_commands_redirect_without_generation_assets():
    for name in ("speckit.arch.generate.md", "speckit.arch.reverse.md"):
        command = (EXTENSION_DIR / "commands" / name).read_text(encoding="utf-8")
        assert "ARCH_COMMAND_RETIRED" in command
        assert "__SPECKIT_COMMAND_CONSTITUTION__" in command
        assert "/speckit." not in command
        assert "Do not write `.specify/memory/architecture.md`" in command

    for retired_path in ("schemas", "scripts", "templates"):
        assert not (EXTENSION_DIR / retired_path).exists()
