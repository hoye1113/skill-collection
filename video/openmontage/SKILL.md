---
name: openmontage
description: OpenMontage 开源 agentic 视频生产系统（外部安装，AGPL-3.0）入口指引。当用户要求端到端制作成片级视频——动画讲解、纪录片混剪（真实素材）、预告片/品牌片、口播/虚拟人、播客切片、多语言配音、角色动画——且需要"调研→提案→脚本→分镜→素材→剪辑→合成"完整管线时使用。本 skill 不含实现代码；执行前必须获取仓库并严格按其 AGENT_GUIDE.md 与 pipeline 操作。
---

# OpenMontage（外部系统入口）

OpenMontage 是把 AI 编码助手变成完整视频制作工作室的开源系统：12 条生产管线、100+ Python 工具、60+ provider（云端 API + 本地 GPU + 免费素材库）、700+ agent 知识文件。它自带 AGPL-3.0 许可，**本体不在本合集内**。

**本 skill 只负责"知道它存在，并正确使用它"。** 实际制作必须先取得 OpenMontage 仓库，并严格按它自己的管线执行——不要凭本文件即兴发挥工作流。

## 何时用 / 何时不用

- **用**：成片级、多阶段任务——动画讲解视频、真实素材纪录片混剪（不是"图片动一动"）、参考视频复刻、电影感预告片、口播视频、播客切片批量产出、多语言配音、角色动画。
- **不用**：单点能力任务（生图、生视频片段、TTS、字幕、网页演示动画）优先用本合集专项 skill（`remotion`、`kinetic-video-creator`、`seedance2-skill-main`、`image-generation`、`tutorial-creator` 等）。OpenMontage 是重型编排器，杀鸡不用牛刀。
- 判断标准：如果任务需要 3 个以上阶段（调研/脚本/素材/剪辑/合成）串成一条生产线，才值得动用它。

## 获取与安装

先探测本机是否已有安装（常见位置或询问用户）；没有则 clone 到固定位置（建议 `~/tools/OpenMontage`，或用户指定路径，并记住该路径）。

```bash
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage && git pull && make setup
```

- 依赖：Python 3.10+、Node.js 18+、FFmpeg、一个编码 agent（本 agent 即可）。
- 无 `make` 的手动安装（含 Windows PowerShell 变体）见仓库 `README.md` Quick Start。
- API key **全部可选**，放 `.env`：零 key 可做图片驱动视频 + 真实素材（Archive.org/NASA/Wikimedia）混剪；Pexels/Pixabay/Unsplash 需免费开发者 key；有 GPU 可 `make install-gpu` 本地免费生成视频。
- 上游活跃（449+ commits）：使用前先 `git pull`，一切细节以仓库当前版本为准。

## 执行契约（必须遵守）

1. **先读契约**：`AGENT_GUIDE.md` → 再读 `PROJECT_CONTEXT.md`。
2. **不要即兴编排**：一切走 `pipeline_defs/`（YAML 管线清单）→ `skills/pipelines/`（各阶段导演指令）→ `tools/`（工具注册表）。
3. **每个视频需求 = 管线选择问题**：先选管线 → 读 manifest → 读阶段 skill → 再调工具。
4. **能力探测**（安装后运行，结果决定可用工具档位）：

   ```bash
   python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.support_envelope(), indent=2))"
   python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.provider_menu(), indent=2))"
   ```

5. **成本与审批**：任何付费生成前向用户报预算并获批准（OpenMontage 自带预算治理，不要绕过）。
6. **渲染运行时**（Remotion / HyperFrames）在提案阶段锁定 `render_runtime`，禁止静默切换。
7. 产物固定在 `projects/<project-name>/renders/final.mp4`；交付前必须走完它内置的自检（ffprobe + 抽帧 + 音频分析）。

## 仓库导航（"细节通过 git 查找"的入口表）

| 想知道 | 打开 |
|---|---|
| 总契约、最短工作路径 | `AGENT_GUIDE.md`、`PROJECT_CONTEXT.md` |
| 有哪些管线、选哪条 | `pipeline_defs/*.yaml`、`README.md` → Pipelines |
| 某管线某阶段怎么做 | `skills/pipelines/<pipeline>/<stage>.md` |
| 有哪些工具、怎么调 | `tools/tool_registry.py`、`tools/` |
| provider 清单与价格 | `docs/PROVIDERS.md` |
| 可直接套用的提示词 | `PROMPT_GALLERY.md` |
| 可视化监工（可选） | `python -m backlot open`（实时看板 / 故事板审批） |

## 注意

- **许可 AGPL-3.0**：只作为外部依赖安装调用；不要把其代码复制进本合集或其他项目再分发。
- **回退链**：安装失败 / 无 key / 无法承担重型制作时，明确告知用户，并降级到本合集轻量 skill（如 `kinetic-video-creator`、`huashu-design` 导出 MP4）完成可交付的部分。
- 上游地址：https://github.com/calesthio/OpenMontage （细节以其当前 main 分支为准）
