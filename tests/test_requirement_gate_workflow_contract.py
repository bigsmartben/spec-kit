"""Contract tests for requirement gates and plan-stage materialization (#61)."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_checklist_is_spec_only_and_never_writes_readiness_artifacts() -> None:
    command = _read("templates/commands/checklist.md")

    assert "check-prerequisites.sh --json --paths-only" in command
    assert "check-prerequisites.ps1 -Json -PathsOnly" in command
    assert "Do not read `plan.md` or `tasks.md`" in command
    assert "Never create\n`planning-readiness.md`" in command
    assert "`checklists/behavior-testability.md`" in command
    assert "Regeneration is recomputation, not append-only" in command


def test_requirement_gate_metadata_and_blocker_routes_are_stable() -> None:
    checklist = _read("templates/checklist-template.md")
    command = _read("templates/commands/checklist.md")

    for field in (
        "**Stage**:",
        "**Domain**:",
        "**Gate**:",
        "**Applicability**:",
        "**Status**:",
        "**Spec Revision**:",
    ):
        assert field in checklist
    assert "[blocker:product-decision]" in command
    assert "[blocker:provider-evidence]" in command
    assert "[return:intake]" in command


def test_specify_hands_off_to_checklist_instead_of_plan() -> None:
    command = _read("templates/commands/specify.md")
    frontmatter = command.split("---", 2)[1]

    assert "agent: speckit.checklist" in frontmatter
    assert "agent: speckit.plan" not in frontmatter


def test_clarify_repairs_product_gaps_but_preserves_provider_blockers() -> None:
    command = _read("templates/commands/clarify.md")

    assert "Prioritize unchecked `[blocker:product-decision]`" in command
    assert "Never turn `[blocker:provider-evidence]` items into product questions" in command
    assert "Update by stable CHK ID" in command
    assert "Do not create\n      `planning-readiness.md`" in command


def test_plan_runs_gate_preflight_before_materialization_and_hooks() -> None:
    command = _read("templates/commands/plan.md")

    assert "setup-plan.sh --json --paths-only" in command
    assert "setup-plan.ps1 -Json -PathsOnly" in command
    assert command.index("## Requirement Gate Preflight") < command.index(
        "## Pre-Execution Checks"
    )
    assert command.index("## Pre-Execution Checks") < command.index(
        "1. **Materialize plan**"
    )
    assert "Do not run hooks, create directories, copy/touch `plan.md`" in command
    assert "Create Checklist" not in command


def test_builtin_workflow_uses_requirement_gate_order() -> None:
    workflow = yaml.safe_load(_read("workflows/speckit/workflow.yml"))
    step_ids = [step["id"] for step in workflow["steps"]]

    assert step_ids.index("specify") < step_ids.index("checklist")
    assert step_ids.index("checklist") < step_ids.index("clarify")
    assert step_ids.index("clarify") < step_ids.index("plan")
