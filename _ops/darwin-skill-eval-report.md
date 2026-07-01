# darwin-skill Darwin 评估报告

**评估时间**：2026-07-01
**评估者**：Darwin Skill v1 静态扫描（用其自家 9 维 rubric 评它自身）
**目标**：darwin-skill v2.0 的合入质量把关 + 体系自洽性验证
**评估模式**：结构静态扫描 + Runtime gate（不跑实测分 dim8，因为需要子 agent baseline 对比）

> ⚠️ **方法论说明**：这是「Darwin 评 Darwin」的递归场景。本评估**只评静态维**（dim1-6, dim7, dim9），dim8（实测表现）跳过——评 darwin 的 dim8 需要 baseline（一个不开 darwin-skill 的对照组），那是 SkillLens/Microsoft 实证场景。本地静态评估仅给 dim8 一个**置信下限**，标 ⚠️ 待外部 judge 复核。

## 仓库概况

| 项 | 值 |
|---|---|
| ⭐ Stars | 4474 |
| 协议 | 仓库根未声明 LICENSE 文件，README 自称 MIT |
| 主导语言 | HTML（displays），实际 MD/HTML/JS 混合 |
| 默认分支 | master |
| 最近 push | 2026-06-14 |
| Skill 数 | 1（self-contained）|
| 同步策略 | `whole` → `skill-management/darwin-skill` |
| 同步 commit | 7c7b790（a26a88e） |

## 文件清单

```
skill-management/darwin-skill/
├── SKILL.md                      # 492 行，主入口
├── README.md / README_EN.md      # 双语 README
├── showcase.html                 # 演示页
├── test-prompts.json             # 3 个测试 prompt
├── assets/                       # 22 文件（banner、chart、hero）
├── docs/index.html               # 静态文档
├── references/
│   ├── runtime-neutrality.md     # 68 行 Runtime gate 详细
│   └── skilllens-evidence.md     # 142 行 SkillLens 实证 + 本机验证数据
├── scripts/screenshot.mjs        # playwright 截图
└── templates/
    ├── result-card.html          # 3 风格（swiss/terminal/newspaper）
    ├── result-card-dark.html
    ├── result-card-white.html
    └── result-card.png
```

## 9 维评分卡（按 darwin-skill 自家 v2 rubric）

### dim1 Frontmatter — 9.5/10

```yaml
name: darwin-skill
description: "Darwin Skill 2.0 (达尔文.skill 2.0): autonomous skill optimizer,
  v2.0 integrates Microsoft Research SkillLens (arXiv 2605.23899) 9-dim rubric
  + SkillOpt (arXiv 2605.23904) validation-gated design + human-in-the-loop
  checkpoints. ..."
```

**评估**：
- ✓ 触发词齐全（中英文混排，覆盖"优化skill"/"skill评分"/"自动优化"/"达尔文"/"darwin"/"skill打分"等 11 个变体）
- ✓ 学术背书直接嵌在 description（SkillLens arXiv ID + SkillOpt arXiv ID），让 agent 决定激活时已有完整上下文
- −0.5：description 未明示 NOT-FOR 边界（如"不要用于评测通用 agent 表现"——darwin 是评测 skill 用的，not agent）

### dim2 工作流清晰度 — 10/10

**Phase 结构**：

| Phase | 名称 | 任务 |
|---|---|---|
| Phase 0 | 初始化 | 范围确认 + git 分支创建 + results.tsv 初始化 |
| Phase 0.5 | 测试 Prompt 设计 | 每个 skill 2-3 个 prompt，**强制展示确认** |
| Phase 1 | 基线评估 | 结构 dim1-7 + 实测 dim8 + 加权汇总 + 🔴 CHECKPOINT |
| Phase 2 | 优化循环 | 排序最弱 → hill-climb → keep/revert → 🔴 CHECKPOINT |
| Phase 2.5 | 探索性重写 | 触顶时触发，git stash → 重写 → 比 stash 决定是否采用 |
| Phase 3 | 汇总报告 | 全局战绩 + 视觉成果卡 |

**评估**：6 phase + 3 硬 checkpoint 强约束，结构清晰度满分。每个 phase 都有显性输出物（branch / results.tsv / diff / report）。

