"""Scaffold regressions for the three-stage Task work-package contract."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TASKS_COMMAND = REPO_ROOT / "templates" / "commands" / "tasks.md"
TASKS_TEMPLATE = REPO_ROOT / "templates" / "tasks-template.md"
IMPLEMENT_COMMAND = REPO_ROOT / "templates" / "commands" / "implement.md"
ANALYZE_COMMAND = REPO_ROOT / "templates" / "commands" / "analyze.md"
CONVERGE_COMMAND = REPO_ROOT / "templates" / "commands" / "converge.md"


def _section(path: Path, start: str, end: str | None = None) -> str:
    text = path.read_text(encoding="utf-8")
    tail = text.split(start, 1)[1]
    if end is not None:
        tail = tail.split(end, 1)[0]
    return " ".join(tail.split())


def test_task_generation_uses_only_the_frozen_specify_contract():
    outline = _section(TASKS_COMMAND, "## Outline", "## Mandatory Post-Execution Hooks")
    for clause in (
        "`spec.md`",
        "`prototype.html`",
        "`quickstart.md`",
        "Treat `spec.md`, `prototype.html`, and `quickstart.md` as read-only",
        "Do not read or infer a technical plan",
        "Implement owns those decisions",
    ):
        assert clause in outline, f"Missing Task input-boundary guidance: {clause}"
    assert "Required**: `plan.md`" not in outline


def test_task_generation_blocks_incomplete_or_conflicting_contracts():
    validation = _section(
        TASKS_COMMAND, "3. **Validate before generation**", "4. **Derive work packages**"
    )
    for clause in (
        "Reject duplicate or malformed source IDs/anchors",
        "Resolve every prototype and requirement reference",
        "Detect contradictions",
        "**STOP**",
        "do not write a new or partial `tasks.md`",
        "Do not invent or repair requirements",
        "`__SPECKIT_COMMAND_SPECIFY__`",
        "`__SPECKIT_COMMAND_CLARIFY__`",
    ):
        assert clause in validation, f"Missing Task blocking rule: {clause}"


def test_task_generation_requires_complete_contract_coverage():
    coverage = _section(
        TASKS_COMMAND, "6. **Prove complete coverage before writing**", "7. **Write `tasks.md`**"
    )
    for clause in (
        "Every `FR-*`",
        "Every `SC-*`",
        "Every `data-spec-ref`",
        "Every `UAT-*`",
        "exactly one `[UAT]`",
        "at least one explicit user story, requirement",
    ):
        assert clause in coverage, f"Missing Task coverage rule: {clause}"


def test_task_format_preserves_technology_neutral_boundaries():
    rules = _section(TASKS_COMMAND, "## Task Generation Rules", "## Done When")
    for clause in (
        "`[BUILD]`",
        "`[UAT]`",
        "source references",
        "completion conditions",
        "framework",
        "repository file path",
        "Implement owns the paths",
    ):
        assert clause in rules, f"Missing Task format rule: {clause}"


def test_task_template_has_coverage_and_uat_sections():
    text = " ".join(TASKS_TEMPLATE.read_text(encoding="utf-8").split())
    for clause in (
        "## Contract Coverage",
        "| Source Kind | Source ID | Task IDs | Coverage Note |",
        "## Phase [N+1]: UAT Execution",
        "Execute UAT-001",
        "Status: PASS",
        "Every UAT must have exactly one `[UAT]` task",
        "chooses the technical approach, repository paths, and testing mechanisms",
    ):
        assert clause in text, f"Missing Task template structure: {clause}"


def test_analyze_checks_all_contract_inventory_and_no_legacy_plan_artifact():
    text = " ".join(ANALYZE_COMMAND.read_text(encoding="utf-8").split())
    for clause in (
        "`spec.md`, `prototype.html`, `quickstart.md`, and `tasks.md`",
        "**Prototype-anchor inventory**",
        "**UAT inventory**",
        "Every prototype anchor with zero associated `[BUILD]` task",
        "Every UAT with no `[BUILD]` coverage",
        "Keyword inference never counts as coverage",
    ):
        assert clause in text, f"Missing Analyze contract rule: {clause}"
    assert "spec.md, plan.md, and tasks.md" not in text
    assert "data-model.md + `Entity.field`" not in text


def test_implement_executes_uat_and_updates_only_result_fields():
    text = " ".join(IMPLEMENT_COMMAND.read_text(encoding="utf-8").split())
    for clause in (
        "**REQUIRED**: Read prototype.html",
        "**REQUIRED**: Read quickstart.md",
        "**Choose the technical approach**",
        "**Execute `[UAT]` tasks**",
        "Preserve all baseline fields verbatim",
        "Set `Status` to `PASS`, `FAIL`, or `BLOCKED`",
        "Actual Result", "Evidence", "Deviation",
        "leave failed/blocked work unchecked",
    ):
        assert clause in text, f"Missing Implement/UAT rule: {clause}"
    assert "**REQUIRED**: Read plan.md" not in text


def test_implement_handles_scoped_and_blocked_runs_without_claiming_full_completion():
    text = " ".join(IMPLEMENT_COMMAND.read_text(encoding="utf-8").split())
    for clause in (
        "Select the invocation scope from `$ARGUMENTS`",
        "Leave out-of-scope tasks and their UAT entries unchanged",
        "A scoped run is complete only when",
        "Do not treat `FAIL` or `BLOCKED` as task completion",
        "return the issue to `__SPECKIT_COMMAND_SPECIFY__`",
        "regenerate the dependent tasks",
    ):
        assert clause in text, f"Missing Implement scope/failure rule: {clause}"
    assert "Verify all required tasks are completed" not in text
    assert "All tasks in tasks.md completed and marked `[X]`" not in text


def test_converge_uses_contract_and_uat_state_without_plan():
    text = " ".join(CONVERGE_COMMAND.read_text(encoding="utf-8").split())
    for clause in (
        "frozen `spec.md`, `prototype.html`, and `quickstart.md`",
        "Treat every `PENDING`, `FAIL`, or `BLOCKED` UAT as remaining work",
        "prototype anchor, UAT outcome",
        "Never rewrite the UAT baseline in Converge",
    ):
        assert clause in text, f"Missing Converge contract rule: {clause}"
    assert "spec, plan, and tasks" not in text
