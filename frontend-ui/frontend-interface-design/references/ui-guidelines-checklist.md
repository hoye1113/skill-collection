# UI Guidelines Checklist

Load this file when reviewing UI code or when doing a final quality pass on a newly built interface.

## Accessibility

- Icon-only buttons need `aria-label`.
- Form controls need a `<label>` or `aria-label`.
- Interactive non-native controls need keyboard handlers when native elements are not possible.
- Use `<button>` for actions and `<a>` or framework link components for navigation.
- Images need `alt`, or `alt=""` if decorative.
- Decorative icons need `aria-hidden="true"`.
- Async status updates need `aria-live="polite"` when appropriate.
- Prefer semantic HTML before adding ARIA.
- Keep heading order hierarchical.
- Add a skip link for main content when the page structure warrants it.
- Use `scroll-margin-top` on heading anchors when sticky headers exist.

## Focus States

- Interactive elements need visible focus styles.
- Never remove outlines without a replacement.
- Prefer `:focus-visible` over `:focus`.
- Use `:focus-within` for compound controls when helpful.

## Forms

- Inputs need meaningful `name`, `type`, and often `autocomplete`.
- Use correct `inputmode` when relevant.
- Do not block paste.
- Make labels clickable.
- Disable spellcheck on emails, usernames, and code-like inputs when appropriate.
- Keep checkbox and radio hit targets unified.
- Keep submit enabled until request start, then show progress.
- Show inline errors near fields and focus the first invalid field on submit.
- Use placeholders as examples, not as labels.
- Warn before navigation when unsaved changes would be lost.

## Animation

- Honor `prefers-reduced-motion`.
- Animate `transform` and `opacity` where possible.
- Never use `transition: all`.
- Set sensible `transform-origin`.
- Keep animations interruptible.

## Typography & Copy

- Use `…` instead of `...`.
- Prefer curly quotes when the product style supports them.
- Use non-breaking spaces where line breaks would look wrong.
- Use tabular numerals for tables and numeric comparisons.
- Balance or pretty-wrap headings when available.
- Write in active voice.
- Use specific button labels.
- Error messages should include the next step or fix.

## Content Handling

- Handle long text with truncation, wrapping, or clamping as appropriate.
- Add `min-w-0` to flex children that need truncation.
- Handle empty states explicitly.
- Consider short, average, and very long user-generated content.

## Images

- Set explicit `width` and `height` on images when applicable.
- Lazy-load below-the-fold images.
- Prioritize above-the-fold critical images.

## Performance

- Virtualize very large lists.
- Avoid layout reads during render.
- Batch DOM reads and writes.
- Keep controlled inputs cheap.
- Preconnect to critical asset domains when justified.
- Preload critical fonts and use `font-display: swap`.

## Navigation & State

- Reflect meaningful UI state in the URL when appropriate.
- Use real links for navigation to preserve browser behavior.
- Require confirmation or undo for destructive actions.

## Touch & Layout

- Set `touch-action: manipulation` where it improves tap latency.
- Set tap highlight color intentionally.
- Contain overscroll in modals, drawers, and sheets.
- Avoid stray horizontal scrollbars.
- Prefer CSS layout systems over JS measurement.
- Consider safe-area insets on full-bleed mobile layouts.

## Theming, Locale, and Hydration

- Set `color-scheme: dark` for dark themes when appropriate.
- Match browser theme color to the page.
- Format dates and numbers with `Intl`.
- Do not infer language from IP.
- Protect code tokens and brand names from auto-translation when needed.
- Avoid hydration mismatches for time- and locale-dependent rendering.

## Review Output Format

Use this format:

```text
## src/Button.tsx

src/Button.tsx:42 - icon button missing aria-label
src/Button.tsx:18 - input lacks label

## src/Card.tsx

pass
```