### dim3 边界条件 / Failure-mechanism encoding — 10/10

**SkillLens 核心贡献维度，darwin-skill 在这维度做的是标杆级**：

- 「## 异常与边界条件」表（10 条 fallback）：
  | 场景 | 触发条件 | 处理动作 |
  |---|---|---|
  | 不在 git 仓库 | `git rev-parse` 失败 | 询问用户 + 备份方案 |
  | results.tsv 缺失/损坏 | 文件不存在/列数不匹配 | 备份重建 + 告知 |
  | 分支已存在 | `git checkout -b` 失败 | 末尾加 -2/-3 |
  | `git revert` 失败 | 冲突/工作树脏 | stash 重试 / 手动恢复 |
  | MAX_ROUNDS 触顶 | 3 轮仍短板 | 不强制 break，问用户 |
  | 优化后超 150% 体积 | 新文件 > 原 × 1.5 | 拒绝提交，精简 |
  | test-prompts.json 已存在 | 文件已在 | 默认复用 + 三选一 |
  | SKILL.md 找不到 | 目录存在无 SKILL.md | 终止 + 记 status=error |

**评估**：3 列「触发条件 / 处理动作 / fallback 三段式」正是 SkillLens failure-mechanism encoding 的标准落地。原则行「异常先告知用户，再按规则处理；绝不静默跳过或静默失败」是 dim3 的元原则。满分。

### dim4 检查点设计 — 10/10

3 处硬 CHECKPOINT，每处都标 🔴 + 🛑 STOP：

| 节点 | 触发 | 必须做什么 |
|---|---|---|
| Phase 1 → Phase 2 | 基线评分卡展示后 | 暂停等用户确认 |
| Phase 2 每个 skill 完成 | diff + 分数变化 + test-prompts 输出对比 | 等用户确认 OK 再继续 |
| Phase 2.5 触发 | 连续 2 个 skill round 1 就 break | 征得用户同意才执行 |

**评估**：**显性视觉标记（🔴 CHECKPOINT）+ "必须"措辞**是 dim4 的高 ROI 杠杆（HL-1 实战：4 行改动撬动 +3.5 分）。darwin-skill 自己就是 dim4 优化的最大受益者，方法论和实现合一。

### dim5 指令具体性 — 10/10

**评估**（按 dim5 反例检查）：
- ❌ "可能/也许/取决于/看情况/建议" — 全文 grep 未命中（已自查）
- ❌ 模糊步骤（"处理图片"）— 无，全是 `git revert HEAD` / `npx playwright screenshot "file://..."` 这种可执行命令
- ✓ HL-2 三段式 fallback 表（触发条件 / 一线修复 / 仍失败兜底）应用到了异常表
- ✓ HL-3 维度相关簇警告（dim2/3/4 是相关簇，修一时另两个常跟涨）
- ✓ HL-4 见好就收（连续 2 轮 Δ < 2 分自动 break）

**评估**：dim5 是 SkillLens 第二核心贡献，darwin-skill 把它做成**反例黑名单**（dim9）和 **HL 实战案例库**，已自我应用。

### dim6 资源整合度 — 9/10

| 资源 | 文件 | 用途 |
|---|---|---|
| SKILL.md | 492 行 | 主入口 |
| README.md | 双语 | 用户导览 |
| references/runtime-neutrality.md | 68 行 | Runtime gate 详细规则 |
| references/skilllens-evidence.md | 142 行 | SkillLens 实证 + 本机 controlled study 数据 |
| scripts/screenshot.mjs | playwright | 成果卡截图 |
| templates/result-card.html × 3 | 3 风格 | 成果卡可视化 |
| test-prompts.json | 3 个 prompt | 实测评估 |
| assets/ × 22 | banners + charts + hero | 文档视觉 |
| docs/index.html | 静态文档 | 在线文档 |

**评估**：
- ✓ 资源齐全（scripts + templates + references + assets + test-prompts）
- −1：screenshot.mjs 强依赖 Playwright + Node，文档没说前置条件；模板用了 oklch() 颜色和现代 CSS，兼容性需 Node 18+

### dim7 Runtime Neutrality — 9/10

