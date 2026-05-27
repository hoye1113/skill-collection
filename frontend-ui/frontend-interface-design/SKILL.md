---
name: frontend-interface-design
description: "Build, refine, and review production-grade frontend interfaces inside real products and codebases. Use when the request is to implement, polish, or audit pages/components that must fit an existing app, repository, or design system, or when a new page/component is being added to a production frontend rather than delivered as a standalone concept artifact. Covers accessibility, semantics, focus behavior, motion quality, responsive behavior, content handling, and interaction design in HTML/CSS/React/Next/Vue code. Triggers: improve this UI, polish this component, add this page to our app, review UI code, accessibility audit, design polish in repo, dashboard UX fix. Not for slide decks, exploratory prototypes, click-through mockups, animation demos, dataviz showcases, or standalone HTML concept pages."
---

IRON LAW: DO NOT TRADE USABILITY FOR STYLE, AND DO NOT FLATTEN STYLE INTO GENERIC SAFETY. THE OUTPUT MUST FEEL INTENTIONALLY DESIGNED AND STILL PASS BASIC ACCESSIBILITY, SEMANTICS, AND INTERACTION CHECKS.

# Frontend Interface Design

Create or review frontend interfaces with two equal goals:

1. Ship visually distinctive UI that avoids generic AI aesthetics.
2. Preserve production-grade interaction quality across accessibility, semantics, copy, performance, and motion.

## Route Guard

Before continuing, verify the request belongs to product UI work:

- If the task is to implement, polish, or audit UI inside an existing app, repo, or design system, continue here.
- If the task is a slide deck, click-through prototype, motion demo, dataviz showcase, or standalone concept artifact, stop and use `web-visual-artifacts`.

## Parameters

Use these when the caller or user already implied them:

- `--mode build|refine|review`
- `--tone minimal|editorial|playful|luxury|brutalist|industrial|retro|custom`
- `--platform html|react|next|vue|other`
- `--strictness standard|high`

## Workflow

Copy this checklist and check off items as you complete them:

```md
- [ ] Step 1: Detect route
  - [ ] 1.1 New UI build -> continue with design + implementation
  - [ ] 1.2 Existing UI polish/refactor -> inspect current files first
  - [ ] 1.3 Review/audit request -> switch to findings-first review mode
- [ ] Step 2: Lock constraints
  - [ ] 2.1 Identify framework, audience, device constraints, and page purpose
  - [ ] 2.2 Decide whether the task optimizes for shipping, restyling, or auditing
  - [ ] 2.3 Choose one strong visual direction before coding
- [ ] Step 3: Execute the route
  - [ ] 3.1 Build/refine: implement the chosen direction with real working code
  - [ ] 3.2 Review: inspect files against `references/ui-guidelines-checklist.md`
- [ ] Step 4: Run quality pass
  - [ ] 4.1 Check semantics, accessibility, focus, motion, and content handling
  - [ ] 4.2 Check typography, states, responsiveness, and empty/long-content cases
  - [ ] 4.3 Confirm the design is still memorable rather than generic
- [ ] Step 5: Deliver
  - [ ] 5.1 For code changes, summarize the design direction and material UX choices
  - [ ] 5.2 For reviews, report findings by file and line with no preamble
```

## Step 1: Detect Route

Ask:

- Is the user asking to build something new?
- Is the user asking to improve an existing UI?
- Is the user asking for a review, audit, or standards check?

If the task is a review, do not drift into implementation advice before you have identified concrete issues.

## Step 2: Lock Constraints

Before changing code, establish:

- Product goal and audience
- Framework and styling constraints
- Desktop/mobile expectations
- Whether accessibility or performance requirements are explicit
- The one design choice the user should remember

Choose a bold but coherent direction. Refined minimalism and expressive maximalism both work. Indecisive design does not.

## Step 3A: Build or Refine

Implement working code that is:

- visually distinctive
- cohesive and context-specific
- production-grade
- responsive on desktop and mobile

Core design rules:

- Typography: choose fonts with character; avoid default safe stacks and overused AI-default pairings.
- Color: commit to a clear palette with CSS variables; avoid washed-out neutrality and purple-gradient defaults.
- Layout: use composition intentionally; asymmetry, overlap, density, or restraint should look deliberate.
- Motion: favor a few meaningful transitions and reveals; respect reduced motion.
- Background: create atmosphere with gradients, textures, patterns, or depth instead of flat emptiness.

Core engineering rules:

- Use semantic elements for their real jobs.
- Preserve visible focus states.
- Avoid interaction patterns that break keyboard or touch use.
- Handle long text, empty states, and loading states intentionally.
- Prefer compositor-friendly animation properties.

When touching existing code, preserve the product's established visual language unless the user asked for a redesign.

## Step 3B: Review Mode

Load `references/ui-guidelines-checklist.md` and inspect the target files.

Check at minimum:

- accessibility and semantics
- focus visibility
- forms and validation UX
- motion and reduced-motion handling
- typography and punctuation details
- content overflow and empty states
- images and layout stability
- performance traps
- navigation, URL state, and destructive actions
- touch behavior, dark mode, locale safety, hydration safety

Output rules:

- Group by file.
- Use `file:line` format when possible.
- State issue plus location.
- Keep it terse.
- No summary before findings.
- If a file passes, mark it with `pass`.

## Anti-Patterns to Avoid

- Generic AI-safe layouts with no point of view
- Styling a broken interaction instead of fixing the interaction
- Replacing semantic HTML with clickable `div` or `span`
- Removing outlines without a focus-visible replacement
- Using `transition: all`
- Shipping icon-only controls without accessible names
- Ignoring reduced motion
- Hardcoding dates, numbers, or locale-sensitive formatting
- Treating placeholders as labels
- Reviewing only visuals while missing accessibility or state bugs

## Pre-Delivery Checklist

- [ ] Visual direction is obvious within one screen
- [ ] No default/generic font stack or template-like color palette slipped in
- [ ] Interactive elements have visible focus and sensible hover/active states
- [ ] Buttons, links, forms, and headings use semantic structure
- [ ] Motion has a reduced-motion fallback
- [ ] Long content, empty content, and loading content are handled cleanly
- [ ] Images have dimensions and appropriate loading behavior
- [ ] Output matches the route: implementation summary for build/refine, findings-first report for review

## Reference Map

- `references/ui-guidelines-checklist.md` for the detailed review checklist and output format
