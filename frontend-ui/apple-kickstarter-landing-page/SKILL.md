---
name: apple-kickstarter-landing-page
description: Use when creating a standalone landing page for a hardware/product Kickstarter campaign that should follow Apple's product page design language — clean typography, generous whitespace, scroll-reveal animations, alternating feature blocks, and a structured hero → story → features → specs → pledge tiers flow.
---

# Apple-Style Kickstarter Landing Page

## Overview

Create a Kickstarter campaign landing page that follows Apple's product introduction page design language. The result is a self-contained HTML artifact — not production UI — ideal for concept previews, investor decks, and early backer campaigns.

**Core principle:** Use design tokens, not ad-hoc styles. Let the design system drive every decision.

## Quick Reference

| Aspect | Choice |
|---|---|
| **Colors** | Background `#fff` / `#f5f5f7` / `#1d1d1f`; Text `#1d1d1f` / `#86868b`; Accent `#0071e3` |
| **Typography** | `system-ui, -apple-system, sans-serif`; Hero `clamp(40px,6vw,64px) 700`; Body `17px` |
| **Spacing** | Base `20px`; Sections `120px` / `160px` vertical padding |
| **Radius** | `6px` / `12px` / `18px` / `9999px` pill |
| **Motion** | Scroll reveal `opacity 0→1 + translateY 40→0`, `0.7s ease-out`; sticky nav hide/show on scroll |

## Module Architecture

Build page in this order using these reusable block types:

```
├── Sticky Nav          (fixed top, auto-hide on scroll down)
├── Hero                (tagline + product mockup + dual CTA + scroll indicator)
├── Story / Pain Points (alternating 2-col: text left, visual right)
├── Core Highlights     (3-column icon grid)
├── Feature × N         (alternating 2-col: text|visual / visual|text)
├── Benchmark Table     (scrollable data table with test notes)
├── Transition Section  (dark bg pivot block, optional)
├── Scenario Cards      (3-col responsive card grid)
├── Tech Specs          (dark bg 2-col key-value specs)
├── Pledge Tiers ×3     (pricing cards, middle card = featured/highlight)
├── Final CTA           (centered hero-style close)
└── Footer              (minimal copyright bar)
```

## Workflow

1. **Extract product data** from user's spec (table/spreadsheet → structured sections)
2. **Map to modules** above — every product detail fits one block
3. **Write design tokens** into `:root` CSS variables (never inline exceptions)
4. **Populate each section** keeping content hierarchy: tag → heading → sub → body
5. **Apply scroll-reveal** using `.reveal` class + `reveal-delay-1/2/3` on staggered elements
6. **Verify** no console errors, responsive at all breakpoints, scroll animation fires correctly

## Reusable CSS Components

### Scroll Reveal

```css
.reveal {
    opacity: 0;
    transform: translateY(40px);
    transition: opacity 0.7s var(--ease-out), transform 0.7s var(--ease-out);
}
.reveal.visible {
    opacity: 1;
    transform: translateY(0);
}
```

JS activator (IntersectionObserver):

```js
const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
```

### Alternating Feature Block

```html
<section class="section">                       <!-- or section-light -->
    <div class="container feature-block">        <!-- or feature-block reverse -->
        <div class="feature-content reveal">     <!-- text side -->
            <p class="feature-tag">Label</p>
            <h3>Heading</h3>
            <p>Body copy...</p>
        </div>
        <div class="feature-visual reveal reveal-delay-1">  <!-- image side -->
            <img src="..." alt="..." />  <!-- or placeholder div -->
        </div>
    </div>
</section>
```

### Pledge Tier Card

```html
<div class="tier-card featured reveal reveal-delay-2">
    <div class="tier-badge">Most Popular</div>
    <div class="tier-price">$XX</div>
    <div class="tier-amount">Super Early · Very Limited</div>
    <h4>Reward Name</h4>
    <ul><li>Feature</li></ul>
    <a href="#" class="btn btn-primary">Select</a>
</div>
```

## Template File

The reusable base template is at:
**`skills/apple-kickstarter-landing-page/template.html`**

To use it:
1. Copy `template.html` to `canvas/Your Campaign Name.html`
2. Search-replace all `[EDIT: ...]` markers with your product content
3. Replace placeholder images (`.ph` divs) with actual product photos
4. Adjust pledge pricing and tier names
5. Open in browser to verify

## Common Mistakes

| Mistake | Fix |
|---|---|
| Mixing `px` and `clamp()` for font sizes | Use `clamp()` for all responsive text |
| Forgetting `.reveal` on new sections | Every section needs it for scroll animation |
| Missing `reveal-delay` sequencing | Add `-1/2/3` to stagger sibling reveals |
| Image break ratio | Keep `aspect-ratio` on `.ph` / `<img>` containers |
| Inline colors instead of CSS vars | Use `var(--accent)`, `var(--bg-light)` etc. |
| Mobile overflow | Test at 375px width; `.bench-table-wrap` needs `overflow-x: auto` |
