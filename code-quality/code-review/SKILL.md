---
name: code-review
description: 按照团队 Code Review 规范审查代码变更（本地 git diff、staged diff、分支范围或 GitHub PR），并在需要时执行深度架构、安全、性能与冗余代码审查。当用户要求 review 代码、审查 PR、检查代码质量、关注 SOLID/架构/安全/race condition/性能/可删除代码时触发。
---

# Code Review

IRON LAW: 先锁定审查目标，再给结论；不要在没有 diff、staged、PR 或 commit range 的情况下静默扫描整个仓库，也不要混用两套严重等级。

依据团队约定，对代码变更执行统一的结构化审查。默认做基线 review；当用户明确要求，或命中高风险条件时，再加载深度审查参考资料补充分析。

## 参数

当用户或调用方已经隐含这些偏好时使用：

- `--depth standard|deep`
- `--focus general|architecture|security|cleanup`

默认值：

- `--depth standard`
- `--focus general`

## 工作流

### Step 1：锁定审查目标

先明确本次 review 的输入，不允许跳过：

1. **本地未暂存变更**：使用 `git diff`
2. **本地已暂存变更**：使用 `git diff --staged`
3. **分支或提交范围**：使用 `git diff <base>...<head>`
4. **远程 PR**：优先通过 GitHub MCP 拉取 PR 元信息、文件列表和 diff；`gh` CLI 仅作为兜底

如果用户只说“做个安全 review / 架构 review”，但当前没有可识别的 diff、staged、PR 或 range，必须先要求用户指定审查目标，不能默认扫描全仓。

大规模变更（> 500 行）先看 `git diff --stat`，按模块分批审查。

### Step 2：决定审查深度

默认走 `--depth standard --focus general`。

满足以下任一条件时，升级到 `--depth deep`：

- 用户明确提到：架构、SOLID、安全、race condition、性能、可删除代码、冗余代码
- 变更超过 500 行
- 变更涉及 auth、payments、data writes、network、shared primitives、公共组件、共享状态、API 签名

`--focus` 决定深度审查的主视角：

- `general`：标准代码审查
- `architecture`：架构、职责边界、SOLID、扩展性
- `security`：安全、权限、可靠性、并发风险
- `cleanup`：冗余逻辑、死代码、删除计划、后续迭代建议

### Step 3：建立变更上下文

在深入逐行审查前，先形成全局认知：

1. **目标**：从 PR 标题、描述、Issue/Ticket、commit message 中提炼业务意图
2. **核心改动**：一句话概括做了什么，再按模块罗列关键变更
3. **动机**：为什么做这个改动（修缺陷、重构、新功能、性能调优）
4. **波及面**：预判受影响的模块、页面、调用方和回归风险

如果 PR 描述缺失或含糊，在输出中标注：`PR 描述信息不足，以下基于 diff 推断。`

### Step 4：执行基线审查

所有 review 都必须经过这一步，对照 [RULES.md](RULES.md) 检查：

1. **正确性**：行为错误、状态异常、边界条件、数据闪烁
2. **风险**：安全、权限、回归、破坏性兼容变更
3. **可维护性**：重复逻辑、魔法值、职责混乱、模块放置不合理
4. **一致性**：是否遵循项目既有约定与团队规则
5. **体验细节**：加载态、错误态、交互反馈、响应式表现

### Step 5：按需执行深度审查

仅在 `--depth deep` 时加载对应参考资料：

- `references/solid-checklist.md`
- `references/security-checklist.md`
- `references/code-quality-checklist.md`
- `references/removal-plan.md`

深度审查关注点：

- **architecture**：SRP/OCP/LSP/ISP/DIP、边界划分、耦合度、抽象是否过度
- **security**：XSS、注入、SSRF、路径遍历、AuthZ/AuthN、密钥泄露、race condition、TOCTOU
- **general / security**：错误处理、性能热点、N+1、缓存、CPU/内存热点、空值/边界条件
- **cleanup**：死代码、冗余逻辑、可立即删除项、建议延后删除项与验证计划

