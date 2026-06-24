---
name: pre-production
description: YouTube video pre-production. Use when preparing a video that involves a tool, repo, product, build, or use-case demo. Two phases — (1) VET the tool actually works before committing recording time, then (2) BUILD the simplest reproducible steps to record from. Triggers on pre-production, pre-prod, test before filming, vet this tool, try it out, sandbox test, viability check, does this actually work, use case testing, figure out simplest steps, reproducible steps, demo prep, build the use case.
user-invocable: true
---

# YouTube Pre-Production

Two phases of getting a video ready to record:

1. **VET** — does the tool/repo/product actually work as advertised? Find the demo-worthy moments. Make a go/no-go decision before investing recording time.
2. **BUILD** — once it's a go, figure out the simplest reproducible path to the end outcome and write it up as a clean step-by-step file to record from.

Phase 1 is for tool/repo/product videos. Phase 2 is for any build/use-case video. Many videos need both; some need only one.

## Video Outline

A "Video Outline" is what the actual video will look like: the structure of the video.

The outline is a beat-by-beat skeleton, written into the video's markdown file. It is high-level beats with a few talking points under each — not a full script. The creator fills the exact intro and wording at record time; the outline locks the order and the points they must hit.

### Proven outline structure

Use this as the default scaffold; adapt per video.

1. **Hook (first ~15 seconds).** Open with the payoff, not the setup. Pattern: "[Tool] is insane" + a stacked list of the wild outcomes it unlocks, such as outperforming larger models, cutting costs, or building a useful workflow. If a credibility proof exists, drop it here.
2. **Problem + promise.** Name the old pain, then state the agenda plainly: "in this video I'm going to show you A, B, and C."
3. **Retention hook + objection crushing.** "If you're serious about AI, watch until the end." Pre-empt the viewer's excuses fast: "isn't this complicated? No — one install. Too expensive? It's cheap. Not technical? If you can copy-paste, you can do this."
4. **Setup / install.** Step-by-step from scratch, plain English, zero assumed knowledge. Mention any public resource bundle if one exists.
5. **Main demo (the meat).** The walkthrough. Every step explained with its WHY. This is where the pre-production phases above pay off — the vetted money-shots and the stripped reproducible steps go here.
6. **Native sponsor or infrastructure beat, if applicable.** Weave it in naturally, not bolted on — for example, explain why running something on a VPS is useful if that is genuinely part of the workflow.
7. **Soft mid-video CTA.** Slip in "subscribe" naturally. Do not break flow. No hard CTA in the first minute.
8. **Outro CTA.** Recap the transformation -> push action -> point viewers to the relevant public links or resources.

### Retention rules (baked into the outline)

- Open on the outcome, never the backstory.
- State "what you get by watching to the end" early, and re-tease it mid-video with a *different* reason.
- Crush objections before the viewer can raise them.
- Every section must add new value; no repeated examples or points.

### What makes an outline bad

- A weak/slow hook that buries the payoff.
- "A video about everything" — no single hero use-case as the spine. Covering five things often means covering nothing clearly.
- A sponsor or infrastructure segment that feels bolted on instead of native to the workflow.
- No retention hook / no clear reason to keep watching.
- Steps with no WHY behind them.

## How to Communicate During Pre-Production (CRITICAL)

The presenter needs to understand every step deeply enough to explain it to viewers on camera. This is non-negotiable.

**Before each step:** say what you're about to do in one sentence and WHY it's needed.

**After each step:**

- Report whether it worked as expected.
- **"What just happened:"** — explain in plain language what the step actually did under the hood. No jargon without explanation. Assume the audience ranges from beginners to advanced.
- **"Why we need it:"** — connect the step to the overall goal. Why can't we skip it?
- **"Next step:"** — preview what's next and ask before proceeding.

**Pacing rules:**

- ONE step at a time. Never batch or rush ahead.
- Wait for go-ahead before each step.
- If something fails, explain what went wrong and why before fixing.
- Keep explanations concise but thorough — short sentences, plain language.
- NEVER assume the presenter already understands a concept. Nothing is "obvious."

