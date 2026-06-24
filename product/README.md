# Product Skills

PM（产品经理）方法论合集，源自 [phuryn/pm-skills](https://github.com/phuryn/pm-skills)（MIT 协议）。

## 来源

- **原作者**：Paweł Huryn（[The Product Compass Newsletter](https://www.productcompass.pm/)）
- **上游仓库**：https://github.com/phuryn/pm-skills
- **协议**：MIT License（见 `LICENSE` 文件）
- **原始规模**：9 plugins / 68 skills / 42 commands

## 收录策略

从上游 68 个 skills 中精选 **15 个** 高价值、独立、与现有分类无重叠的 skill：

### 本目录（12 个）

| Skill | 用途 |
|-------|------|
| `opportunity-solution-tree` | Teresa Torres OST 框架：outcome→opportunities→solutions→experiments |
| `identify-assumptions-new` | 新产品 8 类风险假设识别 |
| `identify-assumptions-existing` | 已有产品 4 类风险假设识别 |
| `prioritize-assumptions` | Impact × Risk 矩阵排序 + 实验建议 |
| `metrics-dashboard` | North Star Metric + 输入指标设计 |
| `product-strategy` | 9 段 Product Strategy Canvas |
| `value-proposition` | 6 部分 JTBD 价值主张画布 |
| `strategy-red-team` | 对抗性假设压力测试（Darwin 86.9，全场最高） |
| `pre-mortem` | 预失败分析：Tigers / Paper Tigers / Elephants |
| `brainstorm-okrs` | 团队级 OKR 头脑风暴 |
| `outcome-roadmap` | outcome-focused 路线图 |
| `review-resume` | PM 简历评审（10 条最佳实践） |

### 收录到 `research/`（3 个，PM-research 类）

| Skill | 用途 |
|-------|------|
| `user-personas` | 用户画像提炼 |
| `market-sizing` | TAM/SAM/SOM 估算 |
| `summarize-interview` | 客户访谈纪要 |

## 不收录的 skill

- `pricing-strategy`（与 `business/pricing-strategy` 重大重叠）
- `porters-five-forces`（与 `research/competitive-analysis` 重叠）
- `create-prd`（输出模板与现有 PRD 类 skill 类似）

## 引用关系（软提示，非硬依赖）

部分 skill 在 SKILL.md 内提及"建议先用 X"（软引用），主要链路：
- `prioritize-assumptions` → `prioritization-frameworks`（上游未收录）
- `strategy-red-team` → `pre-mortem`
- `value-proposition` ← `gtm-strategy`, `ideal-customer-profile`, `growth-loops`, ...
- `product-vision` ↔ `product-strategy`

这些引用是文字提示，**不构成硬依赖**——每个 skill 独立可用。

## 不收录的部分

- **commands（42 个 slash 命令）**：绑 Claude Code `/slash` 机制，**Runtime gate 钉死风险**，未收录
- **pm-ai-shipping（2 个 AI 文档/审计 skill）**：与 `agent/` 和 `code-quality/` 部分重叠，**暂不收录**

## 同步策略

通过 `_ops/sync-config.json` 的 `pm-skills` 条目自动同步。当上游有新版本时，运行：

```powershell
& "D:\workSpace\hoye-skills-main\skill-collection\_ops\scripts\sync-skills.ps1"
```

即可拉取最新改动（仅拉取这 15 个映射的 skill，不影响上游其他 53 个 skill）。