当发现非小修小补级别的问题时，给出**最小可行修复方向**或**分步演进计划**，不要默认建议大重构。

### Step 6：统一格式输出

所有 findings 只允许使用以下标签：

| 标签 | 含义 | 是否阻断合并 |
|------|------|-------------|
| `[Required]` | 必须修改 | 是 |
| `[Optional]` | 建议改进 | 否 |
| `[Question]` | 需要作者澄清 | 视澄清结果而定 |
| `[FYI]` | 信息同步或后续建议 | 否 |

映射规则：

- 明确阻断合并的安全、正确性、回归、硬约束违规问题 → `[Required]`
- 非阻断但建议本 PR 处理的设计/质量问题 → `[Optional]`
- 需要作者补充上下文才能判断的问题 → `[Question]`
- 不要求当前处理的信息同步或后续建议 → `[FYI]`

每条反馈遵循 **问题 → 原因 → 建议** 的三段式，并带可点击定位。

输出结构：

```text
# 审查结果

## 变更摘要

**目标：** <本次变更要解决的问题或需求>
**核心改动：** <一句话概括>
**动机：** <为什么改>
**波及面：** <涉及的功能区域>

## 影响点评估

<对已有功能的影响范围及风险点，无影响注明“无”>

## 审查结论

**审查深度：** <standard | deep>
**关注重点：** <general | architecture | security | cleanup>
**总体判断：** <可合并 / 建议修改后合并 / 需澄清后再判断>

## 逐文件反馈

### <文件名>

#### [Required] <简短标题>
**定位：** [`<文件路径>:<起始行>-<结束行>`](<文件路径>)

<问题代码片段（使用 CODE REFERENCES 格式引用源码）>

**问题：** <哪里有问题>
**原因：** <为什么有问题>
**建议：** <如何修复>

## Next Steps

共发现 X 个问题（Required: _、Optional: _、Question: _、FYI: _）。

1. **全部修复** — 自动修复所有问题
2. **仅修复 Required** — 只处理阻断项
3. **指定修复** — 告诉我要修复哪些
4. **仅审查** — 不需要修改，审查结束
```

### Step 7：确认后再修改

默认是 **review-first** 工作流：

- 首次输出只做审查，不直接改代码
- 只有在用户明确选择修复方案后，才进入修改流程
- 修改完成后，重新运行必要的 lint、类型检查或测试，并汇总每条反馈的处理结果

## 输出规范

**无问题时**：不能只说“没问题”，必须说明：

- 检查了哪些方面
- 哪些范围未覆盖
- 残留风险或建议补做的验证

**定位要求**：

- 每条 `[Required]` / `[Optional]` / `[Question]` 反馈必须给出 `定位`
- 多处问题拆成多条反馈，避免一条反馈覆盖多个不连续区域

**格式约束**：

- 不要输出 `P0/P1/P2/P3`
- 不要混用另一套 severity 术语
- 不要在 review 结果前先给长篇总结

## Blocking 清单

以下类型的问题始终标记为 `[Required]`，不可降级：

- 用户可感知的行为错误
- 权限或安全漏洞
- 违反已确定的技术约束
- 可预见的回归风险
- 绕过静态检查的注释

## 作者自查清单

- [ ] 权限控制与角色匹配
- [ ] 无硬编码魔法值
- [ ] 复用了已有公共能力
- [ ] 关键交互已验证多端表现
- [ ] 公共资源变更已补充测试

## 辅助资源

- 团队规则基线：[RULES.md](RULES.md)
- 历史审查日志：[review-log.md](review-log.md)
- 深度审查参考：`references/solid-checklist.md`、`references/security-checklist.md`、`references/code-quality-checklist.md`、`references/removal-plan.md`
- PR 评论采集脚本：`scripts/fetch-pr-comments.mjs`
