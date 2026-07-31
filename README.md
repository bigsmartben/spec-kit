<div align="center">
    <img src="https://raw.githubusercontent.com/bigsmartben/spec-kit/main/media/logo_large.webp" alt="Spec Kit Logo" width="180" height="180"/>
    <h1>Spec Kit Local Extensions</h1>
    <h3><em>面向本地增强工作流的 Spec Kit 分发版。</em></h3>
</div>

<p align="center">
    <strong>这个仓库的重点不是复述基础用法，而是提供一套小而清晰的默认流程，以及按需启用的扩展和预设。</strong>
</p>

---

## 本地定位

这个 checkout 是一个带本地增强能力的 Spec Kit 仓库。它保留核心 `specify` 工作流，默认只安装核心 `git` 扩展和 `workflow-preset` 预设；其他扩展均按需启用。

本 README 只介绍仓库中实际存在的本地内容：

- `extensions/` 下的本地扩展。
- `presets/` 下的本地预设。
- `specify init` 默认会安装的增强能力。
- 需要手动安装的可选能力。
- 扩展和预设运行后会写入的主要产物。

如果你只是想知道这个仓库相比基础流程多了什么，可以先看这三件事：

- 默认扩展：`git`。
- 默认预设：`workflow-preset`。
- 可选扩展：`discovery`、`preview`、`agent-context`、`arch`、`bug`。

## 快速开始

在本仓库开发或试用时，优先从仓库地址安装 CLI：

```bash
uv tool install specify-cli --from git+https://github.com/bigsmartben/spec-kit.git
```

初始化一个项目：

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

初始化完成后，`git` 扩展和默认预设会被复制到项目的 `.specify/` 目录，并注册到所选 agent 的命令或 skill 目录中。

## 默认安装内容

`specify init` 当前默认安装这些本地扩展和预设：

| 类型 | ID | 来源目录 | 作用 |
| --- | --- | --- | --- |
| 默认扩展 | `git` | `extensions/git` | 提供特性分支、远端检查和提交辅助命令。 |
| 默认预设 | `workflow-preset` | `presets/workflow-preset` | 从 Specify 引入 UI/UX 需求，从 Plan 引入 BDD、集成与 E2E 测试设计，由 Tasks 映射为执行清单，最终交给标准 Core Implement。 |

默认扩展列表在 `src/specify_cli/commands/init.py` 的 `DEFAULT_BUNDLED_EXTENSIONS` 中维护。默认预设列表在同文件的 `DEFAULT_BUNDLED_PRESETS` 中维护。

## 扩展审计与迁移

| 扩展 | 状态 | 原因与迁移 |
| --- | --- | --- |
| `git` | 默认保留 | 核心分支工作流，体积小且普遍适用。 |
| `discovery` | 内置、按需安装 | 技术调研仍有价值，但不是所有项目的必经阶段；使用 `specify extension add discovery`。 |
| `preview` | 内置、按需安装 | 实现前评审仍有价值，但不是默认流程；使用 `specify extension add preview`。 |
| `inception` | 已移除 | 旧产品启动和迁移命令不再作为权威阶段；把仍有价值的材料直接作为 `/speckit.specify` 的输入。 |
| `intake` | 已移除 | 工作流不再依赖其 schema、artifact 或 blocker route；由用户选择的来源工具提供证据，并在规格中记录来源。 |
| `repository-governance` | 已移除 | 其上下文投影与 `agent-context` 的独占职责冲突；需要受管上下文时显式安装 `agent-context`。 |

升级 CLI 不会扫描或删除既有项目的 `.specify/extensions/` 内容。因此，旧项目中已经安装的退役扩展文件会原样保留；如需清理，请由项目维护者显式运行 `specify extension remove <id>`。

## 可选扩展

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

### `agent-context`

`agent-context` 是完全 opt-in（显式启用）的上下文维护扩展。只有用户显式安装并启用它后，它才会更新 `AGENTS.md`、`CLAUDE.md` 或 `.github/copilot-instructions.md` 等文件。

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

## 视频概览

