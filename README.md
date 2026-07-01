# All Skills

Claude Code 技能合集，收录来自多个来源的 Skills，按功能域分类管理。

## 目录结构

```
all-skills/
├── code-quality/       # 代码质量 — 审查、清理、审计、AI 痕迹去除
├── dev-workflow/       # 开发工作流 — 构思、计划、执行、调试、验证
├── frontend-ui/        # 前端/UI — 组件、设计系统、视觉工程、设计工具
├── creative/           # 创意生成 — 图像、视频、音频、音乐、PPT
├── writing/            # 内容写作 — 报告、论文、文案、广告、新闻
├── research/           # 研究分析 — 市场、竞品、趋势、SEO/GEO、用户洞察
├── learning/           # 知识学习 — 阅读、知识库构建、自适应学习
├── business/           # 商业运营 — 投研金融、SaaS 定价、留存、转化
├── productivity/       # 效率工具 — 文档处理、邮件收发、数据导出
├── product/            # 产品管理 — 发现、策略、OKR、roadmap、PM 简历（来自 phuryn/pm-skills, MIT）
├── skill-management/   # Skill 管理 — 创建、发现、进化
├── agent/              # Agent 相关 — 工作空间生成与优化
└── maps/               # 任务地图 — 按目标组合 skill（见下方）
```

## Skills 列表

