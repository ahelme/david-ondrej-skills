---
name: setup-help
description: Walk the user through setting up anything step by step. Use when the user asks for help setting up, configuring, installing, or getting something working — "help me set up X", "walk me through this", "setup-help". Differentiator: gives one current step at a time, then always lists the remaining steps after each response.
disable-model-invocation: true
---

# setup-help

Guide the user through any setup, one step at a time, in plain English.

## Response format (every single response)

1. **Current step** — clear, simple, step-by-step instructions for the ONE thing to do right now. Plain English. Very concise.
2. A `----` divider.
3. **Still remaining** — a short numbered list of all the other steps left after this one.

Repeat this format for every response until setup is done.

## Rules

- Only give instructions for the current step. Do not jump ahead.
- Keep it concise. Short sentences. No filler.
- After the user finishes a step, move the next "remaining" item up to "Current step".
- Update the "Still remaining" list each time as steps get done.
- When nothing remains, say setup is complete instead of showing the list.
