# Fireworks AI — exact SFT dataset format & workflow

Source of truth: docs.fireworks.ai/fine-tuning. Fireworks is Moonshot's launch
partner for K2.5/K2.6/K2.7, so Kimi models are first-class for fine-tuning.
Managed **supervised fine-tuning (SFT) is LoRA-based** (parameter-efficient) —
Kimi **K2.6** and **K2.7 Code** both show "Fine-tuning: Supported (LoRA)" on their
Fireworks model pages. **DPO** and **reinforcement fine-tuning (RFT)** are also
available; true *full-parameter* tuning is currently only via the full-parameter
RFT **private preview** (Kimi K2.5). Note: **serverless LoRA is not supported** —
a fine-tuned Kimi is served on a **dedicated deployment**.

## Dataset file

- **Format**: JSONL — one JSON object per line, extension `.jsonl`.
- **Each line** is a chat sample: `{"messages": [ ... ]}` in OpenAI-compatible
  chat-completion format. No CSV, no wrapping array.

Minimal example (one line):

```json
{"messages":[{"role":"system","content":"You are a senior React engineer. Return ONE self-contained App.tsx component, no prose."},{"role":"user","content":"A pricing section with three cards, pro plan highlighted, mobile stacking."},{"role":"assistant","content":"export default function App(){ /* ...tsx... */ }"}]}
```

### Message fields

