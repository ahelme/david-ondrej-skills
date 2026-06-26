---
name: perplexity-deep-research
description: Run a Deep Research query with Perplexity sonar-deep-research via an OpenRouter-compatible provider using credentials supplied securely outside the repository. Builds a rigorous one-paragraph research prompt, submits it, and returns a cited markdown report. Use when a source-backed deep research run is needed. Expect 60-180s per run.
disable-model-invocation: true
---

# Perplexity Deep Research

Send a deep-research prompt to Perplexity **`perplexity/sonar-deep-research`** through an OpenRouter-compatible chat-completions provider. The model autonomously searches, reads, and synthesizes web sources, then returns a cited report.

## Expect 60-180 seconds

This is **not** a normal chat call. The model runs multi-step web research, so a single request can take **60-180 seconds** or longer. Wait for completion and use a long request timeout, such as 300 seconds. Do not retry or assume failure before roughly 3 minutes.

## Credentials

Use only credentials provided securely by the runtime environment, secrets manager, or approved local configuration. Do **not** commit API keys, tokens, auth headers, shell profile details, machine-specific setup notes, or credential names to this file.

## Model facts

- Model slug: `perplexity/sonar-deep-research`
- Large context window; text input/output.
- Pricing can change. Check the provider’s current pricing before running large jobs.

## Step 1 — Build the research prompt

Write **one self-contained paragraph** following the `research-prompt` skill:

- Lead with the single question and the decision or end use it informs.
- Embed all context needed to answer without back-and-forth.
- Number 3-6 inline sub-questions: `1`, `2`, `3`, etc.
- Keep one mission per prompt.
- State include/avoid constraints.
- Prefer primary sources.
- Treat forums and social media as weak signals only.
- Separate fact from inference and flag low-confidence claims.
- Per finding: include source link, specific claim, and one-line “why it matters.”
- End with: “Output everything into a single detailed markdown file.”

Save it to a temporary prompt file to avoid quoting issues:

```bash
cat > /tmp/dr_prompt.txt <<'EOF'
<your one-paragraph deep research prompt here>
EOF
```

## Step 2 — Run the request

Submit the prompt to your approved OpenRouter-compatible client or wrapper using the model slug:

```text
model: perplexity/sonar-deep-research
input: contents of /tmp/dr_prompt.txt
timeout: 300 seconds
```

Credentials must be injected by the approved runtime or client configuration, not hard-coded in the command or repository.

## Step 3 — Save the report and citations

After the response completes:

1. Extract the assistant message content as the markdown report.
2. Extract any citation URLs returned by the provider.
3. Save the report to a markdown file.
4. Append or list citation URLs beneath the report.
5. Optionally record approximate usage/cost if the provider returns it.
