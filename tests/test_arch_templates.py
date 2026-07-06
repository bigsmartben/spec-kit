"""Quality guards for the bundled architecture planning contract extension."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARCHITECTURE_EXTENSION = PROJECT_ROOT / "extensions" / "arch"
TEMPLATES = ARCHITECTURE_EXTENSION / "templates"
COMMANDS = ARCHITECTURE_EXTENSION / "commands"


def _read_template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def test_arch_commands_are_single_planning_contract_surface():
    command_files = sorted(COMMANDS.glob("speckit.arch.*.md"))

    assert [path.name for path in command_files] == [
        "speckit.arch.generate.md",
        "speckit.arch.reverse.md",
    ]

    for command_file in command_files:
        content = command_file.read_text(encoding="utf-8")
        assert "scripts:" in content
        assert ".specify/extensions/arch/scripts/bash/setup-arch.sh --json" in content
        assert ".specify/extensions/arch/scripts/powershell/setup-arch.ps1 -Json" in content
        assert "ARCH_SCHEMA_FILE" in content
        assert "ARCH_VALIDATOR_FILE" in content
        assert "planning_gate" in content
        assert "ready_gate" in content
        assert "BLOCKER" in content
        assert "Write only `ARCH_FILE`" in content
        assert "Do not create, update, or require separate 4+1 view files" in content
        assert ".specify/memory/architecture/" not in content
        assert "__SPECKIT_COMMAND_UC__" not in content


def test_arch_generate_and_reverse_keep_evidence_inside_single_artifact():
    generate = (COMMANDS / "speckit.arch.generate.md").read_text(encoding="utf-8")
    reverse = (COMMANDS / "speckit.arch.reverse.md").read_text(encoding="utf-8")

    assert "Source / Basis" in generate
    assert "Open Architecture Questions" in generate
    assert "instead of inventing planning rules" in generate

    assert "observable repository evidence" in reverse
    assert "Source / Basis" in reverse
    assert "not in a secondary evidence file" in reverse
    assert "Do not create, update, or require `.specify/memory/architecture-repo-facts.md`" in reverse


def test_architecture_template_defines_planning_contract_sections():
    content = _read_template("architecture-template.md")

    for section in [
        "Architecture Intent",
        "Planning Scope Rules",
        "Capability Boundaries",
        "Required Constraints",
        "Architecture Decisions Already Made",
        "Allowed Extension Points",
        "Prohibited Plan Directions",
        "Open Architecture Questions",
        "Plan Review Checklist",
    ]:
        assert f"## {section}" in content

    assert content.count("Source / Basis") == 9
    assert "Planning Status" in content
    assert ".specify/memory/architecture-scenario-view.md" not in content
    assert ".specify/memory/architecture-repo-facts.md" not in content
    assert ".specify/memory/architecture/" not in content


def test_init_next_steps_do_not_list_arch_as_core_workflow():
    init_source = (PROJECT_ROOT / "src" / "specify_cli" / "commands" / "init.py").read_text(
        encoding="utf-8"
    )

    assert "_display_cmd('arch')" not in init_source
    assert '"git",' in init_source
    assert "specify extension add arch" not in init_source


def test_removed_legacy_view_templates_are_not_bundled():
    assert sorted(path.name for path in TEMPLATES.glob("architecture-*.md")) == [
        "architecture-template.md"
    ]


def test_schema_and_validator_enforce_planning_quality_gate():
    schema = (ARCHITECTURE_EXTENSION / "schemas" / "architecture-artifacts.schema.json").read_text(
        encoding="utf-8"
    )
    bash_validator = (
        ARCHITECTURE_EXTENSION / "scripts" / "bash" / "validate-arch-artifacts.sh"
    ).read_text(encoding="utf-8")
    ps_validator = (
        ARCHITECTURE_EXTENSION / "scripts" / "powershell" / "validate-arch-artifacts.ps1"
    ).read_text(encoding="utf-8")

    for content in [schema, bash_validator, ps_validator]:
        assert "ARCH_SOURCE_MISSING" in content
        assert "ARCH_UNSUPPORTED_CONCLUSION" in content
        assert "ARCH_OPEN_QUESTION_STATUS_INVALID" in content

    assert "planningScopeRuleRecord" in schema
    assert "openArchitectureQuestionRecord" in schema
