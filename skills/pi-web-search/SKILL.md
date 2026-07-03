---
name: pi-web-search
description: Web access workflow for Pi Agents — search, fetch URLs/PDFs/YouTube/GitHub. Use whenever a task needs current info, docs, news, prices, or content from a specific URL.
---

# Web Search

Use the available web access tools for search, code lookups, and fetching content from URLs.

## CRITICAL: always pass `workflow: "none"`

Every `web_search` call MUST include `workflow: "none"`. This skips any interactive browser or curator popup. No exceptions — single query or batched `queries`, always set `workflow: "none"`.

```js
web_search({ queries: ["query 1", "query 2"], workflow: "none" })
```

## Tools

- `web_search` — search the web; returns synthesized answers with citations. Can be called many times per turn. **Always pass `workflow: "none"`.**
- `code_search` — use for library/API/code lookups instead of generic `web_search`.
- `fetch_content` — fetch URL(s) to markdown; handles PDFs, YouTube, and GitHub URLs when supported by the environment.
- `get_search_content` — large pages may be truncated in responses but stored in full; call this to retrieve remaining content on demand.

## fetch_content specifics

- **GitHub URLs** — use for repository or source-code lookups when supported by the environment.
- **PDFs** — may be extracted to markdown for section-by-section reading when supported by the environment.
- **YouTube/video** — may provide transcripts or frame extraction when supported by the environment and required dependencies are configured.

## Routing — match the user's phrasing

Always use the `web_search` tool. These counts are HARD MINIMUMS — count your queries before answering and do not stop short:

- **"web search"** → **at least 2** queries, varied keywords/angles, then synthesize.
- **"extensive web research"** → **at least 4** queries, totally different keywords and angles.
- **"deep research"** → **at least 8** queries, totally different keywords and angles, run across 2–3 successive batches, refining angles after each batch to learn as much as possible about the topic.

A single batched `web_search` call counts each query in `queries[]` toward the total. If your first batch is under the minimum, fire another batch before synthesizing.
