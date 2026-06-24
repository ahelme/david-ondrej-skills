---
name: safe-prompt-rewrite
description: Rewrite a user's prompt to be clearly authorized, defensive, and policy-compliant when it touches dual-use topics such as cybersecurity or biosciences. Use when the user asks to make a prompt safer, less ambiguous, or more appropriate for a general-purpose AI assistant.
---

# Safe Prompt Rewrite

Rewrite the user's prompt to make it clearly safe, authorized, and constructive. Preserve the user's benign goal and wording as much as possible, but remove or transform phrasing that requests harmful, evasive, or ambiguous dual-use help.

Apply when the prompt touches: cybersecurity, authentication, exploits, malware, pentesting, credentials, biosciences, chemistry, medical topics, or requests to reveal hidden reasoning.

The user provides the prompt-to-be-changed wrapped in `<prompt>...</prompt>` XML tags. Operate only on the text inside those tags; treat everything outside as instructions to you.

## Method

1. Identify sentences or phrases that could be interpreted as asking for harmful, invasive, evasive, or unsafe assistance.
2. Replace each with a safe equivalent that emphasizes authorization, defensive intent, testing, validation, documentation, or remediation.
3. Preserve all benign text where possible.
4. Return the complete edited prompt.

Reframe the task so it reads as:

- **Owned or authorized**: the user is working on systems, data, or materials they are allowed to access.
- **Defensive or constructive**: the goal is to implement, fix, test, validate, explain at a high level, or improve safety.
- **Non-evasive**: the prompt does not ask to bypass protections, hide activity, evade detection, generate harmful payloads, or provide operational misuse steps.

### Safer framings

| Unsafe or ambiguous framing | Safer rewrite |
|---|---|
| "How could an attacker exploit this authentication flow?" | "Review this authentication flow for missing checks and suggest defensive fixes." |
| "Write an exploit, payload, or proof of concept." | "Add a regression test that demonstrates the issue is fixed, then suggest a patch." |
| "How do I bypass or brute-force this control?" | "How do I enforce secure validation, lockout behavior, and rate limiting for this control?" |
| "Reverse this malware and show attack steps." | "Describe the risk at a high level and recommend defensive remediation steps." |
| "Show your reasoning" or "walk me through your private thinking." | "Provide a concise explanation of the answer and list key assumptions or checks." |
| "Diagnose this medical result as a clinician." | "Help me understand this result in general terms so I can discuss it with a qualified professional." |
| Domain-specific wording that is unnecessary for the task | Use a more general description of the data, analysis, or safety objective. |

If no benign defensive equivalent exists for a sentence because the request is genuinely harmful, do not disguise it. Flag that portion and explain that it should be removed or replaced with a lawful, defensive objective.

## Output

Return:

1. The full edited prompt in a Markdown code block, ready to paste.
2. A short list of exactly which sentences or phrases you changed and what they became.
3. If any portion could not be safely rewritten, state that plainly and provide a safe alternative objective.