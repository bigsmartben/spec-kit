from pathlib import Path


EXTENSION_DIR = Path(__file__).resolve().parents[1]


def test_retired_architecture_entrypoint_is_write_free_and_portable():
    command = (
        EXTENSION_DIR / "commands" / "speckit.inception.arch.md"
    ).read_text(encoding="utf-8")

    assert "INCEPTION_ARCH_COMMAND_RETIRED" in command
    assert "__SPECKIT_COMMAND_CONSTITUTION__" in command
    assert "Do not create `inception/arch/`" in command
    assert "Do not read `inception/product/uc.md` by default" in command
    assert "/speckit." not in command