可通过[视频概览](https://www.youtube.com/watch?v=a9eR1xsfvHg&pp=0gcJCckJAYcqIYzv)了解 Spec Kit 的基本工作方式：

[![Spec Kit video header](https://raw.githubusercontent.com/github/spec-kit/main/media/spec-kit-video-header.jpg)](https://www.youtube.com/watch?v=a9eR1xsfvHg&pp=0gcJCckJAYcqIYzv)

## 社区资源

上游文档站收录了社区贡献的扩展、预设、bundle、walkthrough 和相关项目：

- [Extensions](https://github.github.io/spec-kit/community/extensions.html) — commands, hooks, and capabilities
- [Presets](https://github.github.io/spec-kit/community/presets.html) — template and terminology overrides
- [Bundles](https://github.github.io/spec-kit/community/bundles.html) — role and team stacks composed from existing components
- [Walkthroughs](https://github.github.io/spec-kit/community/walkthroughs.html) — end-to-end SDD scenarios
- [Friends](https://github.github.io/spec-kit/community/friends.html) — projects that extend or build on Spec Kit

贡献扩展、预设或 bundle 时，分别参考 [Extension Publishing Guide](extensions/EXTENSION-PUBLISHING-GUIDE.md)、[Presets Publishing Guide](presets/PUBLISHING.md) 和 [Community Bundles guide](docs/community/bundles.md)。

> [!NOTE]
> 社区贡献由各自作者独立创建和维护。安装或使用前请审查来源与代码。

## 可选本地扩展

### `bug`

`bug` 提供三段式 bug 工作流：评估、修复、验证。

命令：

```text
/speckit.bug.assess
/speckit.bug.fix
/speckit.bug.test
```

主要产物：

```text
.specify/bugs/<slug>/assessment.md
.specify/bugs/<slug>/fix.md
.specify/bugs/<slug>/test.md
```

安装：

```bash
specify extension add bug
```

### `git`

`git` 是内置可选扩展，不在当前默认扩展列表中。它负责 Git 初始化、feature branch、branch validation、remote 检测和可配置自动提交。

命令：

```text
/speckit.git.initialize
/speckit.git.feature
/speckit.git.validate
/speckit.git.remote
/speckit.git.commit
```

配置文件：

```text
.specify/extensions/git/git-config.yml
```

安装：

```bash
specify extension add git
```

## 可选本地预设

### `lean`

`lean` 把核心流程压缩成更轻量的命令，适合小功能、实验、低仪式感任务。

它覆盖这些命令：

```text
/speckit.constitution
/speckit.specify
/speckit.plan
/speckit.tasks
/speckit.implement
```

安装：

```bash
specify preset add lean
```

## 开发和测试用本地包

这些目录主要服务扩展/预设作者或测试，不建议作为普通项目主流程：

| 类型 | ID | 来源目录 | 用途 |
| --- | --- | --- | --- |
| 扩展模板 | `template` | `extensions/template` | 新扩展作者复制和改造的起始模板。 |
| 扩展测试 | `selftest` | `extensions/selftest` | 验证扩展发现、安装和注册生命周期。 |
| 预设模板 | `scaffold` | `presets/scaffold` | 新预设作者复制和改造的起始模板。 |
| 预设测试 | `self-test` | `presets/self-test` | 覆盖核心模板和命令，用于测试 preset 解析与组合。 |

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
/speckit.constitution        # greenfield；用户指定输入和更新范围
/speckit.specify
/speckit.clarify
/speckit.checklist
/speckit.plan
/speckit.tasks
/speckit.analyze
/speckit.implement
```

需要技术调研或 UI 评审时，先显式安装 `discovery` 或 `preview`，再把对应命令插入上述链路。

### 旧仓库接入

```text
/speckit.constitution        # brownfield；显式授权仓库证据范围
/speckit.specify
/speckit.checklist
/speckit.plan
/speckit.tasks
/speckit.implement
```

### 已有 PRD、设计或测试用例

把材料路径和来源说明直接传给 `/speckit.specify`；缺失或矛盾的证据保持为 blocker（阻塞项），由用户选择的来源工具补齐。

### 前端和交互功能

```text
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
specify extension add --dev extensions/discovery
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
specify extension add --dev extensions/preview
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
