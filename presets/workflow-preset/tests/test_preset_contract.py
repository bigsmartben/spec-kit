from __future__ import annotations

import unittest
import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from validators.speckit_behavior_contract import (
    validate_behavior_case_coverage,
    validate_behavior_contract_bundle,
    validate_behavior_draft_contract,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PRESET_PATH = REPO_ROOT / "preset.yml"
README_PATH = REPO_ROOT / "README.md"
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"
CROSS_AGENT_PROTOCOL_PATH = REPO_ROOT / "tests" / "contracts" / "speckit-cross-agent-protocol.md"
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
EXTENSION_GOVERNANCE_PATH = REPO_ROOT / "docs" / "extension-governance.md"
SPECIFY_COMMAND_PATH = REPO_ROOT / "commands" / "speckit.specify.md"
CLARIFY_COMMAND_PATH = REPO_ROOT / "commands" / "speckit.clarify.md"
CHECKLIST_COMMAND_PATH = REPO_ROOT / "commands" / "speckit.checklist.md"
CONSTITUTION_COMMAND_PATH = REPO_ROOT / "commands" / "speckit.constitution.md"
ANALYZE_COMMAND_PATH = REPO_ROOT / "commands" / "speckit.analyze.md"
PLAN_COMMAND_PATH = REPO_ROOT / "commands" / "speckit.plan.md"
TASKS_COMMAND_PATH = REPO_ROOT / "commands" / "speckit.tasks.md"
IMPLEMENT_COMMAND_PATH = REPO_ROOT / "commands" / "speckit.implement.md"
CONSTITUTION_TEMPLATE_PATH = REPO_ROOT / "templates" / "constitution-template.md"
PLAN_TEMPLATE_PATH = REPO_ROOT / "templates" / "plan-template.md"
SPEC_TEMPLATE_PATH = REPO_ROOT / "templates" / "spec-template.md"
REQUIREMENTS_DEV_PATH = REPO_ROOT / "requirements-dev.txt"
BEHAVIOR_SCHEMA_PATHS = {
    "speckit.behavior.scenarios.draft.v1": REPO_ROOT
    / "schemas"
    / "speckit.behavior.scenarios.draft.v1.schema.json",
    "speckit.behavior.uif.intent.v1": REPO_ROOT
    / "schemas"
    / "speckit.behavior.uif.intent.v1.schema.json",
    "speckit.behavior.data_fixtures.intent.v1": REPO_ROOT
    / "schemas"
    / "speckit.behavior.data-fixtures.intent.v1.schema.json",
    "speckit.behavior.uif.expected.v1": REPO_ROOT
    / "schemas"
    / "speckit.behavior.uif.expected.v1.schema.json",
    "speckit.behavior.scenario_instances.v1": REPO_ROOT
    / "schemas"
    / "speckit.behavior.scenario-instances.v1.schema.json",
    "speckit.behavior.data_fixtures.v1": REPO_ROOT
    / "schemas"
    / "speckit.behavior.data-fixtures.v1.schema.json",
    "speckit.behavior.assertions.v1": REPO_ROOT
    / "schemas"
    / "speckit.behavior.assertions.v1.schema.json",
}
BEHAVIOR_TEMPLATE_PATHS = {
    "behavior-bdd-draft-template": REPO_ROOT / "templates" / "behavior" / "bdd-draft.feature",
    "behavior-scenarios-draft-template": REPO_ROOT
    / "templates"
    / "behavior"
    / "behavior-scenarios-draft.json",
    "behavior-uif-intent-template": REPO_ROOT / "templates" / "behavior" / "uif-intent.json",
    "behavior-data-fixtures-intent-template": REPO_ROOT
    / "templates"
    / "behavior"
    / "data-fixtures-intent.json",
    "behavior-testability-checklist-template": REPO_ROOT
    / "templates"
    / "behavior"
    / "behavior-testability-checklist.md",
    "behavior-bdd-contract-template": REPO_ROOT / "templates" / "behavior" / "bdd-contract.feature",
    "behavior-uif-expected-template": REPO_ROOT / "templates" / "behavior" / "uif-expected.json",
    "behavior-scenario-instances-template": REPO_ROOT
    / "templates"
    / "behavior"
    / "scenario-instances.json",
    "behavior-data-fixtures-template": REPO_ROOT / "templates" / "behavior" / "data-fixtures.json",
    "behavior-assertions-template": REPO_ROOT / "templates" / "behavior" / "assertions.json",
}

FEATURE_PATH = "specs/001-demo"












def minimal_behavior_scenarios_draft(
    *,
    scenario_id: str = "SCN-001",
    scenario_type: str = "positive",
) -> dict:
    return {
        "contract_type": "speckit.behavior.scenarios.draft.v1",
        "feature": "refund-application",
        "scenarios": [
            {
                "id": scenario_id,
                "title": "Submit refund",
                "type": scenario_type,
                "given": ["FIX-BUYER"],
                "when": ["click_refund", "submit_refund"],
                "then": ["show_refund_submitted"],
                "source": "plan-phase-0",
            }
        ],
    }


def minimal_uif_intent() -> dict:
    return {
        "contract_type": "speckit.behavior.uif.intent.v1",
        "feature": "refund-application",
        "intents": [
            {
                "id": "UIF-INTENT-001",
                "start_view": "OrderDetailPage",
                "events": [{"name": "submit_refund", "label": "Submit refund"}],
                "expected_feedback": ["Refund submitted"],
                "possible_transition_types": ["local_route", "api_call"],
            }
        ],
    }


def minimal_data_fixtures_intent() -> dict:
    return {
        "contract_type": "speckit.behavior.data_fixtures.intent.v1",
        "fixtures": [
            {
                "id": "FIX-BUYER",
                "description": "Buyer user",
                "required_for": ["SCN-001"],
                "required_states": {"user.role": "buyer"},
            }
        ],
    }


def minimal_uif_expected() -> dict:
    return {
        "contract_type": "speckit.behavior.uif.expected.v1",
        "id": "UIF-001",
        "source": "behavior/uif.intent.json",
        "type": "expected",
        "start_view": {"id": "VIEW-ORDER-DETAIL", "name": "Order detail"},
        "steps": [
            {"id": "EVT-SUBMIT-REFUND", "type": "user_event", "label": "Submit refund"},
            {"type": "api_call", "api": {"method": "POST", "path": "/orders/{orderId}/refund"}},
        ],
        "feedback_candidates": [
            {"id": "FB-SUCCESS", "type": "toast", "message": "Refund submitted"}
        ],
    }


def minimal_behavior_scenario_instances() -> dict:
    return {
        "contract_type": "speckit.behavior.scenario_instances.v1",
        "scenarios": [
            {
                "id": "SCN-001",
                "title": "Submit refund",
                "type": "positive",
                "uif_path_id": "UIF-001",
                "fixture_ids": ["FIX-BUYER"],
                "request_case": {"id": "REQ-001", "reason": "QUALITY_ISSUE"},
                "expected_response": {"business_code": "SUCCESS"},
                "expected_feedback": {"message": "Refund submitted"},
                "assertion_ids": ["AST-001"],
            }
        ],
    }


def minimal_exception_behavior_scenario_instances(*, scenario_type: str = "permission") -> dict:
    instances = minimal_behavior_scenario_instances()
    scenario = instances["scenarios"][0]
    scenario["id"] = "SCN-ERR-001"
    scenario["title"] = "Reject refund request"
    scenario["type"] = scenario_type
    scenario["request_case"] = {
        "id": "REQ-ERR-001",
        "case_kind": scenario_type,
        "outcome": "failure",
        "trigger": "submit_refund_without_required_permission",
    }
    scenario["expected_response"] = {
        "business_code": "REJECTED",
        "status": 403,
        "error_code": "ERR_PERMISSION_DENIED",
    }
    scenario["expected_feedback"] = {
        "type": "inline_error",
        "message": "Permission denied",
    }
    scenario["assertion_ids"] = ["AST-001"]
    return instances


def minimal_case_coverage() -> dict:
    return {
        "case_coverage": [
            {
                "story": "Refund request",
                "case_id": "CASE-001",
                "case_type": "permission",
                "status": "Required",
                "source": "spec.md#user-story-1",
                "scenario_id": "SCN-ERR-001",
            }
        ]
    }


def minimal_case_coverage_with_blocker() -> dict:
    return {
        "case_coverage": [
            {
                "story": "Refund request",
                "case_id": "CASE-002",
                "case_type": "validation",
                "status": "Required",
                "source": "spec.md#user-story-1",
                "blocker_id": "BLK-001",
            }
        ]
    }


def minimal_behavior_data_fixtures() -> dict:
    return {
        "contract_type": "speckit.behavior.data_fixtures.v1",
        "fixtures": [
            {
                "id": "FIX-BUYER",
                "name": "Buyer user",
                "entities": ["user"],
                "required_states": {"user.role": "buyer"},
                "constraints": [],
                "setup_strategy": "factory",
            }
        ],
    }


def minimal_behavior_assertions() -> dict:
    return {
        "contract_type": "speckit.behavior.assertions.v1",
        "assertions": [
            {
                "id": "AST-001",
                "target": "refund.status",
                "operator": "equals",
                "expected": "PENDING",
            }
        ],
    }


def minimal_exception_behavior_assertions() -> dict:
    return minimal_exception_behavior_assertions_with_intent("state_invariant")


def minimal_exception_behavior_assertions_with_intent(intent: str) -> dict:
    assertions = minimal_behavior_assertions()
    assertions["assertions"][0]["intent"] = intent
    return assertions


class PresetContractTests(unittest.TestCase):

    def test_preset_manifest_contract(self) -> None:
        data = yaml.safe_load(PRESET_PATH.read_text(encoding="utf-8"))
        entries = {entry["name"]: entry for entry in data["provides"]["templates"]}

        self.assertEqual("1.3.12", data["preset"]["version"])
        self.assertEqual(
            "Behavior-first specification, design-aware planning, and scoped change governance",
            data["preset"]["description"],
        )
        self.assertEqual(["behavior", "bdd", "planning", "implementation"], data["tags"])
        self.assertEqual(28, len(entries))
        self.assertEqual(
            "Execute the implementation plan defined in tasks.md",
            entries["speckit.implement"]["description"],
        )
        self.assertEqual("replace", entries["speckit.implement"]["strategy"])
        for name, path in (
            ("speckit-implement-manifest-v1-schema", "speckit.implement.manifest.v1.schema.json"),
            ("speckit-implement-handoff-v2-schema", "speckit.implement.handoff.v2.schema.json"),
            ("speckit-implement-receipt-v1-schema", "speckit.implement.receipt.v1.schema.json"),
        ):
            self.assertNotIn(name, entries)
            self.assertFalse((REPO_ROOT / "schemas" / path).exists())

    def test_implement_command_uses_standard_single_session_workflow(self) -> None:
        command = IMPLEMENT_COMMAND_PATH.read_text(encoding="utf-8")

        self.assertIn(
            "Execute the implementation plan by processing and executing all tasks defined in tasks.md",
            command,
        )
        self.assertIn("scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks", command)
        self.assertIn("## Pre-Execution Checks", command)
        self.assertIn("## Mandatory Post-Execution Hooks", command)
        self.assertIn("mark the task off as [X] in the tasks file", command)
        for forbidden in (
            "Core Agent",
            "Vertical Planner Agent",
            "Worker Agent",
            "handoff",
            "context_digest",
            "allowed_write_paths",
            "Manual Worker Queue",
        ):
            self.assertNotIn(forbidden, command)

    def test_plan_command_wrapper_contract(self) -> None:
        command = PLAN_COMMAND_PATH.read_text(encoding="utf-8")

        self.assertIn("{CORE_TEMPLATE}", command)
        self.assertIn("class-diagram.md", command)
        self.assertIn("contracts/sequences.md", command)
        self.assertNotIn("test-plan.md", command)
        self.assertIn("strategy: wrap", command)
        self.assertIn("Generate design artifacts only when the feature requires internal object design or cross-boundary sequence constraints", command)
        self.assertIn("Keep `plan.md` as summary/navigation", command)
        self.assertIn("validation decisions belong in `research.md`", command)
        self.assertIn("executable validation paths belong in `quickstart.md`", command)
        self.assertIn("final report must list generated artifacts", command)
        self.assertIn("Plan Agent Topology", command)
        self.assertIn(
            "Follow cross-agent protocol profile: `speckit.plan.stage_local_planning`",
            command,
        )
        self.assertIn("Plan Core Agent", command)
        for agent_role in (
            "Behavior Projection Agent",
            "Formal Contract Agent",
            "Design Artifact Agent",
            "Validation Planning Agent",
            "UI/UX Planning Agent",
        ):
            self.assertIn(agent_role, command)
        self.assertIn("Each payload declares assigned scope, allowed reads, allowed sections, and output contract", command)
        self.assertIn("rather than subagent conversation history", command)
        self.assertNotIn("speckit.tasks", command)
        self.assertNotIn("speckit.implement", command)

    def test_plan_template_navigation_contract(self) -> None:
        template = PLAN_TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn("{CORE_TEMPLATE}", template)
        self.assertIn("## Design Artifacts", template)
        self.assertIn("./class-diagram.md", template)
        self.assertIn("./contracts/sequences.md", template)
        self.assertNotIn("test-plan.md", template)
        self.assertIn("./data-model.md", template)
        self.assertIn("./contracts/", template)
        self.assertIn("./quickstart.md", template)

    def test_plan_ui_ux_substage_enhancement_contract(self) -> None:
        command = PLAN_COMMAND_PATH.read_text(encoding="utf-8")
        template = PLAN_TEMPLATE_PATH.read_text(encoding="utf-8")
        readme = README_PATH.read_text(encoding="utf-8")
        governance = EXTENSION_GOVERNANCE_PATH.read_text(encoding="utf-8")

        for term in (
            "UI/UX Planning Responsibilities",
            "accepted `UI-###` and `UX-###` requirements",
            "Applicability is `Required` and Readiness is `Ready`",
            "return to `/speckit.checklist` or `/speckit.clarify`",
            "Do not project `Not Applicable` rows",
            "interaction tradeoffs",
            "viewport support",
            "accessibility approach",
            "Reference the applicable `UI-###` or `UX-###` requirement IDs",
            "UI interaction sequences",
            "responsive branch triggers",
            "executable acceptance paths",
        ):
            self.assertIn(term, command)

        for term in (
            "UI/UX Planning Navigation",
            "UI/UX planning decisions: `./research.md`",
            "Interaction contracts: `./contracts/uif/` and `./contracts/behavior/`",
            "Cross-boundary UI flows: `./contracts/sequences.md`",
            "UI/UX acceptance paths: `./quickstart.md`",
        ):
            self.assertIn(term, template)

        for document in (readme, governance):
            self.assertIn("research.md", document)
            self.assertIn("UI/UX", document)
            self.assertIn("contracts", document)
            self.assertIn("contracts/sequences.md", document)

        self.assertIn(
            "fixed R/M/U/O model: R is Repository / Workspace, M is Module / Capability, U is Unit / Design Object, and O is Operation / Detail",
            readme,
        )
        self.assertIn(
            "Blocks constitution writes when a generated draft changes the fixed R/M/U/O mapping",
            readme,
        )
        self.assertIn(
            "Routes architecture decisions, domain facts, object design, flows, and interface contracts to architecture SSOT artifacts instead of embedding concrete implementation content in ratified constitution principles",
            readme,
        )

    def test_constitution_change_scope_granularity_contract(self) -> None:
        command = CONSTITUTION_COMMAND_PATH.read_text(encoding="utf-8")
        template = CONSTITUTION_TEMPLATE_PATH.read_text(encoding="utf-8")

        exact_mapping = [
            "R: Repository / Workspace. Environment only; too broad for scoped changes.",
            "M: Module / Capability. Hard outer boundary.",
            "U: Unit / Design Object. Primary planning boundary.",
            "O: Operation / Detail. Execution detail.",
        ]
        forbidden_mapping_drift = [
            "R, Requirement",
            "R: Requirement",
            "M, Model",
            "M: Model",
            "U, User/API Interface",
            "U: User/API Interface",
            "O, Operations",
            "O: Operations",
        ]

        for document in (command, template):
            self.assertIn("{CORE_TEMPLATE}", document)
            self.assertIn("Change Scope Granularity", document)
            self.assertIn("R/M/U/O", document)
            self.assertIn("Planning locks M + U", document)
            for mapping in exact_mapping:
                self.assertIn(mapping, document)
            for forbidden in forbidden_mapping_drift:
                self.assertNotIn(forbidden, document)

        self.assertIn("strategy: wrap", command)
        self.assertIn("Spec Kit planning and execution MUST use R/M/U/O scope granularity", template)
        self.assertIn("This principle applies from planning onward", template)
        self.assertIn("Requirement specification, clarification, and checklist readiness MUST NOT infer M/U/O boundaries", template)
        self.assertIn("preserve the Change Scope Granularity principle", command)
        self.assertIn("must not remove, weaken, or contradict", command)
        self.assertIn("The R/M/U/O letter mapping is fixed and MUST remain exact", command)
        self.assertIn("preserves the exact R/M/U/O letter mapping", command)
        self.assertIn("CONSTITUTION_RMUO_MAPPING_DRIFT", command)
        self.assertIn("CONSTITUTION_TEMPLATE_STATUS_UNCHECKED", command)
        self.assertIn("do not report it as missing", command)
        self.assertIn("do not treat that as the workflow-preset template being absent", command)
        self.assertIn("Architecture SSOT Boundary", command)
        self.assertIn("Architecture SSOT Compliance", command)
        self.assertIn("Ratified constitution principles must be durable governance rules, not architecture fact storage", command)
        self.assertIn(
            "Architecture decisions, domain facts, object design, flows, and interface contracts belong in their architecture SSOT artifacts",
            command,
        )
        self.assertIn("specs/<feature>/data-model.md", command)
        self.assertIn("specs/<feature>/class-diagram.md", command)
        self.assertIn("specs/<feature>/contracts/sequences.md", command)
        self.assertIn("specs/<feature>/contracts/", command)
        self.assertIn("specs/<feature>/research.md", command)
        self.assertIn(
            "MUST NOT capture, discover, extract, migrate, store, validate, or repair architecture facts",
            command,
        )
        self.assertIn("do not embed them in ratified principles", command)
        self.assertIn("name the responsible workflow-preset SSOT artifact type", command)
        self.assertIn("Do not write concrete `specs/<feature>/...` paths", command)
        self.assertIn("check those paths", command)
        self.assertIn("create or update those artifacts", command)
        self.assertIn("CONSTITUTION_ARCH_SSOT_GAP", command)
        self.assertIn("copy concrete implementation facts", command)
        self.assertIn("Planning outputs MUST comply with existing Architecture SSOT artifacts", command)
        self.assertIn("MUST NOT contradict, relocate, weaken, or silently replace architecture SSOT content", command)
        self.assertIn("requires planning outputs to comply with existing Architecture SSOT artifacts", command)
        self.assertIn(
            "routes architecture decisions, domain facts, object design, flows, and interface contracts to workflow-preset SSOT artifact types",
            command,
        )
        self.assertNotIn("unless the current Spec Kit context already provides an existing feature path", command)
        self.assertNotIn("required existing SSOT path is absent", command)
        self.assertIn("The R/M/U/O letter mapping is fixed", template)
        self.assertIn("Architecture SSOT Boundary", template)
        self.assertIn("Architecture SSOT Compliance", template)
        self.assertIn("Ratified constitution principles are durable governance rules, not architecture fact storage", template)
        self.assertIn(
            "Architecture decisions, domain facts, object design, flows, and interface contracts belong in their architecture SSOT artifacts",
            template,
        )
        self.assertIn("specs/<feature>/data-model.md", template)
        self.assertIn("specs/<feature>/class-diagram.md", template)
        self.assertIn("specs/<feature>/contracts/sequences.md", template)
        self.assertIn("specs/<feature>/contracts/", template)
        self.assertIn("specs/<feature>/research.md", template)
        self.assertIn("may reference these SSOT artifact types", template)
        self.assertIn(
            "must not copy concrete implementation facts, temporary repository observations, or module responsibility inventories",
            template,
        )
        self.assertIn("Planning outputs MUST comply with existing Architecture SSOT artifacts", template)
        self.assertIn("Planning MUST NOT contradict, relocate, weaken, or silently replace architecture SSOT content", template)

    def test_change_scope_granularity_stage_references(self) -> None:
        plan = PLAN_COMMAND_PATH.read_text(encoding="utf-8")
        tasks = TASKS_COMMAND_PATH.read_text(encoding="utf-8")
        analyze = ANALYZE_COMMAND_PATH.read_text(encoding="utf-8")
        implement = IMPLEMENT_COMMAND_PATH.read_text(encoding="utf-8")

        self.assertIn("Apply the constitution's Change Scope Granularity principle.", plan)
        self.assertIn("During planning, lock the change scope to `M + U`", plan)
        self.assertIn("Do not lock operation-level implementation details or concrete write paths.", plan)
        self.assertNotIn("Architecture SSOT Compliance", plan)
        self.assertNotIn("PLANNING_ARCH_SSOT_CONFLICT", plan)

        self.assertIn("Preserve the planned `M + U` scope", tasks)
        self.assertIn("Do not generate execution metadata or write-path fields.", tasks)

        self.assertIn("Check that tasks preserve the planned `M + U` scope.", analyze)
        self.assertIn("Report missing, widened, or ambiguous scope boundaries as blockers.", analyze)

        self.assertIn("Read plan.md for tech stack, architecture, and file structure", implement)
        self.assertIn("Respect dependencies", implement)

    def test_preplanning_commands_do_not_infer_scope_granularity(self) -> None:
        for path in (SPECIFY_COMMAND_PATH, CLARIFY_COMMAND_PATH, CHECKLIST_COMMAND_PATH):
            command = path.read_text(encoding="utf-8")
            for forbidden in (
                "Change Scope Granularity",
                "R/M/U/O",
                "M + U",
                "U -> concrete paths",
                "module/capability plus design object",
                "concrete write paths",
                "allowed_write_paths",
                "context_gaps",
            ):
                self.assertNotIn(forbidden, command, f"{path} contains {forbidden}")

    def test_tasks_command_wrapper_contract(self) -> None:
        tasks = TASKS_COMMAND_PATH.read_text(encoding="utf-8")

        self.assertIn("{CORE_TEMPLATE}", tasks)
        self.assertIn("class-diagram.md", tasks)
        self.assertIn("contracts/sequences.md", tasks)
        self.assertNotIn("test-plan.md", tasks)
        self.assertIn("strategy: wrap", tasks)
        self.assertIn("implementation, integration, orchestration", tasks)
        self.assertIn("existing checklist format and user-story organization", tasks)
        self.assertIn("`/speckit.tasks` owns implementation, validation, and review task definition in `tasks.md`", tasks)
        self.assertIn("must not invent validation strategy", tasks)
        self.assertIn("change requirements, update contracts, or widen scope", tasks)
        self.assertIn("Task-Derivation Subagents", tasks)
        self.assertIn("context-reduced multi-subagent derivation model", tasks)
        self.assertIn("derivation-time partitioning rule only", tasks)
        self.assertIn("do not create implementation transfer artifacts", tasks)
        self.assertIn("Tasks Core Agent", tasks)
        for agent_role in (
            "Story Task Agent",
            "Contract Validation Agent",
            "UI/UX Task Agent",
            "Review Task Agent",
        ):
            self.assertIn(agent_role, tasks)
        for payload_field in (
            "`assigned_scope`",
            "`allowed_read_paths`",
            "`allowed_sections`",
            "`output_contract`",
        ):
            self.assertIn(payload_field, tasks)
        self.assertIn("TASK_DERIVATION_CONTEXT_GAP", tasks)
        self.assertIn("must not consume full conversation history", tasks)
        self.assertIn("Split checklist items only when the validation level, implementation owner, dependency order, evidence source, or review scope differs", tasks)
        self.assertIn("Planning Input Taxonomy", tasks)
        self.assertIn("validation level taxonomy", tasks)
        self.assertIn("fixture strategy and external-system execution mode taxonomy", tasks)
        self.assertIn("Evidence binding", tasks)
        self.assertIn("Validation Task Derivation", tasks)
        self.assertIn("derive the validation level", tasks)
        self.assertIn("fixture strategy, external-system execution mode", tasks)
        self.assertIn("inline evidence requirement", tasks)
        self.assertIn("validation task taxonomy", tasks)
        for validation_scope in (
            "`contract_validation`",
            "`ui_acceptance`",
            "`data_side_effect_validation`",
            "`integration_e2e_validation`",
        ):
            self.assertIn(validation_scope, tasks)
        self.assertIn("Final Code Review", tasks)
        self.assertIn("append the final phase after user-story tasks", tasks)
        self.assertIn("final review scope taxonomy", tasks)
        self.assertIn("`boundary`, `interface_contract`, `ui_ux`, `data_side_effect`, `behavior_contract`, and `sequence_consistency`", tasks)
        self.assertIn("Checked sources include", tasks)
        self.assertIn("`contracts/uif/`", tasks)
        self.assertIn("`spec.md` UI/UX requirements", tasks)
        self.assertIn("UI/UX Specification Readiness", tasks)
        self.assertIn("data side-effect review", tasks)
        self.assertIn("field-level update/delete", tasks)
        self.assertIn("runtime database writes", tasks)
        self.assertIn("boundary review", tasks)
        self.assertIn("task scope stays within planned `M + U`", tasks)
        self.assertIn("no implementation task changed `spec.md`, `contracts/`, readiness checklists, or UI/UX Specification Readiness", tasks)
        self.assertIn("UI consistency review", tasks)
        self.assertIn("implemented journeys, navigation, states, viewport behavior", tasks)
        self.assertIn("accepted `UI-###` and `UX-###` requirements", tasks)
        self.assertIn("UI/UX task taxonomy", tasks)
        self.assertIn("story-local task granularity", tasks)
        self.assertIn("`ui_setup` -> `ui_implementation` -> `ui_accessibility` and/or `ui_acceptance`", tasks)
        self.assertIn("Do not create a separate UI/UX lifecycle phase", tasks)
        self.assertIn("UI/UX tasks must name the applicable `UI-###` or `UX-###` requirement ID", tasks)
        self.assertIn("report a readiness blocker instead of generating an ambiguous task", tasks)
        self.assertIn("required state, viewport, and accessibility coverage", tasks)
        self.assertIn("real-system e2e environment readiness", tasks)
        self.assertIn("Review evidence binding", tasks)
        self.assertIn("concrete review scope, source artifacts, implementation surfaces, and evidence refs", tasks)
        self.assertIn("bounded repair permission", tasks)
        self.assertIn("review evidence, bounded repair permission, or a blocker", tasks)
        self.assertIn("record a blocker instead of treating the change as implementation work", tasks)
        self.assertNotIn("handoff", tasks)
        self.assertNotIn("allowed_write_paths", tasks)
        self.assertNotIn("receipt", tasks)
        self.assertNotIn("task_type: code_review", tasks)
        self.assertNotIn("data_side_effect_review", tasks)
        self.assertNotIn("review_conclusion", tasks)
        self.assertNotIn("checked_sources", tasks)
        self.assertNotIn("consistency_repairs", tasks)
        self.assertNotIn("deferred_validation_todos", tasks)
        self.assertNotIn("empty arrays or objects indicate no entries", tasks)
        self.assertNotIn("task_type: visual_verification", tasks)
        self.assertNotIn("`visual_validation`", tasks)
        self.assertNotIn("`visual_verification`", tasks)
        self.assertNotIn("`final_visual_review`", tasks)
        self.assertNotIn("visual regression tests", tasks)
        self.assertNotIn("screenshot comparison, state or viewport coverage validation", tasks)
        self.assertNotIn("task_type: interface_validation", tasks)
        self.assertNotIn("task_type: data_side_effect_validation", tasks)

    def test_behavior_first_command_wrapper_contracts(self) -> None:
        specify = SPECIFY_COMMAND_PATH.read_text(encoding="utf-8")
        clarify = CLARIFY_COMMAND_PATH.read_text(encoding="utf-8")
        checklist = CHECKLIST_COMMAND_PATH.read_text(encoding="utf-8")
        spec_template = SPEC_TEMPLATE_PATH.read_text(encoding="utf-8")
        checklist_template = BEHAVIOR_TEMPLATE_PATHS[
            "behavior-testability-checklist-template"
        ].read_text(encoding="utf-8")

        for command in (specify, clarify, checklist):
            self.assertIn("{CORE_TEMPLATE}", command)
            self.assertIn("strategy: wrap", command)
            self.assertIn(
                "This wrapper must not redefine core-owned User Input, Pre-Execution Checks, extension hooks, base path resolution, or core file handling.",
                command,
            )

        for term in (
            "Spec-Only Requirement Policy",
            "Preset-added requirement output writes only `spec.md`",
            "Resolve the active `spec-template`",
            "only stable UI/UX output structure",
            "`Required`: populate every applicable UI/UX field",
            "`Not Applicable`: record a concrete product-level rationale",
            "`Unknown`: record the unresolved product decision",
            "stable `UX-###` IDs",
            "stable `UI-###` IDs",
            "observable user outcomes",
            "Specification Quality Validation",
            "Done When",
        ):
            self.assertIn(term, specify)
        self.assertNotIn("## User Input", specify)
        self.assertNotIn("## Pre-Execution Checks", specify)
        self.assertNotIn("## UI/UX Specification", specify)
        self.assertNotIn(
            "| Requirement ID | Surface or Journey | Observable Requirement |",
            specify,
        )

        self.assertIn("{CORE_TEMPLATE}", spec_template)
        for term in (
            "## UI/UX Specification",
            "**Applicability**: Required | Not Applicable | Unknown",
            "### Experience Goals",
            "### Information Architecture and Navigation",
            "### Interaction and Feedback",
            "### UI States",
            "### Responsive Behavior",
            "### Accessibility",
            "### Content and Visual Requirements",
            "### UI/UX Acceptance Criteria",
            "| Requirement ID | Surface or Journey | Observable Requirement | Applicable States | Viewports | Acceptance Criterion | Status |",
        ):
            self.assertIn(term, spec_template)

        for term in (
            "Use `spec.md` as the clarification source",
            "UI/UX Requirement Clarification Strategy",
            "UI/UX Applicability `Unknown`",
            "incomplete `UI-###` or `UX-###` requirements",
            "Ask at most 5 high-impact questions",
            "exactly one question at a time",
            "Responsive reflow",
            "accessibility behavior",
            "Objective UI/UX acceptance criteria",
            "Save `spec.md` after each accepted answer",
            "Do not generate checklist artifacts",
        ):
            self.assertIn(term, clarify)

        for term in (
            'Checklist Purpose: "Unit Tests for English"',
            "NOT for verification/testing",
            "CORE PRINCIPLE - Test the Requirements, Not the Implementation",
            "Resolve `behavior-testability-checklist-template`",
            "only stable authority for checklist headings",
            "Do not reproduce those structures in this command",
            "Populate the resolved checklist template directly from `spec.md`",
            "keep requirement applicability",
            "separate from specification readiness",
            "Gate Status: PASS",
            "Gate Status: BLOCKED",
            "BDD/NFR/UI/UX readiness status",
        ):
            self.assertIn(term, checklist)
        self.assertNotIn("## UI/UX Coverage Matrix", checklist)
        self.assertNotIn(
            "| Requirement ID | Source `spec.md` Section | Applicability | Readiness |",
            checklist,
        )
        self.assertIn("## UI/UX Coverage Matrix", checklist_template)

    def test_behavior_first_plan_and_tasks_awareness_contract(self) -> None:
        plan = PLAN_COMMAND_PATH.read_text(encoding="utf-8")
        tasks = TASKS_COMMAND_PATH.read_text(encoding="utf-8")
        template = PLAN_TEMPLATE_PATH.read_text(encoding="utf-8")
        implement = IMPLEMENT_COMMAND_PATH.read_text(encoding="utf-8")

        for term in (
            "behavior/bdd.draft.feature",
            "behavior/uif.intent.json",
            "behavior/data-fixtures.intent.json",
            "contracts/bdd/",
            "contracts/uif/",
            "contracts/behavior/",
            "formal behavior contracts",
            "must formalize",
            "N/A or blocker",
            "research.md",
            "test level",
            "fixture strategy",
            "mock/external-system strategy",
            "BehaviorScenarioInstance",
            "DataFixture",
            "UIFPath",
            "FeedbackView",
            "BehaviorAssertion",
            "Required case types from `checklists/behavior-testability.md`",
            "must project into `behavior/behavior-scenarios.draft.json`",
            "must formalize into `contracts/behavior/scenario-instances.json`",
            "Do not continue with only positive scenarios when Required case types exist",
            "Map each Required Case ID to a Scenario ID or `case_coverage_blockers` entry",
            "write `case_coverage_blockers`",
            "record `N/A or blocker` with the Case ID",
        ):
            self.assertIn(term, plan)

        for term in (
            "Phase 0 Preflight",
            "Phase 0 Behavior Projection",
            "checklists/behavior-testability.md has passed",
            "Blocking Items: none` or a `Blocking Items` section containing only `- none`",
            "before core research or design work",
            "UI/UX Planning Responsibilities",
            "accepted `UI-###` and `UX-###` requirements",
            "Applicability is `Required` and Readiness is `Ready`",
            "If a row is `Unknown` or `Blocked`",
            "report-only/no-write upstream gate failure",
            "Do not project `Not Applicable` rows into planning outputs",
            "behavior/behavior-scenarios.draft.json",
            "report-only/no-write failure",
            "must not create or update behavior artifacts",
            "Do not discover new requirement problems",
            "Do not ask clarification questions",
            "Do not modify `spec.md`",
            "upstream gate failure",
            "Return to `/speckit.checklist` or `/speckit.clarify`",
        ):
            self.assertIn(term, plan)

        self.assertNotIn("empty, or records only an upstream gate failure", plan)
        self.assertNotIn("behavior/open-questions.json", plan)
        self.assertNotIn("test-plan.md", plan)

        for term in (
            "contracts/bdd/",
            "contracts/uif/",
            "contracts/behavior/",
            "`spec.md` UI/UX requirements",
            "`checklists/behavior-testability.md` UI/UX Specification Readiness",
            "`UI-###` and `UX-###` requirements",
            "test-first",
            "existing checklist format and user-story organization",
            "For each BehaviorScenarioInstance",
            "fixture task",
            "BDD/E2E or contract test task",
            "implementation task",
            "verification evidence task",
            "Expected UIF contract step with type `user_event`",
            "Expected UIF contract step with type `api_call`",
            "UI/UX task taxonomy",
            "`ui_acceptance`",
            "UI acceptance task",
            "required state and viewport coverage",
            "accessibility behavior",
            "For each quickstart validation path",
            "derive the validation level",
            "fixture strategy, external-system execution mode",
            "inline evidence requirement",
            "Planning Input Taxonomy",
            "`/speckit.tasks` owns implementation, validation, and review task definition in `tasks.md`",
            "must not invent validation strategy",
            "validation level taxonomy",
            "fixture strategy and external-system execution mode taxonomy",
            "Evidence binding",
            "validation task taxonomy",
            "`contract_validation`",
            "`ui_acceptance`",
            "`data_side_effect_validation`",
            "`integration_e2e_validation`",
            "Use UI/UX Specification Readiness as the only UI/UX planning-readiness source",
            "Applicability is `Required` and Readiness is `Ready`",
            "Do not generate implementation, validation, acceptance, or review tasks for `Not Applicable`, `Unknown`, or `Blocked` rows",
            "Route `Unknown` and `Blocked` requirement rows back",
            "only decomposes UI/UX specifications that passed the readiness gate",
            "Do not generate execution metadata or write-path fields.",
            "Missing Required case coverage is a coverage blocker, not silently skipped work",
            "`negative`, `boundary`, `permission`, `validation`, or `state_conflict`",
            "For each BehaviorScenarioInstance with type",
            "derive fixture, contract or BDD test, implementation, and verification evidence tasks",
            "UI consistency review",
            "implemented journeys, navigation, states, viewport behavior",
            "UI/UX task taxonomy",
            "story-local task granularity",
            "`ui_setup` -> `ui_implementation` -> `ui_accessibility` and/or `ui_acceptance`",
            "`ui_accessibility`",
            "Do not create a separate UI/UX lifecycle phase",
            "UI/UX tasks must name the applicable `UI-###` or `UX-###` requirement ID",
            "report a readiness blocker instead of generating an ambiguous task",
            "Generate UI/UX tasks only from Required and Ready checklist rows",
            "Review evidence binding",
            "bounded repair permission",
            "final review scope taxonomy",
            "`boundary`, `interface_contract`, `ui_ux`, `data_side_effect`, `behavior_contract`, and `sequence_consistency`",
            "boundary review",
            "no implementation task changed `spec.md`, `contracts/`, readiness checklists, or UI/UX Specification Readiness",
        ):
            self.assertIn(term, tasks)

        self.assertNotIn("task_type: interface_validation", tasks)
        self.assertNotIn("task_type: data_side_effect_validation", tasks)
        self.assertNotIn("test-plan.md", tasks)

        self.assertIn("./behavior/bdd.draft.feature", template)
        self.assertIn("./contracts/bdd/", template)
        self.assertIn("./contracts/uif/", template)
        self.assertIn("./contracts/behavior/", template)

        self.assertNotIn("tests/contracts/", implement)
        self.assertIn("Read contracts/ for API specifications and test requirements", implement)
        self.assertIn("Read quickstart.md for integration scenarios", implement)

    def test_bdd_formalization_strengthens_reasoning_without_traceability_system(self) -> None:
        plan = PLAN_COMMAND_PATH.read_text(encoding="utf-8")
        bdd_contract_template = BEHAVIOR_TEMPLATE_PATHS[
            "behavior-bdd-contract-template"
        ].read_text(encoding="utf-8")

        for term in (
            "When formalizing BDD Draft into `contracts/bdd/*.feature`",
            "Preserve scenario intent and business outcome from the draft.",
            "Convert ambiguous Given steps into formal fixture, actor, state, permission, or start-view conditions.",
            "Convert When steps into formal user events, request cases, or system triggers aligned with UIF/API contracts.",
            "Convert Then steps into formal feedback, response, business state, or assertion expectations.",
            "If a step cannot be formalized without inventing information, record `N/A or blocker` instead of guessing.",
            "Do not introduce independent traceability mechanisms for BDD formalization.",
        ):
            self.assertIn(term, plan)

        for forbidden in (
            "@SCN-",
            "trace table",
            "coverage matrix",
            "reverse index",
        ):
            self.assertNotIn(forbidden, plan)
            self.assertNotIn(forbidden, bdd_contract_template)

    def test_analyze_command_owns_vertical_consistency_contract(self) -> None:
        analyze = ANALYZE_COMMAND_PATH.read_text(encoding="utf-8")

        self.assertIn("{CORE_TEMPLATE}", analyze)
        self.assertIn("strategy: wrap", analyze)
        self.assertIn("vertical consistency", analyze)
        self.assertIn("spec -> BDD/UIF intent -> contracts -> tasks", analyze)
        self.assertIn("spec.md user stories have BDD coverage", analyze)
        self.assertIn("BDD Given steps map to fixtures", analyze)
        self.assertIn("BDD When steps map to UIF events or API requests", analyze)
        self.assertIn("BDD Then steps map to feedback or behavior assertions", analyze)
        self.assertIn("behavior/uif.intent.json is formalized into contracts/uif/*.expected.json", analyze)
        self.assertIn("behavior drafts exist but formal contracts are missing", analyze)
        self.assertIn("source draft and missing planning input", analyze)
        self.assertNotIn("behavior/open-questions.json", analyze)
        self.assertIn("N/A or blocker", analyze)
        self.assertIn("UIF API calls exist in contracts/api/", analyze)
        self.assertIn("behavior contracts cover scenarios, fixtures, and assertions", analyze)
        self.assertIn("tasks.md covers BDD, UIF, API, fixtures, and quickstart validation paths", analyze)
        self.assertIn("case coverage", analyze)
        self.assertIn("Required case types in `checklists/behavior-testability.md`", analyze)
        self.assertIn("case types are either covered or have `N/A or blocker` evidence", analyze)
        self.assertIn(
            "failure scenarios declare error code, failure feedback, and state invariant, rollback, or compensation assertion",
            analyze,
        )
        self.assertIn("quickstart validation paths cover Required failure scenarios", analyze)
        self.assertIn("Build a one-pass artifact inventory before deep reading", analyze)
        self.assertIn("Use stable IDs as the primary consistency surface", analyze)
        self.assertIn("CASE-", analyze)
        self.assertIn("SCN-", analyze)
        self.assertIn("UIF-", analyze)
        self.assertIn("FIX-", analyze)
        self.assertIn("AST-", analyze)
        self.assertIn("BLK-", analyze)
        self.assertIn("Read surrounding prose only when a required ID, source section, or blocker explanation is missing or ambiguous", analyze)
        self.assertIn("Stop expanding a branch after the first blocker that proves the downstream link cannot be closed", analyze)
        self.assertNotIn("uif.actual.json", analyze)
        self.assertNotIn("uif.diff.json", analyze)
        self.assertNotIn("Actual UIF", analyze)

    def test_actual_uif_artifacts_are_not_part_of_preset_contract(self) -> None:
        paths = [
            README_PATH,
            SPECIFY_COMMAND_PATH,
            CLARIFY_COMMAND_PATH,
            CHECKLIST_COMMAND_PATH,
            ANALYZE_COMMAND_PATH,
            PLAN_COMMAND_PATH,
            TASKS_COMMAND_PATH,
            IMPLEMENT_COMMAND_PATH,
            PRESET_PATH,
        ]
        forbidden_terms = [
            "Expected UIF vs Actual UIF",
            "Actual UIF",
            "uif.actual.json",
            "uif.diff.json",
            "from implementation",
            "implementation-derived UIF",
            "static analysis tooling",
        ]
        for path in paths:
            document = path.read_text(encoding="utf-8")
            for term in forbidden_terms:
                self.assertNotIn(term, document, f"{path} contains {term}")

    def test_behavior_first_templates_exist_and_are_decoupled(self) -> None:
        for path in BEHAVIOR_TEMPLATE_PATHS.values():
            self.assertTrue(path.exists(), path)

        self.assertIn("Feature:", BEHAVIOR_TEMPLATE_PATHS["behavior-bdd-draft-template"].read_text())
        self.assertIn("Feature:", BEHAVIOR_TEMPLATE_PATHS["behavior-bdd-contract-template"].read_text())
        self.assertIn(
            "Behavior Testability Checklist",
            BEHAVIOR_TEMPLATE_PATHS["behavior-testability-checklist-template"].read_text(),
        )
        behavior_checklist_template = BEHAVIOR_TEMPLATE_PATHS[
            "behavior-testability-checklist-template"
        ].read_text(encoding="utf-8")
        self.assertIn("Case Coverage Matrix", behavior_checklist_template)
        self.assertIn("one row per story or capability case type", behavior_checklist_template)
        self.assertIn("Status: Required|Not Applicable|Unknown", behavior_checklist_template)
        self.assertIn("| Case ID | Story/Capability | Case Type | Status | Source `spec.md` section | Blocking Item ID | Rationale |", behavior_checklist_template)
        self.assertIn(
            "Required case type must cite the source `spec.md` section",
            behavior_checklist_template,
        )
        self.assertIn(
            "Each row must have a stable Case ID",
            behavior_checklist_template,
        )
        self.assertIn(
            "Scenario IDs and `case_coverage_blockers` are assigned during `/speckit.plan`",
            behavior_checklist_template,
        )
        self.assertIn("Not Applicable requires rationale", behavior_checklist_template)
        self.assertIn("Unknown must appear in Blocking Items", behavior_checklist_template)
        self.assertIn("Non-Functional Requirement Readiness", behavior_checklist_template)
        self.assertIn("Status: Required|Not Applicable|Unknown", behavior_checklist_template)
        self.assertIn("Performance", behavior_checklist_template)
        self.assertIn("Security and Privacy", behavior_checklist_template)
        self.assertIn("Reliability and Recovery", behavior_checklist_template)
        self.assertIn("Accessibility", behavior_checklist_template)
        self.assertIn("Compliance and Auditability", behavior_checklist_template)
        self.assertIn("Observability", behavior_checklist_template)
        self.assertIn("Compatibility", behavior_checklist_template)
        self.assertIn("Data Lifecycle", behavior_checklist_template)
        self.assertIn("Cost and Operational Constraints", behavior_checklist_template)
        self.assertIn("explicitly declared in `spec.md`", behavior_checklist_template)
        self.assertIn("without prescribing architecture", behavior_checklist_template)
        self.assertIn("UI/UX Specification Readiness", behavior_checklist_template)
        self.assertIn(
            "UI/UX Applicability is declared as `Required`, `Not Applicable`, or `Unknown`",
            behavior_checklist_template,
        )
        self.assertIn(
            "Every applicable requirement has a stable `UI-###` or `UX-###` ID",
            behavior_checklist_template,
        )
        self.assertIn(
            "Required UI/UX requirements describe observable user outcomes rather than implementation details",
            behavior_checklist_template,
        )
        self.assertIn("Experience goals and critical journeys are explicit", behavior_checklist_template)
        self.assertIn("Interaction feedback, validation behavior, and recovery outcomes are explicit", behavior_checklist_template)
        self.assertIn("Responsive reflow, scrolling, safe-area, viewport, and long-content behavior are explicit", behavior_checklist_template)
        self.assertIn("Keyboard, focus, semantics, contrast, announcements, and error accessibility behavior are explicit", behavior_checklist_template)
        self.assertIn("Every Required UI/UX requirement has an objective acceptance criterion", behavior_checklist_template)
        self.assertIn("UI/UX Coverage Matrix", behavior_checklist_template)
        self.assertIn("Applicability and Readiness are evaluated independently", behavior_checklist_template)
        self.assertIn("Readiness uses only `Ready` or `Blocked`", behavior_checklist_template)
        self.assertIn("Gate Status: PASS|BLOCKED", behavior_checklist_template)
        self.assertIn("Blocking Items:", behavior_checklist_template)
        self.assertIn("none", behavior_checklist_template)
        self.assertNotIn(
            "No unchecked BDD readiness item blocks `/speckit.plan`",
            behavior_checklist_template,
        )
        self.assertFalse((REPO_ROOT / "templates" / "behavior" / "open-questions.json").exists())
        self.assertFalse(
            (
                REPO_ROOT
                / "schemas"
                / "speckit.behavior.open-questions.v1.schema.json"
            ).exists()
        )

        for template_name in (
            "behavior-scenarios-draft-template",
            "behavior-uif-intent-template",
            "behavior-data-fixtures-intent-template",
            "behavior-uif-expected-template",
            "behavior-scenario-instances-template",
            "behavior-data-fixtures-template",
            "behavior-assertions-template",
        ):
            self.assertIn(
                "contract_type",
                BEHAVIOR_TEMPLATE_PATHS[template_name].read_text(encoding="utf-8"),
            )

        scenario_instances_template = BEHAVIOR_TEMPLATE_PATHS[
            "behavior-scenario-instances-template"
        ].read_text(encoding="utf-8")
        self.assertIn('"case_coverage_blockers"', scenario_instances_template)
        self.assertIn('"type": "permission"', scenario_instances_template)
        self.assertIn('"case_kind": "permission"', scenario_instances_template)
        self.assertIn('"error_code"', scenario_instances_template)
        self.assertIn('"expected_feedback"', scenario_instances_template)

        assertions_template = BEHAVIOR_TEMPLATE_PATHS["behavior-assertions-template"].read_text(
            encoding="utf-8"
        )
        self.assertIn('"intent": "state_invariant"', assertions_template)

    def test_ui_ux_specification_readiness_contract(self) -> None:
        command = CHECKLIST_COMMAND_PATH.read_text(encoding="utf-8")
        template = BEHAVIOR_TEMPLATE_PATHS[
            "behavior-testability-checklist-template"
        ].read_text(encoding="utf-8")

        for term in (
            "Resolve `behavior-testability-checklist-template`",
            "only stable authority for checklist headings",
            "Do not reproduce those structures in this command",
            "Populate the resolved checklist template directly from `spec.md`",
            "keep requirement applicability",
            "separate from specification readiness",
            "Gate Status: PASS",
            "Gate Status: BLOCKED",
        ):
            self.assertIn(term, command)
        self.assertNotIn("## UI/UX Coverage Matrix", command)
        self.assertNotIn(
            "| Requirement ID | Source `spec.md` Section | Applicability | Readiness |",
            command,
        )

        for term in (
            "UI/UX Specification Readiness",
            "UI/UX Coverage Matrix",
            "Source `spec.md` section",
            "Applicability",
            "Readiness",
            "States Covered",
            "Responsive Coverage",
            "Accessibility Coverage",
            "Blocking Items",
            "Applicability and Readiness are evaluated independently",
            "Readiness uses only `Ready` or `Blocked`",
            "Every Required row cites its source `spec.md` section",
            "UI/UX Coverage Matrix is the only UI/UX specification-readiness matrix",
        ):
            self.assertIn(term, template)
        self.assertEqual(
            len(
                re.findall(
                    r"^## UI/UX Coverage Matrix$",
                    template,
                    flags=re.MULTILINE,
                )
            ),
            1,
        )
        self.assertEqual(
            template.count(
                "| Requirement ID | Source `spec.md` Section | Applicability | Readiness | States Covered | Responsive Coverage | Accessibility Coverage | Blocking Item ID |"
            ),
            1,
        )





    def test_behavior_first_schema_contracts_accept_minimal_examples(self) -> None:
        examples = {
            "speckit.behavior.scenarios.draft.v1": minimal_behavior_scenarios_draft(),
            "speckit.behavior.uif.intent.v1": minimal_uif_intent(),
            "speckit.behavior.data_fixtures.intent.v1": minimal_data_fixtures_intent(),
            "speckit.behavior.uif.expected.v1": minimal_uif_expected(),
            "speckit.behavior.scenario_instances.v1": minimal_behavior_scenario_instances(),
            "speckit.behavior.data_fixtures.v1": minimal_behavior_data_fixtures(),
            "speckit.behavior.assertions.v1": minimal_behavior_assertions(),
        }

        for contract_type, path in BEHAVIOR_SCHEMA_PATHS.items():
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual("object", schema["type"])
            self.assertIn("required", schema)
            self.assertIn("properties", schema)
            self.assertEqual(contract_type, schema["properties"]["contract_type"]["const"])
            Draft202012Validator(schema).validate(examples[contract_type])

    def test_behavior_draft_schema_rejects_empty_given_when_then(self) -> None:
        schema = json.loads(
            BEHAVIOR_SCHEMA_PATHS["speckit.behavior.scenarios.draft.v1"].read_text(
                encoding="utf-8"
            )
        )

        for field in ("given", "when", "then"):
            with self.subTest(field=field):
                draft = minimal_behavior_scenarios_draft()
                draft["scenarios"][0][field] = []

                with self.assertRaises(ValidationError):
                    Draft202012Validator(schema).validate(draft)

    def test_behavior_scenario_instances_schema_rejects_empty_contract_refs(self) -> None:
        schema = json.loads(
            BEHAVIOR_SCHEMA_PATHS["speckit.behavior.scenario_instances.v1"].read_text(
                encoding="utf-8"
            )
        )

        for field in ("fixture_ids", "assertion_ids"):
            with self.subTest(field=field):
                instances = minimal_behavior_scenario_instances()
                instances["scenarios"][0][field] = []

                with self.assertRaises(ValidationError):
                    Draft202012Validator(schema).validate(instances)

    def test_behavior_scenario_instances_schema_accepts_structured_exception_cases(self) -> None:
        schema = json.loads(
            BEHAVIOR_SCHEMA_PATHS["speckit.behavior.scenario_instances.v1"].read_text(
                encoding="utf-8"
            )
        )

        for scenario_type in ("negative", "boundary", "permission", "validation", "state_conflict"):
            with self.subTest(scenario_type=scenario_type):
                Draft202012Validator(schema).validate(
                    minimal_exception_behavior_scenario_instances(
                        scenario_type=scenario_type,
                    )
                )

    def test_behavior_scenario_instances_schema_rejects_exception_case_shells(self) -> None:
        schema = json.loads(
            BEHAVIOR_SCHEMA_PATHS["speckit.behavior.scenario_instances.v1"].read_text(
                encoding="utf-8"
            )
        )
        invalid_mutations = [
            ("case_kind", lambda scenario: scenario["request_case"].pop("case_kind")),
            ("trigger", lambda scenario: scenario["request_case"].pop("trigger")),
            ("expected_response", lambda scenario: scenario.update({"expected_response": {}})),
            ("error_code", lambda scenario: scenario["expected_response"].pop("error_code")),
            ("expected_feedback", lambda scenario: scenario.update({"expected_feedback": {}})),
            ("feedback_type", lambda scenario: scenario["expected_feedback"].pop("type")),
            ("feedback_message", lambda scenario: scenario["expected_feedback"].pop("message")),
        ]

        for label, mutate in invalid_mutations:
            with self.subTest(label=label):
                instances = minimal_exception_behavior_scenario_instances()
                mutate(instances["scenarios"][0])

                with self.assertRaises(ValidationError):
                    Draft202012Validator(schema).validate(instances)

    def test_behavior_scenario_instances_schema_rejects_mismatched_exception_case_kind(self) -> None:
        schema = json.loads(
            BEHAVIOR_SCHEMA_PATHS["speckit.behavior.scenario_instances.v1"].read_text(
                encoding="utf-8"
            )
        )
        instances = minimal_exception_behavior_scenario_instances(scenario_type="permission")
        instances["scenarios"][0]["request_case"]["case_kind"] = "validation"

        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(instances)

    def test_behavior_scenario_instances_schema_accepts_case_coverage_blockers(self) -> None:
        schema = json.loads(
            BEHAVIOR_SCHEMA_PATHS["speckit.behavior.scenario_instances.v1"].read_text(
                encoding="utf-8"
            )
        )
        instances = minimal_behavior_scenario_instances()
        instances["case_coverage_blockers"] = [
            {
                "id": "BLK-001",
                "case_id": "CASE-002",
                "case_type": "validation",
                "source": "spec.md#user-story-1",
                "reason": "Validation rule is marked Unknown in checklist.",
                "downstream_contract_path": "contracts/behavior/scenario-instances.json",
            }
        ]

        Draft202012Validator(schema).validate(instances)

    def test_behavior_scenario_instances_schema_rejects_incomplete_case_coverage_blockers(self) -> None:
        schema = json.loads(
            BEHAVIOR_SCHEMA_PATHS["speckit.behavior.scenario_instances.v1"].read_text(
                encoding="utf-8"
            )
        )
        required_fields = (
            "id",
            "case_id",
            "case_type",
            "source",
            "reason",
            "downstream_contract_path",
        )

        for field in required_fields:
            with self.subTest(field=field):
                instances = minimal_behavior_scenario_instances()
                blocker = {
                    "id": "BLK-001",
                    "case_id": "CASE-002",
                    "case_type": "validation",
                    "source": "spec.md#user-story-1",
                    "reason": "Validation rule is marked Unknown in checklist.",
                    "downstream_contract_path": "contracts/behavior/scenario-instances.json",
                }
                blocker.pop(field)
                instances["case_coverage_blockers"] = [blocker]

                with self.assertRaises(ValidationError):
                    Draft202012Validator(schema).validate(instances)

    def test_behavior_scenario_instances_schema_accepts_success_boundary_case(self) -> None:
        schema = json.loads(
            BEHAVIOR_SCHEMA_PATHS["speckit.behavior.scenario_instances.v1"].read_text(
                encoding="utf-8"
            )
        )
        instances = minimal_exception_behavior_scenario_instances(scenario_type="boundary")
        scenario = instances["scenarios"][0]
        scenario["request_case"]["outcome"] = "success"
        scenario["expected_response"] = {"business_code": "ACCEPTED_AT_LIMIT"}
        scenario["expected_feedback"] = {"message": "Limit accepted"}

        Draft202012Validator(schema).validate(instances)

    def test_behavior_scenario_instances_schema_rejects_boundary_failure_without_error(self) -> None:
        schema = json.loads(
            BEHAVIOR_SCHEMA_PATHS["speckit.behavior.scenario_instances.v1"].read_text(
                encoding="utf-8"
            )
        )
        instances = minimal_exception_behavior_scenario_instances(scenario_type="boundary")
        scenario = instances["scenarios"][0]
        scenario["request_case"]["outcome"] = "failure"
        scenario["expected_response"] = {"status": 422}
        scenario["expected_feedback"] = {"message": "Limit exceeded"}

        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(instances)

    def test_behavior_assertions_schema_accepts_exception_assertion_intent(self) -> None:
        schema = json.loads(
            BEHAVIOR_SCHEMA_PATHS["speckit.behavior.assertions.v1"].read_text(
                encoding="utf-8"
            )
        )

        Draft202012Validator(schema).validate(minimal_exception_behavior_assertions())

    def test_expected_uif_schema_rejects_underspecified_typed_steps(self) -> None:
        schema = json.loads(
            BEHAVIOR_SCHEMA_PATHS["speckit.behavior.uif.expected.v1"].read_text(
                encoding="utf-8"
            )
        )

        underspecified_steps = [
            {"type": "api_call"},
            {"type": "local_route"},
            {"type": "user_event"},
        ]
        for step in underspecified_steps:
            with self.subTest(step_type=step["type"]):
                uif = minimal_uif_expected()
                uif["steps"] = [step]

                with self.assertRaises(ValidationError):
                    Draft202012Validator(schema).validate(uif)

    def test_behavior_draft_validator_rejects_fixture_for_unknown_scenario(self) -> None:
        fixtures = minimal_data_fixtures_intent()
        fixtures["fixtures"][0]["required_for"] = ["SCN-404"]

        with self.assertRaises(ValueError):
            validate_behavior_draft_contract(
                minimal_behavior_scenarios_draft(),
                fixtures,
            )

    def test_behavior_draft_validator_rejects_empty_given_when_then(self) -> None:
        for field in ("given", "when", "then"):
            with self.subTest(field=field):
                draft = minimal_behavior_scenarios_draft()
                draft["scenarios"][0][field] = []

                with self.assertRaisesRegex(ValueError, field):
                    validate_behavior_draft_contract(
                        draft,
                        minimal_data_fixtures_intent(),
                    )

    def test_behavior_draft_validator_accepts_valid_cross_fields(self) -> None:
        validate_behavior_draft_contract(
            minimal_behavior_scenarios_draft(),
            minimal_data_fixtures_intent(),
        )

    def test_behavior_contract_validator_rejects_missing_fixture_reference(self) -> None:
        instances = minimal_behavior_scenario_instances()
        instances["scenarios"][0]["fixture_ids"] = ["FIX-MISSING"]

        with self.assertRaises(ValueError):
            validate_behavior_contract_bundle(
                instances,
                minimal_behavior_data_fixtures(),
                minimal_behavior_assertions(),
                [minimal_uif_expected()],
            )

    def test_behavior_contract_validator_rejects_empty_contract_refs(self) -> None:
        for field in ("fixture_ids", "assertion_ids"):
            with self.subTest(field=field):
                instances = minimal_behavior_scenario_instances()
                instances["scenarios"][0][field] = []

                with self.assertRaisesRegex(ValueError, field):
                    validate_behavior_contract_bundle(
                        instances,
                        minimal_behavior_data_fixtures(),
                        minimal_behavior_assertions(),
                        [minimal_uif_expected()],
                    )

    def test_behavior_contract_validator_rejects_underspecified_uif_steps(self) -> None:
        for step in (
            {"type": "api_call"},
            {"type": "local_route"},
            {"type": "user_event"},
        ):
            with self.subTest(step_type=step["type"]):
                uif = minimal_uif_expected()
                uif["steps"] = [step]

                with self.assertRaises(ValueError):
                    validate_behavior_contract_bundle(
                        minimal_behavior_scenario_instances(),
                        minimal_behavior_data_fixtures(),
                        minimal_behavior_assertions(),
                        [uif],
                    )

    def test_behavior_contract_validator_rejects_exception_case_shells(self) -> None:
        invalid_mutations = [
            ("case_kind", lambda scenario: scenario["request_case"].pop("case_kind")),
            ("trigger", lambda scenario: scenario["request_case"].pop("trigger")),
            ("expected_response", lambda scenario: scenario.update({"expected_response": {}})),
            ("error_code", lambda scenario: scenario["expected_response"].pop("error_code")),
            ("expected_feedback", lambda scenario: scenario.update({"expected_feedback": {}})),
            ("feedback_type", lambda scenario: scenario["expected_feedback"].pop("type")),
            ("feedback_message", lambda scenario: scenario["expected_feedback"].pop("message")),
        ]

        for label, mutate in invalid_mutations:
            with self.subTest(label=label):
                instances = minimal_exception_behavior_scenario_instances()
                mutate(instances["scenarios"][0])

                with self.assertRaisesRegex(ValueError, label):
                    validate_behavior_contract_bundle(
                        instances,
                        minimal_behavior_data_fixtures(),
                        minimal_exception_behavior_assertions(),
                        [minimal_uif_expected()],
                    )

    def test_behavior_contract_validator_rejects_exception_without_state_or_rollback_assertion(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "state_invariant_rollback_or_compensation_assertion",
        ):
            validate_behavior_contract_bundle(
                minimal_exception_behavior_scenario_instances(),
                minimal_behavior_data_fixtures(),
                minimal_behavior_assertions(),
                [minimal_uif_expected()],
            )

    def test_behavior_contract_validator_rejects_mismatched_exception_case_kind(self) -> None:
        instances = minimal_exception_behavior_scenario_instances(scenario_type="permission")
        instances["scenarios"][0]["request_case"]["case_kind"] = "validation"

        with self.assertRaisesRegex(ValueError, "case_kind"):
            validate_behavior_contract_bundle(
                instances,
                minimal_behavior_data_fixtures(),
                minimal_exception_behavior_assertions(),
                [minimal_uif_expected()],
            )

    def test_behavior_contract_validator_accepts_structured_exception_cases(self) -> None:
        for scenario_type in ("negative", "boundary", "permission", "validation", "state_conflict"):
            with self.subTest(scenario_type=scenario_type):
                validate_behavior_contract_bundle(
                    minimal_exception_behavior_scenario_instances(
                        scenario_type=scenario_type,
                    ),
                    minimal_behavior_data_fixtures(),
                    minimal_exception_behavior_assertions(),
                    [minimal_uif_expected()],
                )

    def test_behavior_contract_validator_accepts_rollback_and_compensation_assertions(self) -> None:
        for intent in ("rollback", "compensation"):
            with self.subTest(intent=intent):
                validate_behavior_contract_bundle(
                    minimal_exception_behavior_scenario_instances(),
                    minimal_behavior_data_fixtures(),
                    minimal_exception_behavior_assertions_with_intent(intent),
                    [minimal_uif_expected()],
                )

    def test_behavior_contract_validator_accepts_success_boundary_case(self) -> None:
        instances = minimal_exception_behavior_scenario_instances(scenario_type="boundary")
        scenario = instances["scenarios"][0]
        scenario["request_case"]["outcome"] = "success"
        scenario["expected_response"] = {"business_code": "ACCEPTED_AT_LIMIT"}
        scenario["expected_feedback"] = {"message": "Limit accepted"}

        validate_behavior_contract_bundle(
            instances,
            minimal_behavior_data_fixtures(),
            minimal_behavior_assertions(),
            [minimal_uif_expected()],
        )

    def test_behavior_contract_validator_rejects_boundary_failure_without_error(self) -> None:
        instances = minimal_exception_behavior_scenario_instances(scenario_type="boundary")
        scenario = instances["scenarios"][0]
        scenario["request_case"]["outcome"] = "failure"
        scenario["expected_response"] = {"status": 422}
        scenario["expected_feedback"] = {"message": "Limit exceeded"}

        with self.assertRaisesRegex(ValueError, "error_code"):
            validate_behavior_contract_bundle(
                instances,
                minimal_behavior_data_fixtures(),
                minimal_exception_behavior_assertions(),
                [minimal_uif_expected()],
            )

    def test_behavior_case_coverage_validator_rejects_missing_required_case(self) -> None:
        with self.assertRaisesRegex(ValueError, "Required case"):
            validate_behavior_case_coverage(
                minimal_case_coverage(),
                minimal_behavior_scenarios_draft(),
                minimal_behavior_scenario_instances(),
                "T001 implement SCN-001",
                "Validate SCN-001",
            )

    def test_behavior_case_coverage_validator_rejects_empty_matrix(self) -> None:
        with self.assertRaisesRegex(ValueError, "case_coverage"):
            validate_behavior_case_coverage(
                {},
                minimal_behavior_scenarios_draft(),
                minimal_behavior_scenario_instances(),
                "T001 implement SCN-001",
                "Validate SCN-001",
            )

    def test_behavior_case_coverage_validator_requires_tasks_and_quickstart_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "tasks.md"):
            validate_behavior_case_coverage(
                minimal_case_coverage(),
                minimal_behavior_scenarios_draft(
                    scenario_type="permission",
                    scenario_id="SCN-ERR-001",
                ),
                minimal_exception_behavior_scenario_instances(),
                "T001 implement SCN-001",
                "Validate SCN-ERR-001",
            )

        with self.assertRaisesRegex(ValueError, "quickstart.md"):
            validate_behavior_case_coverage(
                minimal_case_coverage(),
                minimal_behavior_scenarios_draft(
                    scenario_type="permission",
                    scenario_id="SCN-ERR-001",
                ),
                minimal_exception_behavior_scenario_instances(),
                "T001 implement SCN-ERR-001",
                "Validate SCN-001",
            )

    def test_behavior_case_coverage_validator_accepts_closed_required_case(self) -> None:
        validate_behavior_case_coverage(
            minimal_case_coverage(),
            minimal_behavior_scenarios_draft(
                scenario_type="permission",
                scenario_id="SCN-ERR-001",
            ),
            minimal_exception_behavior_scenario_instances(),
            "T001 implement SCN-ERR-001 and AST-001",
            "Validate SCN-ERR-001 through quickstart path",
        )

    def test_behavior_case_coverage_validator_accepts_formal_blocker_for_required_case(self) -> None:
        instances = minimal_behavior_scenario_instances()
        instances["case_coverage_blockers"] = [
            {
                "id": "BLK-001",
                "case_id": "CASE-002",
                "case_type": "validation",
                "source": "spec.md#user-story-1",
                "reason": "Validation rule is still Unknown in checklist.",
                "downstream_contract_path": "contracts/behavior/scenario-instances.json",
            }
        ]

        validate_behavior_case_coverage(
            minimal_case_coverage_with_blocker(),
            minimal_behavior_scenarios_draft(),
            instances,
            "T001 blocked by BLK-001",
            "BLK-001 blocks quickstart validation",
        )

    def test_behavior_case_coverage_validator_requires_blocker_downstream_evidence(self) -> None:
        instances = minimal_behavior_scenario_instances()
        instances["case_coverage_blockers"] = [
            {
                "id": "BLK-001",
                "case_id": "CASE-002",
                "case_type": "validation",
                "source": "spec.md#user-story-1",
                "reason": "Validation rule is still Unknown in checklist.",
                "downstream_contract_path": "contracts/behavior/scenario-instances.json",
            }
        ]

        with self.assertRaisesRegex(ValueError, "tasks.md"):
            validate_behavior_case_coverage(
                minimal_case_coverage_with_blocker(),
                minimal_behavior_scenarios_draft(),
                instances,
                "T001 implement SCN-001",
                "BLK-001 blocks quickstart validation",
            )

        with self.assertRaisesRegex(ValueError, "quickstart.md"):
            validate_behavior_case_coverage(
                minimal_case_coverage_with_blocker(),
                minimal_behavior_scenarios_draft(),
                instances,
                "T001 blocked by BLK-001",
                "Validate SCN-001",
            )

    def test_behavior_case_coverage_validator_rejects_blocker_source_mismatch(self) -> None:
        instances = minimal_behavior_scenario_instances()
        instances["case_coverage_blockers"] = [
            {
                "id": "BLK-001",
                "case_id": "CASE-002",
                "case_type": "validation",
                "source": "spec.md#different-story",
                "reason": "Validation rule is still Unknown in checklist.",
                "downstream_contract_path": "contracts/behavior/scenario-instances.json",
            }
        ]

        with self.assertRaisesRegex(ValueError, "source"):
            validate_behavior_case_coverage(
                minimal_case_coverage_with_blocker(),
                minimal_behavior_scenarios_draft(),
                instances,
                "T001 blocked by BLK-001",
                "BLK-001 blocks quickstart validation",
            )

    def test_behavior_contract_validator_accepts_valid_cross_fields(self) -> None:
        validate_behavior_contract_bundle(
            minimal_behavior_scenario_instances(),
            minimal_behavior_data_fixtures(),
            minimal_behavior_assertions(),
            [minimal_uif_expected()],
        )
























































































    def test_agents_references_extension_governance(self) -> None:
        agents = AGENTS_PATH.read_text(encoding="utf-8")

        self.assertIn("docs/extension-governance.md", agents)
        self.assertIn("Extension Governance", agents)

    def test_implementation_docs_remove_handoff_contracts(self) -> None:
        readme = README_PATH.read_text(encoding="utf-8")
        governance = EXTENSION_GOVERNANCE_PATH.read_text(encoding="utf-8")
        protocol = CROSS_AGENT_PROTOCOL_PATH.read_text(encoding="utf-8")

        self.assertIn("upstream standard implementation workflow", readme)
        self.assertIn("standard implementation task execution only", governance)
        for document in (readme, governance, protocol):
            self.assertNotIn("persistent_handoff_orchestration", document)
            self.assertNotIn("Vertical Planner Agent", document)
            self.assertNotIn("Worker Agent", document)

    def _workflow_on(self, workflow: dict) -> dict:
        return workflow.get("on") or workflow.get(True) or {}

    def test_github_actions_contract_workflow(self) -> None:
        workflow_path = REPO_ROOT / ".github" / "workflows" / "ci.yml"
        if not workflow_path.exists():
            self.skipTest("source repository workflow file is not packaged in the preset")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        self.assertEqual("Preset Contract", workflow["name"])
        self.assertEqual({"contents": "read"}, workflow["permissions"])
        triggers = self._workflow_on(workflow)
        self.assertIn("pull_request", triggers)
        self.assertEqual(["main"], triggers["push"]["branches"])
        self.assertIn("workflow_dispatch", triggers)

        contract_job = workflow["jobs"]["contract"]
        self.assertEqual("ubuntu-latest", contract_job["runs-on"])
        self.assertEqual(
            ["3.10", "3.13"],
            contract_job["strategy"]["matrix"]["python-version"],
        )
        workflow_text = workflow_path.read_text(encoding="utf-8")
        self.assertIn("python3 -m pip install -r requirements-dev.txt", workflow_text)
        self.assertIn("python3 -m unittest tests/test_preset_contract.py", workflow_text)

    def test_github_actions_artifact_release_and_integration_pr_workflow(self) -> None:
        workflow_path = REPO_ROOT / ".github" / "workflows" / "preset-artifact.yml"
        if not workflow_path.exists():
            self.skipTest("source repository workflow file is not packaged in the preset")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        self.assertEqual("Preset Artifact", workflow["name"])
        self.assertEqual({"contents": "write"}, workflow["permissions"])
        triggers = self._workflow_on(workflow)
        self.assertEqual(["v*"], triggers["push"]["tags"])
        self.assertIn("workflow_dispatch", triggers)
        inputs = triggers["workflow_dispatch"]["inputs"]
        self.assertIn("version", inputs)
        self.assertIn("spec_kit_ref", inputs)
        self.assertIn("create_integration_pr", inputs)

        workflow_text = workflow_path.read_text(encoding="utf-8")
        required_terms = [
            "spec-kit-workflow-preset-v${VERSION}.zip",
            "NEXT_PATCH_VERSION",
            "python3 -m unittest tests/test_preset_contract.py",
            "python3 -m venv \"${GITHUB_WORKSPACE}/.venv-specify-smoke\"",
            "echo \"${GITHUB_WORKSPACE}/.venv-specify-smoke/bin\" >> \"${GITHUB_PATH}\"",
            'PATH="${GITHUB_WORKSPACE}/.venv-specify-smoke/bin:${PATH}"',
            'project_dir="$(mktemp -d "${RUNNER_TEMP}/workflow-preset-smoke.XXXXXX")"',
            'resolve_out="${RUNNER_TEMP}/plan-template-resolve.txt"',
            'constitution_resolve_out="${RUNNER_TEMP}/constitution-template-resolve.txt"',
            "PIP_CONFIG_FILE: /dev/null",
            'PYTEST_ADDOPTS: ""',
            'export TMPDIR="${RUNNER_TEMP}"',
            'export TEMP="${RUNNER_TEMP}"',
            'export TMP="${RUNNER_TEMP}"',
            'specify init --here --integration claude --script sh --ignore-agent-tools',
            "specify preset remove workflow-preset",
            "specify preset add --dev",
            "specify preset resolve plan-template",
            "specify preset resolve constitution-template",
            "R: Repository / Workspace",
            "M: Module / Capability",
            "U: Unit / Design Object",
            "O: Operation / Detail",
            ".claude/skills/speckit-implement/SKILL.md",
            "SPEC_KIT_FORK_PR_TOKEN",
            "bigsmartben/spec-kit",
            "workflow-preset-release-v${VERSION}",
            "gh pr create",
            "gh pr edit",
            "WORKFLOW_PRESET_DOWNLOAD_URL",
            "presets/catalog.community.json",
            "community_catalog_path",
            "community_catalog",
            "download_url",
            'assert entry\\["version"\\] == "[0-9]+\\.[0-9]+\\.[0-9]+"',
            "tests/test_presets.py",
            "__pycache__",
            ".pyc",
            "*.pyc",
            "ZipInfo",
            "1980, 1, 1",
            "github.ref_type == 'tag' || (github.event_name == 'workflow_dispatch' && env.CREATE_INTEGRATION_PR == 'true')",
            "env.CREATE_INTEGRATION_PR == 'true'",
            "refs/tags/v${VERSION}",
            "^[0-9]+\\.[0-9]+\\.[0-9]+$",
            "persist-credentials: false",
            "git rev-parse HEAD",
            "refs/tags/v${VERSION}^{}",
            "SPEC_KIT_FORK_PR_TOKEN is required when integration PR creation is requested.",
            "exit 1",
        ]
        for term in required_terms:
            self.assertIn(term, workflow_text)
        forbidden_terms = [
            "specify preset resolve workflow-preset plan-template",
            "specify preset resolve workflow-preset speckit.implement",
            "client_payload[version]",
            "client_payload[download_url]",
            "repository_dispatch",
            "repos/bigsmartben/spec-kit/dispatches",
            "tests/contracts/speckit-cross-agent-protocol.md",
            "tests/contracts/speckit-cross-agent-subagents.md",
            "::warning::SPEC_KIT_FORK_DISPATCH_TOKEN",
            "skipping integration PR",
        ]
        for term in forbidden_terms:
            self.assertNotIn(term, workflow_text)
        self.assertNotIn("github/spec-kit", workflow_text)


if __name__ == "__main__":
    unittest.main()
