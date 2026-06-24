---
name: brain-to-docs
description: Use when the user wants to extract project vision, decisions, and preferences into clear documentation through a back-and-forth Q&A loop. Triggers on "brain-to-docs", "build out the docs", "extract the vision", "let's document this project".
---

# brain-to-docs

The purpose: extract the user's taste, judgment, knowledge, vision, preferences, and decisions into text. Save it as clear, concise Markdown docs for the project. README holds the vision; `docs/adr/` holds the decisions.

## The loop

1. **Check docs first, every time.** Read `docs/adr/` and `README.md` before doing anything. Other agents and people may add or edit ADRs.
2. **Ask 5 different questions** in plain text. Never use a questions UI. Default to 5 unless the user asks for a different number. Make them high-variety: a wide, creative spectrum of unique angles. Do not make them all the same type, such as all "tech stack," all "product," or all "monetization." Exception: if the user asks for a specific focus area, follow it.
3. **Update docs after every answer.** No exceptions. Decide whether the answer updates `README.md` or becomes a new ADR.
4. Repeat until the user says "we're done" or something similar.

## Rules

- All answers and responses during this process must be very concise.
- Use short sentences.
- Write in plain English.
- ADRs: short, numbered `NNNN-slug.md`, with Status, Context, Decision, and Consequences.
- README: vision only. Decisions go in ADRs.
- Do not challenge the user's thinking unless they ask, or they are making a severe mistake.
