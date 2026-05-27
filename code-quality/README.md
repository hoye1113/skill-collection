# Code Quality

代码质量保障类 Skills —— 覆盖代码审查、文档清理、仓库审计等环节。

## Skills

| Skill | 说明 | 来源 |
|-------|------|------|
| [agent-readiness](agent-readiness/) | 5 阶段静态审计，评估仓库对自主 Agent 的就绪度（82 项标准、9 大类别） | hoye-skills |
| [code-review](code-review/) | 按团队规范审查代码变更，支持标准/深度两种模式，聚焦通用/架构/安全/清理 | hoye-skills |
| [code-review-expert](code-review-expert/) | 以高级工程师视角进行 SOLID 违规、安全风险检测，提出可执行改进方案 | sanyuan-skills |
| [neat-freak](neat-freak/) | 会话结束后的文档与记忆同步清理，确保 CLAUDE.md、README、docs 与代码一致 | khazix-skills |
| [humanizer-zh](humanizer-zh/) | 去除中文文本中 AI 生成痕迹，24 种模式识别 + 50 分质量评分体系 | [alchaincyf/openclaw-agent-store](https://github.com/alchaincyf/openclaw-agent-store) |

## 使用场景

- 提交 PR 前检查代码质量
- 评估仓库是否适合引入 AI Agent
- 会话结束时清理过时文档和记忆
- 对代码变更进行架构/安全层面的深度审查
