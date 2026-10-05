---
title: "Tools 101"
description: "Read, Edit, Write, Bash and the rest: how the agent picks a tool, what a result looks like, and why tool use is the signal."
section: fundamentals
group: "How it works"
order: 40
updated: 2026-10-05
sources: ["learn/tier-1/04-tools-101.mdx"]
---

Tools are how a model stops talking and starts doing. Claude Code gives the model a set of built-in tools (read a file, edit it, run a command, fetch a page), and the agent loop is just: pick a tool, look at the result, decide the next step. Knowing the tools helps you read a session, write better prompts, and set permissions that make sense.

## The tools you'll see most

Tool names are exact strings. They're what you type in permission rules, hook matchers and agent definitions, so it's worth knowing them. This list is checked against the official tools reference as of October 2026.

| Tool | What it does | Asks permission by default? |
|---|---|---|
| `Read` | Reads a file (or a slice of one) with line numbers | No |
| `Edit` | Replaces an exact string in a file | Yes |
| `Write` | Creates a file or overwrites one completely | Yes |
| `Bash` | Runs a shell command and returns the output | Yes, except a built-in set of read-only commands |
| `WebFetch` | Fetches a URL | Yes |
| `WebSearch` | Searches the web | Yes |
| `Agent` | Spawns a subagent with its own context window | No |
| `Skill` | Runs a skill (packaged instructions) | Yes |
| `LSP` | Code intelligence: definitions, references, type errors | No |
| `EnterPlanMode` / `ExitPlanMode` | Plan first, then present the plan for approval | Exiting asks |

There are more: task tracking, in-session scheduling, background monitors, notebook editing, and others. Connected MCP servers add their own tools, which show up with names like `mcp__github__list_prs`.

> **Note:** Older tutorials, including the earlier version of this one, list `Grep` and `Glob` as core tools. On macOS, Linux and WSL they're now left out of the default set. Claude searches with `grep` and `find` through `Bash` instead (Claude Code ships fast embedded versions of both), so those searches reach your permission rules and hooks as `Bash` calls. On Windows, and in a few configurations described in the docs, `Grep` and `Glob` are still there.

## Edit is precise on purpose

`Edit` does exact string replacement. No regex, no fuzzy matching. The text to replace has to appear in the file exactly once, down to the whitespace, or the edit fails and the agent has to supply more surrounding context.

That strictness is a feature. A failed edit is loud and harmless. A fuzzy edit that hit the wrong line would be quiet and harmful. It's also why the agent reads a file before it edits it: it needs the exact text.

`Write` replaces the whole file. It's the right tool for a new file and the wrong one for changing three lines in an existing one. If you see an agent rewriting a 500-line file to change one function, ask it to use targeted edits.

## How the agent picks a tool

The model chooses based on what it needs to know or do next, roughly like a developer would:

- Need to find where something lives: search (via `Bash` on most machines), then `Read`.
- Need to understand a file: `Read`.
- Need to change it: `Edit`.
- Need something new: `Write`.
- Need to prove it works: `Bash` to run the tests.
- Need a big investigation without flooding the main context: `Agent`, which does the digging in its own window and returns only a summary.

A normal bug fix chains these in one turn. Search for the function, read the file, edit the line, run the tests, read the failures, edit again, run again.

## What a result looks like

Every tool call returns a result that goes back into the context window. Watching a session, you'll see something like:

```text
Read(src/orders/webhook.py)
  Read 212 lines

Edit(src/orders/webhook.py)
  Updated: address = order.shipping_address

Bash(uv run pytest tests/test_webhook.py -q)
  14 passed in 0.9s
```

Each result is evidence the model reads before deciding what to do next. That chain of calls is the work. It's also your audit trail: you can follow exactly what the agent looked at and why it concluded what it concluded. The start-here section has a full article on [reading the output](/docs/start-here/reading-the-output/).

## Read-only vs state-changing: the basis of permissions

The permission column in the table above isn't random. Tools that only look (read a file, list a directory, check code intelligence) run without asking. Tools that change things (edit a file, run an arbitrary command, fetch from the internet) ask, until you pre-approve them.

That split is the backbone of every safety setting you'll configure:

- **Allow** the commands you run constantly and trust, like your test runner, so you stop clicking yes.
- **Ask** for anything with side effects you want to see first, like `git push`.
- **Deny** what should never happen, like reading your `.env`.

One thing to know before you rely on a deny rule: a `Bash` rule matches the command text the agent writes. `Bash(rm *)` stops `rm -rf build/`. It doesn't stop `/bin/rm -rf build/` or `bash -c 'rm -rf build/'`. The official docs say plainly that it isn't a security boundary around the program. For things that truly must not happen, you want a hook, a sandbox, or a gate in your own code. The [settings and permissions](/docs/fundamentals/settings-and-permissions/) article covers the rules in detail.

## Tool use is the signal

One result convinced me tools matter more than model choice for a lot of real work.

In April 2026 I had an MBA analytics final. It was a take-home, and the course allowed LLMs. I built a pipeline for it: a classifier that recognized the question type, playbooks for each method (regression, logistic, clustering, conjoint, text analytics, SQL), a solver that actually computed answers with pandas, statsmodels and scikit-learn against the real data, and a verifier. On the practice exam it scored 30 of 30, and on the final its answers matched the answer key.

As a comparison I gave the same practice exam to frontier models of the time, answering straight from the page with no tools. They scored between about 15 and 21 out of 30. Swapping one frontier model for another moved the score a few points. Giving the work tools to compute with moved it from the high teens to 30.

The models weren't dumb. They pattern-matched instead of computing, because nothing let them compute. A model that explains how to run a regression is a chatbot. A model that loads the data, runs the regression, reads the output and catches its own mistake is an agent.

Honest read: when an agent gives you a confident wrong answer, the first question isn't "do I need a bigger model." It's "did it have a tool that would have told it the truth, and did it use it?"

**Next:** [Prompting Claude Code well](/docs/fundamentals/prompting-the-cli/)
