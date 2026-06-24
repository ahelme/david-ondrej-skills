---
name: web-search
description: How the assistant accesses the web — search, fetch URLs/PDFs/YouTube/GitHub, and retrieve current information. Use whenever a task needs facts, docs, current/latest info, news, prices, versions, or content from a specific URL. Routes by the user's phrasing: web search, extensive web research, or deep research. Backed by an installed web-access package.
---

# Web Search

A web-access package is available. It supports zero-config search with fallback providers.

## CRITICAL: always pass `workflow: "none"`

Every `web_search` call MUST include `workflow: "none"`. This skips any interactive browser curator popup. No exceptions — single query or batched `queries`, always set `workflow: "none"`.

```js
web_search({ queries: ["query 1", "query 2"], workflow: "none" })
```

## Tools

- `web_search` — search the web; returns synthesized answers with citations. Can be called many times per turn. **Always pass `workflow: "none"`.**
- `code_search` — code-context search. Use for library/API/code lookups instead of generic `web_search`.
- `fetch_content` — fetch URL(s) → markdown; handles PDFs, YouTube, GitHub.
- `get_search_content` — big pages may be truncated in responses but stored in full; call this to pull the rest on demand so they don't blow context.

## fetch_content specifics

- **GitHub URLs are cloned, not scraped** — you get real files plus a local path to explore with read/shell tools. Private repos may require appropriate authenticated CLI access.
- **PDFs** → auto-extracted to markdown in a local downloads directory, readable in sections (text-only, no OCR).
- **YouTube/video** → transcripts and optional frame extraction when supported. Video frame extraction may require a configured API key and local media tools.

## Routing — match the user's phrasing

Always use the `web_search` tool. These counts are HARD MINIMUMS — count your queries before answering and do not stop short:

- **"web search"** → **at least 2** queries, varied keywords/angles, then synthesize.
- **"extensive web research"** → **at least 4** queries, totally different keywords and angles.
- **"deep research"** → **at least 8** queries, totally different keywords and angles, run across 2–3 successive batches, refining angles after each batch, to learn as much as possible about the topic.

A single batched `web_search` call counts each query in `queries[]` toward the total. If your first batch is under the minimum, fire another batch before synthesizing.
