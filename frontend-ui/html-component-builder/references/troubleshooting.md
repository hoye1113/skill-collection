# Troubleshooting Guide

Debug common issues when building componentized HTML pages.

---

## Fetch-Related

### Symptom: fetch returns empty or CORS error
**Likely cause**: Opening HTML file directly via `file://` protocol instead of HTTP server.
**Diagnosis**: Check the browser address bar. If it starts with `file://`, that's the problem.
**Fix**: Run `node scripts/serve.js --dir .` and access via http://localhost:3000

### Symptom: Component loads but scripts don't execute
**Likely cause**: Dynamically inserted `<script>` tags don't auto-execute in the browser.
**Diagnosis**: Open DevTools console. No errors, but component behavior is missing.
**Fix**: The `loadComponent` function must extract inline script content and create new `<script>` elements:

```js
const script = document.createElement('script');
script.textContent = originalScript.textContent;
container.appendChild(script);
```

---

## CSS-Related

### Symptom: Component styles leak to other components
**Likely cause**: Selectors missing the `.cmp-{name}` prefix.
**Diagnosis**: Run `node scripts/validate.js --dir .` to scan for violations.
**Fix**: Add the component prefix to every selector. Example: `.btn` becomes `.cmp-navbar .btn`.

### Symptom: Styles work in standalone preview but break in assembled page
**Likely cause**: CSS specificity conflict. Another component's selector overrides yours.
**Diagnosis**: Inspect the element in DevTools. Check the "Styles" panel for struck-through rules.
**Fix**: Ensure both components use distinct `.cmp-{name}` prefixes. Remove any global selectors (`html`, `body`, `*`) from component CSS.

### Symptom: Component looks wrong after another component is modified
**Likely cause**: Cross-component CSS. One component's styles reference another component's class names.
**Diagnosis**: Search the modified component's CSS for class names belonging to the broken component.
**Fix**: Each component must only style its own `.cmp-{name}` classes. Use a CSS Grid layout component for cross-component spacing and arrangement.

---

## JavaScript-Related

### Symptom: Button click does nothing in component
**Likely cause**: `componentRoot` is null. The element with `data-component="{name}"` was not found.
**Diagnosis**: Add `console.log(componentRoot)` at the top of the IIFE. If it logs `null`, the selector is wrong.
**Fix**: Ensure the component's root element has `data-component="{name}"` matching the IIFE's `document.querySelector('[data-component="{name}"]')`.

### Symptom: Component A's action doesn't trigger Component B's behavior
**Likely cause**: Component A uses `document.querySelector` to reach into Component B's DOM directly.
**Diagnosis**: Search Component A's script for selectors targeting elements with `.cmp-{B}` classes.
**Fix**: Use `CustomEvent` for communication. Component A dispatches, Component B listens:

```js
// Component A
document.dispatchEvent(new CustomEvent('item-added', { detail: { id } }));

// Component B
document.addEventListener('item-added', (e) => { /* handle */ });
```

### Symptom: TypeError: Cannot read properties of null (reading 'addEventListener')
**Likely cause**: The IIFE runs before the component's DOM is injected into the page.
**Diagnosis**: Check the script tag position. If it's in `<head>` or before the HTML elements, that's the issue.
**Fix**: The `<script>` must be the last element inside the component's body, after all HTML elements.

---

## Layout-Related

### Symptom: Components overlap or stack incorrectly
**Likely cause**: Multiple components using `position: fixed` or `position: absolute`.
**Diagnosis**: Inspect overlapping elements in DevTools. Check computed `position` values.
**Fix**: Only modal/overlay components should use `fixed` positioning. Use `position: relative` for normal components. Use a CSS Grid layout component for page-level arrangement.

### Symptom: Sidebar/navbar takes unexpected space
**Likely cause**: Component has hardcoded width/height that conflicts with the grid layout.
**Diagnosis**: Check the component's CSS for fixed pixel values on the root element.
**Fix**: The layout component (page-layout) controls grid areas. Individual components should fill their container with `width: 100%` and `height: 100%`.

---

## Server-Related

### Symptom: Port already in use error
**Likely cause**: A previous server instance is still running, or another tool is using port 3000.
**Diagnosis**: Run `netstat -ano | findstr :3000` to see what's using the port.
**Fix**: Use `--port 8080` flag to pick a different port, or kill the existing process.

### Symptom: 404 for component that exists
**Likely cause**: Path mismatch between the fetch URL and the actual file location.
**Diagnosis**: Check the Network tab in DevTools for the exact URL being requested.
**Fix**: Match the fetch path to the directory structure. Shared components: `components/{name}/component.html`. Page-specific: `pages/{page}/components/{name}/component.html`.

---

## Quick Diagnostic Commands

```bash
# Check if server is running
curl http://localhost:3000/components/navbar/component.html

# Validate component conformance
node scripts/validate.js --dir .

# Test single component in isolation
# Open: http://localhost:3000/components/{name}/component.html
```
