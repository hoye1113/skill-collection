---
name: content-density-review
description: >-
  Reviews frontend product pages (framework-agnostic: HTML/CSS/JS,
  React/Vue/JSX/WXML) for text-overload and visual-density problems common
  in AI-assisted "vibe coding" — redundant, explanatory copy stuffed next to
  every UI element, over-labeling, duplicate messaging, cluttered layouts
  that bury key info/actions under low-value text. Produces a structured
  Markdown audit report (no code changes): every offending spot with
  file/line refs, why it hurts usability, and a concrete rewrite/removal fix,
  ranked by priority. Trigger when asked to review, audit, check, diagnose,
  or clean up a page/product for being "文字太多/信息过载/啰嗦/冗余/杂乱/不够
  克制/AI 味" (too much text, info overload, verbose, redundant, cluttered,
  lacks restraint, "AI-generated feel"), or for a content/visual density
  pass before a page is done. Also use when the user asks if a page's copy
  is too dense, or wants a checklist for minimal UI copy going forward.
---

# Content Density Review

A systematic audit skill for catching a specific, extremely common AI-vibe-coding failure mode: **explanation-itis** — the compulsion to caption, describe, and re-explain every element on a page, until the signal (key info, key actions) drowns in noise (redundant labels, restated obvious facts, decorative micro-copy).

This skill produces a **review report only** — it never edits the user's code. The user reads the report, decides what to act on, and applies fixes themselves (or asks Claude to fix specific items afterward in a separate pass).

## Why this happens (context for the review, not to explain to the user unless asked)

Models trained to be "helpful" default to explaining. In UI copy this manifests as:
- A stat next to a label next to a caption next to a tooltip, all saying the same thing three different ways
- Every icon getting an adjacent text description even when the icon + position already convey meaning
- Section headers followed by a full sentence "explaining" what the section is, when the section's contents already make it obvious
- CTAs padded with justification text ("点击下方按钮即可开始体验") instead of just being a clear button
- Empty states, tooltips, and helper text applied everywhere by default rather than where genuinely needed
- No editorial pass to *remove* — the model adds, never subtracts

The fix isn't "write better sentences" — it's **information hierarchy discipline**: decide what's actually signal, delete or demote everything else.

## When to reach for supporting references

- `references/principles.md` — the evaluation framework (signal/noise, hierarchy, redundancy patterns, visual density heuristics). Read this before starting any review to calibrate judgment — it has the concrete checklist and the redundancy-pattern taxonomy used to classify findings.
- `references/report-template.md` — the exact Markdown structure the final report must follow. Read this before writing the report.

Read both reference files at the start of a review; they're short and the review quality depends on applying the checklist consistently rather than improvising ad hoc.

## Workflow

### Step 1: Scope the review

Confirm (or infer from context) which files/pages are in scope. This skill is framework-agnostic — it works on raw HTML/CSS/JS, React/JSX/TSX, Vue, WXML, or any markup-producing source. If the user points at a project directory, use `bash_tool`/`view` to enumerate the page/component files (skip node_modules, dist, build, vendor, lock files).

If scope is ambiguous (e.g. a large multi-page project with no page named), ask which page(s)/route(s) to prioritize rather than reviewing everything blindly — but if the user says "review the project" and it's a small project (roughly <15 page/component files), just review all of it.

**Also establish the audience/usage-frequency profile before judging what's "obvious."** What counts as redundant is not absolute — it depends on who's looking at the screen and how often:
- **First-time / occasional consumer users** (marketing pages, onboarding, checkout, public-facing tools) — some explanatory text earns its place because the user genuinely hasn't seen the UI before. Judge "obviousness" against a first encounter.
- **Trained, repeat, internal/operator users** (admin panels, ops dashboards, internal tooling used daily by staff) — the bar for what's "obvious" should be much stricter. Static explanatory copy that only helps on the first visit is waste on visit #200. Favor cutting aggressively and pushing explanation into one-time onboarding or on-demand help rather than permanent on-screen real estate.

If this isn't clear from context, ask the user (or infer from the project: an internal `/admin`, `/ops`, `/management` path used by staff behaves very differently from a public marketing site). State the assumption in the report's 总体结论/summary so the user can see which calibration was applied.

