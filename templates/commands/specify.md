---
description: Create the feature specification, executable prototype, and pending UAT baseline from a natural language feature description.
handoffs:
  - label: Build Task Work Packages
    agent: speckit.tasks
    prompt: Translate the frozen specification, prototype, and UAT contract into work packages
  - label: Clarify Spec Requirements
    agent: speckit.clarify
    prompt: Clarify specification requirements
    send: true
scripts:
  sh: scripts/bash/resolve-template.sh spec-template --json
  ps: scripts/powershell/resolve-template.ps1 spec-template -Json
  py: scripts/python/resolve_template.py spec-template --json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before specification)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_specify` key
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
    - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
    - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
    - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
    - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Outline

The text the user typed after `__SPECKIT_COMMAND_SPECIFY__` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `{ARGS}` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. **Generate a concise short name** (2-4 words) for the feature:
    - Analyze the feature description and extract the most meaningful keywords
    - Create a 2-4 word short name that captures the essence of the feature
    - Use action-noun format when possible (e.g., "add-user-auth", "fix-payment-bug")
    - Preserve technical terms and acronyms (OAuth2, API, JWT, etc.)
    - Keep it concise but descriptive enough to understand the feature at a glance
    - Examples:
        - "I want to add user authentication" → "user-auth"
        - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
        - "Create a dashboard for analytics" → "analytics-dashboard"
        - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. **Branch creation** (optional, via hook):

   If a `before_specify` hook ran successfully in the Pre-Execution Checks above, it will have created/switched to a git branch and output JSON containing `BRANCH_NAME` and `FEATURE_NUM`. Note these values for reference, but the branch name does **not** dictate the spec directory name.

   If the user explicitly provided `GIT_BRANCH_NAME`, pass it through to the hook so the branch script uses the exact value as the branch name (bypassing all prefix/suffix generation).

3. **Create the feature directory and resolve all Specify templates**:

   Specs live under the default `specs/` directory unless the user explicitly provides `SPECIFY_FEATURE_DIRECTORY`.

   **Resolution order for `SPECIFY_FEATURE_DIRECTORY`**:
    1. If the user explicitly provided `SPECIFY_FEATURE_DIRECTORY` (e.g., via environment variable, argument, or configuration), use it as-is
    2. Otherwise, auto-generate it under `specs/`:
        - Check `.specify/init-options.json` for `feature_numbering` (preferred) or `branch_numbering` (deprecated, migration only — will be removed in a future release)
        - If `"timestamp"`: prefix is `YYYYMMDD-HHMMSS` (current timestamp)
        - If `"sequential"` or absent: prefix is `NNN` (next available 3-digit number after scanning existing directories in `specs/`)
        - Construct the directory name: `<prefix>-<short-name>` (e.g., `003-user-auth` or `20260319-143022-user-auth`)
        - Set `SPECIFY_FEATURE_DIRECTORY` to `specs/<directory-name>`
        - If `branch_numbering` was used (and `feature_numbering` was absent), emit a one-line warning: "⚠️ `branch_numbering` in init-options.json is deprecated. Rename to `feature_numbering`."

   **Create the directory and resolve the artifacts**:
    - Run `{SCRIPT}` from the repository root and parse `TEMPLATE_CONTENT` as `SPEC_TEMPLATE_CONTENT`, the active `spec-template`.
    - Run the same resolver command again, replacing the literal `spec-template` template argument in `{SCRIPT}` with `prototype-template`, and parse `TEMPLATE_CONTENT` as `PROTOTYPE_TEMPLATE_CONTENT`.
    - Run the same resolver command again, replacing the literal `spec-template` template argument in `{SCRIPT}` with `quickstart-template`, and parse `TEMPLATE_CONTENT` as `QUICKSTART_TEMPLATE_CONTENT`.
    - Each shared resolver call composes project overrides, preset layers, and extension layers over its core template, including `append`, `prepend`, and `wrap` strategies. If any call fails, stop and report the resolution error. Never fall back to a single layer or copy a template file directly from disk.
    - `mkdir -p SPECIFY_FEATURE_DIRECTORY`
    - Set `SPEC_FILE` to `SPECIFY_FEATURE_DIRECTORY/spec.md`
    - Set `PROTOTYPE_FILE` to `SPECIFY_FEATURE_DIRECTORY/prototype.html`
    - Set `QUICKSTART_FILE` to `SPECIFY_FEATURE_DIRECTORY/quickstart.md`
    - Treat `SPEC_TEMPLATE_CONTENT`, `PROTOTYPE_TEMPLATE_CONTENT`, and `QUICKSTART_TEMPLATE_CONTENT` as the starting structures. Do not copy template files from disk: each resolved value is the fully composed active template.
    - Persist the resolved path to `.specify/feature.json`:
     ```json
     {
       "feature_directory": "<resolved feature dir>"
     }
     ```
     Write the actual resolved directory path value (for example, `specs/003-user-auth`), not the literal string `SPECIFY_FEATURE_DIRECTORY`.
     This allows downstream commands (`__SPECKIT_COMMAND_TASKS__`,
     `__SPECKIT_COMMAND_IMPLEMENT__`, etc.) to locate the feature directory
     without relying on git branch name conventions.

   **IMPORTANT**:
    - You must only create one feature per `__SPECKIT_COMMAND_SPECIFY__` invocation
    - The spec directory name and the git branch name are independent — they may be the same but that is the user's choice
    - The feature directory and all three Specify artifacts are always created by this command, never by the hook

4. Use all three resolved template contents to understand the required sections, prototype contract, and UAT baseline schema.

5. **IF EXISTS**: Load `/memory/constitution.md` for project principles and governance constraints.

6. Follow this execution flow:
    1. Parse user description from arguments
       If empty: ERROR "No feature description provided"
    2. Extract key concepts from description
       Identify: actors, actions, data, constraints
    3. For unclear aspects:
        - Make informed guesses based on context and industry standards
        - Only mark with [NEEDS CLARIFICATION: specific question] if:
            - The choice significantly impacts feature scope or user experience
            - Multiple reasonable interpretations exist with different implications
            - No reasonable default exists
        - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**
        - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details
    4. Fill User Scenarios & Testing section
       If no clear user flow: ERROR "Cannot determine user scenarios"
    5. Generate Functional Requirements
       Each requirement must be testable
       Use reasonable defaults for unspecified details (document assumptions in Assumptions section)
    6. Generate the executable medium-fidelity prototype
        - Express the visible layout, information hierarchy, component relationships, interaction order, responsive behavior, and applicable normal, empty, loading, error, validation, disabled, and success states
        - Use the resolved prototype structure and keep the result self-contained: inline CSS and only the small inline JavaScript needed to demonstrate behavior
        - Do not depend on a production framework, external design tool, network resource, font CDN, image CDN, or real backend service
        - Give every page, region, meaningful component, and state a stable, unique `data-spec-ref`
        - Start from the current user's primary task and design one coherent, production-ready screen before adding secondary flows
        - Build a clear hierarchy: task context, current content or input, one primary action, contextual secondary actions, and state feedback
        - Use progressive disclosure for advanced options, settings, consent, and supporting explanations; keep the main path focused on the current task
        - Write realistic end-user copy that tells the user what to do, what happens next, and what changed. Use concise action-oriented labels instead of feature descriptions
        - Put the primary action in the natural completion position and keep secondary actions quieter, contextually relevant, and easy to reach
        - Treat empty, loading, success, validation, disabled, and error views as alternate states of the same product screen, not as a catalog of states to display together
        - Keep visible prototype content limited to copy a product user would see. Use labels, values, actions, help, and state feedback that belong to the product
        - Never render requirement IDs, prototype anchors, UAT IDs, or internal validation notes as visible prototype text
        - Keep traceability details in nonvisual attributes such as `data-spec-ref`, `data-prototype-state`, and `data-state`
        - Do not add feature overviews, implementation notes, design rationale, generation notes, or navigation that exists only to explain the prototype
        - Do not turn an internal workflow, ordered acceptance scenario, or UAT into a visible progress navigator. Acceptance sequence is not automatically product UI
        - Only add navigation, progress indicators, headers, sidebars, or multi-step layouts when explicitly required by the specification and justified by the user task
        - Default to the current user's primary task screen. Do not add an application-wide shell or a showcase of every workflow stage merely because the feature spans multiple steps
        - Do not expose prototype-only controls, sample data buttons, demo modes, debug panels, or state switchers. Include an example-data or trial path only when the feature specification makes it an end-user requirement
        - Do not expose vendor, provider, API, backend, model, recognition-service, or implementation settings as user-facing copy. Describe the user outcome or capability instead
        - Show privacy and data-use explanations only for the current action and the exact data it handles. Do not combine unrelated future-step data flows or cross-feature permissions into the current screen
        - Make the page credible as production UI: every visible control must represent a real user action with a clear reason to be there
        - Treat the prototype as a construction contract. Do not soften the command with "for reference", "inspiration", or discretionary redesign language
    7. Generate the UAT baseline
        - Derive acceptance scenarios only from `spec.md` and `prototype.html`; do not infer acceptance from an implementation that already exists
        - Assign unique, stable `UAT-###` identifiers
        - For every UAT, record the user/role, preconditions, ordered actions, observable expected result, requirement references, and exact prototype `data-spec-ref` values
        - Set every initial status to `PENDING`
        - Leave actual results and evidence unexecuted and do not produce `PASS` or `FAIL` conclusions
        - Ensure every user story with user-visible behavior has at least one UAT
        - Every UAT resolves to both requirement and prototype references
    8. Define Success Criteria
       Create measurable, technology-agnostic outcomes
       Include both quantitative metrics (time, performance, volume) and qualitative measures (user satisfaction, task completion)
       Each criterion must be verifiable without implementation details
    9. Identify Key Entities (if data involved)
    10. Return: SUCCESS only when the specification, prototype, and UAT baseline are complete and internally consistent

