# concept-fable Darwin 评估报告

**评估时间**：2026-07-01
**评估者**：Darwin Skill（9 维度静态扫描 + Runtime gate）
**目标**：concept-fable（原创 prompt 转 skill）的合入质量把关
**评估模式**：结构静态扫描（dim8 实测需外部 judge，本评估仅给静态估分）

> ⚠️ **方法论说明**：concept-fable 来自原创 prompt（无上游 sync），因此不做 dim8 baseline 对比。给 dim8 估分时基于示例质量（references/examples.md 3 个完整示例的内部一致性）。

## 仓库概况

| 项 | 值 |
|---|---|
| 来源 | 原创 prompt（hoye-custom，无 GitHub upstream）|
| 同步策略 | 不需 sync-config（原创）|
| 目标位置 | `writing/concept-fable/` |
| 文件清单 | 4 个 md（SKILL.md + 3 个 references/）|
| 字数总计 | SKILL.md ~250 行 + references ~880 行 |

## 文件结构

```
writing/concept-fable/
├── SKILL.md                        # 250 行，主入口
└── references/
    ├── blacklist.md                # 5 类黑名单 + 替换建议
    ├── angles.md                   # 30+ 切入角度（按 3 大类）
    └── examples.md                 # 3 个完整示例
```

## 9 维评分卡

### dim1 Frontmatter — 9/10

```yaml
name: concept-fable
description: "围绕用户给的 {concept} 写一则寓言来完整地解释它。1000字以内的
  虚构故事，2-3 个角色，全程不出现概念名称/术语，最后让读者隐约意识到讲的是
  什么；接着给概念解析 + 2 个具体可答的检验问题..."
```

**评估**：
- ✓ 触发词齐全：「用寓言讲 X」「写个故事解释 X」「fable explain X」「讲个寓言」「concept-fable」「/concept-fable」
- ✓ NOT FOR 边界明示（纯名词解释 / 长报告 / 文案写作）
- ✓ 描述长度适中（200+ 字），让 agent 决定激活时已有完整上下文
- −1：未提供具体的反向触发词案例（如「不要用 concept-fable 解释……」，仅抽象 NOT FOR）

### dim2 工作流清晰度 — 9/10

**流程图**（SKILL.md 显性）：

```
输入 {concept}
   ↓
1. 拆解概念
2. 选切入角度（→ references/angles.md）
3. 设计场景骨架
4. 黑名单自检（→ references/blacklist.md）
5. 写寓言正文
6. 写概念解析
7. 提 2 个检验问题
```

**评估**：
- ✓ 7 步流程清晰，每步有显性输出物
- ✓ 步骤间引用 references/（angles + blacklist + examples）
- ✓ 输出格式 3 部分（寓言 + 解析 + 问题）硬性
- −1：缺少 Phase 0 的「确认目标概念边界」步骤——可能误用「沉没成本」既可指心理学概念也可指经济学术语

### dim3 边界条件 / Failure-mechanism encoding — 10/10

**评估**：本 skill 的 dim3 是**核心引擎**，处理极好。

**SKILL.md 内的边界 / 失败模式表**：

| 场景 | 触发条件 | 处理 |
|---|---|---|
| 概念名出现在寓言中 | grep 命中 | 重写，用隐喻对象替代 |
| 角色开口讲解 | 看到「你看，这就是……」 | 重写，让动作承载 |
| 意象命中黑名单 | grep 18 个意象 | 替换 |
| 检验问题空泛 | 「你怎么看 X」 | 问具体可论证子问题 |
| 字数超 1000 | 字数检查 | 砍场景/角色/旁白 |
| 角色 4+ 个 | 角色计数 | 砍到 2-3 个 |
| 元素映射不一一对应 | 解析时发现 | 每行明确指出 |

**评估**：7 条 fallback + 三列「触发条件 / 处理动作 / 替代做法」+ 元原则「异常先告知用户，再处理；绝不静默跳过」。**SkillLens failure-mechanism encoding 标准落地**。满分。

### dim4 检查点设计 — 9/10

**自检清单**（SKILL.md「检验 / 自检」段）：

