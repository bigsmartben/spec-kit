<div align="center">
    <img src="./media/logo_large.webp" alt="Spec Kit Logo" width="200" height="200"/>
    <h1>🌱 Spec Kit</h1>
    <h3><em>Define what to build before building it — with any AI coding agent.</em></h3>
</div>

<p align="center">
    <strong>An open source toolkit for building high-quality software with any AI coding agent — a ready-to-use spec-driven process (or bring your own), endlessly extensible, community-driven, and built for your whole organization.</strong>
</p>

<p align="center">
    <a href="https://github.com/github/spec-kit/releases/latest"><img src="https://img.shields.io/github/v/release/github/spec-kit" alt="Latest Release"/></a>
    <a href="https://github.com/github/spec-kit/stargazers"><img src="https://img.shields.io/github/stars/github/spec-kit?style=social" alt="GitHub stars"/></a>
    <a href="https://github.com/github/spec-kit/blob/main/LICENSE"><img src="https://img.shields.io/github/license/github/spec-kit" alt="License"/></a>
    <a href="https://github.github.io/spec-kit/"><img src="https://img.shields.io/badge/docs-GitHub_Pages-blue" alt="Documentation"/></a>
</p>

<p align="center">
    <strong>English</strong> ·
    <a href="./README.zh-CN.md">简体中文</a>
</p>

---

## 本地定位