7. Write all three artifacts:
    - Write the specification to `SPEC_FILE` using `SPEC_TEMPLATE_CONTENT`, replacing placeholders with concrete details from the feature description while preserving section order and required headings.
    - Write `prototype.html` to `PROTOTYPE_FILE` using `PROTOTYPE_TEMPLATE_CONTENT` as the starting structure. The file MUST contain raw standalone HTML, not a Markdown code fence or a link to an external prototype. Replace every bracketed placeholder and remove sample-only guidance, template comments, and all internal explanatory copy from the rendered page.
    - Write the UAT baseline to `QUICKSTART_FILE` using `QUICKSTART_TEMPLATE_CONTENT`. Replace every bracketed placeholder and remove the sample UAT instead of leaving generic acceptance content.

8. **Specification Quality Validation**: After writing the three initial artifacts, validate them together:

   a. **Create Spec Quality Checklist**: Generate a checklist file at `SPECIFY_FEATURE_DIRECTORY/checklists/requirements.md` using the checklist template structure with these validation items:

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]

      **Purpose**: Validate specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]

      ## Content Quality

      - [ ] No production implementation details in spec.md (languages, frameworks, APIs); prototype HTML/CSS/JS is limited to expressing the UX contract
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed
      - [ ] prototype.html is linked from spec.md and opens as standalone HTML
      - [ ] Visible prototype content contains only product UI and copy; requirement, anchor, UAT, checklist, and generation metadata remain nonvisual
      - [ ] The prototype presents one coherent current-task screen with clear context, content or input, a primary action, contextual secondary actions, and feedback
      - [ ] Advanced options and supporting explanations use progressive disclosure instead of crowding the primary flow
      - [ ] The prototype contains no workflow map, progress navigator, header, sidebar, or multi-step shell unless the specification explicitly requires it
      - [ ] No prototype-only demo control, sample-data shortcut, debug panel, state switcher, or provider implementation setting appears as production UI
      - [ ] Privacy and data-use copy is scoped to the current action and exact data handled on this screen
      - [ ] quickstart.md is linked from spec.md and contains the UAT baseline

      ## Requirement Completeness

      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified
      - [ ] Every material user-visible requirement maps to a prototype reference
      - [ ] Every prototype reference is unique and resolves to an exact data-spec-ref
      - [ ] Every user-visible user story has at least one UAT
      - [ ] Every UAT maps to at least one requirement and one prototype reference
      - [ ] All applicable normal, empty, loading, error, validation, disabled, and success states are represented in the prototype and UAT

      ## Feature Readiness

      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No production implementation details leak into specification prose or UAT expectations
      - [ ] prototype.html is self-contained and has no external runtime dependencies
      - [ ] UAT identifiers are stable and unique
      - [ ] Every UAT status is PENDING
      - [ ] No UAT contains an actual result, evidence claim, or pass/fail conclusion

      ## Notes

      - Items marked incomplete require contract updates before `__SPECKIT_COMMAND_CLARIFY__` or `__SPECKIT_COMMAND_TASKS__`
      ```

   b. **Run Validation Check**: Review `spec.md`, `prototype.html`, and `quickstart.md` together against every checklist item:
    - For each item, determine if it passes or fails
    - Document specific issues found (quote the relevant artifact section or `data-spec-ref`)
    - Confirm every prototype reference used in `quickstart.md` exists exactly once in `prototype.html`
    - Confirm every `UAT-###` appears once in the acceptance baseline and traceability summary

   c. **Handle Validation Results**:

    - **If all items pass**: Mark checklist complete and proceed to the Mandatory Post-Execution Hooks section

    - **If items fail (excluding [NEEDS CLARIFICATION])**:
        1. List the failing items and specific issues
        2. Update all affected artifacts together so their requirements, prototype anchors, and UAT references stay aligned
        3. Re-run validation until all items pass (max 3 iterations)
        4. If still failing after 3 iterations, document remaining issues in checklist notes and warn user

    - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all [NEEDS CLARIFICATION: ...] markers from the spec
        2. **LIMIT CHECK**: If more than 3 markers exist, keep only the 3 most critical (by scope/security/UX impact) and make informed guesses for the rest
        3. For each clarification needed (max 3), present options to user in this format:

           ```markdown
           ## Question [N]: [Topic]

           **Context**: [Quote relevant spec section]

           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

           **Suggested Answers**:

           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |

           **Your choice**: _[Wait for user response]_
           ```

        4. **CRITICAL - Table Formatting**: Ensure markdown tables are properly formatted:
            - Use consistent spacing with pipes aligned
            - Each cell should have spaces around content: `| Content |` not `|Content|`
            - Header separator must have at least 3 dashes: `|--------|`
            - Test that the table renders correctly in markdown preview
        5. Number questions sequentially (Q1, Q2, Q3 - max 3 total)
        6. Present all questions together before waiting for responses
        7. Wait for user to respond with their choices for all questions (e.g., "Q1: A, Q2: Custom - [details], Q3: B")
        8. Update the spec by replacing each [NEEDS CLARIFICATION] marker with the user's selected or provided answer, then update affected prototype content and UAT mappings
        9. Re-run cross-artifact validation after all clarifications are resolved

   d. **Update Checklist**: After each validation iteration, update the checklist file with current pass/fail status

## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check if `.specify/extensions.yml` exists in the project root.
- If it does not exist, or no hooks are registered under `hooks.after_specify`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_specify` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue to the Completion Report.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
    - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
    - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
    - **Mandatory hook** (`optional: false`) — **You MUST emit `EXECUTE_COMMAND:` for each mandatory hook**:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
    - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

## Completion Report

Report completion to the user with:
- `SPECIFY_FEATURE_DIRECTORY` — the feature directory path
- `SPEC_FILE` — the spec file path
- `PROTOTYPE_FILE` — the prototype preview path
- `QUICKSTART_FILE` — the pending UAT baseline path
- Readiness for the next phase (`__SPECKIT_COMMAND_CLARIFY__` or `__SPECKIT_COMMAND_TASKS__`)

Keep the completion message concise and user-facing. Report validation failures in detail only when the generated contract does not pass validation. Do not reproduce requirement mappings, prototype-anchor inventories, UAT matrices, or checklist contents after a successful validation; keep them in the artifacts.

**NOTE:** Branch creation is handled by the `before_specify` hook (git extension). Feature directory creation and all three Specify artifacts are always handled by this core command.

## Quick Guidelines

- Focus on **WHAT** users need and **WHY** in `spec.md`.
- Avoid HOW to implement in `spec.md` (no production tech stack, APIs, or code structure).
- Use `prototype.html` to define visible UX and interaction behavior exactly enough to implement, but do not turn it into production application code.
- Keep `prototype.html` visually indistinguishable from a product preview: traceability belongs in nonvisual attributes and the other contract artifacts, not in explanatory UI.
- Do not convert specification journeys, user stories, UAT action order, or downstream workflow stages into visible app navigation.
- Treat every visible element as production UI. Remove demo/sample affordances, technical service controls, and unrelated data-flow explanations unless the user-facing requirements explicitly make them part of the product.
- Design the primary task screen first: give it clear context, the current content or input, one obvious primary action, quiet contextual secondary actions, and immediate feedback.
- Use concise, realistic end-user copy and progressive disclosure. Do not write a feature tour into the screen.
- Use `quickstart.md` to freeze observable acceptance expectations before implementation; this command does not execute UAT.
- Written for business stakeholders, not developers.
- DO NOT create any checklists that are embedded in the spec. That will be a separate command.

### Section Requirements

- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### Prototype Guidelines

- The prototype is part of the requirement, not a design suggestion
- Use medium fidelity: clear layout, hierarchy, spacing, component behavior, state transitions, and responsive behavior
- Start with one coherent production screen for the current task; express other states as alternatives reached through real product interactions
- Show only product UI and user-facing copy; do not present requirement IDs, anchor names, UAT metadata, validation notes, or design rationale in the page
- Make the hierarchy legible: task context, content/input, primary action, contextual secondary actions, then feedback
- Add progress navigation, global headers, sidebars, and multi-step shells only when the user-facing specification explicitly requires them
- Do not add prototype-only sample data, demo toggles, debug/state controls, vendor names, provider settings, API/backend labels, or cross-feature privacy explanations
- Keep it self-contained and executable without network access
- Never duplicate text-only requirements as an implementation substitute; prototype anchors must trace back to specification requirements

### UAT Guidelines

- Use stable `UAT-###` identifiers
- Each UAT describes a user-observable journey, not an implementation or unit test
- Include exact prototype references and requirement IDs
- Keep every status as `PENDING`
- Do not record actual results, evidence, deviations, or pass/fail decisions during Specify