```
□ 字数 ≤ 1000？
□ 角色 ≤ 3 个？
□ 全文 grep 概念名 = 0 命中？
□ 全文 grep 该领域术语 = 0 命中？
□ 意象黑名单 5 类全过？
□ 没有角色跳出来讲解？
□ 结尾有没有留痕？
□ 概念解析的元素映射是否一一对应？
□ 检验问题是否具体可答？
```

**评估**：
- ✓ 9 项检查清单（自检维度清晰）
- ✓「概念名 grep」「术语 grep」是可执行的机器检查
- −1：缺少「必须先停」式的 🔴 CHECKPOINT 视觉标记（参考 ljg-skills / darwin-skill / beautiful-article 都用 🔴 + 🛑 STOP）

### dim5 指令具体性 — 10/10

**评估**（按 dim5 反例检查）：
- ❌ 「可能/也许/取决于/看情况/建议」等软化措辞 — 全文 grep 未命中
- ❌ 模糊步骤（"处理图片"）— 无，全是「grep 18 个意象」「字数 ≤ 1000」可执行命令
- ✓ 替换建议章节（blacklist.md）给出**每个禁用意象的替代候选**，避免 agent 偷懒
- ✓ 角度 → 概念速查表（angles.md）把抽象概念映射到具体场景

**评估**：dim5 是本 skill 强项——**不只说「不能这样」，还明确给出「应该那样」**，agent 可执行性强。满分。

### dim6 资源整合度 — 10/10

| 资源 | 文件 | 用途 |
|---|---|---|
| SKILL.md | 250 行 | 主入口 |
| references/blacklist.md | ~150 行 | 5 类黑名单 + 替换建议 |
| references/angles.md | ~200 行 | 30+ 切入角度 |
| references/examples.md | ~400 行 | 3 个完整示例（每个 ~850 字）|

**评估**：
- ✓ 资源齐全（4 文件，结构清晰）
- ✓ 引用关系明确（SKILL.md 主流程引用 references/，references 内部不互相嵌套）
- ✓ 每个 references 文件有明确「何时读」场景
- ✓ examples.md 自带「反向学习」表——把失败模式列出来，比单纯给示例更有价值
- 满分

### dim7 Runtime Neutrality — 10/10

**SKILL.md 自查**：

| 红灯类型 | 命中 |
|---|---|
| Badge 钉死 | 0 |
| 措辞钉死 | 0（SKILL.md 全程说「用户」「agent」，未绑特定 runtime）|
| 安装命令钉死 | 0 |
| 工具调用钉死 | 0 |
| 路径硬编码 | 0（无任何 `~/.claude/skills/` 或 `.claude/agents/` 引用）|

**评估**：
- ✓ 无任何 runtime-specific 引用
- ✓ 输出格式（Markdown 三部分）兼容所有 skills-aware runtime
- ✓ grep 命令是通用 Unix 工具
- 满分

### dim8 实测表现 — ⚠️ 静态估 9/10（待外部 judge 复核）

**references/examples.md 提供的 3 个完整示例**：

| # | 概念 | 寓言字数 | 角色数 | 关键观察 |
|---|---|---|---|---|
| 1 | 沉没成本 | ~850 字 | 1 主 + 客串 | grep 概念名 0 命中，6 元素映射一一对应 |
| 2 | 幸存者偏差 | ~880 字 | 1 主 + 客串 | grep 概念名 0 命中，6 元素映射一一对应 |
| 3 | 拓扑学 | ~880 字 | 2 | grep 概念名 0 命中，6 元素映射一一对应 |

**评估**：
- ✓ 3 个示例的内部一致性（黑名单自检记录表全过）
- ✓ 每个示例都做了一一对应的元素映射
- ✓ 检验问题具体可答（不是「你怎么看 X」式开放题）
- ⚠️ 本评估仅做静态一致性核对，未跑外部 judge 对比 baseline（无 baseline 可比——这是原创 skill）
- 给 9 分基于：3 个示例质量稳定 + 流程可执行

### dim9 High-Risk Action Blacklist — 10/10

**显式反例黑名单**（SKILL.md「反例」段）：

