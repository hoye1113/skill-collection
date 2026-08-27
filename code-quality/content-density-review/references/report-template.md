# Report Template

Follow this structure when writing the Markdown report file. Section headers can be translated/adapted to the user's language (mirror whatever language the user is using), but keep the structure.

```markdown
# 内容密度审查报告：<项目/页面名>

**审查范围**：<列出审查的文件/页面>
**目标用户/使用频率**：<一句话说明这是内部重复使用工具还是消费者首次使用场景，据此决定审查阈值的严格程度>
**审查日期**：<date>

## 总体结论

<2-4 句话，直接说明整体严重程度和最突出的问题模式。别客套，直接下判断。>

**审查对象画像**：<首次/偶发用户 或 训练有素的重复/内部用户，及判断依据；这决定了下面"显而易见"的判断尺度>

**预估精简空间**：<给一个粗略但具体的量化锚点，例如"核心路径首屏文字量预计可减少 40%-50%"或"关键屏幕的独立文本块数量可从 X 个降到 Y 个"。用于用户改完之后复验是否改够，不要求精确，给数量级即可。>

## 问题清单（按优先级排序）

### P0 — 与核心信息/操作抢注意力

#### 1. <简短问题标题>
- **位置**：`<file path>:<line number(s)>` （或组件名）
- **现状**：<引用/复述当前文案，简短>
- **问题类型**：<redundancy pattern 名称，如 Triple-statement / CTA padding 等>
- **危害**：<具体说明这段文字/元素抢走了什么注意力，或掩盖了什么关键信息>
- **建议**：<具体的删除/精简/降权方案 — 给出建议后的文案或处理方式，不要只说"精简一下">

#### 2. ...

### P1 — 重复/多次表达同一信息

(同上结构)

### P2 — 低价值标注/标签

(同上结构)

### P3 — 填充性/过渡性文字

(同上结构)

## 保留清单（这些文字是合理的，不建议删）

- `<file:line>` — <文字内容简述> — <为什么该保留，比如"错误提示，具体且可操作">
- ...

## 系统性观察

<如果多个问题在项目中反复出现（比如"每个卡片组件都有冗余 caption"），在这里指出根因/模式，并给出一条可以写进组件规范或设计系统的通用规则，而不是逐个修。>

## 修改优先级建议

<给用户一个简短的行动顺序：先改哪几处收益最大，哪些可以批量处理（如统一删除某类 caption），哪些可以留到之后。>
```

## Formatting rules

- Every finding needs a **location** — no vague "the page" references. If line numbers aren't stable (e.g. templated/dynamic strings), reference the component/variable name instead.
- Keep the "现状" quote short — enough to identify it, not a wall of pasted code.
- The "建议" (recommendation) must be actionable and specific — either the exact replacement text, or a concrete structural instruction ("移除这行，保留卡片本身的数字即可" / "移到 tooltip，默认不显示").
- Don't pad the report with generic UX theory — every paragraph should trace back to something concrete in the reviewed files.
- If a finding pattern repeats 5+ times across the page/project, don't list all 5+ instances individually at full length — group them ("以下 6 处 stat card 均存在相同的 Triple-statement 问题：`a.tsx:12`, `b.tsx:8`, ...") and give one shared recommendation.
