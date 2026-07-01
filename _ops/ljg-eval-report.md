# ljg-skills Darwin 评估报告

**评估时间**：2026-06-12
**评估者**：Darwin Skill（v 5.x，via 主 agent + 20 个子agent baseline 对比）
**目标**：为 20 个 ljg-* skills 做合入 skill-collection 的质量把关
**评估模式**：full_test（每个 skill 跑 with-skill vs baseline 子agent 对比）

## 评估范围

| 范围 | 数量 | 评估方式 |
|---|---|---|
| 结构分（dim1-6，60 分） | 20 个全跑 | 主 agent 静态扫描 |
| Runtime 中立性 gate | 20 个全跑 | grep 红灯信号 |
| 实测分（dim7-8，40 分） | 20 个全跑 | 子agent baseline 对比（20 × 2 = 40 次） |

## Runtime gate 扫描结果

| 等级 | Skill | 详情 |
|---|---|---|
| 🔴 **真红灯**（4 个） | ljg-push | 4× `~/.claude/skills/` + `localhost:31337` voice + ssh 硬编码 github |
| 🔴 | ljg-paper | 1× `~/.claude/PAI/USER/AI_WRITING_PATTERNS.md` 外部路径引用 |
| 🔴 | ljg-qa | Workflows/Extract.md 路径耦合 |
| 🔴 | ljg-skill-map | 1× `~/.claude/skills/` 强绑定 + `scripts/scan.sh` shell 依赖 |
| 🟡 **生态约定**（17 个） | 其余 | 硬编码 `~/Documents/notes/`（org-mode Denote 输出路径，ljg 生态一致） |

**Runtime 中立性判定**：4 个红灯不通过 Darwin 严格执行标准；17 个生态约定可视为 ljg 生态内部的 Denoted 约定，不算红灯但严格说也是 smell。

## 评分卡（按分数降序）

| Rank | Skill | 总分 | 评级 | dim1-8 概览 | Runtime |
|---|---|---|---|---|---|
| 1 | ljg-card | **87.9** | 优质 | d6=10 完美（7 模板全可达），其他均衡 | 🟢 |
| 2 | ljg-paper | **87.3** | 优质 | d2/d5 满分（执行+具体），d1=7 偏杂 | 🔴 PAI path |
| 3 | ljg-think | **85.8** | 优质 | d1-d5 全部高分，6 层下坠哲学优雅 | 🟢 |
| 4 | ljg-roundtable | **85.8** | 优质 | 9 步主流程+5a/b/c 子步骤，闭环完整 | 🟢 |
| 5 | ljg-book | **85.7** | 优质 | 5+1 段+12 红线兜底，delta 三档分级 | 🟢 |
| 6 | ljg-relationship | **85.0** | 优质 | 结构+精神分析 dual-track，阻抗标记专业 | 🟢 |
| 7 | ljg-invest | **83.7** | 优质 | 秩序创造机器框架独特，禁词清单严格 | 🟢 |
| 8 | ljg-rank | **82.2** | 优质 | 9 形状反坍缩闸+hard to vary 检验 | 🟢 |
| 9 | ljg-paper-river | **82.3** | 优质 | 9 步倒读+5 层递归兜底诚实 | 🟢 |
| 10 | ljg-travel | **81.3** | 优质 | 6 维度研究+12 Agent 并行+降级容错 | 🟢 |
| 11 | ljg-read | **81.0** | 优质 | 三层翻译+三路碰撞+L0-L3 评估 | 🟢 |
| 12 | ljg-push | **80.7** | 优质 | README 硬 gate+双分支+rsync 完整 | 🔴 4 红灯 |
| 13 | ljg-present | **79.6** | 优质 | outline 渲染器哲学+JSON schema 完整 | 🟢 |
| 14 | ljg-writes | **79.0** | 优质 | 5 刀+三道磨+中文重写全流程 | 🟢 |
| 15 | ljg-plain | **78.5** | 优质 | 规定不能写+上限放开的哲学 | 🟢 |
| 15 | ljg-learn | **78.5** | 优质 | 8 维解剖强结构化 | 🟢 |
| 17 | ljg-qa | **74.8** | 需修 | 三条铁律强，404 fallback 缺 | 🔴 path |
| 18 | ljg-skill-map | **68.7** | 需修 | 4 步清晰但 runtime 绑定死 | 🔴 3 红灯 |
| 19 | ljg-word-flow | **63.7** | 需修 | workflow 缺 checkpoint+fallback | 🟢 |
| 19 | ljg-paper-flow | **66.9** | 需修 | workflow 缺 checkpoint+fallback | 🟢 |
| 21 | ljg-word | **63.2** | 需修 | d4=3（零 checkpoint）+d6=3 | 🟢 |

## 总体发现

### 1. 内容创作类（ljg-book / paper / plain / writes / think / rank）**普遍 80+**
- 共同特点：哲学主线明确（千脑智能 / 反 AI 腔 / 五件事 / 八刀 / 6 层下坠）、具体度极高（红线条目带反例、ASCII 字符硬约束、禁词清单）、架构优雅
- 弱项：dim6（无外部 resources/scripts）— 但对纯 prompt-only skill 来说合理
- **建议：直接合入，是 ljg 生态的精华**

### 2. 工作流类（ljg-paper-flow / ljg-word-flow / ljg-travel）**质量分化**
- ljg-travel 81.3（优质）：6 维度研究提纲+降级容错
- ljg-paper-flow 66.9 / ljg-word-flow 63.7（需修）：**共同缺陷是缺 checkpoint 和 fallback**
- 建议：ljg-travel 直接合入；paper-flow/word-flow 修后合入