| Field | Where | Meaning |
|---|---|---|
| `role` | every message | `system` \| `user` \| `assistant` \| `tool` |
| `content` | every message | string, **or** a list of text parts `[{"type":"text","text":"…"}]`. Image parts are accepted **only in the separate vision-SFT flow** (base64 data-URIs, not raw URLs) — not in text SFT. |
| `weight` | optional, per message | `0` or `1`. `0` = include the turn as context but **exclude it from the loss** (don't train on it). Use to mask user/system turns or bad assistant turns. |
| `tool_calls` | optional, assistant | function calls, same shape as OpenAI (`[{"id","type":"function","function":{"name","arguments"}}]`). |
| `tool_call_id` / `name` | optional, tool msg | link a `role:"tool"` result back to its call. |
| `reasoning_content` | optional, assistant | thinking trace, trained separately from the final `content`. Useful for K2.7's reasoning. |

Root-level (per line) optional fields:

- `tools`: array of function/tool definitions available for that sample (pairs
  with `tool_calls`).
- `weight`: a float loss multiplier applied to the **whole** sample (up/down-weight
  important or noisy examples).

### Function-calling / agentic sample (one line, formatted for readability)

```json
{
  "tools": [{"type":"function","function":{"name":"get_ticket","parameters":{"type":"object","properties":{"id":{"type":"string"}},"required":["id"]}}}],
  "messages": [
    {"role":"system","content":"You are our support agent. Use tools when needed."},
    {"role":"user","content":"What's the status of ticket AB-42?"},
    {"role":"assistant","content":"","tool_calls":[{"id":"c1","type":"function","function":{"name":"get_ticket","arguments":"{\"id\":\"AB-42\"}"}}]},
    {"role":"tool","tool_call_id":"c1","name":"get_ticket","content":"{\"status\":\"resolved\"}"},
    {"role":"assistant","content":"Ticket AB-42 is resolved."}
  ]
}
```

## Limits & requirements

| Rule | Value |
|---|---|
| Minimum examples (hard) | **3** |
| Maximum examples per dataset (hard) | **3,000,000** |
| Upload size | ~150 MB streamlined upload; **1 GB** hard max (UI for <500 MB, `firectl` for larger) — medium-confidence, verify |
| Recommended for SFT | **~1,000+** |
| Default max training context | **≥32,768 tokens** (longer examples truncated; configurable) |
| `system` message | if present, **must be the first message** |
| `tool_calls[].function.arguments` | must be a **JSON string**, not an object (re-serialize if you parsed it) |
| Assistant tool-only turn | `content` may be empty, but **include the key** (`"content":""`); the `tool_calls` turn is itself a valid training target |
| Last message | should be an `assistant` turn (that's the training target) |
| At least one trainable assistant turn | assistant with content **or** `tool_calls`, `weight≠0` — otherwise nothing to learn |

### Multi-turn unrolling — the cost gotcha for agent trajectories

Fireworks trains a multi-turn (esp. reasoning) conversation by **unrolling it into N
single-turn examples — one per assistant turn** (earlier thinking traces stripped to
match inference). A trajectory with 40 assistant turns becomes ~40 training examples.
So your **billed/trained token count is far larger than the raw dataset size**, and
long SWE-agent trajectories amplify this hard. Budget time + cost accordingly, and
prefer fewer, higher-quality (`resolved==1`) trajectories over raw volume.

The bundled `validate_fireworks_dataset.py` enforces all of these before you
waste an upload/train cycle.

## End-to-end `firectl` workflow

```bash
# 0. install + auth (once)
#    pip install firectl   (or the documented installer);  firectl signin

# 1. upload the dataset
firectl dataset create my-kimi-sft ./out/train.jsonl

# 2. (optional) upload the eval split as its own dataset
firectl dataset create my-kimi-eval ./out/eval.jsonl

# 3. launch a supervised (LoRA) fine-tune from the K2.7 base
firectl sftj create \
  --base-model accounts/fireworks/models/kimi-k2p7-code \
  --dataset my-kimi-sft \
  --evaluation-dataset my-kimi-eval \  # or use --eval-auto-carveout
  --output-model my-kimi-k2p7-tuned \
  --epochs 1 \            # default 1; 1–3 typical, >3 tends to overfit
  --lora-rank 8          # default 8; power of 2, up to 32 (use 32 for complex tasks + lower LR)

# 4. watch it  (verb order varies by firectl version — confirm with `firectl --help`)
firectl get sftj <JOB_ID>

# 5. deploy — serverless LoRA is NOT supported, so create a dedicated deployment
#    ("live-merge" merges the LoRA into the base; multi-LoRA can host many addons)
firectl deployment create my-kimi-k2p7-tuned
```

First confirm the base model is tunable: `firectl model get -a fireworks kimi-k2p7-code`
(look for **Tunable: true**; K2.7 Code supports LoRA + tools + 262K context).

### LoRA SFT settings (`firectl sftj create`)

| Flag | Default | Notes |
|---|---|---|
| `--lora-rank` | 8 | power of 2, **max 32**; **16** is a good start. Higher rank + long context can OOM. |
| `--epochs` | 1 | non-integer allowed (e.g. `2.0`); 1–3 typical, >3 tends to overfit. |
| `--learning-rate` | auto (per model) | e.g. `1e-4`; don't override without reason. Lower it when you raise rank. |
| `--learning-rate-warmup-steps` | 0 | e.g. `200` for stability on long/agentic runs. |
| `--max-context-length` | ≥32,768 (examples cut at 32,768) | **raise for long agent trajectories** or their tails (incl. the final patch = the target) get truncated. Only as far as needed — high rank + long context OOMs. |
| `--batch-size` / `--gradient-accumulation-steps` | auto / 1 | sequence packing; grad-accum >1 raises effective batch size. |
| `--evaluation-dataset` | auto carve-out | point at a held-out JSONL for a clean eval signal. |
| `--wandb-project` / `--wandb-api-key` / `--wandb-entity` | — | optional W&B logging. |

Continue training an existing LoRA with `--warm-start-from <model>` instead of
`--base-model`. If the model learns the wrong tokens, use **Render Samples** on the
job page to inspect the loss mask. `earlyStop=True` stops when val loss plateaus.

## SFT vs RFT (quick rule)

- **SFT** (what this skill formats for): you have example *outputs* to imitate.
  Needs ~1000+ examples. Default choice.
- **RFT** (reinforcement fine-tuning): you can *score* an output automatically
  (unit tests pass, JSON validates, exact match, a judge). Needs far fewer
  examples and can beat SFT on verifiable tasks. Fireworks supports full-parameter
  RFT for Kimi K2. Same `messages` JSONL, plus you supply an evaluator/reward.
