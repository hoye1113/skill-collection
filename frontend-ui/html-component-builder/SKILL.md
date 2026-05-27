---
name: "html-component-builder"
description: "组件化 HTML 页面构建。为 UI 设计师和前端开发者提供模块化的 HTML 开发规范，将单体 HTML 拆分为独立组件（导航栏、标签页、弹窗、卡片、表单、侧边栏、轮播图、下拉菜单、面包屑、页脚、表格等），每个组件独立 HTML 文件，自带 CSS 命名空间隔离（.cmp-{name}）和 JS 作用域（IIFE 闭包）。通过 fetch 动态加载，组件间 CustomEvent 通信。支持 HTTP 服务器开发和单组件独立预览。Actions: create page, build HTML, component, UI 设计转 HTML, 设计稿还原，UI 切图，组件化，创建页面，模块化，搭建页面，UI 原型，html prototype, modular HTML, scoped CSS, 拆分组件，serve, preview, 页面搭建，页面交互，前端页面开发，快速原型。Triggers: '创建页面', '做个 HTML', '组件化 HTML', '拆分组件', '页面组件化', '拆页面', '写个页面', 'UI 页面开发', '设计稿还原', 'UI 切图', 'UI 转 HTML', '前端还原', '改一个按钮不影响其他', 'CSS 样式冲突', '样式互相影响', '交付前端', '给前端用', '前端接手 HTML', '模块化页面', '做网页', 'html 页面', '前端页面开发', '做个页面', '快速做网页'."
---

IRON LAW: 每个组件文件必须可独立在HTTP下预览。组件间零耦合：CSS用.cmp-{name}命名空间隔离，JS用IIFE闭包。永远不要把多个组件的功能写进一个文件。

## 为什么用 HTTP + fetch 而不是 build/split 脚本

- 组件文件保持独立、可直接预览
- 主页面通过 fetch 动态加载，天然模块化
- 避免复杂的 CSS/JS 拆分和重组逻辑
- 文件即组件，所见即所得

## Skill 边界

**本 skill 负责**: 组件化 HTML 结构规范、HTTP 开发服务器、组件加载模式（fetch）、合规性校验

**本 skill 不负责**: 具体 UI/UX 设计、构建打包（无 build/bundle）、部署上线、React/Vue 组件转换、设计稿转 HTML

## 工作流程

- [ ] Step 1: 页面架构规划 [REQUIRED]
  **输入**: 用户需求描述或设计稿
  **输出**: 组件清单（名称 + scope + 依赖关系）
  **验证**: 拆分合理，命名符合规范
  - [ ] 识别页面所有独立功能区域
  - [ ] 拆分为组件，确定scope（shared/page-specific）
  - [ ] 确定组件命名（kebab-case英文或拼音）
  - [ ] 确定组件在页面中的排列顺序
- [ ] Step 2: 项目初始化 [BLOCKING]
  **输入**: 组件清单
  **输出**: 目录结构 + components.json
  **验证**: 目录和配置文件存在
  - [ ] 创建目录结构（手写或用 init.js 生成脚手架）
  - [ ] 创建 components.json 配置文件
- [ ] Step 3: 编写组件 [REQUIRED]
  **输入**: 组件规格（名称、元素结构、交互需求）
  **输出**: component.html 文件
  **验证**: validate.js 通过
  - [ ] 每个组件创建为独立的 component.html 文件
  - [ ] 参考 references/component-standard.md
  - [ ] 运行 `node {SKILL_DIR}/scripts/validate.js --dir .` 检查合规性
- [ ] Step 3.5: 变更确认 [CONFIRMATION]
  - 覆盖已有组件文件? -> 提示用户确认
  - 修改 components.json 配置? -> 提示用户确认
  - 删除或重命名组件? -> 必须确认
  - 普通新增组件? -> 无需确认
- [ ] Step 4: 注册组件到 components.json
  **输入**: 新组件信息（名称、scope）
  **输出**: 更新的 components.json
  **验证**: 配置与实际文件匹配
  - [ ] 将新组件添加到对应页面的 components 数组
  - [ ] scope: "shared" 或 scope: "page"
