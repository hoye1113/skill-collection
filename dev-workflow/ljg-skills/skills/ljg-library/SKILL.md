---
name: ljg-library
description: "一本书 → 一幅清晰的「取景框」意向画面 → 一张 2050 图书馆借书卡（PNG）。取景框 = 作者从哪个角度看什么问题、看到了哪幅画面；卡上有真实封面、作者头像、书目信息。取景框 block 用费曼式讲解把这幅意向画面讲得通俗又准确；图解 block 用 AI 生图把这幅画面画出来，继刚是固定主角（从其墨像参考生成、认得出的他）。图解风格：吉田诚治式绘本感（异世界日常空间、暖光斜射、治愈又精致）。浅色光学玻璃卡身、强调色从封面动态提取、宽高自适应。合上书记住这幅画面，就没白读。Use when user says '取景框卡', '图书馆卡', 'library card', '书卡', '铸书卡', '一本书一句话一张卡', '/ljg-library', or provides a book name and wants it distilled into one collectible card. NOT FOR 拆书结构分析（用 ljg-book）、纯文字金句（用 ljg-card -b）、信息图（用 ljg-card -i）、视觉笔记（用 ljg-card -v）。"
user_invocable: true
version: "3.2.0"
---

# ljg-library：取景框借书卡

一本书，铸成一张 2050 图书馆借书卡。封面、作者、书目是身份；**核心是把这本书独创的「取景框」压成一幅意向画面**——作者从某个角度看某个问题，看到了一幅别人没看到的画面。文字 block 用费曼式把这幅画面讲透，图解 block 用 AI 生图把它画出来。合上书半年后，瞥一眼这张卡，那幅画面回来——这是「没白读」的物证。

> **图解 block = AI 生成插画**（不再手搓 SVG）。继刚是固定主角——把他的真墨像（`assets/ljg-portrait.png`）当 character reference 喂给模型，生成「认得出的他」在这幅意向画面里当「你」（在做/经历那个核心动作）。图解风格固定为**吉田诚治式绘本感**：绘本感异世界日常空间、暖光斜射、蜜糖/琥珀/木棕暖调、建筑透视扎实、植物/书/器物细节堆叠、治愈系幻想生活场所（魔法工房/旧书店/图书馆），继刚作小身形人物栖居其中。
>
> 生图用 `assets/gen_illustration.py`（直调 marswave gemini-3-pro，绕交互门控、可进批量管线）。完整设计历程见 `[[reference_ianxiaohei_drawing_upgrade]]` 记忆。

## 约束

输出为视觉文件（PNG），不适用 Org-mode / Denote / ASCII-only 规范。

## 灵魂：意向画面提炼 + 图文同呈

卡好不好看是壳，**能不能从一本书提炼出它独创的看世界方式、压成一幅意向画面、用费曼讲解 + 手绘图形分别呈现它，才是命**。这一步若失手，整张卡退化成豆瓣读书卡。

> **核心：取景框 = 角度 + 问题 + 画面。** 作者从某个机位看某个问题，看到一幅别人没看到的画面。这幅意向画面是枢轴——文字讲它、图形画它，两者是同一幅画面的两次呈现。

> **第一要义：把画面讲清楚，不求压短。** 取消一切「压成一句」之类的字数约束——画面具体、讲解通俗准确，比讲短重要。

执行前，**先 Read `references/extraction.md`**：第一部分走取景六步（对象 → 角度 → 旧画面 → 意向画面 → 费曼讲解 → 校验）产出意向画面 + 文字（主句 `{{FRAME}}` + 费曼讲解 `{{EXP}}`，**`{{EXP}}` 必走 `feynman-eli5` skill**）；第二部分把意向画面写成一段英文 frame 构图、生图（`gen_illustration.py`）——**继刚是固定主角「你」，在画面里做/经历那个核心动作**。

**输入弹性**：继刚常常自己已经想透（读完顺手就想铸卡）。给了思想就直接用（只走校验 + 画图）；没给则走全程提炼。

## 视觉规格

生成 HTML 前，**先 Read `references/visual.md`**——浅色玻璃卡身规格、卡身动态强调色、字体、吉田诚治风格的生图规格 + 主角配方 + 图解板裱框、踩过的坑全在里面。这是视觉质量底线。

## 图解风格

