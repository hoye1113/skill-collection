# Information Acquisition Priority

Use this reference when writing capability statements, tool usage guidance, or any workflow that involves fetching external information.

## Default Priority Stack

When an agent needs to acquire information, use this exact priority order:

1. **`web_fetch`** — for known authoritative URLs
2. **`uv`-driven scripts** — for batch scraping, structured extraction, or reproducible processing
3. **`web_search`** — for discovering candidate sources, completing entry points, or locating pages
4. **`browser`** — for rendered pages, interactive pages, or as a fallback when `web_fetch` fails

## Rules by Tool

### `web_fetch` (Primary)

- Use when the URL is known and authoritative
- Treat as the default main path for content acquisition
- Do not use `web_search` first when you already know the target URL

### `uv`-driven Scripts (Secondary)

- Use when you need batch operations, structured data extraction, or reproducible processing
- Prefer Python scripts executed via `uv` over ad-hoc prompt-driven scraping
- These are conditional capabilities; the script exists but depends on runtime availability

### `web_search` (Discovery Only)

- Use **only** for finding candidate sources, not for final content acquisition
- Do not treat search result summaries as ground truth
- Never write conclusions based solely on search result snippets
- If `web_search` depends on an external provider or skill, treat it as a fragile/discovery interface, not a default main path

### `browser` (Fallback)

- Use only for pages that require rendering or interaction
- Use as a fallback when `web_fetch` fails
- Do **not** make the browser the default primary acquisition path

## Ground Truth Requirement

Before writing any conclusion:

1. Confirm candidate sources (via search or links)
2. Read the actual source content (via `web_fetch` or `uv` scripts)
3. Base conclusions on the source content, not on search summaries

**Forbidden pattern**: Search → read result summary → write conclusion without fetching the actual page.

## Examples

### Correct

- "Known address → `web_fetch` first, batch extraction → `uv`, search → discovery only."
- "Final conclusions fall back to `web_fetch` results, `uv` artifacts, or local readable files."

### Incorrect

- "Use `web_search` to get the article content."
- "Browser is the default way to read web pages."
- "Search results are sufficient for the final answer."

## Writing Requirement

When you declare information acquisition capabilities in `TOOLS.md`:

- State the priority stack explicitly
- Classify `web_search` as discovery-only
- Classify browser as conditional/render-fallback
- Require that final conclusions cite retrievable sources
