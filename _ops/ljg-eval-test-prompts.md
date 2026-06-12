# ljg-skills 评估 · 测试 Prompt 集

按 Darwin 8 维度评分，为每个 skill 设计 1-2 个**最常见 happy path** prompt（不设计边缘 case）。
评估目标：判断 ljg-skills 20 个是否值得合入 skill-collection。

## 设计原则
- happy path：用户最常说的那句话
- 不设计对抗 prompt：只看基线质量
- 每个 prompt 都可在无外部依赖下独立测试（除非 skill 本身强依赖网络）

---

## 1. ljg-book · 拆书

**Prompt 1（典型）**：拆《思考，快与慢》

**预期**：5 件事（问题/零点/位移/落点/行囊）+ ASCII 参考系图 + 走两步预测

---

## 2. ljg-card · 铸卡

**Prompt 1（典型）**：铸：今天读了《思考，快与慢》，核心是 System 1/2 双系统

**预期**：调用 Playwright 生成 1080×auto PNG，输出到 ~/Downloads/

---

## 3. ljg-invest · 投资分析

**Prompt 1（典型）**：投资分析：Anthropic

**预期**：5 个区块（这是什么 / 秩序创造机器 / 创生公式 / 市场看见 vs 我们看见 / 换不换）

---

## 4. ljg-learn · 概念解剖

**Prompt 1（典型）**：/ljg-learn 熵

**预期**：8 刀（历史/辩证/现象/语言/形式/存在/美感/元反思）+ 内观 + 压缩（公式/一句话/结构图）

---

## 5. ljg-paper · 论文阅读

**Prompt 1（典型）**：把这篇论文讲给我听：https://arxiv.org/abs/2410.18982

**预期**：7 拍故事（主角/困境/旧路/转折/解法/结局/内核）+ org 模式输出

---

## 6. ljg-paper-flow · 论文流

**Prompt 1（典型）**：论文流 https://arxiv.org/abs/2410.18982

**预期**：调用 ljg-paper 生成 org → 调用 ljg-card -v 生成视觉笔记 PNG

---

## 7. ljg-paper-river · 论文倒读

**Prompt 1（典型）**：倒读：https://arxiv.org/abs/1706.03762

**预期**：递归 5 层挖前序 + 1-3 篇后续 + 演化线 + 溯源地图 + 费曼叙事

---

## 8. ljg-plain · 白话

**Prompt 1（典型）**：白话说：什么是 transformer

**预期**：一篇连贯 org 文件，12 岁小孩能复述，零学术腔

---

## 9. ljg-present · 演讲铸造

**Prompt 1（典型）**：present 一下：把 org 文件 `~/Documents/notes/foo.org` 铸成演讲

**预期**：单文件 HTML，黑/红/黄/cyber 主题之一，可浏览器翻页

---

## 10. ljg-push · 推送 skills

**Prompt 1（典型）**：/ljg-push

**预期**：检测 ~/.claude/skills/ljg-* 差异 → 推 master → 推 md → 报告

**Runtime gate 影响**：🔴 真红灯（强 Claude Code 绑定）

---

## 11. ljg-qa · 问答提取

**Prompt 1（典型）**：/ljg-qa https://example.com/article

**预期**：Q-A 链（每 Q 切要害，每 A 四段：结论/形式化/步骤/边界）

**Runtime gate 影响**：🟡 引用外部路径

---

## 12. ljg-rank · 降秩

**Prompt 1（典型）**：降秩：创业

**预期**：root rank + 可选坐标系 + ASCII 结构图（按 rank 形状选九种之一）

---

## 13. ljg-read · 伴读

**Prompt 1（典型）**：陪我读：https://example.com/essay

**预期**：Phase 0 全局地图 → Phase 1 三层翻译 → Phase 2 骨架段深读 → Phase 4 复盘

---

## 14. ljg-relationship · 关系分析

**Prompt 1（典型）**：/ljg-relationship 我跟老板最近总是吵架

**预期**：对话流 + 五层结构诊断图 + 核心洞察

---

## 15. ljg-roundtable · 圆桌

**Prompt 1（典型）**：圆桌讨论：AI 是否拥有真正的创造力？

**预期**：3-5 位真实人物 + 主持人 + 多轮动态发言 + ASCII 框架图 + 知识网络

---

## 16. ljg-skill-map · 技能地图

**Prompt 1（典型）**：技能地图

**预期**：扫描 ~/.claude/skills/ → 5 类分组 → ASCII 方框图

**Runtime gate 影响**：🟡 强 ~/.claude/skills/ 路径绑定

---

## 17. ljg-think · 追本之箭

**Prompt 1（典型）**：追本：为什么人会拖延

**预期**：下坠式叙事，3-7 层，每层命名，层间有裂缝，终点要狠

---

## 18. ljg-travel · 旅行研究

**Prompt 1（典型）**：旅行研究：西安

**预期**：org 文档（历史/博物馆/古建/考古/人文/路线）+ 2 张卡片（信息图+长图）

---

## 19. ljg-word · 单词精通

**Prompt 1（典型）**：Deeply explain "Serendipity"

**预期**：标题行 + 核心语义（原始画面/核心意象/解释）+ 一语道破

---

## 20. ljg-writes · 写作引擎

**Prompt 1（典型）**：写：为什么现代人越来越难专注

**预期**：1000-1500 字，层层推进，反 AI 痕迹，三道磨

---

## 评估维度（Darwin 8 维）

| 维度 | 权重 | 评分标准 | 评估方式 |
|---|---|---|---|
| 1. Frontmatter 质量 | 8 | name/description 触发词齐全，≤1024 字符 | 静态 |
| 2. 工作流清晰度 | 15 | 步骤可执行，有输入/输出 | 静态 |
| 3. 边界条件覆盖 | 10 | 异常处理、fallback | 静态 |
| 4. 检查点设计 | 7 | 关键决策有用户确认 | 静态 |
| 5. 指令具体性 | 15 | 参数/格式/示例明确 | 静态 |
| 6. 资源整合度 | 5 | references/scripts 引用正确 | 静态 |
| 7. 整体架构 | 15 | 层次清晰，不冗余，与生态一致 | 实测 |
| 8. 实测表现 | 25 | 带 skill vs 不带 skill 输出对比 | 实测（子agent baseline） |

**Runtime gate**：4 个真红灯，0 个通过严格执行。

---

## 测试 prompt 集待审

请你：
1. 审这 20 个 prompt 是否切中"最常见 happy path"
2. 决定：20 个全跑实测 vs 选一个子集
3. 提醒：每个实测 = 2 次子agent（with skill + baseline），成本不低
