# 从单体HTML迁移到组件化

适用场景：用户已有一个完整的单体HTML文件，需要拆分为组件化结构。

## 目录

1. [分析单体文件](#分析单体文件)
2. [规划拆分方案](#规划拆分方案)
3. [启动HTTP服务器](#启动HTTP服务器)
4. [逐个创建组件](#逐个创建组件)
5. [更新主页面](#更新主页面)
6. [验证完整性](#验证完整性)
7. [常见拆分模式](#常见拆分模式)
8. [共享状态处理](#共享状态处理)

## 分析单体文件

通读整个HTML文件，标记出独立的功能区域。判断标准：

- 该区域可以独立运行，不依赖其他区域的DOM结构
- 该区域有自己的交互逻辑（点击、切换、表单提交等）
- 该区域在页面上有明确的视觉边界

典型可拆分区域：导航栏、标签页、弹窗/对话框、卡片列表、表单区块、侧边栏、页脚、轮播图。

## 规划拆分方案

对每个识别出的区域，确定：

| 属性 | 选项 | 说明 |
|------|------|------|
| 组件名 | kebab-case | 如 navbar, tab-panel, modal-confirm |
| scope | shared / page | shared 被多个页面复用，page 仅当前页面 |
| 依赖 | 无 / 其他组件 | 如果有依赖，记录依赖关系 |

示例规划：

```
navbar        -> scope: shared,  无依赖
page-layout   -> scope: page,    无依赖（用CSS Grid编排）
tab-panel     -> scope: page,    无依赖
modal-confirm -> scope: shared,  监听 open-modal 事件
footer        -> scope: shared,  无依赖
```

## 启动HTTP服务器

迁移过程中需要HTTP环境。启动开发服务器：

```bash
node {SKILL_DIR}/scripts/serve.js --dir .
```

确认 http://localhost:3000 可访问。后续每步完成后都可刷新验证。

## 逐个创建组件

对规划中的每个区域，按以下流程操作：

### 1. 创建组件目录和文件

```
components/{name}/component.html
```

### 2. 复制HTML

从单体文件中把该区域的HTML结构复制到组件 body 中。确保：

- 根元素有 `data-component="{name}"` 属性
- 根元素有 `class="cmp-{name}"` 类名
- 所有子类名加上 `cmp-{name}__` 或 `cmp-{name}--` 前缀

### 3. 提取CSS

把单体文件中该区域相关的 CSS 规则提取到组件的 style 标签中。要求：

- 每条选择器都加上 .cmp-{name} 前缀
- 删除全局选择器（html, body, *）
- 把需要的全局变量移到 .cmp-{name} 作用域内

```css
/* 单体文件中的 */
.header { padding: 16px; }
.header .logo { font-size: 20px; }

/* 迁移后 */
.cmp-navbar { padding: 16px; }
.cmp-navbar__logo { font-size: 20px; }
```

### 4. 提取JS

把单体文件中该区域相关的 JS 逻辑提取到 IIFE 中：

```javascript
(function(componentRoot) {
  'use strict';
  // 用 componentRoot 替代 document
  var items = componentRoot.querySelectorAll('.cmp-tab-panel__tab');
  items.forEach(function(item) { /* ... */ });
})(document.querySelector('[data-component="tab-panel"]'));
```

转换要点：
- `document.querySelector` 替换为 `componentRoot.querySelector`
- `document.getElementById` 替换为 `componentRoot.querySelector('#id')`
- 全局变量改为 IIFE 内的局部变量
- 跨组件调用改为 CustomEvent

### 5. 验证组件独立预览

在浏览器中直接访问 `http://localhost:3000/components/{name}/component.html`，确认组件渲染正确、交互正常。

### 6. 重复上述步骤

对每个组件执行相同流程。建议按页面从上到下的顺序处理。

## 更新主页面

所有组件创建完成后，重写 index.html：

1. 删除原来的所有样式和脚本
2. 保留页面结构占位 div
3. 添加 fetch 加载逻辑

```html
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Page Title</title>
</head>
<body>
<div id="component-navbar"></div>
<div id="component-tab-panel"></div>
<div id="component-modal-confirm"></div>
<div id="component-footer"></div>

<script>
async function loadComponent(name, targetId) {
  var response = await fetch('components/' + name + '/component.html');
  var html = await response.text();
  var target = document.getElementById(targetId);
  target.innerHTML = html;

  var scripts = target.querySelectorAll('script');
  scripts.forEach(function(script) {
    var newScript = document.createElement('script');
    if (script.src) {
      newScript.src = script.src;
    } else {
      newScript.textContent = script.textContent;
    }
    document.body.appendChild(newScript);
    script.remove();
  });
}

(async function() {
  await loadComponent('navbar', 'component-navbar');
  await loadComponent('tab-panel', 'component-tab-panel');
  await loadComponent('modal-confirm', 'component-modal-confirm');
  await loadComponent('footer', 'component-footer');
})();
</script>
</body>
</html>
```

## 验证完整性

在 http://localhost:3000 访问主页面，逐项确认：

- [ ] 所有组件正确渲染在预期位置
- [ ] 导航栏交互正常（菜单展开/收起）
- [ ] 标签页切换正常
- [ ] 弹窗打开/关闭正常
- [ ] 表单提交/验证正常
- [ ] 跨组件事件正常（如点击导航栏按钮能打开弹窗）
- [ ] 每个组件独立访问也正常（直接打开组件URL）
- [ ] 修改某个组件不影响其他组件

## 常见拆分模式

| 单体结构 | 组件化后 | 说明 |
|----------|----------|------|
| `<div class="header">` | components/navbar/ | 导航栏 |
| `<div class="modal-backdrop">` | components/modal-{name}/ | 弹窗 |
| `<div class="tabs">` | components/tab-panel/ | 标签页 |
| `<div class="card-grid">` | components/card + components/card-grid | 卡片拆分列表和单卡 |
| `<div class="sidebar">` | components/sidebar/ | 侧边栏 |
| `<form>` | components/{name}-form/ | 表单 |
| `<div class="content">` + layout CSS | components/page-layout/ | 布局组件 |

## 共享状态处理

组件之间不能共享变量。处理跨组件状态的两种方式：

### data 属性

适合简单的状态传递：

```html
<!-- 组件 A 设置状态 -->
<div class="cmp-navbar" data-component="navbar" data-user-logged="true">
```

```javascript
// 组件 B 读取状态
var navbar = document.querySelector('[data-component="navbar"]');
var isLogged = navbar.dataset.userLogged === 'true';
```

### CustomEvent

适合事件驱动的状态变化：

```javascript
// 表单组件提交成功后通知弹窗
(function(componentRoot) {
  'use strict';
  var form = componentRoot.querySelector('.cmp-form__el');
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    document.dispatchEvent(new CustomEvent('show-toast', {
      detail: { message: 'Submit success' }
    }));
  });
})(document.querySelector('[data-component="contact-form"]'));

// Toast 组件监听
(function(componentRoot) {
  'use strict';
  document.addEventListener('show-toast', function(e) {
    var msg = componentRoot.querySelector('.cmp-toast__message');
    msg.textContent = e.detail.message;
    componentRoot.classList.add('cmp-toast--visible');
    setTimeout(function() {
      componentRoot.classList.remove('cmp-toast--visible');
    }, 3000);
  });
})(document.querySelector('[data-component="toast"]'));
```

### 迁移检查清单

- [ ] 每个单体区域已提取到独立的 component.html
- [ ] 所有 CSS 在 .cmp-{name} 命名空间下
- [ ] 所有 JS 在 IIFE 中，使用 componentRoot
- [ ] 跨组件事件用 CustomEvent
- [ ] 主页面 fetch 加载所有组件
- [ ] 所有交互正常工作（标签页、弹窗、表单等）
- [ ] 组件可独立修改，互不影响
