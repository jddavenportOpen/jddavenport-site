---
title: "Sessions and context windows"
description: "What a session holds, why the context window fills, what compaction does, and when to start fresh instead."
section: fundamentals
group: "How it works"
order: 10
updated: 2026-10-05
sources: ["learn/tier-1/01-sessions-and-context.mdx"]
---

A session is one conversation with Claude Code: everything you typed, every file it read, every command it ran and every result it got back. All of that sits in the context window, and the window is finite. When it fills, Claude Code compacts the conversation into a summary and keeps going. That's fine for chat. It's a problem for anything you need to keep, so the rule in my system is simple: if it matters, it goes in a file, and any session can die without losing work.

## What you'll learn

- What loads into a session before you type a word
- How big the window is (it depends) and what happens when it fills
- The commands that manage context: `/context`, `/compact`, `/clear`, `--continue`, `--resume`
- When to start fresh instead of pushing on
- Why a huge context makes the agent slow, with numbers from my own cockpit

## What a session holds

Run `claude` in a folder and a lot happens before your first prompt:

- Your `CLAUDE.md` files load (user, project, and any parent folders).
- Auto memory loads, if it's on.
- A one-line description of each available skill loads. The full skill only loads when it's used.
- MCP servers connect. Their tool definitions are deferred by default, so mostly just the names cost context until a tool is actually called.

Then the conversation grows. Every file the agent reads, every test run it watches, every reply it writes, all of it stays in the window. A 2,000-line log dumped by one careless command can cost more than the whole conversation before it.

Run `/context` at any point to see the breakdown by category, including which memory files loaded. It's the single most useful command for understanding why a session feels heavy.

## How big is the window

It depends on the model and where you run it. As of October 2026, on the Anthropic API, current Sonnet, Opus (4.7 and later) and Fable models run with a 1 million token window. Some older models, some cloud providers, and setups that turn extended context off run at 200K. Don't assume. Check `/context`.

A token is a few characters of English. A long source file can run tens of thousands of tokens. A million sounds infinite until an agent reads half a repo and a few hundred lines of test output.

## What happens when it fills

Claude Code compacts automatically as you approach the limit. On a 1M model that happens at about 967K tokens by default. Compaction replaces the conversation history with a structured summary. Your project CLAUDE.md and auto memory are re-read from disk, and Claude Code re-reads up to five of the files it was working on, most recently modified first.

What can get lost is detail from early in the conversation: a constraint you mentioned once in turn three, the exact error text from an hour ago, the reason you rejected an approach. The summary keeps what it guesses is important. It's a good guess, not a guarantee.

You can steer it:

| Command | What it does |
|---|---|
| `/context` | Shows what's using the window right now |
| `/compact focus on the auth fix` | Summarizes now, keeping what you name |
| `/autocompact 500k` | Compacts earlier than the default for this model |
| `/clear` | Starts a new conversation with empty context |
| `/rewind` | Rolls the conversation and/or code back to an earlier point |
| `claude --continue` | Reopens the most recent conversation in this folder |
| `claude --resume` | Picks a past session from a list, or by name or ID |

You can also add a "Compact Instructions" section to CLAUDE.md to tell the summarizer what must survive.

## When to start fresh

A new session is cheap. A confused one is expensive. Start over when:

- **The task is done.** Don't run one mega-session forever. Close it, and let the next task start clean.
- **You've corrected the same thing twice.** The window is now full of failed approaches, and the model keeps tripping on them. Run `/clear` and write a better first prompt that includes what you learned. Anthropic's best-practices page gives the same advice.
- **You're switching to unrelated work.** Context from task A leaks into task B. Clear between them.
- **You're about to start something long.** Compact with a focus first, or clear and point the new session at the files that matter.

> **Tip:** Resuming keeps more than the conversation. A resumed session restores the model it was started with, too. In my system that means a change to the default model never reaches an already-running session, so an hourly guard checks live sessions and repairs the drift. If you change models and nothing seems different, check whether you're in an old session.

## My operating rule: state lives in files

Sessions in my system are disposable. They crash, they get compacted, they get restarted, and occasionally I kill one by accident. None of that loses work, because nothing important lives only in the conversation.

When a session starts, it reads its instructions, a digest of the last session, the master changelog, and the open loops ledger (the list of promises still pending). That's the whole handoff. The new session knows what shipped, what's in flight and what's owed, without inheriting a single token of the old conversation.

That's why the next article, files as state, is the most important one in this section. Compaction is only scary when the conversation is the only copy.

## Big context makes chat slow

This one I learned the measured way. On October 1, 2026 I ran a read-only audit of why chat felt slow in my cockpit (the web app where I talk to every agent session). The answer was not the network, the database or the web app. Model time was about 85 to 90% of the wait.

Two settings caused most of it. Every chat pane was running at the top effort level, and the median pane context was around 434K tokens. First visible text took 38 seconds at the median and 140 seconds at the 90th percentile. Every turn, the model reprocesses everything in the window. Caching helps, but a giant context is still a giant context.

The fix was boring. Interactive panes now default to high effort instead of the top level, and top effort is a per-pane choice. The other half is a habit, not a setting: clear or compact a long session instead of letting it grow. Honest read: a 1M window is a ceiling, not a target. Use it when the task needs it. Don't carry 400K tokens of yesterday into a quick question.

## The short version

- The context window holds everything, and it's finite.
- Compaction keeps you going but can drop early detail.
- `/context` before guessing, `/clear` between tasks, `/compact` with a focus before long work.
- Anything that must survive goes in a file, so a dead session costs nothing.

**Next:** [Files as state, not chat memory](/docs/fundamentals/files-as-state/)