### For AI Generation

When creating this spec from a user prompt:

1. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps
2. **Document assumptions**: Record reasonable defaults in the Assumptions section
3. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers - use only for critical decisions that:
   - Significantly impact feature scope or user experience
   - Have multiple reasonable interpretations with different implications
   - Lack any reasonable default
4. **Prioritize clarifications**: scope > security/privacy > user experience > technical details
5. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
6. **Common areas needing clarification** (only if no reasonable default exists):
   - Feature scope and boundaries (include/exclude specific use cases)
   - User types and permissions (if multiple conflicting interpretations possible)
   - Security/compliance requirements (when legally/financially significant)

**Examples of reasonable defaults** (don't ask about these):

- Data retention: Industry-standard practices for the domain
- Performance targets: Standard web/mobile app expectations unless specified
- Error handling: User-friendly messages with appropriate fallbacks
- Authentication method: Standard session-based or OAuth2 for web apps
- Integration patterns: Use project-appropriate patterns (REST/GraphQL for web services, function calls for libraries, CLI args for tools, etc.)

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools
3. **User-focused**: Describe outcomes from user/business perspective, not system internals
4. **Verifiable**: Can be tested/validated without knowing implementation details

**Good examples**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"
- "Task completion rate improves by 40%"

**Bad examples** (implementation-focused):

- "API response time is under 200ms" (too technical, use "Users see results instantly")
- "Database can handle 1000 TPS" (implementation detail, use user-facing metric)
- "React components render efficiently" (framework-specific)
- "Redis cache hit rate above 80%" (technology-specific)

## Done When

- [ ] `SPEC_FILE`, `PROTOTYPE_FILE`, and `QUICKSTART_FILE` written from all three composed templates
- [ ] Prototype is executable, self-contained, and authoritative for visible behavior
- [ ] UAT baseline is complete, mapped, and entirely pending
- [ ] All three artifacts pass the cross-artifact quality checklist
- [ ] Extension hooks dispatched or skipped according to the rules in Mandatory Post-Execution Hooks above
- [ ] Completion reported to user with all three paths, mapping summary, and checklist results
