# ljg-skills

> 李继刚 (lijigang) 个人 Claude Code 技能集合 — 涵盖内容创作 / 投资分析 / 关系分析 / 旅行研究 等多领域

**合入来源**：https://github.com/lijigang/ljg-skills
**合入时间**：2026-06-12
**合入评分**：通过 Darwin 8 维度评分 + Runtime 中立性 gate

## 收录情况

**14 个 skills**（A 档 — 优质 + 无 Runtime 红灯）

| Skill | Darwin 分 | 用途 | 依赖 |
|---|---|---|---|
| [ljg-book](skills/ljg-book/) | **85.7** | 拆书 — 5 件事 + 认知地图 + 走两步 | 纯 prompt |
| [ljg-card](skills/ljg-card/) | **87.9** | 铸 — 内容转 PNG 视觉卡（7 模具） | Playwright（需 npm install） |
| [ljg-invest](skills/ljg-invest/) | **83.7** | 投资分析 — 秩序创造机器判定 + 创生公式 | 纯 prompt |
| [ljg-learn](skills/ljg-learn/) | **78.5** | 概念解剖 — 8 维切开 + 压缩 | 纯 prompt |
| [ljg-paper](skills/ljg-paper/) | **90.1** | 论文正读 — 7 拍故事弧（主角/困境/旧路/转折/解法/结局/内核）| 纯 prompt |
| [ljg-paper-river](skills/ljg-paper-river/) | **82.3** | 论文倒读法 — 5 层递归溯源 + 演化线 | 纯 prompt |
| [ljg-plain](skills/ljg-plain/) | **78.5** | 白话 — 12 岁孩子能 grok | 纯 prompt |
| [ljg-present](skills/ljg-present/) | **79.6** | 演讲铸造器 — org → slogan-style HTML | 纯 prompt |
| [ljg-qa](skills/ljg-qa/) | **75.3** | 问答抽取 — 三条铁律（Q 切要害 / A 形式化 / Q 链方向）| 纯 prompt |
| [ljg-rank](skills/ljg-rank/) | **82.2** | 降秩 — 找出领域不可再分生成器 | 纯 prompt |
| [ljg-read](skills/ljg-read/) | **81.0** | 伴读 — 三层翻译 + 三路碰撞 + L0-L3 评估 | 纯 prompt |
| [ljg-relationship](skills/ljg-relationship/) | **85.0** | 关系分析 — 五层结构 + 精神分析 dual-track | 纯 prompt |
| [ljg-roundtable](skills/ljg-roundtable/) | **85.8** | 圆桌讨论 — 张力网络选人 + ASCII 框架图 | 纯 prompt |
| [ljg-think](skills/ljg-think/) | **85.8** | 追本之箭 — 纵向深钻到不可再分 | 纯 prompt |
| [ljg-travel](skills/ljg-travel/) | **81.3** | 旅行研究 — 6 维度研究 + org 文档 + 双卡 | Research + ljg-card |
| [ljg-writes](skills/ljg-writes/) | **79.0** | 写作引擎 — 5 刀 + 三道磨 + 中文重写 | 纯 prompt |
| [ljg-word](skills/ljg-word/) | **74.7** | 英文单词深度拆解 — 7 类边界条件（多义词/复合词/俚语/专有名词/虚词/超长词/非英文）| 纯 prompt |

**未收录**（共 6 个 — B/C/D 档，待修或 Runtime 强绑定）

| Skill | Darwin 分 | 评级 | 原因 |
|---|---|---|---|
| ljg-push | 80.7 | 优质但 Runtime 🔴 | 4× `~/.claude/skills/` + localhost:31337 + ssh 硬编码 — 作者专属 CI 工具 |
| ljg-paper | 87.3 → **90.1** | 已合入（Phase 2 r1）| 引用 `~/.claude/PAI/USER/AI_WRITING_PATTERNS.md` 外部路径 → 删 + 内联反翻译腔自检表 |
| ljg-qa | 74.8 → **75.3** | 已合入（Phase 2 r2）| 删 voice notification 段（localhost:31337 curl 块），Runtime gate fail→pass；404 fallback 留待 R3+ |
| ljg-word | 63.2 → **74.7** | 已合入（Phase 2 r3）| 补 7 类边界条件（多义词/复合词/俚语/专有名词/虚词/超长词/非英文）；dim4 self-check 仍待 R4+ |
| ljg-skill-map | 68.7 | 需修 + Runtime 🔴 | 强 `~/.claude/skills/` 绑定 + bash 脚本依赖 |
| ljg-word-flow | 63.7 | 需修 | workflow 缺 checkpoint 和 fallback |
| ljg-paper-flow | 66.9 | 需修 | workflow 缺 checkpoint 和 fallback |

## 生态特性

1. **prompt-only 思维** — 多数 skill 无 scripts/assets 依赖，"资产"全在 SKILL.md 里
2. **强中文母语化要求** — 汪曾祺/王小波/阿城/李娟的笔调，反 AI 腔
3. **org-mode + Denote 约定** — 输出到 `~/Documents/notes/{timestamp}--{title}__{type}.org`
4. **ASCII-only 图表** — 禁 Unicode 绘图字符
5. **强个人风格** — 千脑智能参考系、五件事 / 八刀 / 6 层下坠等独家框架

## 评估依据

完整 Darwin 8 维度评分卡见 [`../../_ops/ljg-eval-report.md`](../../_ops/ljg-eval-report.md)
- 评估时间：2026-06-12
- 评估方法：20 个 skill × 子agent baseline 对比（full_test 模式）
- Runtime gate 严格执行 Darwin 标准

## 使用方式

每个 skill 是自包含目录，含 `SKILL.md`（含 YAML frontmatter + 完整执行指令）。

安装到本地 Claude Code：

```bash
# 复制单个 skill 到 ~/.claude/skills/
cp -r skills/ljg-book ~/.claude/skills/

# 或复制全部 14 个
cp -r skills/ljg-* ~/.claude/skills/
```

注意：**ljg-card 需额外装依赖**：

```bash
cd ~/.claude/skills/ljg-card && npm install && npx playwright install chromium
```

## 同步与更新

本集合通过 `_ops/sync-config.json` 同步上游 lijigang/ljg-skills：

```json
{
  "name": "ljg-skills",
  "remoteUrl": "https://github.com/lijigang/ljg-skills.git",
  "strategy": "mapped",
  "mappings": [
    { "source": "skills/ljg-book", "target": "dev-workflow/ljg-skills/skills/ljg-book" },
    ...14 mappings
  ]
}
```

跑 sync 脚本即可拉取上游更新（仅 A 档 14 个，B/C/D 档被映射过滤）。

## 设计哲学摘录（来自各 skill）

- **ljg-book**：一本书的价值不在它说了什么，在它挪动了什么
- **ljg-paper**：把论文讲成有钩子的故事，不是九段独立汇报
- **ljg-think**：表象之下必有机理，机理之下必有原理，原理之下必有公理
- **ljg-rank**：秩是动一根就塌的好解释，不是关键要素清单
- **ljg-writes**：外科医生的手，朋友的口

详细哲学见各 skill 的 SKILL.md。
