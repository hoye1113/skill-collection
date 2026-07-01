# Worked 范例：AI 影视生态地形图（验过图）

照搬改 frame 即可。frame 只写「这个行业的地形怎么布」（价值之河 + 各环节地貌 + 瓶颈隘口 + 价值捕获宝藏 + 地名）；风格、瓶颈红牌/价值捕获金牌/继刚测量员由 `gen_illustration.py` 内置，不用写。

## 研究 → 地形（AI 影视）

deep research 出的结构（双头抽租）：价值链 算力→基础视频模型→工具→内容制作(创作者)→分发平台→观众；瓶颈 = 基础视频模型（产能/算力闸，烧钱）；价值捕获 = 算力(英伟达) + 分发平台(抖音/快手) 两端；错位 = 创作者中游创造价值却守薄田、钱被两端抽走。

译成地形：上游算力雪山 + 大坝（宝藏）；中游绿谷创作者村庄 + 内容田（薄田）；上游峡谷隘口 = 瓶颈；下游平台港镇 + 宝藏；外海 = 观众。

### mold -a（动物森友会，默认）

```bash
python3 assets/gen_illustration.py --mold a \
  --frame "A value-river flows left-to-right through an island valley. LEFT/upstream: tall compute mountains with a big wooden dam-tollgate (a major profit pool). MIDDLE: a lush green valley where small creator-villagers grow content crops by the river — value is created here but the villagers are modest. A narrow rocky canyon pass sits just upstream of the middle (a scarce, smoking foundry-hut zone = the base-model layer) constricting the river. RIGHT/downstream: a busy harbor town with a tollgate where boats pay before reaching the open sea (the audience) — another profit pool. So the bottleneck pass is the canyon; the value-capture treasure piles are the upstream dam and the downstream harbor. A few wooden place labels: 算力 / 创作者 / 平台 / 观众." \
  --out /tmp/ljg_map_aifilm_terrain.png
```

出图：算力雪山+坝（金宝藏=价值捕获）、中游创作者村庄+内容田、峡谷红牌「瓶颈」、平台港镇+宝藏、外海观众、继刚作测量员立山头举地图俯瞰。验过：~/Downloads/AI影视-生态地形图.png（整卡）、scratchpad/terrain_aifilm_a.png（图）。

### mold -c（pixel + cyber-hacker）

同一地形描述，`--mold c` 即出暗黑霓虹像素版地形（峡谷隘口=故障收窄、宝藏=发光数据堆、河=数据流）。frame 不变，风格交给 mold。

## 写 frame 的复用要点

- **先有研究**：瓶颈在哪环、价值捕获在哪环、错位还是重合——先 deep research 定准，再译地形。
- **价值之河**：上游→下游一条河/路；各环节 = 地貌（山/谷/港/海）。
- **瓶颈 → 收窄隘口/坝**；**价值捕获 → 宝藏堆**；错位就让宝藏远离创造它的薄田。
- **地名 ≤6、每个 2-6 字**（关键环节名）。别多——生图会糊。
- **精确件不进图**：base rate 数字、三大问题写进卡的文字块（{{BASE_RATES}}/{{Q1-3}}），不堆进地形图。
- 生图后**必 Read 验**：瓶颈/价值捕获标清、地名不糊、继刚认得出；不行调 frame 重生。
