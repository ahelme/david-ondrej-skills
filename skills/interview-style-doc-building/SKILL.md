---
name: interview-style-doc-building
description: Use when a user wants to build a structured strategic document by answering questions (priorities, goals docs, framework files, ranked lists, principles, reviews). Interview one question at a time, patch the file after each answer, then re-ask. Not for day planning.
---

# Interview-Style Doc Building

A workflow for creating durable strategic docs. The assistant does NOT propose content — the assistant asks one question, the user answers, the assistant patches the file, then asks the next question. The file IS the conversation's output, updated incrementally.

## When to use

- Building a new SSOT file, such as priorities, vision, principles, frameworks, or ranked lists.
- Filling out a structured doc the user explicitly wants to author themself.
- Quarterly/annual reviews where the user's words go into the file.

**NOT for:** day planning, task triage, or anything where the assistant proposes content first.

## The Loop

1. **Create the file** with a skeleton: header, sections, and "to be filled in" placeholders. Use a single file write for the new file. After this, NEVER overwrite — only patch.
2. **Ask ONE question.** Concise. Specific. Single-faceted. Open-ended where possible.
3. **Wait for the answer.** Don't ask the next question yet.
4. **Patch the file** with the user's answer in the correct section.
5. **Re-ask** — next question, or follow-up if the answer was incomplete.
6. Repeat until the file is complete.

## Hard Rules

- **One question at a time.** Never dump multiple questions in a single message.
- **Patch, don't overwrite.** After the initial skeleton, use patching for every update. Never rewrite an existing doc from scratch.
- **Update the file BEFORE asking the next question.** Order: receive answer → patch file → ask next question. Not the reverse.
- **Lists from the user are UNORDERED SETS.** When the user lists items in response to "which X should we cover?" or "what are the Ys?", that is a SET, not a ranking. Never infer rank, priority, or sequence from the order they typed them. If you need ordering, ask explicitly: "Which of these is #1?"
- **Ask dynamics, not names.** When the user references a person, don't ask "who is X?" — ask about the role/dynamic.
- **No snark, no attitude, no filler.** Concise questions, concise acknowledgments.
- **No speculative additions.** Don't invent sections, edge cases, or "anything else?" prompts unless the user asks.

## Question Design

- **Domain-discovery, not confirmation.** "What wins against everything else?" — not "Is this category #1?"
- **Surface new reality.** Each question should pull out info the assistant doesn't already have.
- **Engine-move framing where applicable.** "What's the thing that, if true, makes the rest obvious?"
- **Concrete over abstract.** "What's #2 — the domain that wins against everything except #1?" beats "Tell me about your second priority."

## File Patching Pattern

After each answer:
1. Read the relevant section, if not already in context.
2. Patch with `old_string` = placeholder or previous entry, `new_string` = updated content with the user's words preserved.
3. Confirm the diff. Move on.

For ranked lists, append one rank at a time:
```markdown
1. **Domain A** — user-provided goal or principle.
2. **Domain B** — user-provided goal or principle.
```
Each rank gets patched in as the user confirms it.

## Common Pitfalls

- **Assuming order from a set.** User lists "A, B, C, D" → assistant writes "1. A, 2. B, 3. C, 4. D" → this is wrong. ALWAYS confirm rank explicitly.
- **Asking too many questions at once.** Even bundling 2 violates the rule.
- **Overwriting the file** instead of patching specific sections — destroys prior content.
- **Adding assistant-generated content** to fill out sections. Sections stay empty until the user provides the content.
- **Skipping the file update** between Q&A pairs — the doc falls out of sync.

## Pairing with Other Workflows

- Day planning — different pattern, usually task triage rather than interview-style authoring.
- Task organization — separate workflow.
- Memory management — separate from this; persona/preferences go to memory, not into the strategic doc unless explicitly requested.
