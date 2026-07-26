# 快速开始

这份指南面向本仓库分发版的 Spec Kit。它保留核心 Spec-Driven Development 流程，同时默认带上 Constitution 托管的单文件项目架构、仓库治理、BDD/UIF 行为契约、HTML 预览、实现期 handoff 和最终 code review receipt。

> [!NOTE]
> 自动化脚本同时提供 Bash (`.sh`) 和 PowerShell (`.ps1`) 版本。`specify` CLI 会按系统自动选择，也可以通过 `--script sh|ps` 显式指定。

## 推荐流程

> [!TIP]
> Spec Kit 会根据当前 Git 分支自动识别 active feature，例如 `001-photo-album`。切换规格时通常只需要切换分支。

生产功能建议使用默认增强链路：

```text
/speckit.inception.product        # 可选；仅在用户选择其产物作为输入时
/speckit.constitution             # 同时托管 constitution.md 与 architecture.md
/speckit.repository-governance.generate
/speckit.specify
/speckit.checklist
/speckit.clarify
/speckit.plan
/speckit.preview.wireflow mid
/speckit.tasks
/speckit.analyze
/speckit.implement
/speckit.converge
```

`/speckit.checklist` 在规划前根据 `spec.md` 生成多领域需求门禁；`/speckit.clarify` 修复其中的产品决策缺口并重评门禁。Planning Readiness 是运行时聚合结果，不会生成独立文件。`/speckit.analyze` 在实现前检查 spec、plan 和 tasks 的一致性；`/speckit.converge` 在实现后对照 feature artifacts 检查剩余缺口。如果 converge 追加了新任务，继续运行 `/speckit.implement` 并再次 converge，直到功能收敛。

接手旧仓库时仍运行 `/speckit.constitution`，但明确指定 brownfield（老项目）模式、允许检查的仓库范围，以及每项证据的角色。代码、README、Git 历史或约定路径不会自动成为架构事实。

小实验可以安装 `lean` 预设后走轻量路径：

```bash
specify preset add lean
```

```text
/speckit.specify -> /speckit.checklist -> /speckit.clarify -> /speckit.plan -> /speckit.tasks -> /speckit.implement
```

## 1. 安装 Specify

