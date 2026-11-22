"""Expected file inventory for init defaults."""

DEFAULT_EXTENSION_COMMANDS: tuple[str, ...] = ()


def bundled_personal_default_files(
    integration_key: str,
    *,
    skills_mode: bool = False,
    commands_dir: str | None = None,
    include_registered_commands: bool = True,
) -> list[str]:
    """Return extension files added by default initialization."""
    return []
