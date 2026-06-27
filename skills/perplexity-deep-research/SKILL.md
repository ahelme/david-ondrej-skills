---
name: perplexity-deep-research
description: Run a Deep Research query via Perplexity "sonar-deep-research" on OpenRouter. Builds a rigorous one-paragraph research prompt, sends it to the model, and returns a cited report saved to markdown. Use when a deep, source-backed research run is requested. Expect several minutes per run.
disable-model-invocation: true
---

# Perplexity Deep Research

Send a deep-research prompt to Perplexity **`perplexity/sonar-deep-research`** via OpenRouter. The model autonomously searches, reads, and synthesizes web sources, then returns a cited report.

## Expect several minutes, not seconds

This is not a normal chat call. The model runs multi-step web research, so a single request can take several minutes. Use a long request timeout and avoid retrying before the request has had enough time to complete.

**Success check — do not trust HTTP status alone.** Some providers may return an HTTP success status before the final streamed response is complete. Confirm success by parsing the response body, not only the status code:

```bash
jq -e '.choices[0].message.content' /tmp/dr_result.json >/dev/null && echo OK || echo "FAIL (no report content)"
```

## Credentials

Use your own OpenRouter API key, stored securely outside the repository, such as in an environment variable or secrets manager. Do not hardcode keys, tokens, cookies, or authorization headers in this file.

Endpoint: `POST https://openrouter.ai/api/v1/chat/completions`

## Model facts

- Slug: `perplexity/sonar-deep-research`
- Context and pricing can change; check the provider documentation before running large jobs.

## Step 1 — Build the research prompt

Write one self-contained paragraph following a strong research-prompt structure:

- Lead with the single question and the decision or end use it informs.
- Embed all relevant context so no back-and-forth is required.
- Number 3-6 inline sub-questions: 1, 2, 3, and so on.
- Keep one mission per prompt.
- State include and avoid constraints.
- Prefer primary sources; treat forums and social posts as weak signals only.
- Separate fact from inference and flag low-confidence claims.
- For each finding, include: source link, specific claim, and one-line "why it matters".
- End with: "Output everything into a single detailed markdown file."

Save the prompt to a temporary file. A heredoc avoids quoting issues:

```bash
cat > /tmp/dr_prompt.txt <<'EOF'
<your one-paragraph deep research prompt here>
EOF
```

## Step 2 — Run it

Use your preferred OpenRouter client or HTTP tool, configured with your own secure credentials, and send a request like this payload:

```bash
jq -n --rawfile p /tmp/dr_prompt.txt \
  '{model:"perplexity/sonar-deep-research", messages:[{role:"user",content:$p}]}' \
  > /tmp/dr_request.json
```

Submit `/tmp/dr_request.json` to the OpenRouter chat completions endpoint using your secure credential handling. Save the JSON response to `/tmp/dr_result.json`.

## Step 3 — Read the report and sources

```bash
jq -r '.choices[0].message.content' /tmp/dr_result.json                        # the report
jq -r '.choices[0].message.annotations[].url_citation.url' /tmp/dr_result.json # source URLs, if present
jq -r '.usage.cost' /tmp/dr_result.json                                        # reported cost, if present
```

Save the report to a markdown file and list the citation URLs beneath it.
