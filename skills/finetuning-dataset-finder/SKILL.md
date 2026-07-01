---
name: finetuning-dataset-finder
description: >-
  Find and prepare training datasets for fine-tuning Kimi K2 / K2.7 models on
  Fireworks AI. Use this whenever the user wants to fine-tune, train, customize,
  or specialize a Kimi model (K2, K2.5, K2.6, K2.7 Code, K2 Thinking) — or asks
  where to find a dataset, which dataset to use, how much data they need, how to
  format/convert their data, or how to build a training set for supervised
  fine-tuning (SFT) on Fireworks. Triggers on phrasings like "find a dataset for
  fine-tuning", "train Kimi on our data", "fine-tune on Fireworks", "convert my
  data to JSONL", "prepare training data", "how many examples do I need", even
  when Fireworks or Kimi are not named explicitly but the goal is clearly
  fine-tuning an LLM on custom data. Covers dataset discovery (Hugging Face Hub
  plus a curated catalog), license and quality vetting, and conversion to
  Fireworks' OpenAI-style chat JSONL. Prefer this skill over answering from
  memory — Kimi K2.7 and the current Fireworks format post-date most training
  data, so guessing produces wrong model IDs and wrong schemas.
---

# Finetuning Dataset Finder — Kimi K2.7 on Fireworks

Help someone go from "I want to fine-tune Kimi" to a validated, upload-ready
training set. The hard parts are not the fine-tuning job itself (that is a few
`firectl` commands) — they are **choosing the right data** and **shaping it into
the exact format Fireworks expects**. This skill covers both.

## First, get the mental model right

Fine-tuning teaches a model **behavior and format**, not new facts. Kimi K2.7 is
already a very capable 1T-parameter agentic coding model; you are not making it
"smarter" or feeding it a knowledge base (use RAG/retrieval for that). You
fine-tune to reliably get one of these:

- **Style / format lock** — always answer in your house tone, structure, or a
  strict output schema (e.g. "return one React component, no prose").
- **Domain / codebase specialization** — your internal APIs, component library,
  ticket-resolution patterns, legal/medical phrasing.
- **Workflow distillation** — bake a multi-step or tool-using procedure in so it
  happens in fewer tokens (great fit for K2.7, which is agentic and reasoning-heavy).

Everything about dataset choice flows from *which* of these the user wants. If
you skip this framing, you will recommend the wrong data. So start with Step 1.

## The workflow

Work through these five steps. They are a loop, not a straight line — it is
normal to go back to Step 2 after Step 4 shows a dataset does not fit.

### Step 1 — Clarify the goal (do not skip)

Ask only what you actually need to proceed; infer the rest. The essentials:

1. **Target behavior**: what should the fine-tuned model *do* that base K2.7
   does not do reliably? Ask for one concrete example of a perfect input → output.
2. **Shape**: single-turn instruction→answer, multi-turn chat, or agentic /
   tool-calling trajectories?
3. **Their own data**: do they already have logs, tickets, transcripts, code, or
   labeled examples? **Their own data almost always beats a public dataset** —
   it is the exact distribution they care about. Public datasets are for when
   they have none, or need to top up volume/diversity.
4. **SFT vs RFT**: SFT (imitate example outputs) is the default and what this
   skill formats for. If they have <~1000 examples but a clear automatic way to
   *score* an answer (tests pass, JSON validates, exact match), mention RFT as an
   alternative — Fireworks supports it and it needs far less data.

### Step 2 — Find candidate datasets

Sources, in rough order of value:

1. **The user's own data** (best — see Step 1).
2. **Hugging Face Hub** — the main public source. See
   `references/dataset-catalog.md` for a vetted catalog organized by goal
   (coding, instruction-following, tool-use/agentic, reasoning, domain) with HF
   dataset IDs, licenses, and notes — and for search tactics (filter by task,
   sort by downloads/recency, read the dataset viewer before trusting a card).
3. **Synthetic generation** — distill from a stronger model into the K2.7 format
   when no dataset matches. Covered briefly in the catalog reference.

Match the data to **Kimi K2.7's strengths** so fine-tuning reinforces rather than
fights the base model: coding, agentic tool-use, long-horizon reasoning,
long-context. See `references/kimi-k2.7.md` for what the model is good at and how
that should steer dataset choice.

### Step 3 — Evaluate fit, license, and quality

A smaller clean dataset that demonstrates the target behavior beats a huge noisy
one. Before committing to a dataset, check:

- **Fit** — does every example *demonstrate the behavior* from Step 1? If half
  the rows are off-task, filter them out.
