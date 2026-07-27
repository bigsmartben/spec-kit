# Workflow Preset Plan 阶段职责与产物矩阵

**状态**：Review Baseline

**日期**：2026-07-27

**范围**：`workflow-preset` 的 `/speckit.plan` 阶段

## 1. 结论

Plan 阶段采用一个控制面和四条产物主轴：

```text
Plan Control Plane
└── Architecture Consumption 架构约束消费
    ├── X1 Technical Design 技术设计
    ├── X2 Data & Interface Design 数据与接口设计
    ├── X3 UI/UX Delivery Design UI/UX 交付设计
    └── X4 Test & Acceptance Design 测试与验收设计
```

Architecture Consumption 是控制面（Control Plane），不是与其他四类产物
平级的交付域。它约束四条主轴，但 Plan 不负责修改项目 Architecture。

BDD 不是 Plan 的上位结构。BDD 的归属是：

```text
Plan
└── Test & Acceptance Design
    └── Functional Acceptance
        └── BDD Technique / BDD Contract
```

Tasks 只把 Plan 产物映射成具体执行任务，不重新决定技术设计、测试策略、
UI/UX 验收方式或环境策略。

## 2. 生命周期职责边界

| 阶段 | 应当负责 | 不应负责 |
|---|---|---|
| Specify | 产品行为、UI 状态、视觉要求、验收标准 | 技术方案、测试层级、测试环境 |
| Checklist | 判断需求是否足以进入规划 | 生成场景、Fixture、测试策略 |
| Plan | 技术设计、数据和接口设计、UI/UX 交付设计、测试与验收设计、Task Readiness | Task ID、具体代码文件路径、实现顺序、执行代码 |
| Tasks | 将 Plan 产物映射成带路径和依赖的执行任务 | 重新决定测试层级、Fixture、视觉验证方式 |
| Implement | 执行 Tasks，并执行最后的 Code Review 任务 | 修改 Plan 或 Spec 使实现通过 |

Plan 对 Code Review 的责任是提供完整审查依据：

- `M + U` 设计边界；
- 接口与行为契约；
- 数据副作用和回滚约束；
- UI 状态、Viewport 和资源绑定要求；
- 测试路径与证据要求。

Tasks 将这些依据映射为 Final Code Review 阶段，Implement 按正常任务顺序执行。

## 3. Plan 主轴职责矩阵

| X 轴 | 输入 Input | 核心职责 | 主要输出 Output | 不负责 | 轴级门禁 Gate |
|---|---|---|---|---|---|
| Architecture Consumption | Constitution、Architecture、Spec、Checklist | 将项目级边界、原则、技术决策、约束和 Revisit Condition 投影到 Feature Plan | `plan.md`、`research.md`、Contracts、Quickstart 中的约束引用 | 修改 Architecture、发明架构决策 | 所有产物不得违反 Architecture；冲突返回 Constitution |
| X1 Technical Design | Architecture、Spec、Technical Context | 决定技术栈、模块边界、依赖方向、项目结构、`M + U` 设计对象 | `plan.md`、`research.md`、`class-diagram.md`、Project Structure | 具体 Task、代码文件写入操作、实现代码 | 技术未知项解决；模块和设计对象边界明确 |
| X2 Data & Interface Design | 领域需求、系统边界、技术决策、外部接口 | 定义领域实体、生命周期、接口协议、消息、跨边界序列、数据副作用 | `data-model.md`、`contracts/`、`contracts/sequences.md` | 测试套件、代码模型实现、Task ID | 实体、接口、Sequence 相互一致；失败和副作用可描述 |
| X3 UI/UX Delivery Design | Spec UI/UX、Visual Gate、设计证据、技术设计 | 把 UI/UX 需求转换为 View、State、Viewport、Component、Asset 和 Interaction 设计 | `ui-ux-design.md`、`contracts/uif/`、Visual/Asset Mapping | Provider Evidence 获取、测试执行、代码路径 | 每个 Required VIS/UI 项都有设计对象和交付方式 |
| X4 Test & Acceptance Design | 全部 Required CASE/VIS/UX/SEC/NFR 项，以及 X1-X3 设计产物 | 定义 Test Condition、Level、Type、Technique、Fixture、Environment、Oracle、Execution Path、Evidence | `research.md` 测试决策、`contracts/bdd/`、Test Contracts、`quickstart.md`、`test/test-readiness.md` | 具体测试文件路径、测试代码、执行结果 | 每个 Required Test Condition 可映射到下游测试或验收任务 |