- [ ] Step 5: 编写页面入口 index.html
  **输入**: 组件列表 + 布局需求
  **输出**: index.html
  **验证**: fetch 加载无报错
  - [ ] 使用 fetch 加载组件
  - [ ] 处理加载顺序和错误
- [ ] Step 6: 启动开发服务器
  **输入**: 项目目录
  **输出**: HTTP 服务器运行中
  **验证**: http://localhost:3000 可访问
  - [ ] 运行 `node {SKILL_DIR}/scripts/serve.js --dir .`
  - [ ] 确认 http://localhost:3000 可访问
  - [ ] 检查组件是否正确加载
- [ ] Step 7: 交付检查 [REQUIRED]

## 目录结构

```
project/
  index.html                    # 页面入口，fetch加载组件
  components.json               # 组件注册配置
  components/
    navbar/
      component.html            # 导航栏组件（独立可预览）
    tab-panel/
      component.html            # 标签页组件
    modal-confirm/
      component.html            # 确认弹窗组件
    page-layout/
      component.html            # 页面布局组件（CSS Grid）
```

## components.json 格式

```json
{
  "pages": {
    "index": {
      "entry": "index.html",
      "components": [
        { "name": "navbar", "scope": "shared" },
        { "name": "tab-panel", "scope": "page" },
        { "name": "modal-confirm", "scope": "shared" }
      ]
    }
  }
}
```

## 编写组件检查清单（每个组件完成后逐条自问）

### CSS 检查
- 所有 class 是否都带了 `.cmp-{name}` 前缀?（基础类、子元素 `__`、状态变体 `--`）
- 有没有使用全局选择器（html、body、*）?
- 有没有在 `.cmp-{name}` 作用域外定义 CSS 变量?
- 有没有过高权重的选择器（如 div.cmp-x > span）?

### JavaScript 检查
- JS 是否用 `(function(componentRoot) { ... })(document.querySelector('[data-component="xxx"]'))` 包裹?
- 有没有用 `document.querySelector` 而不是 `componentRoot.querySelector` 来查询元素?
- 跨组件交互是否通过 CustomEvent 实现，而非直接操作对方 DOM?
- `data-component` 属性值是否与 IIFE 中查询的选择器一致?

### 结构检查
- 根元素是否有 `data-component="{name}"` 属性?
- 根元素是否有 `class="cmp-{name}"`?
- 文件是否能独立在 HTTP 下预览?

## 布局规则

用专门的布局组件（如 page-layout）通过 CSS Grid 编排页面级布局。布局组件负责组件之间的间距、排列、响应式断点。

## 按需加载 Reference

| 场景 | 加载文件 | 何时触发 |
|------|---------|---------|
| 创建全新组件 | references/component-standard.md | Step 3 开始时 |
| 从单体 HTML 拆分 | references/migration-guide.md | Step 1 规划拆分方案时 |
| 遇到报错或异常 | references/troubleshooting.md | fetch报错、样式异常、脚本不执行时 |

## 交付检查

逐项确认，每项都必须可验证：

- [ ] 每个组件文件在 HTTP 下直接打开能正常渲染
- [ ] 主页面 fetch 加载所有组件无报错
- [ ] 运行 validate.js 全部通过（零报错）
- [ ] components.json 与实际文件完全匹配（无遗漏、无多余）
- [ ] 所有样式在 .cmp-{name}* 命名空间下
- [ ] 所有 JS 在 IIFE 中，无全局变量
- [ ] 无残留的单体代码
- [ ] 中文文本标签完整
- [ ] 组件命名一致
- [ ] 修改任一组件不影响其他组件

## 反模式

以下是常见错误，出现任何一项都需要纠正：

- 把所有交互（tab、modal、dropdown）写在一个文件
- 用 document.querySelector 而不是 componentRoot.querySelector
- 不用 .cmp- 前缀的class名
- 组件之间直接操作对方DOM
- 用绝对定位覆盖其他组件的布局
- 在 fetch 回调里用 document.getElementById 跨组件操作
- 把所有组件的CSS写在一个 style 标签里