唯一风格 = **吉田诚治式绘本感**：绘本感异世界日常空间、暖光斜射、蜜糖/琥珀/木棕暖调、建筑透视扎实、植物/书/器物细节堆叠、场景内自然手写中文字，治愈系幻想生活场所（魔法工房/旧书店/图书馆），继刚作小身形人物栖居其中。风格 DNA 已写死在 `gen_illustration.py`，frame 只写「画什么」、不用写风格词；主角恒为继刚（从墨像参考生成）。

## 流程

```
输入：书名（或 书名 + 已想透的取景框思想）
  ↓
1. weread 取真封面 + 书目（见下「素材获取」）
2. web 抓作者头像
3. 提封面主色 → 卡身动态强调色（python assets/extract_color.py <封面>）
4. 提炼意向画面：对象 + 角度 → 意向画面（用户给了→校验，没给→走 extraction.md 取景六步）
5. 费曼讲解 → {{FRAME}}（一句话点画面）+ {{EXP}}（走 feynman-eli5 把画面讲透）
6. 写 frame 构图（英文：继刚作主角在做/经历什么、隐喻物件、信息流、3-5 个中文标注），生图：
   python3 assets/gen_illustration.py --frame "<...>" --out /tmp/ljg_lib_{slug}_sketch.png
7. 填 assets/library_template.html 的占位变量（{{SKETCH_IMG}} = file://生成图）
8. 渲染（capture.js，fullpage 自适应高度）
9. Read 自验（看生成图：继刚认得出 ✓、意向画面一眼读懂 ✓、标注中文正确 ✓、与取景框文字同一幅画面 ✓）；不满意调 frame 重生 → 交付路径
```

## 素材获取（关键，按此顺序降级）

### 封面 + 书目（weread）

继刚有微信读书。走 weread skill 的 `/store/search`（先 Read `~/.claude/skills/weread/search.md`）：

```bash
curl -s -X POST "https://i.weread.qq.com/api/agent/gateway" \
  -H "Authorization: Bearer $WEREAD_API_KEY" -H "Content-Type: application/json" \
  -d '{"api_name":"/store/search","keyword":"<书名>","scope":10,"skill_version":"1.0.3"}'
```

- 回包 `results[].books[].bookInfo`（每个 result 组一本）有 `title / author / translator / cover / publisher`。
- **封面 cover URL 是 `s_` 缩略图（70×100，太小会糊）。把 `s_` 换成 `t7_` 拿高清（285×411）**：`.../cover/942/635942/t7_635942.jpg`。下载时带 `-H "Referer: https://weread.qq.com/"`。
- 取不到 weread → 联网搜豆瓣封面（web-access / markdown-proxy）→ 仍无则 CSS 占位书封。

### 作者头像（web）

维基百科原图最稳。Wikipedia API 直接拿 original 图 URL：

```bash
curl -s -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  "https://en.wikipedia.org/w/api.php?action=query&titles=<英文名>&prop=pageimages&piprop=original&format=json"
# 拿到 .original.source 后下载（带 UA）：
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" -o /tmp/lib_avatar.jpg "<original-url>"
```

- **坑：thumb 路径（`/thumb/.../480px-xxx.jpg`）若该尺寸未缓存会返 HTML 错误页。用原图路径（去掉 /thumb/ 和尺寸段），并必须带 User-Agent（缺 UA 被 Wikimedia 拦）。**
- 无头像 → 省略头像（模板作者行不显示 avatar），不阻塞。

### 墨像 = 主角参考图（固定复用）

`assets/ljg-portrait.png`（继刚真头像抠底墨像）现在是**生图的 character reference**——`gen_illustration.py` 把它喂给模型，让模型画出「认得出的继刚」在吉田诚治风格里当主角。不再是合成进图的元素，所以图解里的继刚是模型按吉田诚治风格化的他（场景栖居版），**认得出即可，不追求像素级同一张脸**（继刚已认可这条——选了"像素化/风格化你"）。源头像更新只需替换这个 png。

### 卡身动态强调色

```bash
python3 assets/extract_color.py /tmp/lib_cover.jpg
# 输出形如：#c43d30
```

从封面提取最显著的**彩色**作卡身强调色（换书自动换色：红封→红卡、蓝封→蓝卡）。脚本默认挑「最频繁的彩色」——若封面主体是大面积米 / 灰背景，它会挑出发闷的背景色；**这时改按「鲜艳度 × 频次」重排，从真实像素里挑一个撑得住的彩色**（别凭空写死）。注意：这只是卡身强调色（标签/英文行/关键词高亮/署名印）；图解板是生成图自带的背景（吉田诚治暖光场景），各管各的、不串。强调色挑暖色（棕/橙/绿）更配那块暖调插画。

