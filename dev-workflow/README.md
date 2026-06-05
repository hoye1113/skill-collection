# Dev Workflow

开发工作流方法论 Skills —— 覆盖从构思、计划、执行到验证、收尾的完整开发流程。

## Skills

| Skill | 说明 | 来源 |
|-------|------|------|
| [superpowers](superpowers/) | 完整的开发方法论框架，包含 14 个子 Skill，覆盖构思→计划→执行→调试→测试→验证→收尾全流程 | superpowers |
| [remotion](remotion/) | Remotion (React 视频创作框架) 最佳实践参考，30+ 规则文件覆盖动画/字幕/音频/3D/转场 | [alchaincyf/openclaw-agent-store](https://github.com/alchaincyf/openclaw-agent-store) |
| [html-to-pdf](html-to-pdf/) | HTML 转 PDF，Puppeteer 引擎 + 像素级渲染 + RTL 自动检测 + 5 次修复验证 | [claude-skills-library](https://github.com/nicepkg/claude-skills-library) |
| [html-to-pptx](html-to-pptx/) | HTML 转 PowerPoint，文本/截图双模式 + 自动幻灯片分割 + RTL 检测 | [claude-skills-library](https://github.com/nicepkg/claude-skills-library) |
| [swarm-coding](swarm-coding/) | 多智能体编码协调，git worktree 隔离、设计优先 Web 应用构建 | [kimi-desktop](https://kimi.com) |
| [batch-download](batch-download/) | 批量下载与数据采集编排，四阶段工作流、"永不伪造 URL"原则 | [kimi-desktop](https://kimi.com) |

### Superpowers 子 Skills

| 子 Skill | 说明 |
|----------|------|
| brainstorming | 通过协作对话将想法转化为完整设计和规范 |
| writing-plans | 从需求创建细粒度实施计划（假设执行者零上下文） |
| executing-plans | 加载计划并在独立会话中顺序执行，含检查点审查 |
| subagent-driven-development | 每个任务分派独立子 Agent 执行，含两阶段审查 |
| dispatching-parallel-agents | 将独立任务分派给并行子 Agent 以节省时间 |
| systematic-debugging | 在尝试修复前强制进行根因调查 |
| test-driven-development | 严格红-绿-重构 TDD：没有失败测试就不写生产代码 |
| verification-before-completion | 完成前必须运行验证命令并确认输出 |
| requesting-code-review | 调度 Code Review 子 Agent 并构造上下文 |
| receiving-code-review | 以技术严谨性评估收到的 Code Review 反馈 |
| finishing-a-development-branch | 验证测试、检测环境、结构化地完成分支收尾 |
| using-git-worktrees | 检测隔离状态，必要时创建 Git Worktree |
| writing-skills | TDD 方式创建和验证 Skill |
| using-superpowers | 会话启动框架，建立跨平台 Skill 发现和优先级 |

## 使用场景

- 从零开始一个功能开发的完整流程
- 需要结构化的计划-执行-验证工作流
- 使用子 Agent 并行加速开发
- 遵循严格的 TDD 和调试方法论
- 规范化 Code Review 请求和反馈处理流程