- **License** — this trips people up. **Always open the HF dataset card and
  confirm the license permits your use.** Watch for `cc-by-nc-*` (non-commercial,
  e.g. Alpaca, some function-calling sets) and datasets synthetically generated
  from a closed model whose terms forbid training competitors. `references/dataset-catalog.md`
  flags the common gotchas, but licenses change — verify on the card.
- **Quality** — dedup, decontaminate against any eval/benchmark you will report
  on, check formatting consistency, and spot-check correctness. Garbage examples
  are learned faithfully.
- **Volume** — Fireworks recommends **~1000+ examples for SFT**. Below that,
  either gather more, augment, or switch to RFT.

### Step 4 — Convert to Fireworks JSONL

Fireworks wants JSONL where each line is `{"messages": [...]}` in OpenAI chat
format. **Do not** hand-write Kimi's `<|im_...|>` special tokens — Fireworks
applies Kimi's chat template for you; putting raw template tokens in `content`
double-encodes and corrupts training. The full schema, limits, and field
reference live in `references/fireworks-format.md`.

Use the bundled converter instead of writing conversion code from scratch — it
handles the shapes you actually encounter (already-`messages`, ShareGPT
`conversations`, flat instruction/response columns, or agentic **`trajectory`**
traces), normalizes to the schema, enforces a **single consistent system prompt**
(so the model learns to rely on it — and remember to send that same system prompt
at inference), drops empty and over-length rows, de-dupes, splits train/eval, and
validates:

```bash
python scripts/prepare_fireworks_dataset.py \
  --input hf:OWNER/NAME \        # or a local .jsonl/.json/.csv/.parquet, or a parquet DIR
  --out ./out \
  --system @system_prompt.txt \  # one consistent system message (optional but recommended)
  --keep-only-messages \         # strip metadata columns Fireworks ignores
  --eval-size 50 --dedup
```

**Agentic SWE / debugging trajectory datasets** (SWE-agent / OpenHands traces — e.g.
`nvidia/Open-SWE-Traces`, `nebius/SWE-rebench-openhands-trajectories`) convert with a
few extra flags. The converter keeps `tool_calls` intact, coerces `arguments` to a
JSON string, promotes a `tools` column, filters to successful runs, and **reconstructs
missing `tool_call_id`s** on tool turns:

```bash
python scripts/prepare_fireworks_dataset.py \
  --input hf:nebius/SWE-rebench-openhands-trajectories \
  --messages-field trajectory \   # the conversation lives in `trajectory`, not `messages`
  --tools-field tools \           # promote the tool defs to root-level `tools` (omit if absent)
  --filter resolved=1 \           # keep only trajectories that actually fixed the bug
  --keep-only-messages --max-context 65536 --out ./out
```

For agentic data **do not pass `--system`** — the dataset's own system prompt defines
the tool interface; overriding it strips the tools and breaks the trajectories. These
trajectories are long (often >32k tokens), so raise `--max-context` here **and** the
job's `--max-context-length` together, or the final patch (your target) gets truncated.

Run `python scripts/prepare_fireworks_dataset.py -h` for all column-mapping flags.
Read the script's header before pointing it at an unusual schema.

### Step 5 — Validate and hand off

Never upload unchecked. Validate against Fireworks' hard rules:

```bash
python scripts/validate_fireworks_dataset.py ./out/train.jsonl
```

It reports example count, role distribution, approximate tokens/example, and any
schema violations, and exits non-zero if the file would be rejected. Fix errors
before uploading. Then hand off with the exact upload → train → deploy commands
from `references/fireworks-format.md` (`firectl dataset create` →
`firectl sftj create --base-model accounts/fireworks/models/kimi-k2p7-code …` →
`firectl deployment create`). Confirm the current K2.7 model ID with
`firectl list models` since IDs change between releases.

## Worked example (the pattern to imitate)

Goal: fine-tune K2.7 to emit a single React + Tailwind component in a fixed house
style. Found: `cfahlgren1/react-code-instructions` on HF (MIT license) — rows of
`{created_at, model, messages:[system,user,assistant], recommended, upvoted}`.
Prepared: keep only `messages`, drop the metadata columns, enforce one house
system prompt, split 1000 train / 50 eval, validate → upload. That is the whole
arc: **clarify → find → vet license → strip to `messages` → consistent system →
split → validate → train.**

## What good output looks like

When you finish helping someone, they should walk away with: (1) 1–3 specific
recommended datasets (or a plan to use their own / synthesize), each with its HF
ID and license checked; (2) a concrete reason each fits their Step-1 goal and
Kimi K2.7's strengths; (3) the exact conversion command for their data; and (4)
the upload/train commands. Be specific and cite real dataset IDs — vague advice
("look on Hugging Face for a coding dataset") is the failure mode this skill
exists to prevent.