- [🤔 What is Spec-Driven Development?](#-what-is-spec-driven-development)
- [⚡ Get Started](#-get-started)
- [📽️ Video Overview](#️-video-overview)
- [🌍 Community](#-community)
- [🤖 Supported AI Coding Agent Integrations](#-supported-ai-coding-agent-integrations)
- [🔧 Specify CLI Reference](#-specify-cli-reference)
- [🧩 Making Spec Kit Your Own: Extensions & Presets](#-making-spec-kit-your-own-extensions--presets)
- [📦 Bundles: Role-Based Setups](#-bundles-role-based-setups)
- [📚 Core Philosophy](#-core-philosophy)
- [🌟 Development Phases](#-development-phases)
- [🎯 Experimental Goals](#-experimental-goals)
- [🔧 Prerequisites](#-prerequisites)
- [📖 Learn More](#-learn-more)
- [💬 Support](#-support)
- [🙏 Acknowledgements](#-acknowledgements)
- [📄 License](#-license)

本 README 只介绍仓库中实际存在的本地内容：

- `extensions/` 下的本地扩展。
- `presets/` 下的本地预设。
- `specify init` 默认会安装的增强能力。
- 需要手动安装的可选能力。
- 扩展和预设运行后会写入的主要产物。

如果你只是想知道这个仓库相比基础流程多了什么，可以先看这三件事：

- 默认扩展：`discovery`、`inception`、`intake`、`preview`、`repository-governance`。
- 默认预设：`workflow-preset`。
- 自动上下文扩展：`agent-context`。

Requires **[uv](https://docs.astral.sh/uv/)** ([install uv](./docs/install/uv.md)). Replace `vX.Y.Z` with the latest release tag from [Releases](https://github.com/github/spec-kit/releases) — keep the leading `v` (for example, `v0.12.11`, not `0.12.11`):

```bash
uv tool install specify-cli --from git+https://github.com/bigsmartben/spec-kit.git
```

Prefer installing from PyPI? The `specify-cli` package is also published there:

```bash
uv tool install specify-cli
```

See the [Installation Guide](./docs/installation.md) for alternative methods, verification, upgrade, and troubleshooting.

### 2. Initialize a project

```bash
specify init my-project --integration codex
cd my-project
```

在已有目录里初始化：

```bash
specify init . --integration codex --force
```

如果当前机器没有对应 agent CLI，但你只想生成文件：

```bash
specify init my-project --integration codex --ignore-agent-tools
```

初始化完成后，本地默认能力会被复制到项目的 `.specify/` 目录，并注册到所选 agent 的命令或 skill 目录中。

## 默认安装内容

`specify init` 当前默认安装这些本地扩展和预设：

| 类型 | ID | 来源目录 | 作用 |
| --- | --- | --- | --- |
| 自动扩展 | `agent-context` | `extensions/agent-context` | 维护 AGENTS、CLAUDE、Copilot 等 agent context 文件里的 Spec Kit 受管段。 |
| 默认扩展 | `discovery` | `extensions/discovery` | 在正式计划前做可行性、技术选型、旧代码评估、接口理解、PoC 和场景化技术决策。 |
| 默认扩展 | `inception` | `extensions/inception` | 在正式 SDD 前通过对话收敛可选的产品 UC 和 wireflow；旧架构入口仅提供迁移提示。 |
| 默认扩展 | `intake` | `extensions/intake` | 把 PRD、设计稿、Figma、最终静态 HTML 交付、测试用例等来源归一化为 SDD 可消费的证据包。 |
| 默认扩展 | `preview` | `extensions/preview` | 从规格和计划生成低、中、高保真 Markdown 或自包含 HTML 预览。 |
| 默认扩展 | `repository-governance` | `extensions/repository-governance` | 生成仓库治理 SSOT，帮助 agent 明确目录责任、读取顺序和事实证据。 |
| 默认预设 | `workflow-preset` | `presets/workflow-preset` | 从 Specify 引入 UI/UX 需求，从 Plan 引入 BDD、集成与 E2E 测试设计，由 Tasks 映射为执行清单，最终交给标准 Core Implement。 |

默认扩展列表在 `src/specify_cli/commands/init.py` 的 `DEFAULT_BUNDLED_EXTENSIONS` 中维护。默认预设列表在同文件的 `DEFAULT_BUNDLED_PRESETS` 中维护。

## 默认扩展

### `inception`

`inception` 是正式规格化之前的可选产品启动阶段。它通过对话确认产品材料，并用模板生成 `inception/product/` 下的产物。

产品命令：

```text
/speckit.inception.product
```

主要产物：

```text
inception/product/uc.md
inception/product/wireflow-medium.html
inception/product/wireflow-high.html
```

使用建议：

- 仅在需要产品启动材料时运行 `/speckit.inception.product`。
- `uc.md` 只有在用户后续明确选择时才成为 Constitution 或 Architecture 输入。
- `/speckit.inception.arch` 已退役，只返回迁移提示，不读取 UC、生成架构或运行 PoC。
- `inception` 不生成 `spec.md`、`plan.md`、`tasks.md`、OpenAPI、数据库 schema、生产代码或测试套件变更。

### `arch`

`arch` v3 是可选迁移扩展，不再生成项目架构。旧命令名保留为无写入入口，统一指向 `workflow-preset` 的 `/speckit.constitution`。

常用命令：

```text
/speckit.arch.generate
/speckit.arch.reverse
```

使用建议：

- 新工作流直接运行 `/speckit.constitution`。
- `/speckit.arch.generate` 和 `/speckit.arch.reverse` 只返回 `ARCH_COMMAND_RETIRED`。
- 团队文档完成迁移后可以卸载 `arch`。

### `discovery`

`discovery` 放在 `/speckit.plan` 之前，用来处理“不确定能不能做、怎么做更稳、旧代码到底长什么样”这类问题。

常用命令：

```text
/speckit.discovery.feasibility
/speckit.discovery.techselect
/speckit.discovery.decision
/speckit.discovery.codebase
/speckit.discovery.codebase-api-imp
/speckit.discovery.poc
```

适合场景：

- 需要做 go/no-go 可行性判断。
- 需要比较多个技术方案。
- 需要在 API、性能、迁移、UX、兼容性之间做场景化决策。
- 接手旧代码，需要先评估风险、复用资产和集成边界。
- 需要解释一个已实现 API、SDK 方法、CLI 命令、消息 topic 或内部能力的真实执行路径。
- 静态判断不够，需要一个有边界的 PoC。

典型产物会写在当前 feature 的 discovery 相关文件中，例如 feasibility、tech-selection、legacy codebase risk、PoC plan/result 或 API implementation overview。

### `intake`

`intake` 负责把外部输入变成可追踪证据，而不是直接替你生成需求。它的重点是保留来源、标记不确定性、做结构化归一化，让后续 `/speckit.specify`、`/speckit.plan` 能带着证据继续工作。

常用命令：

```text
/speckit.intake.prd
/speckit.intake.visual-design
/speckit.intake.test-cases
```

支持来源：

- PRD、产品说明、Markdown、PDF、导出的文档。
- 图片、线框图、设计 PDF、Figma 文件、Figma 页面或节点。
- 设计稿派生的视觉 IR、操作回放、动效锚点、视口截图和最终静态 HTML 交付证据。
- 既有测试、Gherkin、手工测试用例、QA 导出、测试管理表格。

主要产物：

```text
specs/<feature>/intake/prd/
specs/<feature>/intake/visual-design/
specs/<feature>/intake/visual-design/visual-ir/
specs/<feature>/intake/visual-design/delivery/
specs/<feature>/intake/test-cases/
```

这些目录中会包含 source manifest、source files、归一化 YAML、evidence packet 和 schema 校验所需材料。

### `preview`

`preview` 在实现前生成评审产物。它不改应用源码，不替代实现；它用当前 feature 的规格、计划和契约生成可以讨论的自包含 HTML wireflow。

常用命令：

```text
/speckit.preview.wireflow <low|mid|high> [design focus]
```

主要产物：

```text
specs/<feature>/preview/wireflow.html
```

使用建议：

- 需求还早期：用 `low` 看主路径和分支。
- 产品、设计和工程需要一起评审：用 `mid`。
- 交互、状态、权限、响应式和错误反馈要确认：用 `high`。

### `repository-governance`

`repository-governance` 生成 agent 可读的仓库治理说明。它把目录职责、SSOT 读取顺序、工具链证据、agent 平台适配和仓库事实投影到当前 agent 的上下文文件中。

常用命令：

```text
/speckit.repository-governance.generate
```

它也注册了 hook，可在 constitution、plan、tasks 之后提示生成或更新治理内容。

主要产物：

```text
.specify/memory/repository-governance.md
```

以及当前集成对应的 agent context 文件中的受管治理段。

使用建议：

- 多 agent 协作时使用。
- 新人或新 agent 接手仓库时使用。
- 仓库目录结构、构建工具、SSOT 或平台适配规则变化后使用。

### `agent-context`

`agent-context` 是上下文维护扩展。它读取集成元数据，并更新当前 agent 的说明文件，例如 `AGENTS.md`、`CLAUDE.md` 或 `.github/copilot-instructions.md`。

常用命令：

```text
/speckit.agent-context.update
```

它主要维护受管 Spec Kit 段，不应覆盖用户在标记之外手写的内容。

## 默认预设

### `workflow-preset`

`workflow-preset` 是这个本地分发版的核心增强预设。它包装规格、检查、规划和任务阶段；实现阶段始终使用当前 Spec Kit core 命令。

它会增强这些命令：

```text
/speckit.specify
/speckit.clarify
/speckit.checklist
/speckit.constitution
/speckit.analyze
/speckit.plan
/speckit.tasks
```

主要增强：

- `/speckit.checklist` 增加 BDD、NFR、视觉保真 readiness gate。
- `/speckit.constitution` 增加 Change Scope Granularity 治理。
- `/speckit.plan` 增加 Phase 0 行为投影、BDD/UIF/data fixture intent 和可选设计产物。
- `/speckit.tasks` 从行为契约、接口契约、`research.md`、`quickstart.md` 映射实现、验证、集成/E2E 和最终 Code Review 清单。
- `/speckit.implement` 不由 preset 复制或覆盖；当前 core 命令按顺序执行 `tasks.md`，其中 Final Code Review 是最后的强制阶段。

典型产物：

```text
specs/<feature>/contracts/bdd/
specs/<feature>/contracts/uif/
specs/<feature>/contracts/behavior/
```

## 社区资源

上游文档站收录了社区贡献的扩展、预设、bundle、walkthrough 和相关项目：

- [Extensions](https://github.github.io/spec-kit/community/extensions.html) — commands, hooks, and capabilities
- [Presets](https://github.github.io/spec-kit/community/presets.html) — template and terminology overrides
- [Bundles](https://github.github.io/spec-kit/community/bundles.html) — role and team stacks composed from existing components
- [Walkthroughs](https://github.github.io/spec-kit/community/walkthroughs.html) — end-to-end SDD scenarios
- [Friends](https://github.github.io/spec-kit/community/friends.html) — projects that extend or build on Spec Kit

> [!NOTE]
> Community contributions are independently created and maintained by their respective authors. Review source code before installation and use at your own discretion.

Want to contribute? See the [Extension Publishing Guide](extensions/EXTENSION-PUBLISHING-GUIDE.md), the [Presets Publishing Guide](presets/PUBLISHING.md), or the [Community Bundles guide](docs/community/bundles.md).

## 🤖 Supported AI Coding Agent Integrations

Spec Kit works with 30+ AI coding agents — both CLI tools and IDE-based assistants. See the full list with notes and usage details in the [Supported AI Coding Agent Integrations](https://github.github.io/spec-kit/reference/integrations.html) guide.

Run `specify integration list` to see all available integrations in your installed version.

## Available Slash Commands

After running `specify init`, your AI coding agent will have access to these slash commands for structured development. For integrations that support skills mode, passing `--integration <agent> --integration-options="--skills"` installs agent skills instead of slash-command prompt files.

### Core Commands

Essential commands for the Spec-Driven Development workflow:

| Command                  | Agent Skill            | Description                                                                |
| ------------------------ | ---------------------- | -------------------------------------------------------------------------- |
| `/speckit.constitution`  | `speckit-constitution` | Create or update project governing principles and development guidelines   |
| `/speckit.specify`       | `speckit-specify`      | Define what you want to build (requirements and user stories)              |
| `/speckit.plan`          | `speckit-plan`         | Create technical implementation plans with your chosen tech stack          |
| `/speckit.tasks`         | `speckit-tasks`        | Generate actionable task lists for implementation                          |
| `/speckit.taskstoissues` | `speckit-taskstoissues`| Convert generated task lists into GitHub issues for tracking and execution |
| `/speckit.implement`     | `speckit-implement`    | Execute all tasks to build the feature according to the plan               |
| `/speckit.converge`      | `speckit-converge`     | Assess the codebase against spec/plan/tasks and append remaining work as new tasks |

### Optional Commands

Additional commands for enhanced quality and validation:

| Command              | Agent Skill            | Description                                                                                                                          |
| -------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `/speckit.clarify`   | `speckit-clarify`      | Clarify underspecified areas (recommended before `/speckit.plan`; formerly `/quizme`)                                                |
| `/speckit.analyze`   | `speckit-analyze`      | Cross-artifact consistency & coverage analysis (run after `/speckit.tasks`, before `/speckit.implement`)                             |
| `/speckit.checklist` | `speckit-checklist`    | Generate custom quality checklists that validate requirements completeness, clarity, and consistency (like "unit tests for English") |

## 🔧 Specify CLI Reference

For full command details, options, and examples, see the [CLI Reference](https://github.github.io/spec-kit/reference/overview.html).

## 🧩 Making Spec Kit Your Own: Extensions & Presets

Spec Kit can be tailored to your needs through two complementary systems — **extensions** and **presets** — plus project-local overrides for one-off adjustments:

| Priority | Component Type                                    | Location                         |
| -------: | ------------------------------------------------- | -------------------------------- |
|      ⬆ 1 | Project-Local Overrides                           | `.specify/templates/overrides/`  |
|        2 | Presets — Customize core & extensions             | `.specify/presets/templates/`    |
|        3 | Extensions — Add new capabilities                 | `.specify/extensions/templates/` |
|      ⬇ 4 | Spec Kit Core — Built-in SDD commands & templates | `.specify/templates/`            |

- **Templates** are resolved at **runtime** — Spec Kit walks the stack top-down and uses the first match.
- Project-local overrides (`.specify/templates/overrides/`) let you make one-off adjustments for a single project without creating a full preset.
- **Extension/preset commands** are applied at **install time** — when you run `specify extension add` or `specify preset add`, command files are written into agent directories (e.g., `.claude/commands/`).
- If multiple presets or extensions provide the same command, the highest-priority version wins. On removal, the next-highest-priority version is restored automatically.
- If no overrides or customizations exist, Spec Kit uses its core defaults.

### Extensions — Add New Capabilities

Use **extensions** when you need functionality that goes beyond Spec Kit's core. Extensions introduce new commands and templates — for example, adding domain-specific workflows that are not covered by the built-in SDD commands, integrating with external tools, or adding entirely new development phases. They expand *what Spec Kit can do*.

```bash
# Search available extensions
specify extension search

# Install an extension
specify extension add <extension-name>
```

For example, extensions could add Jira integration, post-implementation code review, V-Model test traceability, or project health diagnostics.

See the [Extensions reference](https://github.github.io/spec-kit/reference/extensions.html) for the full command guide. Browse the [community extensions](https://github.github.io/spec-kit/community/extensions.html) for what's available.

### Presets — Customize Existing Workflows

Use **presets** when you want to change *how* Spec Kit works without adding new capabilities. Presets override the templates and commands that ship with the core *and* with installed extensions — for example, enforcing a compliance-oriented spec format, using domain-specific terminology, or applying organizational standards to plans and tasks. They customize the artifacts and instructions that Spec Kit and its extensions produce.

```bash
# Search available presets
specify preset search

# Install a preset
specify preset add <preset-name>
```

For example, presets could restructure spec templates to require regulatory traceability, adapt the workflow to fit the methodology you use (e.g., Agile, Kanban, Waterfall, jobs-to-be-done, or domain-driven design), add mandatory security review gates to plans, enforce test-first task ordering, or localize the entire workflow to a different language. The [pirate-speak demo](https://github.com/mnriem/spec-kit-pirate-speak-preset-demo) shows just how deep the customization can go. Multiple presets can be stacked with priority ordering.

See the [Presets reference](https://github.github.io/spec-kit/reference/presets.html) for the full command guide, including resolution order and priority stacking.

## 📦 Bundles: Role-Based Setups

Extensions and presets are individual building blocks. A **bundle** packages a
curated set of them — extensions, presets, steps, and workflows — into a single,
versioned, role-oriented setup so a whole team persona (product manager, business
analyst, security researcher, developer, …) can be provisioned with one command.

A bundle is described by a hand-written `bundle.yml` manifest. It pins each
component to a version and, optionally, targets a specific integration; a bundle
with no `integration` is **agnostic** and inherits whatever integration the
project already uses.

```bash
# Discover bundles in the active catalog stack
specify bundle search [<query>]

# Inspect the exact component set a bundle will add (equals what install does)
specify bundle info <bundle-id>

# Install a bundle's full component set in one operation
specify bundle install <bundle-id>

# See what's installed, then update or remove non-destructively
specify bundle list
specify bundle update <bundle-id>     # or --all
specify bundle remove <bundle-id>     # removes only this bundle's components
```

Bundles resolve from a **priority-ordered catalog stack** (project > user >
built-in). Each source carries an install policy: `install-allowed` sources can
be installed from, while `discovery-only` sources are visible in `search`/`info`
but refuse installation. Manage the stack with `specify bundle catalog list|add|remove`.

Authors validate and package bundles locally. Distribution is hosting the built
artifact and adding a catalog source; community bundle submissions use the
[Bundle Submission](https://github.com/github/spec-kit/issues/new?template=bundle_submission.yml)
issue template so required component catalogs and install evidence can be reviewed:

```bash
specify bundle validate --path ./my-bundle      # structural + reference checks
specify bundle build --path ./my-bundle         # produce a versioned .zip artifact
```

Four ready-to-read example manifests live under
[`examples/bundles/`](examples/bundles/) (product manager, business analyst,
security researcher, developer).

Key guarantees: `info` shows exactly what `install` adds (transparency);
installs are idempotent and confined to the project root; `remove` never touches
components another installed bundle still needs; and all consume/author commands
work **offline** against local or pinned sources.

### When to Use Which

| Goal | Use |
| --- | --- |
| Add a brand-new command or workflow | Extension |
| Customize the format of specs, plans, or tasks | Preset |
| Integrate an external tool or service | Extension |
| Enforce organizational or regulatory standards | Preset |
| Ship reusable domain-specific templates | Either — presets for template overrides, extensions for templates bundled with new commands |
| Provision a complete role-based setup in one command | Bundle |

## 📚 Core Philosophy

Spec-Driven Development is a structured process that emphasizes:

- **Intent-driven development** where specifications define the "*what*" before the "*how*"
- **Rich specification creation** using guardrails and organizational principles
- **Multi-step refinement** rather than one-shot code generation from prompts
- **Heavy reliance** on advanced AI model capabilities for specification interpretation

## 🌟 Development Phases

| Phase                                    | Focus                    | Key Activities                                                                                                                                                     |
| ---------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **0-to-1 Development** ("Greenfield")    | Generate from scratch    | <ul><li>Start with high-level requirements</li><li>Generate specifications</li><li>Plan implementation steps</li><li>Build production-ready applications</li></ul> |
| **Creative Exploration**                 | Parallel implementations | <ul><li>Explore diverse solutions</li><li>Support multiple technology stacks & architectures</li><li>Experiment with UX patterns</li></ul>                         |
| **Iterative Enhancement** ("Brownfield") | Brownfield modernization | <ul><li>Add features iteratively</li><li>Modernize legacy systems</li><li>Adapt processes</li></ul>                                                                |

For existing projects, keep Spec Kit tooling updates separate from feature
artifact evolution: refresh managed project files when upgrading, and update
`specs/` artifacts when intended behavior changes. The
[Evolving Specs guide](./docs/guides/evolving-specs.md) describes the
recommended brownfield loop.

## 🎯 Experimental Goals

Our research and experimentation focus on:

### Technology independence

- Create applications using diverse technology stacks
- Validate the hypothesis that Spec-Driven Development is a process not tied to specific technologies, programming languages, or frameworks

### Enterprise constraints

- Demonstrate mission-critical application development
- Incorporate organizational constraints (cloud providers, tech stacks, engineering practices)
- Support enterprise design systems and compliance requirements

### User-centric development

- Build applications for different user cohorts and preferences
- Support various development approaches (from vibe-coding to AI-native development)

### Creative & iterative processes

- Validate the concept of parallel implementation exploration
- Provide robust iterative feature development workflows
- Extend processes to handle upgrades and modernization tasks

## 🔧 Prerequisites

- **Linux/macOS/Windows**
- [Supported](#-supported-ai-coding-agent-integrations) AI coding agent.
- [uv](https://docs.astral.sh/uv/) for package management (recommended) or [pipx](https://pipx.pypa.io/) for persistent installation
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

If you encounter issues with an agent, please open an issue so we can refine the integration.

## 📖 Learn More

- **[Complete Spec-Driven Development Methodology](./spec-driven.md)** - Deep dive into the full process
- **[Quick Start Guide](https://github.github.io/spec-kit/quickstart.html)** - Step-by-step implementation walkthrough

## Bundle 能力

Bundle 把一组扩展、预设、步骤和 workflow 打包成一个版本化的角色或团队配置。它适合把产品经理、业务分析、安全研究、开发等 persona 的完整工具栈用一次安装交付给项目。

Bundle 使用手写的 `bundle.yml` manifest，声明组件版本，也可以指定目标 integration。未指定 integration 的 bundle 是 agnostic，会继承项目已有 integration。

常用命令：

```bash
specify bundle search [<query>]
specify bundle info <bundle-id>
specify bundle install <bundle-id>
specify bundle list
specify bundle update <bundle-id>     # or --all
specify bundle remove <bundle-id>
```

Bundle 从按优先级排列的 catalog stack 解析（project > user > built-in）。catalog source 可以是 `install-allowed` 或 `discovery-only`；后者可搜索和查看，但不能安装。管理 catalog 使用 `specify bundle catalog list|add|remove`。

作者可本地校验并打包 bundle：

```bash
specify bundle validate --path ./my-bundle
specify bundle build --path ./my-bundle
```

可参考 `examples/bundles/` 下的 product manager、business analyst、security researcher 和 developer 示例。

| 目标 | 使用 |
| --- | --- |
| 新增一个命令或 workflow | Extension |
| 自定义 spec、plan 或 tasks 的格式 | Preset |
| 集成外部工具或服务 | Extension |
| 强制组织级或合规标准 | Preset |
| 发布可复用领域模板 | Extension 或 Preset |
| 一次性安装完整角色工具栈 | Bundle |

## 推荐使用路径

### 新项目

```text
/speckit.inception.product   # 可选
/speckit.constitution        # greenfield；用户指定输入和更新范围
/speckit.specify
/speckit.clarify
/speckit.checklist
/speckit.discovery.feasibility
/speckit.plan
/speckit.preview.wireflow mid
/speckit.tasks
/speckit.analyze
/speckit.implement
```

### 旧仓库接入

```text
/speckit.discovery.codebase
/speckit.constitution        # brownfield；显式授权仓库证据范围
/speckit.repository-governance.generate
/speckit.specify
/speckit.checklist
/speckit.plan
/speckit.tasks
/speckit.implement
```

### 已有 PRD、设计或测试用例

```text
/speckit.intake.prd
/speckit.intake.visual-design
/speckit.intake.test-cases
/speckit.specify
/speckit.clarify
/speckit.plan
```

### 前端和交互功能

```text
/speckit.intake.visual-design
/speckit.specify
/speckit.preview.wireflow low
/speckit.plan
/speckit.preview.wireflow mid
/speckit.tasks
/speckit.implement
```

### 小功能或实验

```bash
specify preset add lean
```

然后使用轻量核心链路：

```text
/speckit.specify
/speckit.plan
/speckit.tasks
/speckit.implement
```

### Bug 修复

```bash
specify extension add bug
```

然后：

```text
/speckit.bug.assess
/speckit.bug.fix
/speckit.bug.test
```

## 产物地图

| 目录或文件 | 来源 | 含义 |
| --- | --- | --- |
| `.specify/memory/architecture.md` | `workflow-preset` 的 `/speckit.constitution` | 项目级边界、概念、技术证据、规划约束和缺口。 |
| `.specify/memory/repository-governance.md` | `repository-governance` | 内部仓库治理 SSOT。 |
| `inception/product/` | `inception` | 产品 UC 和 medium/high wireflow 启动设计产物。 |
| `specs/<feature>/intake/` | `intake` | PRD、视觉设计、测试用例的结构化证据包。 |
| `specs/<feature>/preview/` | `preview` | 单一自包含 HTML wireflow 预览。 |
| `specs/<feature>/contracts/bdd/` | `workflow-preset` | BDD 行为契约。 |
| `specs/<feature>/contracts/uif/` | `workflow-preset` | UI flow / interface fidelity 契约。 |
| `specs/<feature>/contracts/behavior/` | `workflow-preset` | 行为场景、fixture、assertion 等正式契约。 |
| `.specify/bugs/<slug>/` | `bug` | 单个 bug 的 assess/fix/test 报告。 |
| `.specify/extensions/git/git-config.yml` | `git` | Git 分支和自动提交配置。 |

## 本地安装和管理

查看已安装扩展：

```bash
specify extension list
```

安装本地内置扩展：

```bash
specify extension add bug
specify extension add git
```

从本地源码目录安装扩展：

```bash
specify extension add --dev extensions/preview
specify extension add --dev extensions/intake
```

查看已安装预设：

```bash
specify preset list
```

安装本地内置预设：

```bash
specify preset add lean
```

从本地源码目录安装预设：

```bash
specify preset add --dev presets/workflow-preset
```

禁用或启用扩展：

```bash
specify extension disable preview
specify extension enable preview
```

移除预设：

```bash
specify preset remove lean
```

## 开发验证

本仓库是 Python 项目。常用验证命令：

```bash
uv run pytest
```

只验证集成相关测试：

```bash
uv run pytest tests/integrations -v
```

验证本地扩展或预设时，优先在临时项目中使用 `--dev` 安装源码目录：

```bash
specify extension add --dev extensions/preview
specify extension add --dev extensions/intake
specify preset add --dev presets/workflow-preset
```

## 维护提示

- README 中的默认扩展和默认预设必须与 `src/specify_cli/commands/init.py` 保持一致。
- 扩展命令清单应以各自 `extension.yml` 为准。
- 预设覆盖关系应以各自 `preset.yml` 为准。
- `git` 是本地内置可选扩展，不应写成默认安装。
- `template`、`selftest`、`scaffold`、`self-test` 是开发/测试用途，不应包装成普通用户主路径。

## 许可证

本项目使用 MIT License。详见 [LICENSE](./LICENSE)。
