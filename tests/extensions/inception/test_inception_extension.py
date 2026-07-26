from pathlib import Path

from specify_cli.extensions import ExtensionManifest


REPO_ROOT = Path(__file__).resolve().parents[3]
EXTENSION_DIR = REPO_ROOT / "extensions" / "inception"


def _read(rel_path: str) -> str:
    return (EXTENSION_DIR / rel_path).read_text(encoding="utf-8")


def test_manifest_declares_product_and_architecture_migration_commands():
    manifest = ExtensionManifest(EXTENSION_DIR / "extension.yml")

    assert manifest.id == "inception"
    assert manifest.name == "SDD Inception"
    assert manifest.version == "2.0.0"
    assert [command["name"] for command in manifest.commands] == [
        "speckit.inception.product",
        "speckit.inception.arch",
    ]


def test_product_command_keeps_product_only_outputs():
    product = _read("commands/speckit.inception.product.md")

    for expected in (
        "templates/product/uc-template.md",
        "templates/product/wireflow-medium-template.html",
        "templates/product/wireflow-high-template.html",
        "inception/product/uc.md",
        "inception/product/wireflow-medium.html",
        "inception/product/wireflow-high.html",
    ):
        assert expected in product


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


def test_architecture_command_is_write_free_migration_entrypoint():
    command = _read("commands/speckit.inception.arch.md")
    readme = _read("README.md")

    for expected in (
        "INCEPTION_ARCH_COMMAND_RETIRED",
        "/speckit.constitution",
        "Do not read `inception/product/uc.md` by default",
        "Do not create `inception/arch/`",
        "not a prerequisite or automatic authority",
    ):
        assert expected in command

    assert "write-free compatibility" in readme
    assert "No conventional path is mandatory" in readme


def test_architecture_generation_templates_are_removed():
    arch_templates = EXTENSION_DIR / "templates" / "arch"
    assert not list(arch_templates.glob("*"))

    combined = "\n".join(
        [
            _read("extension.yml"),
            _read("README.md"),
            _read("commands/speckit.inception.arch.md"),
        ]
    )
    for retired in (
        "api-capability-template.md",
        "api-poc-template.md",
        "system-boundary-template.md",
        "domain-model-template.md",
        "arch-template.md",
        "POC_CONFIRMATION_MISSING",
        "POC_RUN_EVIDENCE_MISSING",
    ):
        assert retired not in combined
