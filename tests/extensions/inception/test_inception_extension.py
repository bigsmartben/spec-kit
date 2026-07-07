from pathlib import Path

from specify_cli.extensions import ExtensionManifest


REPO_ROOT = Path(__file__).resolve().parents[3]
EXTENSION_DIR = REPO_ROOT / "extensions" / "inception"


def _read(rel_path: str) -> str:
    return (EXTENSION_DIR / rel_path).read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    next_heading = text.find("\n## ", start + len(heading))
    if next_heading == -1:
        return text[start:]
    return text[start:next_heading]


def _assert_markdown_tables_are_rectangular(markdown: str):
    table: list[str] = []
    for line in markdown.splitlines() + [""]:
        if line.startswith("|"):
            table.append(line)
            continue

        if table:
            pipe_count = table[0].count("|")
            assert pipe_count > 1
            assert all(row.count("|") == pipe_count for row in table), table
            table = []


def test_manifest_declares_inception_commands():
    manifest = ExtensionManifest(EXTENSION_DIR / "extension.yml")

    assert manifest.id == "inception"
    assert manifest.name == "SDD Inception"
    assert [command["name"] for command in manifest.commands] == [
        "speckit.inception.product",
        "speckit.inception.arch",
    ]
    assert [command["file"] for command in manifest.commands] == [
        "commands/speckit.inception.product.md",
        "commands/speckit.inception.arch.md",
    ]


def test_commands_reference_templates_and_inception_paths():
    product = _read("commands/speckit.inception.product.md")
    arch = _read("commands/speckit.inception.arch.md")

    for expected in (
        "templates/product/uc-template.md",
        "templates/product/wireflow-medium-template.html",
        "templates/product/wireflow-high-template.html",
        "inception/product/uc.md",
        "inception/product/wireflow-medium.html",
        "inception/product/wireflow-high.html",
    ):
        assert expected in product

    for expected in (
        "templates/arch/api-capability-template.md",
        "templates/arch/api-poc-template.md",
        "templates/arch/system-boundary-template.md",
        "templates/arch/domain-model-template.md",
        "templates/arch/arch-template.md",
        "inception/product/uc.md",
        "inception/arch/api-poc-runs/",
    ):
        assert expected in arch


def test_wireflow_uses_full_fidelity_names_not_abbreviated_files():
    combined = "\n".join(
        [
            _read("extension.yml"),
            _read("README.md"),
            _read("commands/speckit.inception.product.md"),
            _read("templates/product/wireflow-medium-template.html"),
            _read("templates/product/wireflow-high-template.html"),
        ]
    )

    assert "wireflow-medium.html" in combined
    assert "wireflow-high.html" in combined
    assert "wireflow-m.html" not in combined
    assert "wireflow-h.html" not in combined


def test_api_poc_requires_real_run_confirmation_and_evidence():
    arch = _read("commands/speckit.inception.arch.md")
    template = _read("templates/arch/api-poc-template.md")
    combined = arch + "\n" + template

    assert "not pseudocode" in arch
    assert "real code execution evidence" in arch
    assert "Before running any POC code" in arch
    for required in (
        "target capability",
        "validation hypothesis",
        "runtime environment",
        "dependencies",
        "credential/config needs",
        "sample input",
        "external service access",
        "allowed side effects",
        "stop conditions",
    ):
        assert required in combined
    assert "inception/arch/api-poc-runs/<capability-slug>/" in combined
    assert "POC_CONFIRMATION_MISSING" in combined
    assert "POC_RUN_EVIDENCE_MISSING" in combined


def test_api_capability_requires_technology_selection_matrix():
    arch = _read("commands/speckit.inception.arch.md")
    readme = _read("README.md")
    template = _read("templates/arch/api-capability-template.md")
    combined = arch + "\n" + template

    assert "## Technology Selection Matrix" in template
    assert "## Technology Selection Rationale" in template
    assert "technology selection matrix" in readme
    for expected in (
        "Candidate Option",
        "Team Familiarity",
        "POC Required",
        "Recommended Option",
        "Rejected Options",
        "Open Questions",
    ):
        assert expected in template

    for expected in (
        "Extract system capabilities from `uc.md`",
        "Candidate technical options",
        "Recommended option",
        "backup option",
        "tradeoff rationale",
        "TECH_SELECTION_MISSING",
    ):
        assert expected in combined


def test_arch_templates_keep_tables_rectangular_and_blockers_in_quality_gate():
    api_capability = _read("templates/arch/api-capability-template.md")
    api_poc = _read("templates/arch/api-poc-template.md")
    arch_command = _read("commands/speckit.inception.arch.md")

    _assert_markdown_tables_are_rectangular(api_capability)
    _assert_markdown_tables_are_rectangular(api_poc)

    api_capability_gate = _section(api_capability, "## Quality Gate")
    arch_command_gate = _section(arch_command, "## Quality Gates")

    assert "TECH_SELECTION_MISSING" in api_capability_gate
    assert "TECH_SELECTION_MISSING" in arch_command_gate
    assert "POC_CONFIRMATION_MISSING" in _section(api_poc, "## Quality Gate")
    assert "POC_RUN_EVIDENCE_MISSING" in _section(api_poc, "## Quality Gate")


def test_arch_template_excludes_mock_strategy():
    arch_command = _read("commands/speckit.inception.arch.md")
    arch_template = _read("templates/arch/arch-template.md")

    assert "Mock Strategy" not in arch_template
    assert "mock strategy" not in arch_template.lower()
    assert "mock strategy section" in arch_command
    assert "mock boundaries" not in arch_command


def test_arch_template_excludes_standalone_state_model():
    arch_command = _read("commands/speckit.inception.arch.md")
    arch_template = _read("templates/arch/arch-template.md")

    assert "## 11. State Model" not in arch_template
    assert "State Model" not in arch_template
    assert "state ownership, transitions, and invariants" not in arch_template
    assert "Do not expand object state details" in arch_template
    assert "must not include a standalone state model section" in arch_command
    assert "State enumerations, transitions, domain rules, and business invariants belong in `domain-model.md`" in arch_command
    assert "state boundaries" not in arch_command
    assert "For `arch.md`, reference only the domain-model constraints" in arch_command


def test_commands_include_required_blockers_and_scope_guards():
    product = _read("commands/speckit.inception.product.md")
    arch = _read("commands/speckit.inception.arch.md")

    for blocker in (
        "OUTPUT_PATH_MISMATCH",
        "SOURCE_PRIORITY_VIOLATION",
        "SCOPE_LEAK",
        "UNSUPPORTED_INFERENCE",
        "TEMPLATE_BYPASS",
    ):
        assert blocker in product
        assert blocker in arch

    assert "TECH_SELECTION_MISSING" in arch
    assert "EMPTY_PRIMARY_ARTIFACT" in product
    assert "EMPTY_PRIMARY_ARTIFACT" in arch
    assert "spec.md" in product
    assert "plan.md" in arch
    assert "openapi.yaml" in arch
    assert "source code" in arch
