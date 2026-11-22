"""Regression checks for the user-facing Specify prototype."""

from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
SPECIFY_COMMAND = REPO_ROOT / "templates" / "commands" / "specify.md"
PROTOTYPE_TEMPLATE = REPO_ROOT / "templates" / "prototype-template.md"


def test_prototype_template_omits_internal_explanatory_copy():
    text = PROTOTYPE_TEMPLATE.read_text(encoding="utf-8")

    assert "[PAGE PURPOSE]" not in text
    assert "[Replace this scaffold with the exact page structure" not in text
    assert "documented state links" not in text
    assert "<title>[FEATURE NAME] - Prototype</title>" not in text
    assert "<header data-spec-ref" not in text
    assert "[PRIMARY USER TASK]" not in text


def test_specify_keeps_traceability_nonvisual():
    text = SPECIFY_COMMAND.read_text(encoding="utf-8")

    for clause in (
        "Keep visible prototype content limited to copy a product user would see",
        "Never render requirement IDs, prototype anchors, UAT IDs, or internal validation notes",
        "Keep traceability details in nonvisual attributes",
        "Do not turn an internal workflow, ordered acceptance scenario, or UAT into a visible progress navigator",
        "Only add navigation, progress indicators, headers, sidebars, or multi-step layouts when explicitly required by the specification",
        "Do not expose prototype-only controls, sample data buttons, demo modes, debug panels, or state switchers",
        "Do not expose vendor, provider, API, backend, model, recognition-service, or implementation settings as user-facing copy",
        "Show privacy and data-use explanations only for the current action and the exact data it handles",
        "Start from the current user's primary task and design one coherent, production-ready screen",
        "Build a clear hierarchy: task context, current content or input, one primary action, contextual secondary actions, and state feedback",
        "Use progressive disclosure for advanced options, settings, consent, and supporting explanations",
        "Write realistic end-user copy that tells the user what to do, what happens next, and what changed",
    ):
        assert clause in text, f"Missing user-facing prototype boundary: {clause}"

    for traceability_clause in (
        "stable, unique `data-spec-ref`",
        "Every UAT resolves to both requirement and prototype references",
    ):
        assert traceability_clause in text, (
            f"Missing downstream traceability contract: {traceability_clause}"
        )


def test_specify_completion_report_stays_user_focused():
    text = SPECIFY_COMMAND.read_text(encoding="utf-8")
    completion = text.split("## Completion Report", 1)[1].split("## Quick Guidelines", 1)[0]

    assert "Cross-artifact mapping summary" not in completion
    assert "Checklist results summary" not in completion
    assert "prototype preview path" in completion
    assert "Report validation failures in detail" in completion
