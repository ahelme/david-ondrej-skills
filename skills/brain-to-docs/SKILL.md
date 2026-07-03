---
name: brain-to-docs
description: Use when the project owner wants to extract project vision, decisions, and preferences into clear documentation through a back-and-forth Q&A loop. Triggers on "brain-to-docs", "build out the docs", "extract the vision", "let's document this project".
---

# brain-to-docs

The purpose: extract the project owner's taste, judgment, knowledge, vision,
preferences, and decisions into text — saved as clear, concise markdown docs for
the project. README holds the vision; `docs/adr/` holds the decisions.

## The loop

1. **Check docs first, every time.** Read `docs/adr/` and `README.md` before doing anything. Other agents and people may add or edit ADRs.
2. **Ask 5 different questions** in plain text. Do not use a questions UI. Default to 5 unless asked for a different number. Make them varied across different angles, not all the same type. If a specific focus area is requested, follow it.
3. **Update docs after EVERY answer.** No exceptions. Decide whether the answer updates `README.md` or becomes a new ADR.
4. Repeat until the project owner says the process is done.

## Rules

- Keep all answers and responses in this process very concise.
- Use short sentences.
- Write in plain English.
- ADRs: short, numbered `NNNN-slug.md`, with Status, Context, Decision, and Consequences.
- README: vision only. Decisions go in ADRs.
- Do not challenge the project owner's thinking unless asked, or unless there is a severe mistake.
