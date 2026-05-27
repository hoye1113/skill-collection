# 组件文件规范

## 目录

1. [组件文件结构](#组件文件结构)
2. [主页加载方式](#主页加载方式)
3. [命名规范](#命名规范)
4. [常见组件模式](#常见组件模式)
5. [跨组件通信](#跨组件通信)

## 组件文件结构

每个组件是一个完整的HTML文件，包含自己的 CSS 和 JS：

```html
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<style>
/* 所有样式在 .cmp-{name} 命名空间下 */
.cmp-navbar { display: flex; align-items: center; padding: 0 20px; }
.cmp-navbar__logo { font-size: 18px; font-weight: bold; }
.cmp-navbar--active { background: #f0f0f0; }
</style>
</head>
<body>
<!-- HTML: data-component 属性标识组件 -->
<div class="cmp-navbar" data-component="navbar">
  <div class="cmp-navbar__logo">Logo</div>
  <button class="cmp-navbar__toggle">Menu</button>
</div>
<script>
(function(componentRoot) {
  'use strict';
  var toggle = componentRoot.querySelector('.cmp-navbar__toggle');
  toggle.addEventListener('click', function() {
    componentRoot.classList.toggle('cmp-navbar--active');
  });
})(document.querySelector('[data-component="navbar"]'));
</script>
</body>
</html>
```

关键要求：

- CSS 全部在 .cmp-{name} 命名空间下，不写全局选择器
- JS 用 IIFE 包裹，接收 componentRoot 参数
- 从 componentRoot 查询子元素，不用 document
- data-component 属性值与组件目录名一致

## 主页加载方式

主页面通过 fetch 获取组件HTML并注入DOM：

```html
<!-- index.html -->
<div id="component-navbar"></div>
<div id="component-modal-confirm"></div>

<script>
async function loadComponent(name, targetId) {
  var response = await fetch('components/' + name + '/component.html');
  var html = await response.text();
  var target = document.getElementById(targetId);
  target.innerHTML = html;

  // 提取并执行脚本
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

// 按顺序加载组件
loadComponent('navbar', 'component-navbar');
loadComponent('modal-confirm', 'component-modal-confirm');
</script>
```

加载顺序：按页面中占位 div 的顺序依次 fetch。如果组件之间有依赖关系，用 await 串行加载。无依赖的组件可以 Promise.all 并行加载。

## 命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 英文优先 | kebab-case | navbar, sidebar, tab-panel |
| 中文场景 | 拼音 kebab-case | shouye-hero, yonghu-card |
| 子元素 | __element | __title, __content, __input |
| 状态变体 | --modifier | --active, --hidden, --primary |

常用子元素后缀：\_\_title, \_\_content, \_\_input, \_\_footer, \_\_actions, \_\_icon, \_\_body, \_\_header

常用状态后缀：--active, --hidden, --primary, --large, --disabled, --visible, --selected

## 常见组件模式

### 导航栏

```html
<div class="cmp-navbar" data-component="navbar">
  <a class="cmp-navbar__logo" href="/">Logo</a>
  <nav class="cmp-navbar__menu">
    <a class="cmp-navbar__link" href="/about">About</a>
    <a class="cmp-navbar__link" href="/contact">Contact</a>
  </nav>
  <button class="cmp-navbar__toggle">Menu</button>
</div>
```

### 标签页

```html
<div class="cmp-tab-panel" data-component="tab-panel">
  <div class="cmp-tab-panel__tabs">
    <button class="cmp-tab-panel__tab cmp-tab-panel__tab--active" data-tab="tab1">Tab 1</button>
    <button class="cmp-tab-panel__tab" data-tab="tab2">Tab 2</button>
  </div>
  <div class="cmp-tab-panel__content" data-tab-content="tab1">Content 1</div>
  <div class="cmp-tab-panel__content cmp-tab-panel__content--hidden" data-tab-content="tab2">Content 2</div>
</div>
```

```javascript
(function(componentRoot) {
  'use strict';
  var tabs = componentRoot.querySelectorAll('.cmp-tab-panel__tab');
  var contents = componentRoot.querySelectorAll('.cmp-tab-panel__content');
  tabs.forEach(function(tab) {
    tab.addEventListener('click', function() {
      tabs.forEach(function(t) { t.classList.remove('cmp-tab-panel__tab--active'); });
      contents.forEach(function(c) { c.classList.add('cmp-tab-panel__content--hidden'); });
      tab.classList.add('cmp-tab-panel__tab--active');
      var target = componentRoot.querySelector('[data-tab-content="' + tab.dataset.tab + '"]');
      target.classList.remove('cmp-tab-panel__content--hidden');
    });
  });
})(document.querySelector('[data-component="tab-panel"]'));
```

### 弹窗

```html
<div class="cmp-modal cmp-modal--hidden" data-component="modal-confirm">
  <div class="cmp-modal__overlay"></div>
  <div class="cmp-modal__dialog">
    <div class="cmp-modal__header">
      <h3 class="cmp-modal__title">Confirm</h3>
      <button class="cmp-modal__close">&times;</button>
    </div>
    <div class="cmp-modal__body">
      <p>Are you sure?</p>
    </div>
    <div class="cmp-modal__footer">
      <button class="cmp-modal__btn">Cancel</button>
      <button class="cmp-modal__btn cmp-modal__btn--primary">OK</button>
    </div>
  </div>
</div>
```

### 卡片

```html
<div class="cmp-card" data-component="user-card">
  <img class="cmp-card__image" src="avatar.jpg" alt="User">
  <h3 class="cmp-card__title">Username</h3>
  <p class="cmp-card__description">User bio goes here.</p>
  <div class="cmp-card__actions">
    <button class="cmp-card__btn">Follow</button>
  </div>
</div>
```

### 表单区

```html
<div class="cmp-form" data-component="contact-form">
  <div class="cmp-form__field">
    <label class="cmp-form__label">Name</label>
    <input class="cmp-form__input" type="text" placeholder="Your name">
  </div>
  <div class="cmp-form__field">
    <label class="cmp-form__label">Email</label>
    <input class="cmp-form__input" type="email" placeholder="Your email">
  </div>
  <button class="cmp-form__submit">Submit</button>
</div>
```

### 侧边栏

```html
<div class="cmp-sidebar" data-component="sidebar">
  <button class="cmp-sidebar__toggle">Toggle</button>
  <ul class="cmp-sidebar__menu">
    <li class="cmp-sidebar__item"><a class="cmp-sidebar__link" href="#">Dashboard</a></li>
    <li class="cmp-sidebar__item"><a class="cmp-sidebar__link" href="#">Settings</a></li>
  </ul>
</div>
```

## 跨组件通信

组件之间不能直接操作对方DOM。用 CustomEvent 通信：

```javascript
// 组件 A (navbar) 发送事件
(function(componentRoot) {
  'use strict';
  var loginBtn = componentRoot.querySelector('.cmp-navbar__login-btn');
  loginBtn.addEventListener('click', function() {
    document.dispatchEvent(new CustomEvent('open-modal', {
      detail: { modalId: 'login' }
    }));
  });
})(document.querySelector('[data-component="navbar"]'));

// 组件 B (modal-login) 监听事件
(function(componentRoot) {
  'use strict';
  document.addEventListener('open-modal', function(e) {
    if (e.detail.modalId === 'login') {
      componentRoot.classList.remove('cmp-modal--hidden');
    }
  });
  var closeBtn = componentRoot.querySelector('.cmp-modal__close');
  closeBtn.addEventListener('click', function() {
    componentRoot.classList.add('cmp-modal--hidden');
  });
})(document.querySelector('[data-component="modal-login"]'));
```

通信原则：

- 发送方用 document.dispatchEvent 广播事件
- 接收方用 document.addEventListener 监听
- 事件 detail 中携带数据
- 不要在监听里操作发送方的DOM