推荐使用 [uv](https://docs.astral.sh/uv/) 持久安装：

```bash
uv tool install specify-cli --from git+https://github.com/bigsmartben/spec-kit.git
```

从仓库地址安装：

```bash
uv tool install specify-cli --from git+https://github.com/bigsmartben/spec-kit.git
```

也可以一次性运行：

```bash
uvx --from git+https://github.com/bigsmartben/spec-kit.git specify init my-project
```

显式选择脚本类型：

```bash
specify init my-project --script ps  # Force PowerShell
specify init my-project --script sh  # Force POSIX shell
```

## 2. 初始化项目

选择你正在使用的 AI 编码助手：

```bash
specify init my-project --integration codex
cd my-project
```

在已有仓库中初始化：

```bash
specify init . --integration codex --force
```

如果 agent 工具没有安装，但你只想先生成 Spec Kit 文件：

```bash
specify init my-project --integration copilot --ignore-agent-tools
```

Codex 和部分 agent 支持 skills 模式：

```bash
specify init my-project --integration codex --integration-options="--skills"
```

查看当前支持的集成：

```bash
specify integration list
```

## 3. 建立项目原则与治理

在编码助手中先建立项目原则和独立的项目架构：

```text
/speckit.constitution Greenfield. Use this conversation as the selected source, exclude repository scaffolding, and update both Constitution and Architecture.
```

`/speckit.constitution` 会先确认输入协议：新项目/老项目/修订模式、目标、用户选择的来源、排除来源、仓库检查范围，以及本轮允许更新 Constitution、Architecture 或两者。`uc.md` 只是可选外部输入之一，不是门槛。

架构产物固定为一个文件：

```text
.specify/memory/architecture.md
```

其推理顺序是 System Boundary（系统边界）→ Conceptual Model（概念模型）→ Technical Decisions & Evidence（技术决策与证据）→ Planning Guardrails & Gaps（规划守则与缺口），不再生成 4+1、多视图或 PoC 目录。

生成或更新仓库治理规范：

```text
/speckit.repository-governance.generate
```

治理命令会生成或更新当前 integration 对应的 agent 上下文文件中的受管段，并维护内部治理记忆：

```text
.specify/memory/repository-governance.md
```

它用于约束 SSOT 读取顺序、目录责任、agent 平台适配和仓库事实证据。

## 4. 确认项目架构

项目架构已在 `/speckit.constitution` 阶段创建或修订。开始 feature（功能）规格前，确认该文件已经表达架构目标、用户授权来源，以及至少一个明确的责任边界：

主要产物：

```text
.specify/memory/architecture.md
```

后续 `/speckit.plan` 必须读取它：`research.md` 遵循已有技术决策和证据，`data-model.md` 保留概念及不变量，`contracts/` 保留系统边界和依赖方向，`plan.md` 与 `quickstart.md` 继续携带适用约束和缺口。若 feature 需要改变项目架构，停止 plan 并返回 `/speckit.constitution`。

## 5. 创建、检查并澄清规格

创建功能规格时只描述用户目标、业务规则和验收语义，不要过早指定技术栈：

```text
/speckit.specify Build a photo album app. Users can create albums, group photos by date, reorder albums by drag and drop, and preview photos as tiles. The UI must support mobile browsing and desktop bulk organization.
```

生成 requirements、behavior、UX、security、NFR 和 visual 领域的需求门禁：

```text
/speckit.checklist
```

如果门禁中存在产品决策缺口，再运行：

```text
/speckit.clarify Focus on album permissions, empty states, reorder conflict behavior, responsive UI states, and validation boundaries.
```

检查生成的领域清单：

```text
specs/<feature>/checklists/requirements.md
specs/<feature>/checklists/behavior.md
specs/<feature>/checklists/ux.md
specs/<feature>/checklists/security.md
specs/<feature>/checklists/nfr.md
specs/<feature>/checklists/visual.md
```

如果清单指出产品决策缺失，使用 `/speckit.clarify` 修复；provider 证据缺口返回对应 intake。所有适用门禁通过后，`/speckit.plan` 才会写入规划产物。

## 6. 预览 UI/UX 规格

对 UI、流程或交互有不确定性时，先生成保真度合适的预览产物：

```text
/speckit.preview.wireflow mid mobile album browsing and reorder flow
```

打开输出文件评审：

```text
specs/<feature>/preview/wireflow.html
```

这个文件只用于实现前评审 flow、信息架构、状态和交互假设，不会修改生产代码。也可以按需要使用 `/speckit.preview.wireflow low` 或 `/speckit.preview.wireflow high`。

## 7. 生成计划与行为契约

规划阶段再指定技术栈和工程约束：

```text
/speckit.plan Use Vite, TypeScript, SQLite, and a minimal dependency set. Store photo metadata locally and do not upload images.
```

默认 `workflow-preset` 会把已通过 readiness gate 的需求投影为 BDD、UIF 和 fixture intent，并在规划中正式化为契约。常见产物包括：

```text
specs/<feature>/behavior/bdd.draft.feature
specs/<feature>/behavior/uif.intent.json
specs/<feature>/behavior/data-fixtures.intent.json
specs/<feature>/contracts/bdd/
specs/<feature>/contracts/uif/
specs/<feature>/contracts/behavior/
specs/<feature>/quickstart.md
specs/<feature>/behavior/behavior-testability.md
```

`behavior/behavior-testability.md` 在计划收尾时把 Required Case、正式契约、fixture、assertion、视觉/NFR 引用和 `quickstart.md` 路径映射为 Task Readiness；它不属于需求清单目录。

## 8. 拆任务、分析并实现

生成任务：

```text
/speckit.tasks
```

默认任务生成会从 BDD、UIF、行为契约、接口契约、`research.md` 和 `quickstart.md` 派生测试层级、fixture/mock/sandbox 策略和验证证据要求。

实现前做一致性检查：

```text
/speckit.analyze
```

开始实现：

```text
/speckit.implement
```

中大型功能会进入 Core/Vertical Planner/Worker 三层 handoff 编排，常见输出：

```text
specs/<feature>/handoffs/implement/<run-id>/handoff-manifest.json
specs/<feature>/handoffs/implement/<run-id>/<shard>.json
specs/<feature>/handoffs/implement/<run-id>/<shard>.context.md
specs/<feature>/handoffs/implement/<run-id>/results/<shard>.json
```

如果当前 agent runtime 不支持隔离 subagent，按输出的新 worker 指令在干净会话中执行单个 handoff：

```text
/speckit.implement Use handoff JSON specs/<feature>/handoffs/implement/<run-id>/<shard>.json
```

Final Code Review 会以 `task_type: code_review` receipt 记录已检查的设计、sequence、contract、quickstart 来源、数据副作用审查、授权范围内的一致性修复和真实 e2e 缺口。

## 9. 收敛验证

实现后运行 converge，检查当前代码是否已经覆盖 feature artifacts，并把未完成工作追加回 `tasks.md`：

```text
/speckit.converge
```

如果 converge 追加了新任务，重新运行 `/speckit.implement`，再运行 `/speckit.converge`，直到它报告功能已收敛。

大型项目可以分阶段实现和验证，例如先完成核心结构，再做交互行为，最后补齐评论、权限、分配等垂直切片，避免单次上下文过载。

## 10. 可选：运行带 review gate 的 workflow

如果你想体验可恢复的端到端 workflow：

```bash
specify workflow add speckit
specify workflow run speckit --input spec="Build a small photo album app with album reorder and tile preview"
specify workflow status
specify workflow resume <run_id>
```

内置 `speckit` workflow 会串联 specify、plan、tasks、implement，并在 spec review 和 plan review 处暂停等待人工确认。

## 常见操作

查看增强能力：

```bash
specify extension search
specify preset search
specify workflow search
```

重新安装默认增强能力：

```bash
specify extension add arch
specify extension add inception
specify extension add preview
specify extension add repository-governance
specify preset add workflow-preset
```

升级当前项目中的 integration 文件：

```bash
specify integration upgrade
```

卸载某个 integration：

```bash
specify integration uninstall <key>
```

## 下一步

- 阅读 [完整方法论](../spec-driven.md)。
- 查看 [扩展系统](../extensions/README.md)、[预设系统](../presets/README.md) 和 [workflow 系统](../workflows/README.md)。
- 本地开发 CLI 时参考 [local-development](./local-development.md)。
