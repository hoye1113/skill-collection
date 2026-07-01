# Research Wishlist

记录**未收录但值得调研 / 借鉴**的外部仓库 / 工具 / 论文。

目的：
- 留个"待研究"账本，避免每次从头搜
- 标注收录决策的理由（收录 / 暂不收录 / 待评估）
- 后续如需收录可快速回溯

---

## Fission-AI/OpenSpec — 📋 待研究 / 暂不收录

**链接**：https://github.com/Fission-AI/OpenSpec
**记录时间**：2026-07-01
**状态**：❌ 不进 sync-config（理由如下）

### 仓库概况

| 项 | 值 |
|---|---|
| ⭐ Stars | 58074 |
| 协议 | MIT |
| 主导语言 | TypeScript |
| 默认分支 | main |
| 最近 push | 2026-06-28 |
| npm 包 | `@fission-ai/openspec` |

### 不收录理由（核心）

OpenSpec 是 **TypeScript CLI 工具**（`@fission-ai/openspec` on npm），不是 SKILL.md 形式的 skill 集合。
- 仓库结构：`src/` + `bin/` + `schemas/` + `test/`，无独立 SKILL.md
- 安装方式：`npm install -g @fission-ai/openspec` —— 不通过 `~/.claude/skills/`
- `/opsx:propose` 等 slash 命令是 CLI 安装时注册的运行时绑定，不是 standalone skill

### 同类对比

| 工具 | 定位 | 与 OpenSpec 区别 |
|---|---|---|
| [GitHub Spec Kit](https://github.com/github/spec-kit) | SDD 重流程 | OpenSpec 更轻，迭代感强 |
| [AWS Kiro](https://kiro.dev) | SDD + IDE 锁死 | OpenSpec 跨工具，不绑 IDE |
| OpenSpec | 中间路线 | 跨 25+ AI 编程助手 |
| 本集合的 [product/](product/) 目录 | PRD / 机会解 / 指标 / PM 方法论 | 偏 PM 端，不走 SDD 流程 |

### 如果未来想收录

**收录方式 A**（推荐尝试）：
1. 在 OpenSpec 上游找其对应的 Claude Code skill 仓库（如果有），按 mapped 策略 sync
2. 或者将 OpenSpec 的 `/opsx:*` 命令重新打包为独立 SKILL.md（前置工作量大）

**收录方式 B**（最小改动）：
- 仅记录 `references/sdd-methodology.md` 作为方法论参考（不真正安装 OpenSpec）

### 适合阅读的章节

- `docs/opsx.md` — 新 workflow
- `docs/concepts.md` — 完整心智模型
- `docs/supported-tools.md` — 25+ 工具集成列表

### 待观察

- 是否会出独立的 Claude Code skill 子仓库
- 是否会迁移到纯 SKILL.md 协议

---

## 添加新条目模板

```markdown
## {org}/{repo} — {状态 emoji}

**链接**：https://github.com/{org}/{repo}
**记录时间**：YYYY-MM-DD
**状态**：{✅ 已收录 / 📋 待研究 / ❌ 不收录}

### 仓库概况
{stars, license, language, last push}

### 决策理由
{一句话说清收录 / 不收录的理由}

### 同类对比
{与现有 collection 中的相关 skill 对比}

### 未来收录路径
{如果有}
```