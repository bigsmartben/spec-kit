<a id="quick-start-guide"></a>

# Spec-Driven Development Quickstart

这份指南面向本仓库分发版的 Spec Kit。它保留核心 Spec-Driven Development 流程，默认只安装 `git` 扩展和 `workflow-preset`；技术调研、HTML 预览和上下文维护均按需启用。

Use SDD to build a feature or application from a specification. For a repair,
follow the [bug-fixing quickstart](guides/bugfix.md); to decide whether an idea
deserves investment, follow the [idea assessment quickstart](guides/assessment.md).
These are independent processes, not prerequisites for this guide.

> [!NOTE]
> Automation scripts are provided as Bash (`.sh`), PowerShell (`.ps1`), and Python (`.py`) variants. Interactive `specify init` prompts you to choose one; non-interactive runs (no TTY, or `--non-interactive`) default to a shell variant for your OS. Pass `--script sh|ps|py` to select explicitly.

The process steps here use GitHub Copilot's default skills mode (`/speckit-*`).
For other agents or modes, see
[Command invocation](integrations/cli.md#command-invocation).
Invoke each `/speckit-*` skill separately in your agent's chat and review the
result before moving to the next step. These are agent skills, not terminal
commands; only CLI installation and project setup use the terminal.

## Recommended Process

> [!TIP]
> Spec Kit 会根据当前 Git 分支自动识别 active feature，例如 `001-photo-album`。切换规格时通常只需要切换分支。

After installing Spec Kit, each skill below is a step in the process. Two paths are common:

Establish a constitution once per project with `/speckit-constitution` before
starting either path.

```text
/speckit.constitution             # 同时托管 constitution.md 与 architecture.md
/speckit.specify
/speckit.checklist
/speckit.clarify
/speckit.plan
/speckit.tasks
/speckit.analyze
/speckit.implement
/speckit.converge
```

1. `/speckit-specify`
2. `/speckit-tasks`
3. `/speckit-implement`

**Full path** — for production features, adding `/speckit-clarify`, `/speckit-checklist`, and `/speckit-analyze` as quality gates:

1. `/speckit-constitution` (once per project)
2. `/speckit-specify`
3. `/speckit-clarify`
4. `/speckit-checklist`
5. `/speckit-tasks`
6. `/speckit-analyze`
7. `/speckit-implement`

### Install Specify

**In your terminal**, install the CLI from PyPI (requires [uv](install/uv.md)), then initialize your project:

```bash
uv tool install specify-cli
specify init taskify --integration copilot
cd taskify
```

`init` lets you pick your coding agent interactively, or pass it explicitly with `--integration` (e.g. `--integration copilot`). For CI and AI agent harnesses, add `--non-interactive` so unspecified choices use documented defaults instead of hanging on an arrow-key picker.

> [!NOTE]
> Prefer `pipx`, one-time `uvx` runs, a pinned release, or an offline/air-gapped setup? See the [Installation Guide](installation.md) for all supported methods.
> Adding Spec Kit to a repository that already contains code? Follow
> [Adopting Spec Kit in an Existing Project](how-to/existing-projects.md) before
> starting the workflow below.

Launch your coding agent in the project directory. Invoke the following skills
in its chat, one at a time.

<a id="step-1-speckitconstitution--set-the-ground-rules"></a>

### Step 1: `/speckit-constitution` — set the ground rules

Establishes the project's guiding principles, which every later step is evaluated against. Run it once up front, passing your principles as arguments.

```text
/speckit-constitution Taskify is a "Security-First" application. All user inputs must be validated. We use a microservices architecture. Code must be fully documented.
```

<a id="step-2-speckitspecify--describe-what-to-build"></a>

### Step 2: `/speckit-specify` — describe what to build

Creates the feature specification from a natural-language description and
freezes the observable user experience before implementation. The command
produces `spec.md`, a self-contained `prototype.html`, and a pending UAT
baseline in `quickstart.md`. The prototype is the construction contract for
layout and interaction, while each `UAT-*` case maps a user-observable scenario
to requirements and exact prototype anchors. Specify defines acceptance only;
it does not execute or mark UAT as passed.

```text
/speckit-specify Develop Taskify, a team productivity platform where predefined users create projects, assign tasks, comment, and move tasks across Kanban columns (To Do, In Progress, In Review, Done). Five users (one product manager, four engineers), three sample projects, no login for this first phase.
```

<a id="step-3-speckitclarify--resolve-ambiguities"></a>

### Step 3: `/speckit-clarify` — resolve ambiguities

Asks targeted questions about anything underspecified and folds the answers back
into the frozen Specify contract. Run it before task generation, optionally with
a focus area.

```text
/speckit-clarify Focus on task card behavior — status changes, comment permissions, and user assignment.
```

<a id="step-4-speckitchecklist--validate-the-spec"></a>

### Step 4: `/speckit-checklist` — validate the spec

Generates a custom quality checklist — "unit tests for your requirements" — to confirm the spec is complete, clear, and consistent before you break the work down. These custom checklists are reviewer-owned requirements-quality review artifacts: mark an item `[x]` only when the reviewer determines that requirement-quality criterion is satisfied. Checked custom items do not mean implementation work is complete.

```text
/speckit-checklist
```

<a id="step-5-speckittasks--break-the-work-down"></a>

### Step 5: `/speckit-tasks` — break the work down

Reads only `spec.md`, `prototype.html`, `quickstart.md`, and the project
constitution. It creates independently deliverable requirement-level work
packages in `tasks.md` without choosing a stack, architecture, files, or
implementation paths. Every `FR-*`, `SC-*`, prototype `data-spec-ref`, and
`UAT-*` must map to at least one package. Delivery obligations use `[BUILD]`;
every UAT also has one explicit `[UAT]` execution task.

If the frozen contract is internally inconsistent or a required mapping is
missing, Task stops and sends the issue back to Specify or Clarify. It does not
invent requirements or technical design to fill the gap.

```text
/speckit-tasks
```

<a id="step-6-speckitanalyze--check-consistency"></a>

### Step 6: `/speckit-analyze` — check consistency

Reports conflicts, gaps, and ambiguities across `spec.md`, `prototype.html`,
`quickstart.md`, and `tasks.md`. It is read-only. Return requirement, prototype,
or UAT problems to Specify or Clarify, and return coverage or neutrality
problems to Task before implementing.

```text
/speckit-analyze
```

<a id="step-7-speckitimplement--build-it"></a>

### Step 7: `/speckit-implement` — build it

Owns the technical decisions: the stack, architecture, file structure, and
implementation paths. It executes the work packages in `tasks.md` in dependency
order and performs the mapped UAT scenarios.

Before implementation, it reads checklist checkbox state as a gate and asks
before proceeding if any checklist items are unchecked; it does not change any
checklist files or markers. The built-in `checklists/requirements.md` checklist
is maintained by `/speckit-specify` and `/speckit-clarify`, while custom
checklists remain reviewer-owned.

Within `quickstart.md`, Implement updates only the corresponding UAT entry's
`Status`, `Actual Result`, `Evidence`, and `Deviation` fields. It must not change
the frozen requirements, actions, expected results, references, or identifiers.
Set status to `PASS`, `FAIL`, or `BLOCKED` only from observed execution; a UAT
task is complete only when its matching scenario passes.
Run it once to build everything, or scope it to a set of work packages at a time.

```text
/speckit-implement
```

> [!TIP]
> For a full reference on each command — arguments, outputs, work-package
> boundaries, UAT ownership, and how the commands interact — see
> [Agentic SDD](reference/agentic-sdd.md).

大型项目可以分阶段实现和验证，例如先完成核心结构，再做交互行为，最后补齐评论、权限、分配等垂直切片，避免单次上下文过载。

- **Be explicit** about what you're building and why
- **Don't focus on tech stack** during specification phase
- **Freeze** requirements, prototype behavior, and UAT expectations before task generation
- **Keep Task technology-neutral** and route contract conflicts back to Specify
- **Validate** full FR, SC, prototype, and UAT coverage before coding
- **Let Implement own** architecture, files, implementation paths, and UAT evidence

如果你想体验可恢复的端到端 workflow：

- See the [Agentic SDD](reference/agentic-sdd.md) reference for full detail on every command
- Learn how to [customize the process](how-to/customization.md) with extensions, presets, workflows, and bundles
- Read the [complete methodology](https://github.com/github/spec-kit/blob/main/spec-driven.md) for in-depth guidance
- Compare the [core templates](https://github.com/github/spec-kit/tree/main/templates) with
  [community walkthroughs](community/walkthroughs.md) to see how Spec-Driven Development is used in real projects
- Explore the [source code on GitHub](https://github.com/github/spec-kit)
