# Code Review Skill

让 Agent 用一套统一入口完成代码变更审查：既能按团队规范做常规 review，也能在需要时补充架构、安全、性能和冗余代码分析。

> 这是一个单一 skill，深度审查能力已经并入主入口，不再维护独立 expert 入口。

## 能力概览

- **统一入口**：审查本地 `git diff`、`git diff --staged`、分支/提交范围和远程 GitHub PR
- **标准审查**：变更摘要、影响点评估、逐文件反馈、修复后续动作
- **深度审查**：按需检查 SOLID、架构边界、安全风险、race condition、性能热点、错误处理、死代码
- **统一输出**：只使用 `[Required] / [Optional] / [Question] / [FYI]`
- **自动修复**：用户确认后再进入修复流程
- **知识沉淀**：支持通过脚本采集历史 PR 评论沉淀到 `review-log.md`

## 目录结构

```text
code-review/
├── agents/
│   └── agent.yaml
├── references/
│   ├── code-quality-checklist.md
│   ├── removal-plan.md
│   ├── security-checklist.md
│   └── solid-checklist.md
├── scripts/
│   └── fetch-pr-comments.mjs
├── README.md
├── RULES.md
├── SKILL.md
└── review-log.md
```

## 触发方式

以下表达都会命中同一个 skill：

```text
帮我 review 一下当前代码改动
review 这个 PR：https://github.com/owner/repo/pull/123
审查一下 feat/xxx 相对于 main 的变更
重点看这次改动有没有 SOLID 和架构问题
帮我查安全风险和 race condition
看看这次改动有没有可以删掉的冗余代码
```

## 审查模式

### Standard Review

默认模式，关注：

- 正确性
- 风险与回归
- 可维护性
- 一致性
- 体验细节

### Deep Review

以下情况会自动升级到 deep review：

- 用户明确提到：架构、SOLID、安全、race condition、性能、可删除代码、冗余代码
- 变更超过 500 行
- 变更涉及 auth、payments、data writes、network、shared primitives、公共组件、共享状态、API 签名

Deep review 会按需加载 `references/` 下的检查清单：

- `solid-checklist.md`
- `security-checklist.md`
- `code-quality-checklist.md`
- `removal-plan.md`

## 使用方式

### 本地变更

无额外要求，skill 会根据上下文选择：

- `git diff`
- `git diff --staged`
- `git diff <base>...<head>`

### 远程 PR

优先使用 GitHub MCP 获取 PR 元信息和 diff，`gh` CLI 仅作为兜底。

### 重要约束

如果用户只说“做个安全 review / 架构 review”，但当前没有可识别的 diff、staged、PR 或 range，skill 必须先追问审查目标，不能默认扫描整个仓库。

## 输出结构

审查结果统一包含：

1. **变更摘要**：目标、核心改动、动机、波及面
2. **影响点评估**
3. **审查结论**：深度、关注重点、总体判断
4. **逐文件反馈**
5. **Next Steps**：全部修复 / 仅修复 Required / 指定修复 / 仅审查

### 严重等级

| 标签 | 含义 | 是否阻断合并 |
|------|------|-------------|
| `[Required]` | 必须修改 | 是 |
| `[Optional]` | 建议改进 | 否 |
| `[Question]` | 需要澄清 | 视澄清结果而定 |
| `[FYI]` | 信息同步 | 否 |

不会再输出 `P0/P1/P2/P3`。

## 自动修复流程

skill 默认先做 review，不直接改代码。只有在用户明确选择以下选项后，才进入修改阶段：

1. **全部修复**
2. **仅修复 Required**
3. **指定修复**
4. **仅审查**

修复完成后，Agent 应重新运行必要检查，并汇总每条反馈的处理结果。

## 定制点

- **RULES.md**：团队基线规则
- **SKILL.md**：统一工作流、触发和输出格式
- **references/**：深度审查参考清单
- **review-log.md**：历史审查样本

## 辅助脚本

`fetch-pr-comments.mjs` 从 GitHub 拉取历史 PR review 评论，写入 `review-log.md`，帮助沉淀团队审查风格。

```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxx node .cursor/skills/code-review/scripts/fetch-pr-comments.mjs \
  --owner <组织或用户名> \
  --repo <仓库名>
```

## 迁移说明

- 深度审查用到的 `references/` 与 `agent.yaml` 已并入 `code-review`
- 旧的 expert 目录已退役，不再作为单独 skill 使用
- 旧的 expert 命令入口不再维护

## License

MIT