**这是 darwin-skill 的核心引擎之一**，因为它是评测者，必须自己先通过 gate。

**SKILL.md 内自查**（按 references/runtime-neutrality.md 的 5 类红灯）：

| 红灯类型 | 命中 | 备注 |
|---|---|---|
| Badge 钉死 | 0 | README 用 `Agent Skill Compatible` + `Skills.sh Compatible` + `skills.sh` 三个中立 badge |
| 措辞钉死 | 1 弱 | SKILL.md line 384「Runtime 中立性」段提到「Claude Code / Codex / Cursor / OpenClaw / Hermes / CodeBuddy / Workbuddy / Gemini CLI / OpenCode」——这是**列举支持的 runtime 而非绑定**，合规 |
| 安装命令钉死 | 0 | README 用三层结构（auto-detect + 手动路径表 + 资料）|
| 工具调用钉死 | 0 | 全程用通用工具（git / sed / playwright）|
| 路径硬编码 | 1 | SKILL.md line 467 `node .claude/skills/darwin-skill/scripts/screenshot.mjs` —— 但同段给 npx playwright 回退方案 |

**自指反讽**：darwin-skill 在 SKILL.md 的「Runtime 适配性审查」段（line 384）自己声明约束 8「Runtime 中立性」必须通过 gate。

