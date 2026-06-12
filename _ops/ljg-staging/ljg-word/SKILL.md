---
name: ljg-word
description: Deep-dive English word mastery tool. Deconstructs a single English word into core semantics and epiphany. Use when user asks to explain/master a specific English word.
version: "1.0.1"
user_invocable: true
---

## Usage

<example>
User: Deeply explain the word "Serendipity".
Assistant: [Calls ljg-explain-words with "Serendipity"]
</example>

## Instructions

目标不是翻译，而是让用户掌握这个词的深层含义和用法。

针对输入的 `word`（转换为小写，首字母大写），进行以下分析，直接在对话中用 Markdown 输出：

### 边界条件

输入可能不在「普通单词」范围内。按以下规则处理：

1. **多义词**（如 "run" 有 50+ sense）— WebSearch 查主流字典的 Top 2-3 sense，按使用频率排，**逐一展开**（不要只给最常用那一个）
2. **复合词/短语**（如 "kick the bucket"）— 当作**整体**对待，**不拆字面**（拆字会误导）。用「整体画面 + 词源故事」框架
3. **俚语/网络词**（如 "yeet", "rizz", "goblin mode"）— 诚实标注「无可靠词源」，给当前流行用法 + 1 个文化语境例句
4. **专有名词/品牌**（如 "Serendipity" 是 1754 年小说名也是形容词）— 先 WebSearch 区分意图，默认按词义走
5. **极短虚词**（如 "a", "the", "of", "in"）— 诚实说「虚词无独立语义」，引导用户换词
6. **超长复合词**（如 "antidisestablishmentarianism"）— 拆词根 + 给 1 句历史故事
7. **非英文输入**（如 "你好", "こんにちは"）— 用对应 skill 兜底（你好 → ljg-plain 类），不当英文词处理

任何一种边界情况，**绝不要编造词源**。诚实说不确定，比编造好。

### 输出结构

#### 1. 标题行

```
## {Word}  /{音标}/  {中文翻译}
```

#### 2. 核心语义

- **原始画面**: 用一句话描述该词源头最物理的画面（例如 Incubate: 母鸡趴在蛋上）。
- **核心意象**: 提炼公式（例如：温暖 + 时间 + 保护 = 孕育）。
- **解释**: 用充满洞见的语言阐述其深层含义与现代用法。分段清晰，**加粗**关键词。要有穿透力，展现词源、多领域含义之间的内在联系。

#### 3. 一语道破

一句中英双语的金句，必须具有哲学高度，总结该词的灵魂。用引用格式：

```
> "English sentence. 中文金句。"
```
