# Evaluation Framework

Read this fully before starting a review. It defines the taxonomy used to classify findings and the checklist to run against each page/component.

## Calibrate to audience and usage frequency first

The same piece of copy can be legitimate on a first-time consumer screen and pure waste on an internal tool used daily by trained staff. Before applying the checklist below, confirm which profile the reviewed screen fits (see SKILL.md Step 1):

- **First-time/occasional users** → give explanatory text more benefit of the doubt; judge "obvious" against a first encounter with no prior context.
- **Repeat/trained internal users** → apply the checklist strictly. Static copy that only helps once is waste on the 200th visit. Prefer one-time onboarding hints or on-demand help over permanent on-screen explanation.

Note the assumed profile explicitly in the report so the user can see (and challenge) the calibration used.

## Core test for every piece of text on a page

For each string of copy, ask:

1. **If I deleted this, would the user be confused or stuck?** If no → candidate for deletion.
2. **Does this say something the user can already tell from position, icon, color, or a neighboring element?** If yes → redundant, candidate for deletion.
3. **Is this the 2nd/3rd way the same fact is being said on this screen?** If yes → duplicate, keep the strongest instance, cut the rest.
4. **Does this compete for attention with the actual primary action/data on the screen?** If yes → even if the text is "useful," it needs to be demoted (smaller, secondary, moved to expandable/tooltip) not necessarily deleted.
5. **Would a human product designer, under pressure to keep the screen “clean,” have written this?** If it reads like defensive over-explanation rather than a deliberate editorial choice → flag it.

Only text that survives #1 and isn't caught by #2/#3 earns a place at full visual weight.

**Calibrate all five questions against who actually reads this screen and how often.** "Obvious" is not an absolute property of a piece of text — it depends on the audience. A static description of what a page does is load-bearing the first time a new user sees it, and pure noise the fiftieth time a trained daily operator sees it. Before applying the checklist, know (or ask) whether the surface under review is an internal/repeat-use tool vs. a consumer-facing/first-time-use surface — see the audience-profile step in SKILL.md — and hold repeat-use tools to a visibly stricter bar.

## Redundancy pattern taxonomy

Use these pattern names in the report so findings are classified consistently.

**A. Triple-statement** — the same fact stated 3 different ways in close proximity (label + caption + tooltip, or heading + subheading + body sentence, all conveying the identical point). Common on stat cards, feature blocks, empty states.

**B. Obvious captioning** — a text explanation attached to something that's already self-evident from an icon, its position, or standard UI convention (e.g. a trash icon captioned "点击删除此项", a search bar captioned "在此输入以搜索").

**C. Section self-description** — a heading followed by a full sentence describing what the section is/does, when the section's contents make this immediately clear on inspection (e.g. "近期订单" followed by "此处显示您最近的订单记录，方便您查看订单状态").

**D. CTA padding** — justification or instructional text wrapped around a button/action that should just be a clear, well-labeled button (e.g. "点击下方按钮开始使用" above a button literally labeled "开始使用").

**E. Everywhere-tooltips/helper-text** — helper text, hints, or tooltips applied by default to most/all fields or elements rather than reserved for genuinely non-obvious ones. Dilutes the value of the ones that actually matter.

**F. Filler transition/connective copy** — sentences that exist only to bridge sections ("接下来，让我们看看...", "现在您已经了解了...") with no informational content.

**G. Restated data** — a number or state shown once as data (e.g. a badge, a progress bar) and then restated in a full sentence nearby ("当前进度：75%" next to a progress bar already showing 75% visually, followed by "您已完成四分之三的任务").

**H. Over-qualified labels** — a label padded with unnecessary qualifier words that don't add information ("您的个人专属账户余额" vs "余额").

**I. Color-as-restatement** — a status or severity that's already stated in text (and often already implied by position/icon) gets *additionally* re-asserted through a large block of accent/warning color (a whole panel painted red/yellow/purple) rather than a small, local indicator. When multiple such color blocks appear on one screen (e.g. a red blocker panel, a yellow gate-reason card, a purple safety notice, a green passed-state badge, all visible at once), color stops signaling difference and starts competing with the actual task the user needs to act on. Flag this pattern specifically when: (a) the same status is stated in plain text elsewhere on screen AND wrapped in a large colored container, or (b) 3+ distinct accent colors are visible in the same viewport with no single one clearly dominant. Recommendation is usually to keep color only on the smallest necessary element (a dot, a field border, a short label) and remove the full-panel fill, or to reserve strong color for the one thing that's actually actionable right now.

**I. Color-as-restatement** — a status or severity that's already conveyed by text/position/icon gets *additionally* re-asserted through a large block of accent color (a full red panel, a colored banner, a tinted card) applied by default. Unlike a targeted color cue on the one thing that changed, this pattern uses heavy color as a second, competing channel saying the same thing the copy already says. Common failure: several such color blocks stacked on one screen (e.g. a purple stage banner + red problem panel + yellow gate-reason card + green pass indicator, all visible at once), which flattens hierarchy — everything looks equally urgent, so nothing does. Look for this especially on state/status/error pages where every section independently decided it deserves its own color treatment.

## Visual density checklist (only apply if in scope for this review)

- **Competing focal points**: does the page have more than one element visually shouting for attention (multiple bold/colored/bordered blocks) with no clear primary?
- **Insufficient grouping/whitespace**: are unrelated pieces of information packed edge-to-edge with no breathing room, making it hard to tell where one logical group ends and another begins?
- **Flat type hierarchy**: does everything use similar font sizes/weights, forcing the user to read everything to find what matters, instead of 2-3 clear levels (primary data/action, secondary, tertiary/meta)?
- **Decoration outweighing content**: icons, borders, background fills, or dividers applied so heavily that they compete with the actual content rather than organizing it invisibly in the background?
- **No negative space around the primary action**: is the main CTA crowded by adjacent text/elements instead of having visual room to be the obvious next click?

## Severity/priority guide for ranking findings

1. **P0 — Actively competing with the primary action or key metric.** Text/elements that visually or cognitively compete with the one thing this screen exists for.
2. **P1 — Duplicate/triple-stated information.** Same fact said 2-3 times nearby; keep the best version, cut the rest.
3. **P2 — Low-value captioning/labels.** Obvious captions, over-qualified labels, everywhere-tooltips.
4. **P3 — Filler/connective copy.** Transition sentences, throat-clearing, that add no information but aren't actively harmful, just wasted space.

## What counts as legitimate, keep-as-is text

- Error messages and validation feedback (specific, actionable, shown at point of failure)
- Genuinely non-obvious instructions (an unusual gesture, a one-time-only clarification for a non-standard interaction)
- Legal/compliance/safety copy
- Empty states that guide a first-time user toward the one next action (as long as it's a single, tight sentence, not three)
- Confirmation copy for destructive/irreversible actions

Call a few of these out explicitly in the report as a sanity check — it shows the review is discriminating, not just anti-text.
