# 概念解释 Skill 地图

把抽象概念讲清楚的一站式工作流——用寓言做钩子，让读者自己撞上概念。

适用场景：
- 培训课件、内部学习材料
- 公众号「讲清楚一个概念」专题
- 团队分享、技术布道
- 投资人沟通中解释某个机制（如沉没成本、网络效应）
- 自我学习：让抽象概念变成可叙述的具体场景

## 阶段 1：概念定位

先把概念本身搞清楚——定义、典型应用、常见误解。

- [research/market-research](../research/market-research/) — 如果概念属于商业 / 经济学（沉没成本 / 网络效应 / 长尾等），用市场研究框架定位
- [business/value-invest-scorer](../business/value-invest-scorer/) — 如果概念属于投资领域（贝塔系数 / 折现率 / 护城河）
- [research/jtbd-analyzer](../research/jtbd-analyzer/) — 如果概念属于用户行为（Jobs-To-Be-Done / 期望理论）

> **关键**：概念定位不是「找到定义」，而是「找到这个概念**最容易讲错的点**」和「最能让读者撞上的具体场景」。这两个直接决定寓言的切入角度。

## 阶段 2：寓言创作（核心）

**主流程**：用 concept-fable 写一则 ≤1000 字的寓言，让读者合上后恍然。

- [**concept-fable**](../writing/concept-fable/) — 寓言写作主入口
  - 选切入角度（30+ 候选，见 `references/angles.md`）
  - 走 5 类黑名单自检（见 `references/blacklist.md`）
  - 3 段式输出：寓言正文 + 概念解析 + 2 个检验问题

### 触发示例

| 概念类型 | 推荐角度 | 输出形态 |
|---|---|---|
| 经济学 / 心理学 | 具体现代职业（理赔员 / 二手车中介 / 健身房会员）| 单则寓言 + 解析 |
| 跨学科抽象概念 | 非人类视角（工具 / 动物 / 机构）| 单则寓言 + 解析 |
| 系列概念（如「行为经济学 12 讲」）| 每个概念独立寓言 | 12 则寓言合集 |

## 阶段 3：可选增强

把寓言嵌入更长的内容形态：

### 转成长文 / 公众号文章
- [writing/khazix-writer](../writing/khazix-writer/) — 把寓言作为开篇钩子，写成有故事的公众号长文
- [writing/general-writing](../writing/general-writing/) — 把寓言嵌入 essay / 解释文等更长篇体裁

### 转成可视化文章 / 讲义
- [writing/beautiful-article](../writing/beautiful-article/) — 用 React + 主题 profile 把寓言排成可分享的单文件 HTML 文章
- [creative/gpt-image-2](../creative/gpt-image-2/) — 生成配图（封面 / 概念图解 / 场景插画）

### 转成 PDF 交付
- [productivity/pdf](../productivity/pdf/) — 导出 PDF（适合培训资料 / 客户沟通材料）

### 转成讲解视频
- [creative/web-video-presentation](../creative/web-video-presentation/) — 把寓言 + 解析作为视频脚本的章节结构（19:9 录屏演示）

## 阶段 4：质量校验

寓言写完后：

- [code-quality/humanizer-zh](../code-quality/humanizer-zh/) — 检查概念解析段是否「中文 AI 味」过重
- [code-quality/ai-humanizer](../code-quality/ai-humanizer/) — 检查英文表述（如有）是否「AI 味」

## 工作流示例

### 示例 A：解释「沉没成本」给团队

```
1. [research/market-research] — 找到沉没成本的经典应用场景（健身房会员、二手车买卖）
2. [concept-fable] — 写寓言：饺子馆储值卡会员（references/examples.md 示例 1）
3. [writing/khazix-writer] — 把寓言作为开篇，写成 2000 字团队内部分享
4. [writing/beautiful-article] — 排成可分享的单文件 HTML
```

### 示例 B：投资人沟通中讲「幸存者偏差」

```
1. [research/jtbd-analyzer] 或 [research/market-research] — 概念定位
2. [concept-fable] — 写寓言：博物馆展览策展人（references/examples.md 示例 2）
3. [creative/web-video-presentation] — 转成 3 分钟讲解视频给 LP
4. [productivity/pdf] — 导出 PDF 作为附件
```

### 示例 C：技术布道「拓扑学 / 莫比乌斯环」

```
1. 自有知识 — 不需前置研究
2. [concept-fable] — 写寓言：工厂传送带质检员（references/examples.md 示例 3）
3. [creative/gpt-image-2] — 生成传送带示意图作配图
4. [writing/beautiful-article] — 排成精美单文件 HTML，发到团队 wiki
```

## 反例（不该走这条路）

| 情况 | 应该用 |
|---|---|
| 需要正式学术定义 + 文献综述 | [writing/paper-writing](../writing/paper-writing/) |
| 需要结构化研究报告 / 行业分析 | [research/hv-analysis](../research/hv-analysis/) |
| 需要「一句话讲清楚」的口号式表达 | [writing/ad-creative](../writing/ad-creative/) |
| 需要长篇说服性叙事 | [writing/khazix-writer](../writing/khazix-writer/) 直接写 |

## 适合 vs 不适合的概念类型

**适合**（用寓言解释效果好的）：
- 行为经济学 / 心理学概念（沉没成本、幸存者偏差、锚定效应）
- 数学 / 拓扑 / 几何概念（莫比乌斯环、不动点定理、维数）
- 系统科学（涌现、反馈回路、相变）
- 商业机制（长尾、护城河、网络效应）
- 认知偏差（确认偏误、可得性启发、锚定）

**不适合**（用寓言解释反而误导的）：
- 高度技术性的实现细节（如「TCP 三次握手」—— 寓言会扭曲机制）
- 需要精确定义的法律 / 财务概念（如「表外负债」）
- 仍在争议中的前沿概念（寓言会过早定型）
- 高度抽象的数学 / 哲学概念（如「无限」—— 寓言会模糊边界）

## 关键心法

> **寓言不是简化，是浓缩。**
>
> 好的概念解释 = 1 则寓言（钩子）+ 1 段解析（结构）+ 2 个检验题（理解 + 迁移）。
>
> 三件缺一不可：寓言没有解析 = 谜语；解析没有寓言 = 教科书；检验题空泛 = 浪费时间。