# Kimi K2.7 — what it is and how that shapes dataset choice

Moonshot AI's Kimi K2 series is a family of open-weight Mixture-of-Experts (MoE)
models. **Kimi K2.7 Code** (released 2026-06-12, model id on Fireworks
`accounts/fireworks/models/kimi-k2p7-code`, HF `moonshotai/Kimi-K2.7-Code`,
Modified MIT license) is the current coding/agentic flagship. Confirm the exact
serving/fine-tuning id with `firectl list models` — release ids change.

## Architecture (why fine-tuning behaves the way it does)

| Property | Value |
|---|---|
| Total parameters | ~1 trillion (MoE) |
| Active parameters / token | ~32 billion |
| Experts | 384, 8 activated per token |
| Layers | 61 (incl. 1 dense) |
| Attention | Multi-head Latent Attention (MLA), 64 heads |
| Context window | 256K tokens |
| Vocab | ~160K, SwiGLU activations |
| Variants in the series | K2 (Instruct/Base), K2.5, K2.6, **K2.7 Code**, K2 Thinking |

Two practical consequences:

- **It is a sparse MoE.** Different tokens route to different experts. Fine-tuning
  can destabilize routing; Fireworks mitigates this server-side ("Routing Replay",
  caching reference-policy routing). You do not configure this, but it is why you
  should not be surprised that MoE fine-tunes are more sensitive to noisy data —
  keep the dataset clean.
- **It is a reasoning ("thinking") lineage.** K2.7 Code produces internal
  reasoning and spends ~30% fewer thinking tokens than K2.6. If you want to
  preserve or shape that reasoning, you can include thinking traces in training
  data via the optional `reasoning_content` assistant field (see
  `fireworks-format.md`). If you want terse, non-reasoning outputs, train on
  examples without it.

## What it is genuinely good at (steer datasets toward these)

K2.7 is optimized for **agentic coding, tool/MCP use, multi-step reasoning, and
long-context** work. Fine-tuning is most effective when it *reinforces* these
strengths on your specific distribution rather than fighting the base model:

- **Great fits**: your codebase's conventions and component library; reliable
  calls to *your* tools/APIs in *your* schema; a fixed output contract (single
  file, strict JSON, house style); distilling a repeatable agent workflow.
- **Weak fits (don't fine-tune for these)**: injecting factual knowledge (use
  retrieval); tasks far from code/agentic/reasoning where you would be swimming
  upstream against the base model's priors; anything you can't show ~1000 clean
  examples of.

## Prompt format — let Fireworks handle it

Kimi's chat template uses special tokens (`<|im_system|>`, `<|im_user|>`,
`<|im_assistant|>`, `<|im_middle|>`, `<|im_end|>`) and a specific tool-result
convention. **You do not write these tokens in your dataset.** Fireworks (and any
correct serving stack) applies the template from the structured `messages` array.
Your job is only to produce clean `{"role","content", …}` messages. Hand-inserting
template tokens into `content` is a common and costly mistake — it double-encodes.

The one thing to keep consistent between training and inference: the **system
prompt**. If you train with a fixed system prompt, send that same system prompt
when you call the deployed model, or you lose much of the fine-tune's benefit.

## Sizing guidance for K2.7 SFT

- **~1,000+ examples**: Fireworks' recommended floor for supervised fine-tuning.
- **A few thousand, high quality**: the sweet spot for style/format/domain locks.
- **<1,000 with a checkable reward**: consider RFT instead of SFT.
- Keep examples within the training context length (default ≥32,768 tokens;
  longer is configurable but costs more). Over-length examples get truncated,
  which silently corrupts the target — filter them out beforehand.