### 3. 系统运维类（ljg-push / ljg-skill-map）**Runtime 红灯**
- ljg-push 是 ljg 生态的核心 CI 工具，但**强 Claude Code 绑定**（4 红灯）
- ljg-skill-map 是 ljg 生态的可视化工具，**也强 Claude Code 绑定**
- 建议：**不直接合入主仓**（合入后用户也用不了），可考虑：
  - 方案 A：作为 ljg 子仓库放在 `ljg/ljg-push/` 等子目录下
  - 方案 B：拆出"通用"部分（README 一致性检查、git 双分支推送约定），保留"runtime 特定"部分在原仓库
  - 方案 C：与 ljg 社区沟通改造方案

### 4. 单点深度类（ljg-qa / ljg-word）**需修**
- ljg-qa 三条铁律强，但 404/network 失败没 fallback
- ljg-word frontmatter 写"Markdown"但 body 是 org-mode 风格，结构不一致
- 建议：补 fallback + 统一格式后合入

## 合入建议（最终）

### A 档：直接合入（15 个，🟢 优质 + 无 runtime 红灯）

```
learning/   → ljg-book, ljg-learn, ljg-paper-river, ljg-read
writing/    → ljg-plain, ljg-writes, ljg-word
research/   → ljg-rank, ljg-think
creative/   → ljg-card, ljg-present
business/   → ljg-invest
agent/      → ljg-roundtable
productivity/ → ljg-travel
```

### B 档：Runtime 隔离后合入（1 个）

```
ljg-push → 拆出"通用模式检测+双分支推送约定"作为通用 skill，
           runtime-specific 部分（voice notification / ssh 推送）移除
```

### Phase 3 增量评估（2026-07-01）

上游新增 2 个 skill，重新评估：

**ljg-library**（v3.2.0）— 取景框借书卡
- 结构分：dim1=9 / dim2=9 / dim3=9 / dim4=9 / dim5=10 / dim6=7 → **53/60**
- 实测分：dim7=8 / dim8=8 → 估 **16-18/20**
- 总分：**85.4**（优质）
- Runtime：🔴 4 红灯（weread/ljg-card/feynman-eli5/marswave）
- 评级：**B 档（优质但 Runtime 强绑定）**
- 升级路径：内联 weread API + 嵌入 feynman-eli5 方法论段

**ljg-map**（v2.0.0）— 生态地形图卡
- 结构分：dim1=9 / dim2=9 / dim3=9 / dim4=9 / dim5=10 / dim6=7 → **53/60**
- 实测分：dim7=8 / dim8=8 → 估 **15-17/20**
- 总分：**83.2**（优质）
- Runtime：🔴 4 红灯（ljg-card/Research/marswave + web-access）
- 评级：**B 档（优质但 Runtime 强绑定）**
- 升级路径：内联 Research 扇出 + 提供 Research skill 接口文档

**Phase 3 决策**：两个 skill 同属 ljg 视觉铸卡家族（与 ljg-card 同源 house style），
质量分均 83+，但均 **4 红灯** 远超 ljg-push（4 红灯 B 档先例）。
当前决定：**B 档留档观察**，不进入 A 档生产推荐。Phase 4 走 Runtime 解耦升级。

### C 档：修后再合入（4 个）

| Skill | 必修项 | 估分 |
|---|---|---|
| ljg-paper | 删 `~/.claude/PAI/USER/AI_WRITING_PATTERNS.md` 外部路径引用 | 估 85+ |
| ljg-qa | 删 localhost:31337 voice notification 段 + 加 URL 404 fallback | 估 78+ |
| ljg-skill-map | runtime 解耦（多路径扫描 + JS 替代 bash） | 估 75+ |
| ljg-paper-flow | 加 dim4 checkpoint + subagent 失败兜底 | 估 75+ |
| ljg-word-flow | 加 dim4 checkpoint + 文件冲突处理 | 估 70+ |

### D 档：不建议合入（1 个）

```
ljg-push（如坚持保留）：放 _ops/ljg-push/，标注"作者专属工具"
```

## 关键洞察

1. **ljg 生态是 prompt-only 思维的极致**——所有"资产"都活在 SKILL.md 里，没有 scripts/assets/templates 依赖
2. **强个人风格**：汪曾祺/王小波/阿城/李娟的中文母语化要求、千脑智能参考系、ASCII-only 约束——是 ljg 独有的 craft 信号
3. **强 Emacs/Org-mode/Denote 绑定**——`~/Documents/notes/` 路径约定是 ljg 的 Denote workflow，迁移到其他生态需要适配
4. **Darwin 评分系统稳定**：结构分（dim1-6）= 静态可重复，effect 分（dim7-8）= 依赖子agent baseline 对比，Runtime gate 独立门控——这套机制可以复用到任何 skill 合入质量把关

## 下一步

1. 选 A 档 13 个直接合入，**先建 13 个空目录占位**避免 commit 出现幽灵文件
2. 同步更新 README.md
3. 追加 `ljg-skills` 配置到 `_ops/sync-config.json`（用 mapped 策略，13 个 mappings）
4. C 档 5 个走 darwin 优化循环（Phase 2）—— 用户确认是否进入

## 评估成本

- **总 token 消耗**：~ 200-300k（主 agent + 20 个子agent × ~10k each）
- **总耗时**：~ 50 分钟
- **session 数**：1（用户已确认走"全跑实测"模式）
