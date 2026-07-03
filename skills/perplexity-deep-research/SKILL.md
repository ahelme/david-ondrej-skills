---
name: perplexity-deep-research
description: Run a Deep Research-style query via Perplexity on OpenRouter, using a user-supplied API key configured outside the repository. Builds a rigorous one-paragraph research prompt, sends it to the model, and returns a cited markdown report. Use when a deep, source-backed research run is needed. Expect several minutes per run.
disable-model-invocation: true
---

# Perplexity Deep Research

Send a deep-research prompt to Perplexity via OpenRouter. The model can search, read, and synthesize web sources, then return a cited report.

## Expect several minutes, not seconds

This is not a normal chat call. Deep research requests may take several minutes. Use a long client timeout and do not retry prematurely.

**Success check — do not trust the HTTP status alone.** Some providers may keep a connection alive before returning the final JSON. Confirm success by parsing the response body, not only the status code:

```bash
jq -e '.choices[0].message.content' /tmp/dr_result.json >/dev/null && echo OK || echo "FAIL (padding only / no JSON)"
```

## API access

Configure your own OpenRouter API key securely outside this repository, following the provider documentation. Do not commit API keys, auth headers, local shell setup, cookies, or credentials.

## Model facts

- Example model slug: `perplexity/sonar-pro-search`
- Check current context window, pricing, and availability in the provider documentation before running.

## Step 1 — Build the research prompt

Write one self-contained paragraph:

- Lead with the single question and the decision or end use it informs.
- Embed all necessary context so no back-and-forth is needed.
- Number 3-6 inline sub-questions: 1, 2, 3, and so on.
- State include and avoid constraints.
- Prefer primary sources; treat forums and social posts as weak signals only.
- Separate fact from inference and flag low-confidence claims.
- Per finding: include source link, specific claim, and one-line “why it matters.”
- End with: “Output everything into a single detailed markdown file.”

Save it to a file. A heredoc avoids quoting issues:

```bash
cat > /tmp/dr_prompt.txt <<'EOF'
<your one-paragraph deep research prompt here>
EOF
```

## Step 2 — Run the request

Use your preferred OpenRouter-compatible client or script with credentials supplied securely at runtime. Send a chat completion request with:

- model: `perplexity/sonar-pro-search`
- one user message containing the contents of `/tmp/dr_prompt.txt`
- a long timeout appropriate for multi-minute research runs
- output saved to `/tmp/dr_result.json`

Do not place credentials or auth headers in tracked files.

## Step 3 — Read the report and sources

```bash
jq -r '.choices[0].message.content' /tmp/dr_result.json                          # the report
jq -r '.choices[0].message.annotations[].url_citation.url' /tmp/dr_result.json   # source URLs, if provided
jq -r '.usage.cost' /tmp/dr_result.json                                           # cost, if provided
```

Save the report to a markdown file and list citation URLs beneath it.