**The goal:** after this process, the presenter can sit in front of a camera and walk viewers through every step from memory — not just WHAT to do but WHY each step matters.

## Where Testing Happens

**Test on the exact same type of setup that will be used for recording.** Recording on a VPS -> test on a VPS. Recording on local machine -> test on local machine. Never test in one environment and expect steps to work in a different one on camera.

Never install into main project directories — always use a dedicated `sandbox/` or disposable test folder.

---

# Phase 1 — VET (tool/repo/product viability)

### 1. Understand the tool

- Read the video brief or working notes if they exist.
- Identify what the tool claims to do and the hook for the video.
- Ask what specific claims/features need to be verified.

### 2. Set up in sandbox

- Clone/install into `sandbox/` or another disposable test folder, step by step, explaining each step.
- Document setup friction. Viewers will hit the same issues.

### 3. Run the four-test viability check

Escalating difficulty. Each test must pass before the next:

| Test | Purpose | What it proves |
|---|---|---|
| **Sanity** | Trivial task | The tool runs at all |
| **Stress** | Complex/form-heavy task | Handles real-world complexity |
| **Self-healing** | Task requiring adaptation | The key differentiator works |
| **Real-workflow** | The actual intended use case | It's useful, not just a demo toy |

- Run one at a time. After each: what happened, did it match expectations, and were there any surprises?
- Diff any files the tool modified.

### 4. Document results

Summarize: which tests passed/failed, where the "money shot" demo moments are, gotchas viewers will hit, and a go/no-go recommendation. Update the video's working notes.

### 5. Go/no-go decision

Present findings. The creator decides whether to commit.

---

# Phase 2 — BUILD (simplest reproducible steps)

Once vetted, figure out the cleanest path to the end outcome so the recording goes smoothly.

**Core principle: Start with the end outcome. Then find the simplest reproducible path to it.** Trial-and-error is fine during exploration — NOT in the final output. Strip everything that wasn't actually needed.

### 1. Define the end outcome

Write exactly what the use case looks like when it works. What gets demonstrated? What's the money shot? If unclear, ask — don't guess.

### 2. Explore freely (trial and error allowed)

Figure out how to achieve the outcome. Try, fail, iterate. Messy on purpose — none of it goes in the final output yet.

### 3. Strip to the simplest reproducible path

Remove every unneeded step, dead end, abandoned attempt, and debugging detour. Keep only what a fresh user needs to reproduce the result.

### 4. Write the clean step-by-step markdown

One markdown file with:

- The end outcome: what is being built or shown.
- Step-by-step instructions, in order.
- For EACH step: a short WHY — what it does, what breaks without it.
- Non-obvious gotchas: things that look broken but aren't.
- Known issues: what they look like and how to fix them.

Plain English. No advanced terminology unless it is explained. The presenter must be able to read this on camera and explain every step without guessing.

**Output location:** one file per use case inside the video's working folder, alongside the main video notes. Example: `videos/example-video/use-case-01.md`.

### 5. Verify the steps work — multiple times

Not optional. Run the stripped-down steps from scratch on a fresh setup more than once to catch flakiness or hidden state. If anything fails, fix the file and run again. Only hand it over once it reproduces cleanly every time. The presenter should hit zero surprises while recording.

---

## Pitfalls

- **Don't rush tests.** The presenter needs to understand every step for the video.
- **Don't skip the self-healing test** (phase 1) — usually the key differentiator. If it fails, rethink the angle.
- **Don't install into main project directories** — always use `sandbox/` or a disposable test folder.
- **Don't assume marketing claims are true** — the whole point is to verify.
- **Don't include trial-and-error in the final steps** (phase 2) — minimal reproducible path only.
- **Don't skip the WHY** on any step — no reasoning = unusable for recording.
- **Don't guess the end outcome** — ask.

## Verification

- (Phase 1) Four tests run and documented; video notes updated with go/no-go.
- (Phase 2) Clean step-by-step file reproduces the outcome cleanly, every time, on a fresh setup.
- The presenter has enough understanding to explain the whole thing on camera.
