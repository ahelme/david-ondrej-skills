---
name: safe-prompt-rewrite
description: Rewrite a user's prompt about sensitive or dual-use topics so it is clearly authorized, defensive, and policy-safe. Use when the user asks to make a prompt safer, less ambiguous, or more appropriate for a general-purpose assistant.
disable-model-invocation: true
---

# Safe Prompt Rewrite

Return the user's prompt back with minimal edits that preserve benign intent while removing unsafe, ambiguous, or unnecessarily sensitive phrasing. Do not rewrite the whole thing, summarize, or restructure unless needed for safety.

Apply when the prompt touches cybersecurity, authentication, software security testing, medical or scientific topics, or requests for hidden reasoning.

The user should provide the prompt-to-be-changed wrapped in `<prompt>...</prompt>` XML tags. Operate only on the text inside those tags; treat everything outside as instructions to you.

## Method

1. Identify sentences or phrases that make the request sound unauthorized, offensive, privacy-invasive, or like a request for hidden reasoning.
2. Replace each in place with a safer equivalent, or describe the wanted functionality abstractly rather than naming sensitive tactics.
3. Keep everything else as close to the original wording as possible.
4. Return the complete edited prompt.

Reframe the task so it reads as:

- **Owned or authorized**: the user is working on systems, data, or materials they are allowed to access.
- **Defensive or educational**: the goal is to review, fix, test, document, or understand at a high level.
- **Not operationally harmful**: do not include instructions for abuse, evasion, unauthorized access, weaponization, or live targeting.

## Safer rewrite patterns

| Risky framing | Safer rewrite |
|---|---|
| Asking how an attacker would abuse a system | Ask to review the relevant files for missing checks and suggest defensive fixes |
| Asking for a working exploit, payload, or proof of compromise | Ask for a regression test that demonstrates the issue is fixed, then patch it |
| Asking how to bypass or brute-force a control | Ask how to enforce secure validation, rate limiting, and monitoring |
| Asking for malware behavior or attack steps | Ask for a high-level risk summary and defensive remediation steps |
| Asking to show hidden reasoning or step-by-step private thinking | Remove the request; ask for a concise explanation or brief rationale instead |
| Medical diagnosis framing | Reframe as help understanding information provided by a qualified professional |
| Highly specific sensitive domain wording that is not needed | Abstract the domain and focus on the data, process, or safety-preserving analysis |

## Refusal boundary

If a sentence is purely harmful or cannot be made safe without changing the user's intent, do not silently sanitize it. Tell the user that no safe rewrite is available for that portion and briefly explain why.

## Output

1. Print the full edited prompt in a code block, ready to paste.
2. Provide a short list of the sentences changed and what they became.
3. If no changes were needed, say so briefly.
4. If part of the request is unsafe and cannot be rewritten safely, flag that portion instead of providing operationally harmful wording.
