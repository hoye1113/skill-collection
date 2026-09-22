# Agent-Reach 收录评估

评估日期：2026-09-22
上游：<https://github.com/Panniantong/Agent-Reach>
检查快照：`main` / `a19a171fa980a0785849596492e0af4db800c82f`（2026-09-16）

## 结论

**适合完整收录。** 初始评估建议薄收录；用户于 2026-09-22 明确选择完整收录。鉴于上游体量约 1.23 MiB、许可证为 MIT，且静态检查与环境适配测试结果良好，本次以可追踪的完整镜像方式纳入。

目标目录：`agent/agent-reach`。收录上游源码、测试、文档、Skill 与 MIT 许可证；不收录 `.git`、本地虚拟环境、缓存或用户凭据。运行时仍需按上游安装文档在隔离环境中安装，完整收录不代表已安装或各平台已登录。

## 为什么值得收录

1. **能力差异明显**：把网页、GitHub、YouTube、RSS、V2EX，以及需要登录态的 Twitter、Reddit、小红书、Facebook、Instagram、招聘和雪球等入口统一成“多后端路由 + doctor 体检”模型，补足当前集合中跨平台互联网获取能力的空缺。
2. **Skill 形态合格**：主 `SKILL.md` 约 168 行，引用 7 个按需加载的 references，包含触发词、路由表、失败处理、认证边界和工作区规则，适合作为 `agent/` 下的薄入口。
3. **安全边界比一般抓取脚本清楚**：默认 `install` 是检查模式，系统安装、全局工具、MCP 配置和 Skill 注册需要显式 `--system`；Cookie/浏览器登录态要求用户明确提供或使用已有会话，不自动登录。上游还对私密配置做原子写入、权限和符号链接防护。
4. **维护与验证信号良好**：上游最新 release 为 v1.5.0；CI 覆盖 Python 3.10–3.13、Windows、wheel 内容和干净环境安装。许可证为 MIT，Python 要求为 3.10+。

## 使用与同步注意事项

### P0：触发范围会抢占现有 Skill

上游描述写成“只要用户提到任何 URL，或任何互联网调研，都 MUST USE”，同时又要求已有专门 Skill 优先。这会与现有 `agent/browser-skill`、平台专用 Skill、研究 Skill 发生路由竞争。

使用时应在本集合的路由层收窄为：

- 用户明确提到 Agent Reach；或
- 需要跨多个互联网平台、中文平台、登录态平台，并且没有更专用 Skill；或
- 用户明确要求用 CLI/多后端路由获取互联网内容。

不要保留“任意 URL 都必须使用”和“所有互联网调研都必须使用”的全局抢占式触发。

### P1：Skill 内含本机私有环境假设

`SKILL.md` 的环境检查写死“本机 Python 默认是 conda `dl`”，并要求使用 `conda run -n dl`。这不是通用收录内容，会在大多数机器上制造错误路径。

使用时应采用通用检查顺序：`agent-reach doctor --json` → 当前 PATH 中的 `agent-reach` → 按安装文档创建/激活隔离环境；不要预设 conda 环境名。

### P1：它依赖外部运行时，不是自包含 Skill

Skill 只是命令路由和操作规约，实际能力依赖 `agent-reach`、`gh`、`yt-dlp`、`mcporter`、OpenCLI、各平台 CLI/MCP、浏览器扩展、ffmpeg 和可选 API Key。同步进本集合不会自动提供这些运行时。

目录说明必须明确：这是“外部运行时的路由 Skill”，安装需走上游官方 install 文档，不能把收录误宣传成开箱即用。

### P1：动态路由、外部安装和凭据风险要显式降级

上游会根据平台反爬和后端状态更换路由；部分路径会执行 npm/pipx/uv/apt/brew 安装，部分路径会读取用户明确指定的 Cookie、复用 Chrome 登录态、写入 MCP 配置或连接本机 CDP。默认安全模式和测试覆盖是优点，但收录版必须保留以下硬边界：

- 只读任务不自动执行 `--system`、全局安装、MCP 写配置、Cookie 导入或浏览器登录。
- 使用 Cookie/Chrome/CDP 前先取得用户明确授权，优先专用账号和专用浏览器 profile。
- 不把 `doctor` 的“已安装”当成“登录成功/内容可访问”；以真实只读命令的非空结果验收。
- 不把 `check-update` 作为每次大任务的隐式强制动作；改为用户请求、计划任务或收尾可选提示。

### P2：上游自身存在口径漂移

当前不同文件对平台数有 13/16 的不同口径；`SKILL.md`、README、release notes 和项目说明的渠道列表也会随路由变化。收录目录不要复制“16 平台”等易过期数字，改写为“多平台、多后端，具体状态以 doctor 为准”，并在同步记录中保存上游 commit 和复核日期。

## 实际同步形态

在 `_ops/sync-config.json` 中使用 `whole`，完整镜像上游：

```json
{
  "name": "agent-reach",
  "remoteUrl": "https://github.com/Panniantong/Agent-Reach.git",
  "strategy": "whole",
  "source": ".",
  "target": "agent/agent-reach"
}
```

完整镜像保留上游 `SKILL.md` 原文，因此不能把它的宽泛触发词直接视为本集合统一路由规则。每次更新后应重新检查路由冲突、安全文案和环境假设；必要的适配说明应放在集合入口或目录说明中，而不直接改写镜像内容。

## 本次验证

- 上游静态检查：`ruff check agent_reach tests` 通过；`mypy agent_reach` 通过（36 个源文件）。
- 上游 pytest：在临时 Python 3.12.11 环境按 `constraints.txt` 安装成功。
- 环境适配后的测试：`562 passed, 15 skipped, 30 deselected`；被排除的是 Windows 无 symlink 创建权限和 Git Bash 测试进程找不到 Python 的环境前置。
- 未声称完整 pytest 全绿：未过滤运行在本机暴露了上述环境前置失败，不能把它们归因于项目功能失败。
- CLI smoke：`version`、`install --env=auto --safe`、`install --env=auto --system --dry-run`、`doctor --json` 均退出码 0；隔离 HOME 下 safe/dry-run 未写入持久文件。
- 完整收录在独立分支 `feat/collect-agent-reach-full` 完成；干净浅克隆与目标目录的 122 个 Git 跟踪文件逐文件 SHA-256 一致。
- `_ops/sync-config.json` 与 `_ops/sync-state.json` 均可解析，`git diff --check` 通过；本次未运行会自动更新全部来源并自动提交的全库同步脚本。

## 收录验收门槛

1. 以 `whole` 同步建立 `agent/agent-reach`，保留上游源码、测试、文档、Skill 和许可证。
2. 在集合目录与 README 明确其为外部运行时能力层；专用 Skill 优先，跨平台场景再进入 Agent-Reach。
3. 不将 `conda dl`、`--system`、Cookie/CDP 或隐式更新检查作为通用默认操作。
4. 运行集合自身的目录/配置校验、Markdown 检查和路由冲突检查。
5. 用隔离环境验证：无 `agent-reach` 时可给出清晰的缺依赖提示；有运行时但未登录时不会宣称渠道可用；只读诊断不会写工作区。

## 证据来源

- 上游 README、平台能力和安全/安装口径：<https://github.com/Panniantong/Agent-Reach>
- 安装边界与授权模式：<https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/docs/install.md>
- Skill 与触发/路由内容：<https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/agent_reach/skill/SKILL.md>
- 包元数据与 MIT/Python 依赖：<https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/pyproject.toml>
- CI、Windows 和 wheel gate：<https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/.github/workflows/pytest.yml>
- 安全披露范围：<https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/SECURITY.md>
