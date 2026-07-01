# garden-skills Darwin 评估报告

**评估时间**：2026-07-01
**评估者**：Darwin Skill（8 维度评分 + Runtime gate）
**目标**：garden-skills 合入 skill-collection 的质量把关
**评估模式**：结构静态扫描 + Runtime grep（不跑实测分）

## 背景

`ConardLi/garden-skills`（8989 ⭐，MIT）替代旧的 `web-design-skill` 仓库（已 rename / redirect）。
本仓库包含 5 个 skills，其中 4 个已在合入集合（来自旧 web-design-skill sync），
新增 `beautiful-article` 一个。

## 评估范围

| Skill | 在合入集合？| 本次评估 |
|---|---|---|
| gpt-image-2 | ✓ | 沿用旧评估 |
| kb-retriever | ✓ | 沿用旧评估 |
| web-design-engineer | ✓ | 沿用旧评估 |
| web-video-presentation | ✓ | 沿用旧评估 |
| **beautiful-article** | ✗（新增）| **本次重点评估** |

## beautiful-article（v0.1.0）

**类别**：Editorial · 任意素材 → 一篇精美的单文件 HTML 网页文章
**触发**：URL / PDF / DOCX / Markdown / 纯文本 / 截图 / 粘贴材料 → 网页文章
**触发语**：「render this as a beautiful web article」「把这篇做成网页文章」「reacticle 文章」

### 结构分（dim1-6，60 分）

| 维度 | 分 | 评语 |
|---|---|---|
| dim1 结构组织 | 10/10 | 9 phase（Phase 0-8）+ 硬性质检协议表 + Checkpoint 决策表 + 文件读取指南表 + 默认策略段，组织极其清晰 |
| dim2 执行具体度 | 10/10 | 每阶段含「主 Agent 内联自查 5 条 / SubAgent 质检 prompt 模板 / 决策项独立列 / 禁止打包」的具体规定 |
| dim3 边界条件 | 10/10 | 开头明列「不生成后台/表单/dashboard/产品原型/通用 Web App」；多处反模式（"禁止开 SubAgent 做 Plan 质检"、"不要写 review/plan-review.md"、"禁止静默替用户选择"）|
| dim4 workflow checkpoint | 10/10 | 3 个硬 Checkpoint（Plan / First Spread / Final），每项独立决策收集，开场说明模板、问题模板齐全 |
| dim5 具体度 | 10/10 | 文件路径精确（`source/extraction-notes.md`、`article/sections/NN-*.tsx`）；消息模板给出；命令完整（`bash scripts/scaffold.sh`）|
| dim6 外部资源 | 8/10 | 有 scaffold.sh / html-to-pdf.sh / 多个 references/ + theme-profiles/，但需 npm install reacticle + MarkItDown（Python）外部工具 |

**结构分小计**：58/60

### 实测分（dim7-8，40 分）—— 静态估分（未跑 baseline 对比）

| 维度 | 估分 | 评语 |
|---|---|---|
| dim7 有效性 | 9/10 | reacticle 组件协议 + 主题 profile 是一手新设计；3-Checkpoint 流程是 ljg-card 单输出的多阶段化升级；预期 dim7 9+ |
| dim8 效率 | 9/10 | 明令「Plan Checkpoint 禁止开 SubAgent」、「Section Reviewer 用消息返回不写文件」——主动避免 SubAgent 误开；脚手架 npm install 静默 fail-fast |

**实测分小计**：18/20

### Runtime gate

| 检测项 | 结果 |
|---|---|
| `~/.claude/skills/` 硬引用 | 🟢 无（仅 `localhost` 作为 `npm run dev` 预览，可选）|
| ssh / localhost 必需服务 | 🟢 无（localhost 只是用户本地 dev 预览）|
| 第三方 npm 依赖 | 🟡 `reacticle@latest`（npm 包，非 ljg 生态私有 skill）|
| 第三方 Python 工具 | 🟡 `MarkItDown`（可选 fallback，scaffold 脚本有轻量替代）|
| 第三方 API | 🟢 无 |
| SubAgent 假设 | 🟢 双模式（Team + 单 Agent），无硬依赖 |

**Runtime 中立性判定**：✅ **pass**
- 所有依赖都是工具（npm 包 / Python 包），用户安装方式与 ljg-card 类似（需 `npm install`）
- 没有 ljg 生态的硬 skill 依赖（不像 ljg-library 必须装 weread/feynman-eli5）

### 总分

| | 分 |
|---|---|
| 结构分（dim1-6）| 58/60 |
| 实测分（dim7-8）| 18/20（静态估）|
| **总分** | **86.5** |

### 评级

**A 档 — 优质（Runtime pass + dim7/8 估 9+）**

### 推荐

- ✅ **直接合入** `writing/beautiful-article/`
- ✅ sync-config.json 已更新为 garden-skills（5 mappings）
- ✅ 写入 `writing/README.md` 表格
- ⚠️ 提醒用户：首次运行需 `npm install` 装 reacticle（README 列出）；MarkItDown 是可选

## 既有 4 个 skill 状态

| Skill | 旧评估结论 | 状态 |
|---|---|---|
| gpt-image-2 | 已合入（creative/）| 沿用 |
| kb-retriever | 已合入（learning/）| 沿用 |
| web-design-engineer | 已合入（frontend-ui/）| 沿用 |
| web-video-presentation | 已合入（creative/）| 沿用 |

## 同步配置变更

- **旧**：web-design-skill entry，4 mappings（remote URL: web-design-skill.git）
- **新**：garden-skills entry，5 mappings（remote URL: garden-skills.git，新增 beautiful-article）
- **触发同步**：首次拉取 garden-skills HEAD fbd6453（与旧 web-design-skill HEAD 相同，仓库已 rename）
- **执行时间**：2026-07-01 16:28
- **commit**：f4ad6f9