| 分类 | Skill | 说明 |
|------|-------|------|
| **code-quality** | [agent-readiness](code-quality/agent-readiness/) | 仓库 Agent 就绪度审计（82 项标准） |
| | [code-review](code-quality/code-review/) | 按团队规范审查代码变更 |
| | [code-review-expert](code-quality/code-review-expert/) | SOLID / 架构 / 安全视角的专家级 Code Review |
| | [neat-freak](code-quality/neat-freak/) | 会话结束后文档与记忆的洁癖级清理 |
| | [humanizer-zh](code-quality/humanizer-zh/) | 去除中文 AI 痕迹（24 种模式 + 50 分评分体系） |
| | [reality-check](code-quality/reality-check/) | 深度代码审计：虚假测试 / mock 滥用 / 浅层健康检查检测 |
| | [ai-humanizer](code-quality/ai-humanizer/) | 去除英文 AI 写作痕迹：24 种模式检测、统计信号、词汇 3 tier 分级 |
| **dev-workflow** | [superpowers](dev-workflow/superpowers/) | 完整开发方法论框架（14 个子 Skill：构思→计划→执行→调试→测试→验证→收尾） |
| | [remotion](dev-workflow/remotion/) | Remotion React 视频框架最佳实践（30+ 规则文件） |
| | [html-to-pdf](dev-workflow/html-to-pdf/) | HTML 转 PDF（Puppeteer + 像素级渲染 + RTL 自动检测） |
| | [html-to-pptx](dev-workflow/html-to-pptx/) | HTML 转 PowerPoint（文本/截图双模式 + 自动分割） |
| | [swarm-coding](dev-workflow/swarm-coding/) | 多智能体编码协调（git worktree 隔离 / 设计优先 Web 应用） |
| | [batch-download](dev-workflow/batch-download/) | 批量下载与数据采集编排（四阶段工作流） |
| | [ljg-skills](dev-workflow/ljg-skills/) | 李继刚个人技能集合（14 个：内容创作 / 投资 / 关系 / 旅行 / 研究 / 写作，Darwin 评分 78-88） |
| **frontend-ui** | [frontend-interface-design](frontend-ui/frontend-interface-design/) | 生产级前端界面构建与审查 |
| | [react-best-practices](frontend-ui/react-best-practices/) | Vercel 出品的 React/Next.js 性能优化规则集 |
| | [semi-ui-skills](frontend-ui/semi-ui-skills/) | Semi Design 企业级组件库使用指南 |
| | [ui-ux-pro-max](frontend-ui/ui-ux-pro-max/) | UI/UX 设计智能系统（50+ 风格、97 色板） |
| | [web-design-engineer](frontend-ui/web-design-engineer/) | 高视觉品质 Web 制品构建（页面/仪表盘/原型） |
| | [web-visual-artifacts](frontend-ui/web-visual-artifacts/) | 独立视觉 Web 制品（落地页/原型/动画演示） |
| | [impeccable](frontend-ui/impeccable/) | 产品级前端设计（7 领域参考 + 23 命令 + 27 反模式规则 + CLI + 浏览器扩展） |
| | [figma](frontend-ui/figma/) | Figma REST API 全接口 Skill（45 个 API、Token 安全契约） |
| | [apple-kickstarter-landing-page](frontend-ui/apple-kickstarter-landing-page/) | 仿 Apple 风格 Kickstarter 众筹落地页生成器 |
| | [frontend-slides-main](frontend-ui/frontend-slides-main/) | 零依赖 HTML 演示文稿（12 种风格 / PPT 转换 / PDF 导出） |
| | [html-component-builder](frontend-ui/html-component-builder/) | 组件化 HTML 构建规范（CSS 命名空间隔离 + 验证脚本） |
| | [cinematic-slides](frontend-ui/cinematic-slides/) | AI 视频背景电影级 HTML 演示文稿 + GitHub Pages 部署 |
| **creative** | [gpt-image-2](creative/gpt-image-2/) | GPT Image 2 图像生成/编辑（80+ 模板） |
| | [guizang-ppt-skill](creative/guizang-ppt-skill/) | 杂志风横向翻页网页 PPT 生成 |
| | [seedance2-skill-main](creative/seedance2-skill-main/) | 即梦 Seedance 2.0 视频提示词工程 |
| | [web-video-presentation](creative/web-video-presentation/) | 文章转"伪视频"网页演示（可选 TTS） |
| | [image-generation](creative/image-generation/) | Gemini/fal.ai 生图 + Grok/fal.ai 生视频（双 provider） |
| | [music-generator](creative/music-generator/) | ElevenLabs AI 音乐生成（简单/详细双模式） |
| | [kinetic-video-creator](creative/kinetic-video-creator/) | 动态排版视频：脚本→TTS→音乐→动画（Remotion） |
| | [tutorial-creator](creative/tutorial-creator/) | 屏幕录制→专业教程（旁白/音乐/字幕/分发） |
| **writing** | [report-writing](writing/report-writing/) | 端到端长报告创建（4 阶段流水线 / 依赖图分析） |
| | [paper-writing](writing/paper-writing/) | 端到端学术论文创建（贡献声明 / 4 级审校） |
| | [copy-editing](writing/copy-editing/) | 七轮逐层文案编辑（清晰度→语调→价值→证据→具体性→情感→零风险） |
| | [ad-creative](writing/ad-creative/) | 高性能广告创意生成（Google/Meta/LinkedIn/TikTok/Twitter 全平台） |
| | [general-writing](writing/general-writing/) | 通用写作（12 种体裁路由 / 反 AI 写作规则） |
| | [khazix-writer](writing/khazix-writer/) | 卡兹克风格公众号长文写作 |
| | [news-aggregator-skill](writing/news-aggregator-skill/) | 28 信源综合新闻聚合（深度分析 + 关键词过滤） |
| | [aihot](writing/aihot/) | AI HOT 中文 AI 资讯日报查询 |
| | [presentation-architect](writing/presentation-architect/) | 创意→逐页演示脚本（9 元素框架） |
| | [beautiful-article](writing/beautiful-article/) | 任意素材 → 单文件 HTML 精美文章（10 文章类型 × 11 主题 profile，3 硬 checkpoint） |
| | [concept-fable](writing/concept-fable/) | 围绕 {concept} 写一则寓言完整解释它（≤1000 字、2-3 角色、不说破）+ 概念解析 + 2 个具体可答检验题 |
| **research** | [hv-analysis](research/hv-analysis/) | 横纵分析法深度研究：纵向时间线 + 横向竞品对比，产出 PDF 报告 |
| | [prompts](research/prompts/) | 横纵分析法纯文本提示词模板，可在任意 Deep Research 模型中使用 |
| | [market-research](research/market-research/) | 市场研究：TAM/SAM/SOM 分层、4 种研究模式、证据质量分级 |
| | [competitive-analysis](research/competitive-analysis/) | 深度竞品分析：6 层情报框架（Strategy/Product/Pricing/Marketing/Reviews/Health） |
| | [competitor-monitoring](research/competitor-monitoring/) | 竞品持续监测：pricing/feature/positioning 信号追踪，战略档案维护 |
| | [trend-researcher](research/trend-researcher/) | 行业趋势分析：信号识别、生命周期判断、技术前瞻、完整趋势报告模板 |
| | [serp-analysis](research/serp-analysis/) | SERP 搜索结果分析：排名因子、SERP Feature 映射、AI Overview 模式识别 |
| | [geo-content-optimizer](research/geo-content-optimizer/) | GEO 生成式引擎优化：为 ChatGPT/Perplexity/AI Overviews 优化内容可引用性 |
| | [reddit-insights](research/reddit-insights/) | Reddit 语义搜索：用户痛点挖掘、利基市场发现、产品验证 |
| | [jtbd-analyzer](research/jtbd-analyzer/) | Jobs-To-Be-Done 分析：功能/情感/社会三维动机框架 |
| | [seo-audit](research/seo-audit/) | 全面 SEO 审计（技术 / 页面 / 内容 / 权威性） |
| | [user-personas](research/user-personas/) | 用户画像提炼（来自 phuryn/pm-skills，3 personas + JTBD + pains/gains） |
| | [market-sizing](research/market-sizing/) | 市场体量估算 TAM/SAM/SOM（自顶向下 + 自底向上） |
| | [summarize-interview](research/summarize-interview/) | 客户访谈纪要 → JTBD + 满意度信号 + action items |
| **learning** | [book-study](learning/book-study/) | 系统化阅读教练（精读/测试/复习） |
| | [kb-retriever](learning/kb-retriever/) | 本地知识库检索与问答 |
| | [sigma](learning/sigma/) | Bloom 2-Sigma 精通学习 AI 家教 |
| | [wiki-ingest](learning/wiki-ingest/) | 文章/笔记编译为结构化 Wiki 知识库 |
| | [learn](learning/learn/) | 元技能：教 Claude 学习任意主题并保留为永久 skill |
| | [deep-interview](learning/deep-interview/) | 自适应深度访谈提取知识，构建结构化知识库 |
| **business** | [equity-researcher](business/equity-researcher/) | 机构级投研报告生成（投资速览 / 深度研报 / 六维分析） |
| | [value-invest-scorer](business/value-invest-scorer/) | 巴菲特/格雷厄姆价值投资评估（四大维度 20 项评分） |
| | [financial-report-reader](business/financial-report-reader/) | 财报三表深度解读（10 项异常检测 / 三表联动分析） |
| | [stock-finance-profiler](business/stock-finance-profiler/) | 20+ 财务指标 + 杜邦分析（7 大类） |
| | [churn-prevention](business/churn-prevention/) | SaaS 客户流失预防（五阶段取消流程 / 动态挽留） |
| | [pricing-strategy](business/pricing-strategy/) | SaaS 定价策略设计（三轴框架 / Van Westendorp 测量） |
| | [paywall-upgrade-cro](business/paywall-upgrade-cro/) | 应用内付费墙与升级页面 CRO：4 类触发点、价值优先原则 |
| **productivity** | [xlsx](productivity/xlsx/) | Excel 创建与分析（公式强制规则 / 财务建模 / 双主题样式） |
| | [docx](productivity/docx/) | Word 创建/编辑/转换（渐进式披露 / XSD 验证 / OOXML 处理） |
| | [pdf](productivity/pdf/) | PDF 创建与处理（ReportLab/md2pdf/Process 三路由） |
| | [imap-smtp-email](productivity/imap-smtp-email/) | IMAP/SMTP 个人邮箱：6 平台支持、中文别名映射、反幻觉设计 |
| **product** | [opportunity-solution-tree](product/opportunity-solution-tree/) | Teresa Torres OST 框架：outcome→opportunities→solutions→experiments |
| | [identify-assumptions-new](product/identify-assumptions-new/) | 新产品 8 类风险假设识别（Value/Usability/Viability/Feasibility/GTM/Strategy/Team...） |
| | [identify-assumptions-existing](product/identify-assumptions-existing/) | 已有产品 4 类风险假设识别 |
| | [prioritize-assumptions](product/prioritize-assumptions/) | Impact × Risk 矩阵 + 实验建议排序 |
| | [product-strategy](product/product-strategy/) | 9 段 Product Strategy Canvas（vision→defensibility） |
| | [value-proposition](product/value-proposition/) | 6 部分 JTBD 价值主张画布（Who/Why/What before/How/What after/Alternatives） |
| | [strategy-red-team](product/strategy-red-team/) | 对抗性假设压力测试：自反偏差机制 + 元认知章节（Darwin 86.9） |
| | [pre-mortem](product/pre-mortem/) | 预失败分析：Tigers / Paper Tigers / Elephants 分类 |
| | [brainstorm-okrs](product/brainstorm-okrs/) | 团队级 OKR 头脑风暴（与 strategy 对齐） |
| | [outcome-roadmap](product/outcome-roadmap/) | 把 feature 列表转为 outcome-focused 路线图 |
| | [metrics-dashboard](product/metrics-dashboard/) | North Star Metric + 输入指标 + 告警阈值设计 |
| | [review-resume](product/review-resume/) | PM 简历评审（10 条最佳实践 + XYZ+S 公式 + weak/strong 对照） |
| **skill-management** | [find-skills](skill-management/find-skills/) | 发现和安装 Agent Skills |
| | [github-skills-main](skill-management/github-skills-main/) | GitHub 仓库转 Skill / Skill 管理与进化 |
| | [skill-creator](skill-management/skill-creator/) | Skill 创建指南（6 步流程） |
| | [skill-forge](skill-management/skill-forge/) | 生产级 Skill 锻造（token 效率优先） |
| | [skill-review](skill-management/skill-review/) | Skill 质量审查与审计 |
| | [nuwa-skill](skill-management/nuwa-skill/) | 女娲造人：深度调研→思维框架提炼→生成人物 Skill |
| | [darwin-skill](skill-management/darwin-skill/) | 达尔文.skill：评估→改进→实测→保留或回滚，自主循环优化 |
| | [luban](skill-management/luban/) | 鲁班打磨：五道工序全生命周期 Skill 打磨与发布就绪（验料→访行→过尺→慢刨→回炉） |
| **agent** | [openclaw-agent-forge](agent/openclaw-agent-forge/) | OpenClaw/FlowyClaw Agent 工作空间生成与优化 |
| | [agent-browser](agent/agent-browser/) | AI Agent 浏览器自动化 CLI（导航/表单/截图/抓取） |
| | [claudability-analyzer](agent/claudability-analyzer/) | 分析各职业 Claude Code 自动化机会（6 维度 + PDF 报告） |
| | [kimi-webbridge](agent/kimi-webbridge/) | 控制真实浏览器（导航/点击/输入/截图/PDF），通过本地 daemon 交互 |
| | [deep-research-swarm](agent/deep-research-swarm/) | 多智能体深度研究编排（4 种路由 / 7 阶段 / 交叉验证） |

