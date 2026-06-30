"""Static checks for repository GitHub Actions workflows."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
ISSUE_TEMPLATES_DIR = REPO_ROOT / ".github" / "ISSUE_TEMPLATE"
# Match both the dedicated-step form (`        uses: x@sha`) and the
# inline shorthand (`      - uses: x@sha`) used in catalog-assign.yml.
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*(?P<ref>\S+)", re.MULTILINE)
PINNED_SHA_RE = re.compile(r"@[0-9a-f]{40}$", re.IGNORECASE)
ISSUE_TEMPLATE_LABELS_RE = re.compile(
    r'^labels:\s*\[(?P<labels>[^\]]*)\]\s*$', re.MULTILINE
)


def test_github_actions_are_pinned_to_full_commit_shas():
    unpinned_refs = []

    workflows = sorted(
        list(WORKFLOWS_DIR.glob("*.yml")) + list(WORKFLOWS_DIR.glob("*.yaml"))
    )
    assert workflows

    for workflow in workflows:
        workflow_text = workflow.read_text(encoding="utf-8")
        for match in USES_RE.finditer(workflow_text):
            uses_ref = match.group("ref")
            if uses_ref.startswith(("./", "../")):
                continue
            if PINNED_SHA_RE.search(uses_ref):
                continue
            unpinned_refs.append(f"{workflow.relative_to(REPO_ROOT)}: {uses_ref}")

    assert unpinned_refs == []


def test_pinned_action_ref_accepts_uppercase_hex_sha():
    assert PINNED_SHA_RE.search(
        "actions/example@0123456789ABCDEF0123456789ABCDEF01234567"
    )


def test_catalog_submission_issue_templates_apply_workflow_trigger_labels():
    expected = {
        "extension_submission.yml": "extension-submission",
        "preset_submission.yml": "preset-submission",
    }
    assign_workflow_text = (WORKFLOWS_DIR / "catalog-assign.yml").read_text(
        encoding="utf-8"
    )

    for template_name, required_label in expected.items():
        template_text = (ISSUE_TEMPLATES_DIR / template_name).read_text(
            encoding="utf-8"
        )
        labels_match = ISSUE_TEMPLATE_LABELS_RE.search(template_text)

        assert labels_match is not None
        labels = {
            label.strip().strip('"').strip("'")
            for label in labels_match.group("labels").split(",")
        }
        assert required_label in labels
        assert required_label in assign_workflow_text