| # | 反例 | 为什么错 | 替代 |
|---|---|---|---|
| 1 | 寓言中出现概念名 | 钩子失效 | 用隐喻对象替代 |
| 2 | 角色开口讲解 | 破坏叙事纪律 | 让动作 / 对话承载 |
| 3 | 意象命中黑名单 | 陈词滥调 | 替换为具体场景 |
| 4 | 检验问题空泛 | 读者答不上 | 问具体子问题 |
| 5 | 字数超 1000 | 寓言 = 精炼 | 砍场景 |
| 6 | 角色 4+ 个 | 寓意稀释 | 砍到 2-3 个 |
| 7 | 元素映射不一一对应 | 读者无法连接 | 每行明确指出 |

**评估**：7 条反例，**每条都有「为什么错 + 替代做法」**——典型的 dim9 落地格式。**强于多数 A 档 skill 的反例处理**（很多只有「不要 X」，没有「替换 Y」）。满分。

## 总分

| 维度 | 分 |
|---|---|
| dim1 Frontmatter | 9.0 |
| dim2 工作流清晰度 | 9.0 |
| dim3 边界条件 | 10.0 |
| dim4 检查点设计 | 9.0 |
| dim5 指令具体性 | 10.0 |
| dim6 资源整合度 | 10.0 |
| dim7 Runtime Neutrality | 10.0 |
| dim8 实测表现 | ⚠️ 9.0（估）|
| dim9 反例黑名单 | 10.0 |
| **总分** | **86.0** |

## Runtime gate（独立扫描）

```
grep -nE "(在 Claude Code|Claude Code skill|Cursor only|~/\.claude/skills/[a-z]|/plugin install\b)" writing/concept-fable/SKILL.md references/*.md
```

**扫描结果**：0 命中。

**Runtime 判定**：✅ **pass**（零红灯）。

## 评级

**A 档**（86.0/100，Runtime pass）

concept-fable 是本集合的**第三个原创 skill**（继 github-skills-main 之后），填补了「用寓言解释概念」的能力空白。

## 与现有同档 skill 对比

| Skill | 总分 | 评级 | 关键特征 |
|---|---|---|---|
| beautiful-article | 86.5 | A | reacticle 协议 + 3 硬 checkpoint |
| darwin-skill | 86.5 | A+ | 9 维自评 + Microsoft 双向认可 |
| **concept-fable** | **86.0** | **A** | **黑名单 + 元素映射 + 3 完整示例** |

## 优势 / 改进点

### 优势
1. **黑名单处理极完整**（5 类 + 替换建议）
2. **3 个完整示例**含元分析（自检记录 + 元素映射表 + 反向学习）
3. **角度 → 概念速查表**降低 agent 选角度的认知负担
4. **零 Runtime 红灯**

### 改进点（后续可优化，非阻断）

| # | 改进点 | 影响 | 优先级 |
|---|---|---|---|
| 1 | 加 🔴 CHECKPOINT 视觉标记 | dim4 一致性 | 低 |
| 2 | 反向触发词示例（不要用 concept-fable 解释 X）| dim1 触发精度 | 低 |
| 3 | Phase 0 概念边界确认步骤 | dim2 流程闭环 | 中 |
| 4 | dim8 跑一次外部 judge 复核 | 实证验证 | 中 |

## 同步配置

- **source**: 原创（hoye-custom）
- **strategy**: N/A（无上游远程源）
- **sync-config.json 变更**: 无（不需 sync）
- **首次 commit**: 待提交

## 备注

1. **未跑实测分 dim8**：本评估为静态扫描，dim8 给 9 分基于示例质量推断。重要决策建议在外部 judge 环境下复核 3 个示例。
2. **原创 skill 的特殊性**：与 sync-config 同步的 skill 不同，本 skill 无外部源参照，「质量基线」由本集合的 Darwin 评估方法论确定。建议未来如发现使用问题，迭代 SKILL.md 时按 darwin-skill 的 hill-climbing + validation-gated 流程走。
3. **寓言 vs 比喻**：寓言是「完整故事 + 读者自悟」，比喻是「直接对比」——本 skill 强调前者，不混淆两者。