**Also establish the audience/usage profile before judging anything as "obvious" or "not obvious."** The same piece of text can be load-bearing for a first-time user and pure noise for someone who opens the page 50 times a day. Infer this from context (project name/domain, route naming like "admin"/"运营"/"dashboard" vs a public marketing/onboarding page, or ask directly if genuinely unclear) and note it explicitly at the top of the report:
- **Internal/operator tools used repeatedly** (admin consoles, ops dashboards, back-office workflows): default to a strict threshold — static explanations of what a page/section "is" or "does" earn their place once at most (e.g. a one-time onboarding tip), not persistently on every visit. Trained repeat users need state + action, not orientation.
- **Consumer-facing / first-time-use surfaces** (onboarding flows, public marketing pages, first-run empty states): a bit more explanatory copy is legitimate, since the reader may genuinely be seeing it for the first time — but the redundancy patterns (saying the same thing 2-3 times, obvious captioning) still apply regardless of audience.

This judgment call should be stated once, briefly, near the top of the report (e.g. "本审查对象是内部运营工作台，使用者为每日重复操作的客服人员，因此采用较严格的阈值") so the user can see the reasoning behind severity calls rather than wondering why some borderline text got flagged.

### Step 2: Read the actual rendered structure, not just the code

Don't just grep for text strings — understand what's rendered where. For each page/component in scope:
1. Read the source file(s) fully (HTML/JSX template + associated copy strings, including any i18n/locale JSON files if copy is externalized)
2. Mentally (or actually, via a quick static render if useful) reconstruct the page's information hierarchy: what's the ONE primary thing this screen wants the user to see/do? What's secondary? What's tertiary?
3. Note every piece of text on the page and classify it: is it load-bearing (user needs it to understand or act), or decorative/redundant (restates something already obvious from position, icon, or a nearby element)?

### Step 3: Apply the checklist from `references/principles.md`

Go section by section (or component by component) and flag concrete instances against the redundancy-pattern taxonomy. Every finding must be **specific and located** — file path + line number (or component name), not a vague "the page has too much text."

### Step 4: Write the report using `references/report-template.md`

Key rules for the report:
- **Every finding is concrete**: quote (or closely paraphrase) the actual offending copy, give its file:line location, name which redundancy pattern it matches, and explain the specific harm (what does it bury, what attention does it steal from the real CTA/data).
- **Every finding gets a recommendation**: what to cut entirely, what to shorten to, or — if genuinely necessary — how to demote it (smaller type, secondary color, moved to a tooltip/expandable instead of inline).
- **Prioritize.** Not everything is equally bad. Rank findings so the user can fix the worst offenders first (typically: things competing with the primary CTA > duplicate statements of the same fact > low-value micro-labels > everything else).
- **Show a "keep as-is" list too, briefly** — a couple of examples of text that IS earning its place (e.g. an error message, a genuinely non-obvious instruction). This calibrates the report as a targeted audit rather than "delete all text," and helps the user trust the judgment calls elsewhere.
- **Close with a short set of page-level or systemic observations** if a pattern repeats across many spots (e.g. "every stat card has a redundant caption — consider a shared component rule: stat cards show number + one-word label only").

### Step 5: Deliver

This report is a standalone written deliverable meant to be read/shared, not a quick inline answer — create it as a Markdown file via `create_file`, save to `/mnt/user-data/outputs/`, and present it with `present_files`. Do not paste the full report inline in chat; give a short (2-4 sentence) summary of the overall verdict and top 2-3 issues in the chat message, and let the file carry the detail.

If the project is large enough that findings would be very long, it's fine to produce one report file covering multiple pages, organized by page/component sections — don't split into many small files unless the user asks.

## What NOT to do

- Don't rewrite the user's code in this skill. If they want fixes applied, that's a separate, explicit follow-up request.
- Don't produce a generic "reduce text" lecture — every claim in the report must point at a specific location in their actual files.
- Don't flag things that are genuinely necessary (legal/compliance text, safety warnings, form validation errors, first-time onboarding hints that appear once) — the goal is cutting *redundant* and *decorative* text, not all text everywhere. Use judgment; over-flagging necessary text erodes trust in the report.
- Don't limit yourself only to copy if the user has confirmed visual-density scope (spacing, type hierarchy, whitespace) is in scope for this review — check `references/principles.md` for that checklist too.
