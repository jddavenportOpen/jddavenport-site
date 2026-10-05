---
title: "What Claude Code is, and what a harness is"
description: "A model talks. A harness gives it a loop, tools, files and a way to ask you first. Claude Code is the harness these docs teach with."
section: start-here
order: 10
updated: 2026-10-05
sources: ["learn/tier-0/01-what-is-claude-code.mdx"]
---

A chatbot is a model: text in, text out. It can tell you how to rename ten files. It can't rename them. Claude Code can, because it wraps the model in a harness: a loop, tools, files it can read and write, and a way to ask you before it does anything risky.

That one idea, a model inside a harness, is the foundation for everything else in these docs. My whole production system is that idea repeated many times with more guardrails.

## Three words people mix up

| Word | What it is | What it can do |
|---|---|---|
| **Model** | The language engine (Claude, from Anthropic) | Read text, write text. No hands. |
| **Agent** | A model that can take actions, look at the result, and decide the next step | Finish a task instead of describing it |
| **Harness** | The software that turns a model into an agent | Runs the loop, owns the tools, enforces the rules |

Anthropic is the company. Claude is the model. Claude Code is the harness that runs Claude as an agent on your computer. Three different things.

## What the harness adds

A harness gives the model four things it doesn't have on its own:

1. **A loop.** The model doesn't answer once and stop. It acts, reads the result, decides what's next, and keeps going until the job is done or it gets stuck.
2. **Tools.** Concrete actions it can call: read a file, edit a file, run a terminal command, search your code, fetch a web page.
3. **State in files.** The conversation ends. Files don't. Anything worth keeping gets written to disk, where the next session can read it.
4. **A way to talk to you.** It shows you what it's about to do, asks before risky actions, and reports what happened.

The word comes from horses. A harness is the rig that connects a strong animal to a cart so its strength turns into useful work. The model is the strength. The harness points it at your task.

## A concrete example

Say you type: "There's a typo in the heading on my About page. Fix it."

A chatbot replies with instructions: open the file, find the heading, change the word, save. Now it's your job.

Claude Code does the job:

1. Searches your project for files that look like an About page.
2. Reads the most likely one and finds the heading.
3. Edits the typo and shows you the exact before and after.
4. Tells you what it changed and where.

Same model in both cases. The difference is entirely the harness: the loop, the tools, and access to your files.

## Where it runs

Claude Code runs in your terminal, in a desktop app, in VS Code and JetBrains IDEs, and in the browser. These docs use the terminal, because that's where I run everything and because it shows you what's actually happening.

As of October 2026 my default model in Claude Code is Opus 5.5. Model versions change every few months, so the docs avoid depending on any one of them. The harness ideas don't change.

> **Note:** Claude Code isn't the only harness. People build their own, and plenty of open-source ones exist. I build on Claude Code because it's the runtime under my whole system: every agent session in it is a Claude Code process.

## Why this matters for the rest of the docs

Everything advanced you'll read here is this idea scaled up:

- **One session.** You and one agent in one folder. That's the rest of this Start here section.
- **Many agents.** Sub-agents, schedules, isolated workspaces, and a top-level agent routing work to specialists. That's Fundamentals and Patterns.
- **An organization.** 30+ agents in daily production since April 2026, with shared memory, a durable message bus, watchdogs, and a send gate that stops anything from leaving without my yes. That's Inside the Nerve Center.

Each layer is still a model in a loop, using tools, keeping its memory in files. If you remember one sentence from this page: a harness turns a model that can only talk into an agent that can do.

**Next:** [Install Claude Code](/docs/start-here/install-claude-code/)
