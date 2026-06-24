---
name: run-deep-swe
description: Score an AI model on the DeepSWE coding-agent benchmark via the OpenRouter API. Use when the user wants an independent, reproducible coding-agent eval — "run DeepSWE", "benchmark this model on DeepSWE", "score model X on the coding benchmark", "test a model via OpenRouter on DeepSWE", or to verify vendor-reported coding scores. Covers setup, OpenRouter wiring for mini-swe-agent, single-task / subset / full 113-task runs, and leaderboard submission.
---

# Run DeepSWE via OpenRouter

DeepSWE is a Harbor-compatible coding-agent benchmark. It runs via **Pier** driving **mini-swe-agent**. Any model reachable through OpenRouter can be scored.

## Prerequisites — state-check first

```bash
which uv git docker || echo "MISSING: install uv, git, docker"
docker info >/dev/null 2>&1 || echo "MISSING: Docker daemon not running"
echo "OPENROUTER_API_KEY set? ${OPENROUTER_API_KEY:+YES}"
```

**Docker must be running** for local sandboxed task execution, unless you intentionally configure a supported cloud/sandbox backend.

Set `OPENROUTER_API_KEY` in your local shell or secret manager before running. Never commit, print, or paste API keys into tracked files.

## Setup

```bash
git clone https://github.com/datacurve-ai/deep-swe && cd deep-swe
uv tool install datacurve-pier
# or: uv tool install git+https://github.com/datacurve-ai/pier
```

Run all `pier` commands from inside the cloned `deep-swe/` repository, using relative `-p tasks/...` paths as appropriate for the installed version.

## OpenRouter wiring

mini-swe-agent can use OpenRouter with the `OPENROUTER_API_KEY` environment variable and an OpenRouter model slug such as `vendor/model`.

**Route A — native OpenRouter class:**
```bash
pier run -p deep-swe/tasks --agent mini-swe-agent \
  --model vendor/model --model-class openrouter
```

**Route B — LiteLLM provider prefix fallback:**
```bash
pier run -p deep-swe/tasks --agent mini-swe-agent \
  --model openrouter/vendor/model
```

Notes:
- Use the exact OpenRouter model slug from the public model listing.
- Free or zero-cost models can cause cost-tracking errors. If needed, set `export MSWEA_COST_TRACKING=ignore_errors`.
- Flag spelling can vary by version. Confirm with `pier run --help` and the relevant mini-swe-agent help output.

## Smoke test first: 1 task

Always validate end-to-end wiring on a single task before spending tokens on a larger run:

```bash
# list available task ids:
ls deep-swe/tasks

pier run -p deep-swe/tasks/<task-id> --agent mini-swe-agent \
  --model vendor/model --model-class openrouter
```

Pass criteria: the run completes, the model returns actions rather than auth/format errors, and a score or trajectory is emitted.

If it returns HTTP 401, check the API key. If it reports a missing provider or unmapped model, check the slug or switch routes.

## Subset run: deterministic sample

```bash
pier run -p deep-swe/tasks --agent mini-swe-agent \
  --model vendor/model --model-class openrouter \
  --n-tasks 10 --sample-seed 0
```

## Full corpus

Confirm cost and runtime with the user before launching a full benchmark run.

```bash
pier run -p deep-swe/tasks --agent mini-swe-agent \
  --model vendor/model --model-class openrouter
```

If you use a cloud/sandbox backend, configure it separately and follow its public documentation.

## Output & reporting

- Trials are written under the benchmark run output directory, commonly in a `jobs/` tree.
- Inspect results with Pier commands such as `pier view`, `pier analyze`, or `pier critique`, depending on the installed version.
- Report the exact command used, pass/fail, score, and any blockers.
- For official leaderboard submission, follow the public DeepSWE/DataCurve submission instructions.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| HTTP 401 | Bad or missing API key | Re-export `OPENROUTER_API_KEY` locally; do not expose the key in logs or commits |
| "LLM Provider NOT provided" | Missing provider/route information | Use `openrouter/...` or `--model-class openrouter` |
| "model isn't mapped" or cost error | Unknown cost metadata for model | `export MSWEA_COST_TRACKING=ignore_errors` |
| Unknown flag | Version drift | Check `pier run --help` and relevant agent help output |
