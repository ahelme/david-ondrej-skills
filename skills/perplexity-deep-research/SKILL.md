---
name: perplexity-deep-research
description: Run a Deep Research-style query via Perplexity on OpenRouter. Builds a rigorous one-paragraph research prompt, submits it through a configured OpenRouter API key, and returns a cited report saved to markdown. Use when a deep, source-backed research run is requested. Expect several minutes per run.
disable-model-invocation: true
---

# Perplexity Deep Research

Send a deep-research prompt to Perplexity **`perplexity/sonar-pro-search`** via OpenRouter. The model can search, read, and synthesize web sources, then return a cited report.

## Expect minutes, not seconds

This is not a normal chat call. Deep research can take several minutes because the model may perform multi-step web research. Use a long request timeout, and do not retry immediately unless the response body clearly failed.

**Success check — do not rely only on HTTP status.** Some providers may stream keepalive padding before returning the final JSON. Confirm success by parsing the body:

```bash
jq -e '.choices[0].message.content' /tmp/dr_result.json >/dev/null && echo OK || echo "FAIL (no usable JSON content)"
```

## Prerequisites

- Configure an OpenRouter API key in your shell environment before running the request.
- Use the OpenRouter chat completions API according to the provider documentation.
- Do not commit API keys, tokens, authorization headers, or local shell configuration files.

## Model facts

- Slug: `perplexity/sonar-pro-search`
- Input/output: text
- Context and pricing can change; check the provider model page before running high-volume research.

## Step 1 — Build the research prompt

Write one self-contained paragraph following a rigorous research-prompt structure:

- Lead with the single question and the decision or end use it informs.
- Embed all necessary context so no back-and-forth is required.
- Number 3-6 inline sub-questions: 1, 2, 3, etc.
- Keep one mission per prompt.
- State include/avoid constraints.
- Prefer primary sources; treat forums and social media as weak signals only.
- Separate fact from inference and flag low-confidence claims.
- For each finding, include: source link, specific claim, and one-line "why it matters".
- End with: "Output everything into a single detailed markdown file."

Save it to a temporary file; a heredoc avoids quoting issues:

```bash
cat > /tmp/dr_prompt.txt <<'EOF'
<your one-paragraph deep research prompt here>
EOF
```

## Step 2 — Run it

Use your configured OpenRouter API key and include the provider-required authentication in the request. Keep a long timeout.

```bash
curl -s --max-time 600 <openrouter-chat-completions-endpoint> \
  <provider-required-authentication-header> \
  -H "Content-Type: application/json" \
  -d "$(jq -n --rawfile p /tmp/dr_prompt.txt \
        '{model:"perplexity/sonar-pro-search", messages:[{role:"user",content:$p}]}')" \
  > /tmp/dr_result.json
```

## Step 3 — Read the report and sources

```bash
jq -r '.choices[0].message.content' /tmp/dr_result.json
jq -r '.choices[0].message.annotations[]?.url_citation?.url' /tmp/dr_result.json
jq -r '.usage.cost // empty' /tmp/dr_result.json
```

Save the report to a markdown file and list the citation URLs beneath it.
