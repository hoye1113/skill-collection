#!/usr/bin/env python
"""Darwin Phase 3 Result Card 生成器 — 单 skill 版本（R3 ljg-word）"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(r"D:\workSpace\hoye-skills-main\skill-collection")
TPL = REPO / "skill-management/darwin-skill/templates/result-card.html"
OUT_HTML = REPO / "_ops/result-card-r3.html"
OUT_PNG = REPO / "_ops/result-card-r3.png"

# R3 ljg-word 占位数据
DATA = {
    "date": "2026.06.12",
    "skill-name": "英文单词深度拆解",
    "skill-id": "ljg-word",
    "score-before": "63.2",
    "score-after": "74.7",
    "score-delta": "+11.5",
    "top1-name": "边界条件覆盖",
    "top1-from": "4",
    "top1-to": "8",
    "top1-pct": "+100%",
    "top1-story": "从无系统边界到 7 类显式规则（多义词/复合词/俚语/专有名词/虚词/超长词/非英文）",
    "top2-name": "整体架构",
    "top2-from": "6",
    "top2-to": "8",
    "top2-pct": "+33%",
    "top2-story": "Anti-pattern 从隐式提升为显式多条（绝不编造词源/不拆字面/诚实说虚词无独立语义）",
    "improve-1": "补 7 类边界条件段：多义词→WebSearch 查 Top 2-3 sense 逐一展开；复合词→整体不拆字面；俚语→诚实无词源",
    "improve-2": "跨 skill handoff：非英文输入自动转 ljg-plain 等同类 skill，不强行当英文词处理",
    "improve-3": "文件增长仅 10 行 (28→38)，远在 Darwin 150% 限制内，0 Runtime 红灯保持 pass",
    # 8 维度 (dim1-dim8)
    "dim1-old": "7", "dim1-new": "7", "dim1-delta": "0",    # 元数据
    "dim2-old": "7", "dim2-new": "7", "dim2-delta": "0",    # 工作流
    "dim3-old": "4", "dim3-new": "8", "dim3-delta": "+4",   # 边界覆盖 ★
    "dim4-old": "3", "dim4-new": "3", "dim4-delta": "0",    # 检查点
    "dim5-old": "7", "dim5-new": "8", "dim5-delta": "+1",   # 指令精度
    "dim6-old": "3", "dim6-new": "4", "dim6-delta": "+1",   # 资源整合
    "dim7-old": "6", "dim7-new": "8", "dim7-delta": "+2",   # 整体架构
    "dim8-old": "8", "dim8-new": "9", "dim8-delta": "+1",   # 实测表现
}

# 进度环: 74.7% 填充 = 74.7/100 * 565.5 (圆周) = 422.4 (offset 143.1)
# SVG 圆周长 = 2*pi*85 = 533.8
CIRCUMFERENCE = 2 * 3.14159 * 85
PROGRESS_OFFSET = CIRCUMFERENCE * (1 - 74.7 / 100)
DATA["ring-offset"] = f"{PROGRESS_OFFSET:.1f}"

# 8 维度的 arrow class (up-big=+3+, up-mid=+2, up-small=+1, none=0)
def arrow_class(delta_str):
    if delta_str in ("0", "0.0"): return "up-none"
    if delta_str.startswith("+"):
        n = int(delta_str[1:]) if delta_str[1:].isdigit() else 0
        if n >= 3: return "up-big"
        if n == 2: return "up-mid"
        if n == 1: return "up-small"
    return "up-small"

for i in range(1, 9):
    DATA[f"dim{i}-arrow-class"] = arrow_class(DATA[f"dim{i}-delta"])

# 读模板
html = TPL.read_text(encoding="utf-8")

# 1. 替换 data-field 占位
for key, val in DATA.items():
    html = html.replace(f'data-field="{key}">{html[html.find(f"data-field=\"{key}\">")+len(f"data-field=\"{key}\">"):html.find("<", html.find(f"data-field=\"{key}\">"))]}', f'data-field="{key}">{val}')
    # 上面 Python 太复杂，直接用更稳的方式

# 2. 更稳的替换：用正则匹配 data-field="X">原值</X>
def replace_field(html, key, val):
    # 匹配 data-field="key">原内容</...> 替换为新值（不闭合标签）
    pat = re.compile(rf'data-field="{re.escape(key)}">[^<]*')
    return pat.sub(f'data-field="{key}">{val}', html)

# 但 dim1-old/new 这种我们要在 dim-cell 内层替换，需要在 dim-cell 内的特定 span class
# 简化：直接硬编码替换
REPLACEMENTS = {
    "2026.04.14": DATA["date"],
    '<span class="ring-score" data-field="score-after">87</span>': f'<span class="ring-score" data-field="score-after">{DATA["score-after"]}</span>',
    '<span class="hero-skill-name" data-field="skill-name">审校降AI味</span>': f'<span class="hero-skill-name" data-field="skill-name">{DATA["skill-name"]}</span>',
    '<strong data-field="score-before">72</strong>': f'<strong data-field="score-before">{DATA["score-before"]}</strong>',
    '<strong>87</strong>': f'<strong>{DATA["score-after"]}</strong>',
    '<span style="color:#999;font-size:14px;" data-field="skill-id">huashu-proofreading</span>': f'<span style="color:#999;font-size:14px;" data-field="skill-id">{DATA["skill-id"]}</span>',
    '<span data-field="score-delta">+15</span>': f'<span data-field="score-delta">{DATA["score-delta"]}</span>',
    # top1
    '<div class="breakthrough-dim" data-field="top1-name">指令精度</div>': f'<div class="breakthrough-dim" data-field="top1-name">{DATA["top1-name"]}</div>',
    '<span class="breakthrough-from" data-field="top1-from">5</span>': f'<span class="breakthrough-from" data-field="top1-from">{DATA["top1-from"]}</span>',
    '<span class="breakthrough-to" data-field="top1-to">9</span>': f'<span class="breakthrough-to" data-field="top1-to">{DATA["top1-to"]}</span>',
    '<div class="breakthrough-pct" data-field="top1-pct">+80%</div>': f'<div class="breakthrough-pct" data-field="top1-pct">{DATA["top1-pct"]}</div>',
    '<div class="breakthrough-story" data-field="top1-story">从模糊指令到精确可执行，指令精度翻了将近一倍</div>': f'<div class="breakthrough-story" data-field="top1-story">{DATA["top1-story"]}</div>',
    # top2
    '<div class="breakthrough-dim" data-field="top2-name">工作流清晰度</div>': f'<div class="breakthrough-dim" data-field="top2-name">{DATA["top2-name"]}</div>',
    '<span class="breakthrough-from" data-field="top2-from">5</span>': f'<span class="breakthrough-from" data-field="top2-from">{DATA["top2-from"]}</span>',
    '<span class="breakthrough-to" data-field="top2-to">8</span>': f'<span class="breakthrough-to" data-field="top2-to">{DATA["top2-to"]}</span>',
    '<div class="breakthrough-pct" data-field="top2-pct">+60%</div>': f'<div class="breakthrough-pct" data-field="top2-pct">{DATA["top2-pct"]}</div>',
    '<div class="breakthrough-story" data-field="top2-story">线性可执行步骤，每步都有明确检查点</div>': f'<div class="breakthrough-story" data-field="top2-story">{DATA["top2-story"]}</div>',
    # improve
    '<div class="summary-item" data-field="improve-1">补充异常处理fallback路径，边界覆盖从4飙升到7</div>': f'<div class="summary-item" data-field="improve-1">{DATA["improve-1"]}</div>',
    '<div class="summary-item" data-field="improve-2">工作流重组为线性可执行步骤，每步可验证</div>': f'<div class="summary-item" data-field="improve-2">{DATA["improve-2"]}</div>',
    '<div class="summary-item" data-field="improve-3">测试prompt覆盖率从60%提升到95%，实测表现大幅进化</div>': f'<div class="summary-item" data-field="improve-3">{DATA["improve-3"]}</div>',
}

# 8 维度速览 (line 524-587) — 逐 dim 替换
DIM_NAMES = ["元数据", "工作流", "边界覆盖", "检查点", "指令精度", "资源整合", "整体架构", "实测表现"]
for i in range(1, 9):
    old = DATA[f"dim{i}-old"]
    new = DATA[f"dim{i}-new"]
    delta = DATA[f"dim{i}-delta"]
    # 每行硬编码格式: <div class="dim-name">NAME</div>...<span class="dim-old-score">OLD</span><span class="dim-score">NEW</span>...</span>...DELTA</span>
    # 用一个相对简单的替换策略
    REPLACEMENTS[f'<span class="dim-old-score">{old}</span>'] = f'<span class="dim-old-score">{old}</span>'  # placeholder, will replace by index below

# 直接编辑 dims-grid 段（line 523-588）
# 用 Python 抓 8 个 dim-cell 块
import re as _re
DIMS_PATTERN = _re.compile(
    r'(<div class="dim-cell[^"]*">\s*<div class="dim-name">)([^<]+)(</div>\s*<div class="dim-score-row">\s*<span class="dim-old-score">)(\d+)(</span>\s*<span class="dim-score">)(\d+)(</span>\s*</div>\s*<span class="dim-arrow )([^"]+)(">)(\+?\d*)(</span>\s*</div>)',
    _re.DOTALL
)

def repl_dim(m):
    name, old, new, arrow_class_orig, delta = m.group(2), m.group(4), m.group(6), m.group(8), m.group(10)
    # 找 dim i 索引（按 name 匹配）
    try:
        i = DIM_NAMES.index(name) + 1
    except ValueError:
        return m.group(0)
    new_old = DATA[f"dim{i}-old"]
    new_new = DATA[f"dim{i}-new"]
    new_delta = DATA[f"dim{i}-delta"]
    new_arrow_class = DATA[f"dim{i}-arrow-class"]
    return f'{m.group(1)}{name}{m.group(3)}{new_old}{m.group(5)}{new_new}{m.group(7)}{new_arrow_class}{m.group(9)}{new_delta}{m.group(11)}'

html = DIMS_PATTERN.sub(repl_dim, html)

# 替换简单占位
for old, new in REPLACEMENTS.items():
    if old != new:  # skip placeholders
        html = html.replace(old, new)

# 进度环 stroke-dashoffset
html = re.sub(
    r'(<circle cx="100" cy="100" r="85" class="ring-progress"[^/]*stroke-dasharray=")\d+(\.\d+)?("[^/]*stroke-dashoffset=")\d+(\.\d+)?(")',
    rf'\g<1>{CIRCUMFERENCE:.1f}\g<3>{PROGRESS_OFFSET:.1f}\g<5>',
    html
)

# 写
OUT_HTML.write_text(html, encoding="utf-8")
print(f"[OK] wrote {OUT_HTML}")
print(f"  size: {len(html)} chars")

# 跑 playwright screenshot
import shutil
NPX = shutil.which("npx") or r"C:\Users\38788\AppData\Local\mise\shims\npx.cmd"
cmd = [
    NPX, "playwright", "screenshot",
    f"file://{OUT_HTML}",
    str(OUT_PNG),
    "--viewport-size=960,1280",
    "--wait-for-timeout=2000"
]
print(f"\nrunning: {' '.join(cmd)}")
r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
print("STDOUT:", r.stdout[-500:] if r.stdout else "(empty)")
print("STDERR:", r.stderr[-500:] if r.stderr else "(empty)")
print(f"returncode: {r.returncode}")
print(f"PNG exists: {OUT_PNG.exists()}, size: {OUT_PNG.stat().st_size if OUT_PNG.exists() else 0}")