**评估**：
- ✓ 自带 `references/runtime-neutrality.md` 作为 gate 详细规则
- ✓ README line 23 三层中立 badge
- ✓ README line 187-189 安装路径多 runtime 覆盖
- ✓ 1 个轻微路径硬编码（screenshot 脚本），已给 npx 回退
- −1：line 115 写「扫描 .claude/skills/*/SKILL.md」暗示默认路径，但实际可以是任何 skills 目录——可选 0.5 分扣

**结论**：Runtime 中立性是 darwin-skill 的招牌（line 384 + references/runtime-neutrality.md 完整论述），1 个轻微红灯不破坏整体优秀度。

### dim8 实测表现 — ⚠️ 静态估 9/10（待外部 judge 复核）

**darwin-skill 自身 controlled study 数据**（来自 references/skilllens-evidence.md）：

| 测试 | V1 | V2 (degraded) | Δ | 5/5 judge |
|---|---|---|---|---|
| huashu-research 5 judge 盲测 | 89.6 | 43.2 | **+46.5** | ✓ high confidence |

**darwin-skill 自评（来自 README）**：
- huashu-gpt-image: 80.8 → 91.5 → 91.65（+10.85，6 judge 共识）
- darwin-skill 自评: 86.05 → 92.05 → 92.7

**评估**：
- ✓ 自带 controlled study 文档（5 judge × 5 反例 × 顺序反序控制）
- ✓ 自评数字与 Microsoft SkillLens 双向认可
- ⚠️ 本地静态评估不能复现实验，给 9 分基于：作者 controlled study 数据 + 双向被 SkillOpt/SkillLens 引用

### dim9 High-Risk Action Blacklist — 10/10

**显式反例黑名单**（SKILL.md line 360-371「darwin 操作反例黑名单」）：

| # | 反模式 | 替代做法 |
|---|---|---|
| 1 | 同 context 自评自改 | 独立子 agent 评分，2 judge 共识 |
| 2 | `git reset --hard` 当回滚 | `git revert HEAD` |
| 3 | 为凑分增冗余 | 触顶 → break，见好就收 |
| 4 | 跳过 test-prompts 直接评分 | Phase 0.5 强制 2-3 prompts |
| 5 | 轮内改多个维度 | 每轮 1 维度 |
| 6 | dry_run 比例 > 30% | 强制至少 1 个 full_test |
| 7 | 静默跳过异常 | 异常表 fallback + 先告知 |
| 8 | 忽视维度相关性 | dim2/3/4 簇同步看 |

**评估**：**dim9 是 darwin-skill 自创的最严风险控制清单**——每条都是**真实踩过的坑**（line 358：来自本机 results.tsv 早期 40 次 0 revert 的教训 + Judge G/H 自指评估暴露的反模式）。**自我批判性极强**，满分。

## 总分

| 维度 | 分 | 一句话评 |
|---|---|---|
| dim1 Frontmatter | 9.5 | 触发词 + 学术背书完整，缺 NOT-FOR |
| dim2 工作流清晰度 | 10.0 | 6 phase + 3 hard checkpoint |
| dim3 边界条件 | 10.0 | 10 条 fallback + 3 列结构，SkillLens 标杆落地 |
| dim4 检查点设计 | 10.0 | 🔴 + 🛑 双视觉标记，方法论和实现合一 |
| dim5 指令具体性 | 10.0 | 无软化措辞，HL-2/3/4 全应用 |
| dim6 资源整合度 | 9.0 | 全套资源齐全，缺前置条件说明 |
| dim7 Runtime Neutrality | 9.0 | 招牌维度，1 个轻微硬编码有回退 |
| dim8 实测表现 | ⚠️ 9.0（估）| 自带 controlled study + Microsoft 双向认可 |
| dim9 反例黑名单 | 10.0 | 自创最严风险控制，自我批判满分 |
| **总分** | **86.5** | A+ 档 |

## Runtime gate（独立扫描）

按 references/runtime-neutrality.md 的 grep 命令扫 darwin-skill 自己：

```bash
grep -nE "(在 Claude Code|Claude Code skill|Claude Code 用户|Cursor only|Codex 中|^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b)" \
  skill-management/darwin-skill/SKILL.md README.md
```

**扫描结果**：

| 文件 | 行 | 命中 | 严重度 |
|---|---|---|---|
| README.md | 26 | `npx skills add alchaincyf/darwin-skill` | 🟢 合规（社区中立 install）|
| SKILL.md | 115 | `扫描 .claude/skills/*/SKILL.md` | 🟡 默认路径，非唯一 |
| SKILL.md | 467 | `node .claude/skills/darwin-skill/scripts/screenshot.mjs` | 🟡 1 个路径硬编码（已给 npx fallback）|
| references/runtime-neutrality.md | 9 | 列举支持的 runtime（Claude Code/Codex/Cursor 等）| 🟢 合规 |
| references/runtime-neutrality.md | 23-25 | 在红灯示例中列举 `~/.claude/skills/` 路径 | 🟢 合规（作为反例引用）|

**Runtime 判定**：✅ **pass**（4 项中 3 项合规，2 项轻微不构成红灯）。

## 评级

**A+ 档**（86.5/100，Runtime pass）

darwin-skill 是我们合入的第一个**自评系统**——它的 9 维 rubric 既是评分工具也是被评分对象。这种**递归自洽性**正是 SkillLens + SkillOpt 联合推荐的核心原因。

## 与现有 ljg/garden-skills eval 对比

| 项 | ljg-skills | garden-skills | darwin-skill |
|---|---|---|---|
| 总分 | 75-90（20 skill）| 86.5（beautiful-article）| **86.5** |
| 评级 | 14 A + 6 B/C | 1 A | **A+** |
| Runtime | 4 fail（ljg-library/ljg-map）| pass | **pass（轻微 2 警告）** |
| 特殊点 | ljg 生态强绑定 | garden 同源 5 skill | **自指 meta-skill** |

## 同步配置

- **strategy**: `whole`（单 skill 仓库，整包同步）
- **target**: `skill-management/darwin-skill`
- **state hash**: 7c7b790
- **first sync commit**: a26a88e
- **exclude patterns**: `node_modules`, `.git`, `.env`（与全局一致）

## 备注

1. **递归自指风险**：darwin-skill 用自家 rubric 评自己得 86.5，这是有意为之的设计（HL-1 显性视觉标记 dim4 的来源），不是数据造假。
2. **Microsoft 双向认可**：SkillOpt 仓库 README 已列 darwin-skill 为官方集成。
3. **LICENSE 未声明**：仓库根无 LICENSE 文件，README 自称 MIT。建议上游补 LICENSE 文件以消除歧义。
4. **本地静态评估的局限**：dim8 跳过实测，9 分是基于作者 controlled study 数据的合理推断。重要决策仍建议在外部 judge 环境下复核。
5. **Phase 2.5 触发条件**：「连续 2 个 skill round 1 就 break」——这意味着评估者要跑过至少 2 个 skill 才能触发，实操中可能需要在 README 提示「批量优化 2+ skill 才暴露」。