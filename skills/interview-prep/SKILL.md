---
name: interview-prep
description: Use when preparing for candidate interviews from a user-provided application CSV. Builds a concise candidate summary, copies a reusable role-specific question list into a per-candidate working file, generates candidate-specific follow-up questions, tracks asked questions and live notes, compares candidates on paper, and runs a structured post-interview debrief.
---

# Interview Prep

This skill supports a privacy-conscious interview workflow using reusable question banks and per-candidate working notes.

## Files

1. **Master question files, role-specific:** `docs/interview/questions-{role}.md`
   - One master per role, for example `questions-operations.md`, `questions-content.md`, or `questions-engineering.md`.
   - Fallback: `docs/interview/questions.md` if no role-specific file exists.
   - Generic, reusable questions only.
   - **Never edited during interviews.** Source of truth.
   - Numbered list 1–N.

2. **Per-candidate file:** `docs/interview/candidates/{candidate-slug}.md`
   - Created at the start of each interview by copying the role-appropriate master list.
   - Holds: summary, generic questions, custom questions, candidate questions if relevant, notes, asked log, and post-interview verdict.
   - Live interview edits happen **in this file only**.

## When to Use

- "Next candidate" / "parse the CSV" → run **Parse + Init**.
- "Give me custom questions" / "attack the gaps" → run **Generate Custom Questions**.
- "Mark #N as asked" → run **Track Asked Question**.
- "Note:" / "add to notes" / any live observation → run **Add Note**.
- "Compare candidates" / "CSV vs CSV" → run **Compare Candidates**.
- "Debrief" / "interview over" / "extract my impressions" → run **Post-Interview Verdict**.
- "Edit the master" → edit the master question file only; do not touch candidate files.

## Procedure

### 1. Parse + Init Candidate File

1. Confirm the role if unclear.
2. Use the user-provided application CSV. If multiple files are available, ask which one to use rather than guessing.
3. Read the schema/header row and the candidate answer row.
4. Build a concise summary:
   - **Basics:** role-relevant identity/context from the application, avoiding unnecessary protected or sensitive details.
   - **Strengths:** concrete numbers, achievements, relevant experience, and verifiable claims.
   - **Yellow/red flags:** evasions, vague claims, contradictions, or mismatches.
   - **Missing information:** dodged questions, blank answers, missing portfolio/work samples, or unclear availability.
   - **Bottom line:** one-sentence on-paper verdict.
5. If the applicant references public companies, projects, channels, or work samples, verify only from public sources when appropriate. If verification is not possible, say "couldn't verify" rather than fabricating.
6. Create the candidate file: `docs/interview/candidates/{candidate-slug}.md`.
   - Read the role-specific master question list, or the fallback master.
   - Copy the full numbered list into the candidate file under `## Generic Questions`.
   - If the applicant submitted return questions, add `## Candidate Questions to Address` and list them.
   - Use the template below.

### Candidate File Template

```markdown
# Interview — {Candidate Name or Initials}

**Date:** YYYY-MM-DD
**Source CSV:** {user-provided CSV filename}

## Summary
{Basics, strengths, flags, missing information, bottom-line verdict}

## Generic Questions
1. {copied from master}
2. {copied from master}
...

## Custom Questions

{candidate-specific questions added later}

## Candidate Questions to Address
{only if the applicant returned questions in the form}

1. {candidate question}
2. {candidate question}

## Notes during interview
(none captured)

## Already Asked

- ✅ {question text}
- ✅ [candidate] {candidate question}
```

### 2. Generate Custom Questions

Generate 5–6 candidate-specific questions. Append them under `## Custom Questions`, continuing the numbering from where the generic list ended.

Rules:
- Be direct and specific.
- Probe gaps, dodged questions, blanks, vague claims, and inconsistencies.
- Test whether stated experience holds up under concrete follow-ups.
- Match the actual hiring need for the role.
- Add one-line *italic context* under each question explaining what it probes.

If the user later says a custom question is actually reusable, move it to `## Generic Questions` while keeping its number. Ask whether it should also be promoted to the master question file.

