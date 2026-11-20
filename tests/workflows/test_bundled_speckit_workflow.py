"""Guards for the bundled Full SDD Cycle workflow."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from specify_cli.workflows.base import RunStatus
from specify_cli.workflows.engine import WorkflowDefinition, validate_workflow
from specify_cli.workflows.step import gate as gate_module

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLED = REPO_ROOT / "workflows" / "speckit" / "workflow.yml"


def test_bundled_speckit_workflow_has_no_unused_scope_input() -> None:
    """Every declared input must be referenced; scope was a dead prompt (#4384)."""
    text = BUNDLED.read_text(encoding="utf-8")
    definition = WorkflowDefinition.from_string(text)
    assert validate_workflow(definition) == []
    assert "scope" not in definition.inputs
    assert "spec" in definition.inputs

    raw = yaml.safe_load(text)
    assert "scope" not in raw.get("inputs", {})
    assert "inputs.scope" not in text

    for step in raw["steps"]:
        args = (step.get("input") or {}).get("args")
        if args is None:
            continue
        assert "inputs.scope" not in str(args)


def test_bundled_sequence_has_only_the_spec_review_gate() -> None:
    raw = yaml.safe_load(BUNDLED.read_text(encoding="utf-8"))

    assert raw["workflow"]["version"] == "1.0.3"
    assert [step["id"] for step in raw["steps"]] == [
        "specify",
        "review-spec",
        "tasks",
        "implement",
    ]
    assert [
        step["command"]
        for step in raw["steps"]
        if step.get("type") != "gate"
    ] == ["speckit.specify", "speckit.tasks", "speckit.implement"]
    assert "speckit_review_plan_verdict" not in raw["inputs"]
    assert "plan" not in BUNDLED.read_text(encoding="utf-8").lower()


def test_verdict_resume(bundled_review, resume_bundled_review) -> None:
    _, state, commands = bundled_review("speckit", "review-spec")
    previous_commands = commands.copy()

    result, resumed = resume_bundled_review(
        state, "speckit_review_spec_verdict", "approve"
    )

    assert result.exit_code == 0, result.output
    assert resumed.step_results["review-spec"]["output"]["choice"] == "approve"
    assert resumed.step_results["review-spec"]["status"] == "completed"
    assert commands[:len(previous_commands)] == previous_commands
    assert commands[len(previous_commands):] == [
        "speckit.tasks",
        "speckit.implement",
    ]
    assert all(commands.count(command) == 1 for command in previous_commands)
    assert resumed.status is RunStatus.COMPLETED


@pytest.mark.parametrize("explicit_empty", [False, True], ids=["omitted", "empty"])
@pytest.mark.parametrize("tty", [False, True], ids=["non-tty", "tty"])
def test_empty_verdict_preserves_review(
    bundled_review, monkeypatch, explicit_empty, tty
) -> None:
    engine, state, commands = bundled_review("speckit", "review-spec")
    previous_commands = commands.copy()
    input_name = "speckit_review_spec_verdict"
    assert state.inputs[input_name] == ""
    prompts = []

    def prompt(message, options):
        prompts.append((message, options))
        return "reject"

    monkeypatch.setattr(
        gate_module, "sys",
        SimpleNamespace(stdin=SimpleNamespace(isatty=lambda: tty)),
    )
    monkeypatch.setattr(gate_module.GateStep, "_prompt", staticmethod(prompt))

    resumed = engine.resume(
        state.run_id, {input_name: ""} if explicit_empty else None
    )

    assert resumed.status is (RunStatus.ABORTED if tty else RunStatus.PAUSED)
    assert len(prompts) == int(tty)
    assert resumed.inputs[input_name] == ""
    assert resumed.step_results["review-spec"]["output"]["choice"] == (
        "reject" if tty else None
    )
    assert commands == previous_commands


@pytest.mark.parametrize("value", ["reject", "maybe", " ", "aPpRoVe"])
def test_bound_verdict_preserves_decisions(
    bundled_review, value
) -> None:
    engine, state, commands = bundled_review("speckit", "review-spec")
    previous_commands = commands.copy()

    resumed = engine.resume(
        state.run_id, {"speckit_review_spec_verdict": value}
    )

    if value == "aPpRoVe":
        assert resumed.step_results["review-spec"]["output"]["choice"] == "approve"
        assert resumed.step_results["review-spec"]["status"] == "completed"
        assert len(commands) > len(previous_commands)
    else:
        expected = RunStatus.ABORTED if value == "reject" else RunStatus.FAILED
        assert resumed.status is expected
        assert commands == previous_commands
        if value == "reject":
            assert resumed.step_results["review-spec"]["output"]["aborted"] is True
        else:
            assert "does not match any configured option" in resumed.error


def test_other_review_verdict_does_not_approve_gate(
    bundled_review
) -> None:
    engine, state, commands = bundled_review("speckit", "review-spec")
    previous_commands = commands.copy()

    resumed = engine.resume(
        state.run_id, {"speckit_review_plan_verdict": "approve"}
    )

    assert resumed.status is RunStatus.PAUSED
    assert resumed.current_step_id == "review-spec"
    assert resumed.step_results["review-spec"]["output"]["choice"] is None
    assert commands == previous_commands