## 4. Test 子域术语

BDD、测试层级和测试类型必须分开建模。

| 概念 | 含义 | 示例 |
|---|---|---|
| Test Level 测试层级 | 测试跨越多大范围 | unit、component、contract、integration、system、e2e |
| Test Type 测试类型 | 测试什么质量属性 | functional、visual、security、performance、reliability |
| Test Technique 测试技术 | 如何设计测试 | BDD、边界值、状态迁移、截图对比 |
| Execution Mode 执行模式 | 依赖如何运行 | mock、sandbox、real-system |
| Oracle 测试判定 | 如何判断通过 | 状态断言、错误码、UI 反馈、视觉差异 |
| Evidence 验收证据 | 保存什么证明结果 | 命令输出、截图、报告、数据库状态 |

UI/UX 在 Plan 中有双重归属：

| UI/UX 内容 | 所属子域 |
|---|---|
| 页面结构、组件状态、Viewport、资源绑定设计 | UI/UX Delivery Design |
| 状态、视觉、响应式、可访问性和用户旅程的验收方式 | Test & Acceptance Design |

## 5. Plan 内部子阶段

Plan 保留官方 Phase 0 和 Phase 1，并细分为六个内部子阶段：

```text
Y0  Planning Readiness Preflight  规划准入
Y1  Design Basis Projection       设计基础投影
Y2  Research & Decisions          研究与决策
Y3  Formal Design & Contracts     正式设计与契约
Y4  Delivery & Validation Paths   交付与验证路径
Y5  Plan Closeout & Task Handoff  规划收口与 Tasks 交接
```

Gate Consumption 是 Preflight，不占用 Phase 编号。Behavior Projection 是
Y1 在 Test 主轴内的一个动作，不是完整的 Phase 0。

## 6. X × Y 产物矩阵

| Y 子阶段 | Architecture Consumption | X1 Technical | X2 Data & Interface | X3 UI/UX Delivery | X4 Test & Acceptance | 阶段门禁 |
|---|---|---|---|---|---|---|
| Y0 Preflight | 读取 Architecture 和 Constitution；检查权威来源、边界、缺口 | 读取 Technical Context 和现有项目结构 | 识别数据、接口和外部系统范围 | 消费 UX/Visual Gate 和证据状态 | 消费 Behavior、UX、Security、NFR、Visual Gates | G0：Architecture 有效；全部 Requirement Gates PASS；失败时零写入 |
| Y1 Projection | 提取适用于当前 Feature 的边界、约束和 Revisit Conditions | 投影 Module/Capability 和候选 Design Objects | 投影 Entity、Interface、Sequence、Side-effect 候选 | 投影 View、State、Viewport、Component、Asset、Interaction 候选 | 建立统一 Test Conditions；BDD Draft 只覆盖功能行为子集 | G1：每个 Required Requirement 都进入至少一个设计轴或 Test Condition |
| Y2 Research | 验证决策是否服从 Architecture；记录 Revisit Evidence | 决定技术栈、依赖、模块划分和运行拓扑 | 决定存储、协议、接口所有权、事务和一致性策略 | 决定 UI 架构、组件映射、响应式、资产绑定和可访问性实现策略 | 决定 Level、Type、Technique、Fixture、Environment、Oracle、Evidence | G2：影响实现或验收的决策无未解决 Unknown |
| Y3 Formal Design | 检查正式设计没有越过系统边界 | 输出 `plan.md`、Project Structure、`class-diagram.md` | 输出 `data-model.md`、API/Message Contracts、Sequences | 输出 `ui-ux-design.md`、UIF、View/State/Viewport、Asset Mapping | 输出 BDD、Test Scenario、Fixture、Oracle、Visual/NFR/Security Test Definitions | G3：ID 和引用完整；设计、接口、UI、测试契约相互一致 |
| Y4 Paths | 将 Architecture 的运行和验证约束带入路径 | 定义 Setup、运行和部署前置条件，但不创建 Tasks | 定义 Contract、Integration、Data Side-effect 验证入口 | 定义 User Journey、View/State/Viewport、Accessibility 和 Visual Acceptance 路径 | 在 `quickstart.md` 定义可运行路径、环境、预期结果和证据 | G4：每个 Required Test Condition 有可运行路径或稳定 Blocker |
| Y5 Closeout | 检查无 Architecture 冲突或未处理 Revisit | 输出 `M + U` Design Object Index | 输出 Entity/Interface/Sequence/Side-effect Derivation Refs | 输出 UI/UX Delivery Readiness Matrix | 输出 Test Readiness Matrix | G5：所有 Required 产物可被 Tasks 纯映射；不得要求 Tasks 重新设计 |