### 3. Track Asked Questions Live

When the user says "mark #N as asked":
1. Find #N in `## Generic Questions` or `## Custom Questions`.
2. Remove that line from the active list.
3. Append it to `## Already Asked` as `- ✅ {question text}`.
4. **Do not renumber.** Gaps are intentional.

When the user says "mark candidate #N as asked" or equivalent:
- Apply the same flow to `## Candidate Questions to Address`.
- Log it as `- ✅ [candidate] {candidate question}`.

When the user says "add a new question 'X'": append it to the active list with the next sequential number.

### 4. Add Notes During Interview

Append a bullet to `## Notes during interview` in the candidate file. Keep notes terse and factual, one bullet per insight.

Trigger phrases include:
- "note:"
- "add to notes"
- "observation:"
- remarks about communication, professionalism, role fit, red flags, green flags, or follow-up items

Always append. Do not overwrite existing notes.

### 5. Compare Candidates on Paper

When asked to compare candidates from CSVs:
1. Read only the source application CSVs, not post-interview notes.
2. Build a side-by-side table covering role-relevant application fields, such as:
   - Availability or commitment answer
   - Current status or workload constraints
   - Role-specific proof or portfolio evidence
   - Scenario answer quality
   - Work sample or video/audio quality signal, if applicable
   - Curiosity and quality of return questions
   - Required certifications, permissions, or eligibility, if applicable
3. End with a 1–2 sentence verdict on who is stronger **on paper**, explicitly noting that interview impressions are excluded.

### 6. Post-Interview Verdict

When the interview ends:

1. Ask for structured input. Default fields:
   - Overall verdict: strong yes / maybe / pass / backup
   - Energy and communication: high / mid / low / unclear
   - Commitment or availability: strong / verbal-only / weak / unclear
   - Top strengths
   - Red or yellow flags
   - Next step: reject / paid trial / second round / wait / offer
   - Anything else, with a skip option
   - Adapt options to the role.
2. Write a `## Post-Interview Verdict` section at the bottom of the candidate file, after `## Already Asked`.
3. Use clear headers, bullet lists for strengths and flags, and bold the verdict and next step.

### 7. Editing a Master Question File

When the user asks to edit the master question list:
- Confirm the role if ambiguous.
- Edit only the relevant `docs/interview/questions-{role}.md` file.
- The master is just the numbered list: no custom questions, notes, or asked sections.
- **Do not touch candidate files** when editing the master.

## Change Management

- During an active interview, keep edits focused on the candidate file.
- Do not run commits, pushes, deployments, or other remote operations unless the user explicitly asks.
- If the user asks for version control actions, summarize the intended change first and avoid exposing private candidate details in commit messages.

## Pitfalls

- Do not edit the master during a live interview.
- Do not drop reusable questions during a master edit; ask before removing them.
- Do not renumber when marking asked. Numbers are burned and gaps are intentional.
- Do not restart numbering for custom questions. Generic and custom questions share one continuous sequence.
- Do not soften legitimate flags, but keep wording factual and role-relevant.
- Do not fabricate verification. If public verification fails, say "couldn't verify."
- Do not pre-fill answers. Only mark a question asked when explicitly told.
- Do not lose notes by overwriting. Always append unless reconstructing from explicit user instructions.
- Do not mix interview impressions into CSV-vs-CSV comparisons.
- If a question number is ambiguous across sections, ask for clarification.

## Verification

After each operation, verify:
- **Parse + Init:** candidate file exists with Summary, Generic Questions, optional Candidate Questions, empty Custom Questions, Notes, and Already Asked sections.
- **Generate Custom Questions:** custom entries were added, numbering continues, and each has italic context.
- **Track Asked Question:** question was removed from the active list, added to Already Asked, and remaining numbers are unchanged.
- **Add Note:** new bullet was appended to Notes and existing content was preserved.
- **Compare Candidates:** output is a side-by-side table with no interview impressions and an explicit "on paper" verdict.
- **Post-Interview Verdict:** structured section was added at the bottom with bolded verdict and next step.
