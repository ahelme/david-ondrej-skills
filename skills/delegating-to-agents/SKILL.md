---
name: delegating-to-agents
description: MUST be read any time another AI agent is involved — sending a prompt to or polling a Pi/Codex/Claude Code/Hermes/OpenCode agent, driving an agent running in another pane/surface/terminal/tmux window, delegating or relaying anything to an agent in the same workspace, spawning a sub-agent, or orchestrating agent-to-agent work. Read it before the first message you send to another agent. Covers the critical rule that prompts sent to a TUI agent must be one single line, short polling cadence, which agent to pick, and per-agent characteristics. If you are about to type `cmux send`/`tmux send-keys` to any agent, this skill applies.
---

# Delegating to Agents

## Which agent to pick

- **For most tasks → use a fast general-purpose agent.** Pick the agent that is already configured and appropriate for the workspace.
- **Default for coding → use a strong coding agent.** Delegate hard, multi-step engineering work to the most capable coding agent available.
- **Frontend / design → use an agent that is strong at UI and visual work.** For UI, styling, and design tasks, choose the agent/model combination that performs best for design feedback and iteration.
- **A good setup for complex work:** use one agent as the orchestrator and delegate execution to a coding agent in another pane/surface. This is not the only setup that works, but it is a solid default for heavy, long-running tasks.

## Polling cadence — keep sleeps short

General principle: when waiting on another agent, use short `sleep` intervals so you check often. Do not `sleep 30` by default. Start with `sleep 3-5`; if the agent is not done, `sleep 5` again and re-check. Scale up only for genuinely heavy tasks.

After every check, send the user a one-line progress update: what the other agent is doing and whether it is on track. Keep it extremely concise.

Claude Code cmux note: after Claude finishes, it may prefill a predicted next user message; that draft is Claude, not the user speaking.

## Sending prompts — never put newlines in the message body

When sending a prompt to a TUI agent such as Pi, Hermes, Claude Code, Codex, or similar via `cmux send`, `tmux send-keys`, or equivalent, **the message text must be a single line**. In these TUIs a newline = Enter, so a multi-line string submits after the first line and the rest arrive as separate mid-turn messages, cutting off or fragmenting your prompt.

Fixes:
- Send the whole prompt as **one line** using `. ` or `; ` instead of line breaks, then send one explicit Enter.
- For long or multi-step instructions, **write them to a temporary file** and tell the agent to read it, for example: `cmux send --surface surface:N "read /tmp/task.md and follow it"` then `cmux send-key --surface surface:N enter`.

**cmux command names:** to target another agent surface, use `cmux send --surface surface:N` and `cmux send-key --surface surface:N enter`. Do not invent alternate command names; the `--surface` flag goes on the regular `send` / `send-key` commands.

**Always wrap the prompt in double quotes — never escape the outer quotes.** A common bug is emitting `cmux send --surface surface:N \"...\"` with backslash-escaped outer quotes. In bash, this can break parsing and produce quoting errors. Rules:
- Outer quoting is plain double quotes: `cmux send --surface surface:N "your prompt here"`. Do not prefix the outer quotes with backslashes.
- Inside the prompt, avoid apostrophes/single-quotes and literal double quotes where possible. Rephrase instead.
- Do not switch to single-quote outer wrapping as a workaround unless you fully understand the shell-escaping implications. Prefer clean, unescaped double quotes.

## Remote environments

If an agent needs to work in a remote environment, prefer launching the agent within that authorized environment and then driving the on-box agent. This gives it local context and avoids fragile per-command remote round-trips. Do not include private hosts, credentials, IP addresses, or access details in prompts or docs.

## Agent characteristics

- **Pi Agent** — typically starts and responds quickly. Use short polling intervals first.
- **Pi & Hermes** — often suitable for fast orchestration and general-purpose work. Poll with short intervals rather than long waits unless the task is clearly heavy.

## Common agents, compressed reference

Background only — do not over-index on this. Many agents use a portable `SKILL.md`-style standard. Project-local skills usually take precedence over personal skills. One folder can often be shared or symlinked across compatible agents.

- **Pi** — minimal tool-oriented agent with skills, prompt templates, packages, and model-agnostic configuration. Often useful for fast orchestration and general tasks. Skills commonly live under `~/.pi/agent/skills/`.
- **Hermes** — persistent autonomous agent with memory, learning loops, reusable skills, scheduling, messaging integrations, and subagent delegation. Can orchestrate other coding CLIs as workers. Skills commonly live under `~/.hermes/skills/`, with project `skills/` taking precedence when supported.
- **Claude Code** — Claude-centric coding agent with project conventions such as `CLAUDE.md`, rules, agents/subagents, and skills/plugins. Skills are injected instructions in the main conversation rather than separate processes. Skills commonly live under `~/.claude/skills/` and project `.claude/skills/`.
- **Codex CLI** — coding CLI with sandboxing, CI usage, MCP support, and GitHub PR review workflows. Reads `AGENTS.md`. Skills commonly live under `~/.codex/skills/` and project `.codex/skills/`.

## Driving interactive CLIs

- Codex, Pi, OpenCode: tooling that drives them may need `pty=true`.
- Claude Code: often works better in non-interactive print mode with the appropriate permission settings for the task.
- Hermes is commonly used as an orchestrator or persistent agent and can drive coding CLIs rather than only acting as one.