## 任务地图（Maps）

按目标快速组合 skill：

| 地图 | 场景 |
|------|------|
| [产品发布](maps/product-launch.md) | 情报→内容→演示→交付 |
| [投研分析](maps/investment-research.md) | 财报→估值→报告→PDF |
| [内容营销](maps/content-marketing.md) | 趋势→文案→创意→分发 |
| [概念解释](maps/concept-explanation.md) | 概念定位→寓言创作→可视化→PDF/视频 |

## 来源

| 仓库 | 说明 |
|------|------|
| hoye-skills | 主技能库 |
| sanyuan-skills | 三元技能集 |
| garden-skills | Garden 技能集 |
| khazix-skills | 卡兹克技能集 |
| **ljg-skills** | **李继刚个人技能集合（Darwin 评分 A 档 14 个）** |
| superpowers | 开发方法论框架 |
| nuwa-skill | 女娲造人 Skill |
| impeccable | 产品级前端设计 Skill |
| darwin-skill | 达尔文 Skill 自主优化系统 |
| openclaw-agent-store | OpenClaw Agent 技能商店 |
| claude-skills-library | Claude Skills Library |
| kimi-desktop | Kimi Desktop Daimon Skills |
| qclaw | QClaw Skills |
| **luban-skill** | **鲁班 Skill 打磨系统（五道工序全生命周期）** |
| **phuryn/pm-skills** | **PM 方法论合集（9 plugins / 68 skills，Darwin 精选 15 个，MIT 协议）** |
