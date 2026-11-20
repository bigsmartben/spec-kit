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


def test_constitution_command_maintains_single_repository_authority():
    content = CONSTITUTION_COMMAND.read_text(encoding="utf-8")

    assert "single repository authority" in content
    assert "No separate `blueprint.md` authority" in content
    assert "Write only `.specify/memory/constitution.md`" in content
    assert "Do not create or modify `blueprint.md`" in content


def test_constitution_command_resolves_only_one_scaffold():
    content = CONSTITUTION_COMMAND.read_text(encoding="utf-8")

    assert "`blueprint-template`" not in content
    assert "`contract-template`" not in content
    assert "parse `TEMPLATE_CONTENT` as the active template" in content
    assert "single authority scaffold" in content


def test_no_parallel_architecture_template_assets():
    assert not (REPO_ROOT / "templates" / "blueprint-template.md").exists()
    assert not (REPO_ROOT / "templates" / "contract-template.md").exists()

    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "templates/blueprint-template.md" not in pyproject
    assert "templates/contract-template.md" not in pyproject


def test_architecture_structure_lives_in_constitution_template():
    command = CONSTITUTION_COMMAND.read_text(encoding="utf-8")
    template = CONSTITUTION_TEMPLATE.read_text(encoding="utf-8")

    for heading in (
        "### 1. System Capability Use Cases",
        "### 2. System Acceptance Use Cases",
        "### 3. Responsibility Boundaries",
        "### 4. Component Sequences",
        "### 5. Public Contracts",
        "### 6. Architectural Invariants",
        "### 7. Traceability",
        "### 8. Open Architecture Decisions",
    ):
        assert heading in template
        assert heading not in command

    assert "## Repository Blueprint (Architecture SSOT)" in template
    assert "CAP-" in template
    assert "ACCEPT-" in template
    assert "SYS-" in template
    assert "SUB-" in template
    assert "CMP-" in template
    assert "SEQ-" in template
    assert "CON-*" in template
    assert "CON-[CONTRACT_ID]" in template
    assert "INV-" in template
    assert "**Depends on**" in template
    assert "**Dependency direction rule**" in template
    assert "**Long-term stability need**" in template
    assert "Exclude\n  feature-private contracts" in template