## 7. Y0：Planning Readiness Preflight

| 项目 | 内容 |
|---|---|
| 输入 | `.specify/memory/constitution.md`、`architecture.md`、`spec.md`、六类 Checklist |
| 职责 | 判断 Plan 是否有权开始，不产生任何设计 |
| 输出 | 仅内存中的 PASS/BLOCKED 和阻塞报告 |
| 门禁 | Architecture 完整；Checklist Revision 与 Spec 一致；Applicable Gate 全部 PASS |
| 失败路由 | 产品问题回 Clarify；Provider Evidence 回 Intake；架构冲突回 Constitution |
| 禁止 | 创建目录、写 BDD Draft、更新 `plan.md` |

## 8. Y1：Design Basis Projection

该阶段只把需求投影成待设计对象，不做正式方案决策。

| X 轴 | 输入 | 输出 |
|---|---|---|
| Technical | Feature Scope、Architecture Boundary | Module/Capability、候选 Design Object |
| Data & Interface | Entity/State/API/Event Requirements | Entity、Interface、Sequence 候选清单 |
| UI/UX | VIS、UX、Interaction、Asset Requirements | View、State、Viewport、Component、Asset、UIF Intent |
| Test | CASE、VIS、UX、SEC、NFR Requirements | `TEST-*` Test Condition Inventory；功能条件可生成 BDD Draft |

G1 要求：

```text
每一个 Required Requirement
    → 至少一个 Delivery Design Object
    → 至少一个 Test Condition（当需要验收时）
```

示例：

```text
VIS-001 移动端支付失败状态
  → UI-VIEW-CHECKOUT-ERROR
  → UI-STATE-PAYMENT-DECLINED
  → TEST-CHECKOUT-VIS-001

CASE-PAYMENT-NEG-001
  → TEST-CHECKOUT-FUNC-001
  → BDD Draft Scenario
```

## 9. Y2：Research & Decisions

`research.md` 是所有 Plan 子域的决策记录，不只是技术调研或 BDD 测试层级。

| 决策域 | 应记录内容 |
|---|---|
| Technical | 技术栈、依赖、模块拓扑、部署约束 |
| Data | 存储、一致性、事务、迁移、回滚 |
| Interface | Protocol、Schema、API Ownership、External Dependency |
| UI/UX | 组件策略、响应式策略、Design Token、Asset/Fallback、Accessibility |
| Test | Test Level、Test Type、Technique、Priority/Risk、Fixture、Environment、Oracle、Evidence |

Test 决策示例：

```text
TEST-CHECKOUT-FUNC-001
Level: contract + integration + e2e
Type: functional + recovery
Technique: BDD + state transition
Environment: payment sandbox
Fixture: declined-card fixture
Evidence: API output + DB invariant + UI result
```

G2 要求：不能只写“使用 E2E”；必须明确测什么、在哪测、如何判定和收集什么证据。

## 10. Y3：Formal Design & Contracts

### 10.1 产物归属

| 产物 | Owner |
|---|---|
| `plan.md`、Project Structure | Technical Design |
| `class-diagram.md` | Technical Design |
| `data-model.md` | Data Design |
| API/Message Contracts | Interface Design |
| `contracts/sequences.md` | Data & Interface Design |
| `ui-ux-design.md` | UI/UX Delivery Design |
| `contracts/uif/` | UI/UX Interaction Design |
| `contracts/bdd/` | Test & Acceptance：Functional/BDD |
| Scenario/Fixture/Oracle Contracts | Test & Acceptance |
| Visual/Accessibility/NFR Oracles | Test & Acceptance |

### 10.2 职责边界

- `BehaviorScenarioInstance`、Fixture、Assertion 不进入领域 `data-model.md`；
- UIF 的 View、State、Viewport 是 UI/UX 设计产物；
- Test 子域引用 UIF 作为测试依据，不重复定义 UI；
- BDD 只覆盖适合行为表达的 Test Conditions；
- Visual、Accessibility、Performance 等 Test Condition 不强制生成 BDD；
- Formal Contracts 不包含完整实现代码或完整测试套件。

G3 要求：

