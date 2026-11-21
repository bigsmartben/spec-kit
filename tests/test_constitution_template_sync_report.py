"""Covers #4431: /constitution's Sync Impact Report must be documented as
temporary, review-only material rather than committed governance content.

The Outline step that produces the Sync Impact Report must state that it is
scratch material for human review and is expected to be removed before the
amended constitution file is committed.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
CONSTITUTION_COMMAND = REPO_ROOT / "templates" / "commands" / "constitution.md"
CONSTITUTION_TEMPLATE = REPO_ROOT / "templates" / "constitution-template.md"


def test_sync_impact_report_step_documents_temporary_lifecycle():
    content = CONSTITUTION_COMMAND.read_text(encoding="utf-8")
    step = content.split("Produce a Sync Impact Report", 1)[1].split("\n\n", 1)[0]
    assert "temporary" in step.lower(), (
        "Step 4 must document that the Sync Impact Report is temporary, "
        "review-only material, not governance content"
    )
    assert "removed before" in step.lower() and "committed" in step.lower(), (
        "Step 4 must state the report is expected to be removed before the "
        "amended constitution file is committed"
    )


def test_constitution_command_limits_architecture_to_system_boundaries():
    content = CONSTITUTION_COMMAND.read_text(encoding="utf-8")

    assert "high-level system/subsystem/component boundary" in content
    assert "Defer public contracts" in content
    assert "Write only `.specify/memory/constitution.md`" in content
    assert "architecture section contains no capability" in content


def test_constitution_command_resolves_only_one_scaffold():
    content = CONSTITUTION_COMMAND.read_text(encoding="utf-8")

    assert "`blueprint-template`" not in content
    assert "`contract-template`" not in content
    assert "parse `TEMPLATE_CONTENT` as the active template" in content
    assert "Resolve the constitution scaffold" in content


def test_no_parallel_architecture_template_assets():
    assert not (REPO_ROOT / "templates" / "blueprint-template.md").exists()
    assert not (REPO_ROOT / "templates" / "contract-template.md").exists()

    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "templates/blueprint-template.md" not in pyproject
    assert "templates/contract-template.md" not in pyproject


def test_constitution_architecture_is_only_a_boundary_map():
    command = CONSTITUTION_COMMAND.read_text(encoding="utf-8")
    template = CONSTITUTION_TEMPLATE.read_text(encoding="utf-8")
    architecture = template.split("## Repository Architecture", 1)[1].split(
        "## Governance", 1
    )[0]

    assert "## Repository Architecture" in template
    assert "### Responsibility Boundaries" in architecture
    assert "`SYS-*`" in command
    assert "`SUB-*`" in command
    assert "`CMP-*`" in command
    assert "SYS-" in architecture
    assert "SUB-" in architecture
    assert "CMP-" in architecture
    assert "**Boundary**" in architecture

    for forbidden_heading in (
        "Capability Use Cases",
        "Acceptance Use Cases",
        "Component Sequences",
        "Public Contracts",
        "Architectural Invariants",
        "Traceability",
    ):
        assert forbidden_heading not in architecture

    for forbidden_id in ("CAP-", "ACCEPT-", "SEQ-", "CON-", "INV-"):
        assert forbidden_id not in architecture

    for forbidden_field in (
        "**Depends on**",
        "**Dependency direction rule**",
        "**Version and compatibility**",
        "**Long-term stability need**",
    ):
        assert forbidden_field not in architecture
