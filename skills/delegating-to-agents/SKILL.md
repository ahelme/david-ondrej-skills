---
name: delegating-to-agents
description: How to delegate work to another AI agent — picking the right agent, sending prompts to TUI agents, polling progress. Read BEFORE any `cmux send`/`tmux send-keys` to an agent, or whenever delegating, relaying, spawning, or orchestrating agent-to-agent work.
---

# Delegating to Agents

## Which agent to pick

- **Coding tasks → coding-focused CLI agent.** Use a coding agent for complex, long-running software engineering tasks.
- **General tasks → general-purpose agent.** Use a general assistant for research, planning, summarization, and non-code work.
- **Frontend / design → design-capable agent.** Prefer an agent that performs well on UI, styling, and design iteration.
- **Heavy multi-step work:** use yourself as orchestrator and have a worker agent execute in a separate pane/session.

## Sending prompts to a TUI agent

1. **ONE single line — never newlines in the message body.** In a TUI, newline = Enter: a multi-line prompt submits at the first line and the rest arrives as fragmented mid-turn steering messages. Use `. ` or `; ` instead of line breaks, then one explicit enter. For long instructions, write them to a temporary file and send: `read /tmp/task.md and follow it`.
2. **Wrap the prompt in plain double quotes — NEVER escaped.** `cmux send --surface surface:N "your prompt"`. A common bug is emitting `\"`; in bash that can break quoting and fail with `unexpected EOF`. Inside the prompt, avoid apostrophes and literal double quotes; rephrase instead of escaping. If a send failed, check for escaped quotes first.
3. **Exact command names:** `cmux send --surface surface:N` then `cmux send-key --surface surface:N enter`. There is NO `send-surface` or `send-key-surface`.

## Polling

Keep sleeps short: start at 3-5s, re-check, repeat. Avoid long blind sleeps unless the task is genuinely heavy. After every check, send the user a one-line status: what the agent is doing and whether it is on track.

Note: some agents may prefill a predicted next user message after finishing; treat that as an agent draft, not as a real user message.

## Remote environments

For work that must happen in a remote or target environment, launch the worker agent in that environment and drive that session directly. Avoid running a local agent that repeatedly proxies every step into another environment.

## Agent reference

Many CLI agents support portable skill/instruction files. Project-level instructions usually take precedence over global instructions.

- **General-purpose agent:** minimal read/write/edit/bash core; may support extensions, session branching, or resume.
- **Coding CLI agent:** optimized for software engineering tasks; may support sandboxing, non-interactive execution for CI, and repository instruction files.
- **Claude-style coding agent:** may support project conventions, permission modes, and live skill reload.
- **Persistent autonomous agent:** may provide cross-session memory, scheduling, and tool orchestration.

## Driving interactive CLIs

- Interactive terminal agents usually need `pty=true`.
- Non-interactive or print-mode agents may work better without a PTY.