```text
Requirement ID
  → Design Object ID
  → Test Condition ID
  → Contract / Oracle Ref
```

所有引用必须存在，不能只有字符串声明。

## 11. Y4：Delivery & Validation Paths

该阶段由 `quickstart.md` 承载可执行验证路径，但不包含完整测试代码。

| 路径类型 | 必须包含 |
|---|---|
| Contract | 前置服务、请求、预期响应、Contract Ref、证据 |
| Integration | 参与系统、数据准备、调用顺序、副作用、回滚 |
| E2E | Journey Entry、Actor、Environment、跨越边界、最终反馈 |
| UI Interaction | Start View、User Event、Expected State、API/UIF Ref |
| Visual | View、State、Viewport、Theme、Reference、Validation Mode |
| Accessibility | Interaction Mode、Rule、Expected Semantic Result |
| NFR | 测量条件、阈值、数据规模、采样和证据 |
| Security | Actor/Threat Condition、拒绝结果、审计证据 |
| Data Side-effect | Initial State、Mutation、Invariant、Rollback/Compensation |

G4 要求：

- 每个 Required Test Condition 有 Quickstart Path；
- 或有明确 Blocker 和责任路由；
- “后续手动验证”不能作为无环境、无方法、无证据的占位文本。

## 12. Y5：Plan Closeout & Tasks Handoff

Closeout 分成三个不同矩阵，避免 Behavior Matrix 统治所有领域。

### 12.1 Design Object Derivation Index

| Requirement | Axis | Module | Design Object | Artifact Ref | Blocker |
|---|---|---|---|---|---|
| `[REQ-ID]` | `[Technical/Data/Interface]` | `[M]` | `[U]` | `[path#ref]` | `[none/id]` |

用于 Implementation Task 映射。

### 12.2 UI/UX Delivery Readiness Matrix

| VIS/UX ID | View/State | Viewport | Component/Asset | UIF Ref | Delivery Ref | Acceptance Test ID | Blocker |
|---|---|---|---|---|---|---|---|
| `[VIS-ID]` | `[refs]` | `[refs]` | `[refs]` | `[UIF-ID]` | `[path#ref]` | `[TEST-ID]` | `[none/id]` |

用于 UI Implementation、Asset Binding、UI Acceptance 和 UI Review Task 映射。

### 12.3 Test Readiness Matrix

| Test Condition | Source | Type | Technique | Levels | Fixture | Environment | Oracle | Quickstart | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|
| `[TEST-ID]` | `[requirement ref]` | `[types]` | `[techniques]` | `[levels]` | `[refs]` | `[mode/ref]` | `[refs]` | `[path#ref]` | `[requirements]` | `[none/id]` |

BDD 场景通过 Technique 和 Artifact Ref 进入该矩阵，不再作为上位主键。

G5 定义：

```text
Plan Ready for Tasks
=
Technical Ready
+ Data/Interface Ready
+ UI/UX Delivery Ready
+ Test & Acceptance Ready
+ No Architecture Conflict
```

Tasks 只能执行以下映射：

```text
Design Object / Test Condition
  → concrete source/test/config/asset path
  → dependency order
  → checklist task
  → evidence task
  → final review task
```

Tasks 不得重新决定 Test Level、Environment、Visual Validation Mode 或
Fixture Strategy。

## 13. 建议的 Plan 产物结构

```text
specs/<feature>/
├── plan.md
├── research.md
├── data-model.md
├── class-diagram.md
├── ui-ux-design.md
├── quickstart.md
├── contracts/
│   ├── api-or-interface-contracts
│   ├── sequences.md
│   ├── uif/
│   ├── bdd/
│   └── test/
│       ├── scenarios
│       ├── fixtures
│       └── oracles
├── test/
│   └── test-readiness.md
└── tasks.md                  # 不由 Plan 创建
```

`test/test-readiness.md` 不是新的 `test-plan.md`：

- 决策仍在 `research.md`；
- 正式定义仍在 `contracts/`；
- 执行路径仍在 `quickstart.md`；
- Test Readiness 只负责聚合和门禁；
- 不复制已有内容。

## 14. 最终锁定

```text
Architecture Consumption 控制面
    ↓
Technical Design
Data & Interface Design
UI/UX Delivery Design
Test & Acceptance Design
    ↓
Cross-domain Closeout
    ↓
Task-ready Artifact Set
```

`/speckit.plan` 的主体结构应从 “Behavior Projection + BDD Closeout”
调整为以上四轴、六子阶段模型。