## 模板变量（library_template.html）

| 变量 | 内容 |
|------|------|
| `{{ACCENT}}` | 卡身动态强调色 hex（如 `#c43d30`，从封面提取） |
| `{{COVER}}` | 封面的 `file://` 绝对路径 |
| `{{AVATAR_IMG}}` | 整个头像 `<img class="avatar" src="file://…">`（无头像填空字符串，作者行自动省 avatar） |
| `{{TITLE}}` `{{EN}}` `{{SUBTITLE}}` | 书名中 / 英 / 副标题 |
| `{{TAGS}}` | 3-4 个主题标签（书的核心概念），每个 `<span class="tag">…</span>` |
| `{{AUTHOR_CN}}` `{{AUTHOR_META}}` | 作者中文名 / 「英文名 · 出版社 年份」 |
| `{{FRAME}}` | 意向画面**主句**：一句话点出这幅画面的换眼睛主张，关键词用 `<span class="hl">…</span>` 染卡身强调色 |
| `{{EXP}}` | **费曼讲解**：走 feynman-eli5 把这幅意向画面讲通俗讲准、完整流畅，关键词同样 `<span class="hl">` |
| `{{SKETCH_TITLE}}` | 图解板的名字（英文 + 中文，如 `Ergodicity 遍历性`） |
| `{{SKETCH_IMG}}` | 生成插画的 `file://` 绝对路径（由 `gen_illustration.py` 产，见 extraction.md 第二部分） |

## 渲染

```bash
node ~/.claude/skills/ljg-card/assets/capture.js \
  /tmp/ljg_library_{name}.html ~/Downloads/{name}.png 1080 1440 fullpage
```

复用 ljg-card 的 capture.js（playwright 已装在 ljg-card/node_modules）。**必须 `fullpage`**——卡片高度自适应内容，不留底部空白。`file://` 引用本地封面 / 头像 / 墨像可直接渲染。

## 交付

1. Read 输出的 PNG 亲眼验图，并**放大看图解板**（封面加载 ✓、费曼讲解把意向画面讲透 ✓、卡身色协调 ✓、生成图：继刚作主角认得出 ✓、意向画面一眼读懂 ✓、中文标注正确无糊 ✓、与取景框文字同一幅画面 ✓、右侧无空白、底部无留白 ✓）。生图不满意（标注糊 / 继刚不像 / 画面没读懂）就调 frame 重生。
2. 报告文件路径 + 一句意向画面提炼说明。

## Gotchas（务必避开）

- **封面尺寸**：weread `s_` 前缀是 70×100 缩略图，必糊。换 `t7_` 拿 285×411 高清，下载带 `Referer`。
- **头像 thumb 陷阱**：Wikimedia `/thumb/.../NNNpx-` 特定尺寸未缓存会返 HTML 错误页。用原图路径 + User-Agent。
- **生图必看图验收**：生图非确定（每次不同），且 gemini 偶尔糊中文标注 / 继刚不够像 / 没画对动作——**必 Read 生成图亲验**，不行就调 frame 重生（标注少而短、主角说清、隐喻具体最稳）。
- **frame 要"具体可画"**：写继刚在做/经历的那个核心动作 + 真实隐喻物件 + 信息怎么流。抽象命题画不出来——回意向画面把它落成可见的物/动作（见 extraction.md）。
- **主角恒为继刚、风格化不追同一脸**：从墨像参考生成，认得出即可（吉田诚治场景栖居版）。别回头去合成真墨像贴脸——已验证生图风格化远比合成自然（合成见记忆备选档，不用）。
- **两套色别串**：卡身强调色从封面提取（标签/高亮/印）；图解背景是生成图自带（吉田诚治暖光场景）。
- **批量管线**：`gen_illustration.py` 直调 marswave、不走 listenhub skill 的交互门控，所以 ljg-paper-flow 批量铸卡能用；但每张要联网 + 花 API + 看图一回合，比纯 SVG 慢。
- **意向画面是认知位移的成像，不是摘要**：主句「原来不是 X，其实是 Y」+ 费曼讲解讲透机制，不是「本书讲了……」。验收尺：凉脑子瞥一眼，那幅画面回不回得来。
