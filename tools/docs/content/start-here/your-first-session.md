---
title: "Your first session"
description: "Open Claude Code in a folder, ask for something small, watch it read and act, and exit cleanly."
section: start-here
order: 40
updated: 2026-10-05
sources: ["learn/tier-0/04-your-first-session.mdx"]
---

This is where the tool does something. You'll make a scratch folder, start a session, ask one read-only question and one small task, watch the agent work, and leave. Ten minutes, nothing to break.

## What a session is

A session is one running conversation with the agent. While it's open, the agent remembers what you've said and can see the folder you started it in. When it ends, that working memory is gone. Files you created stay. Keep that in mind; it comes back at the end.

## Step 1: make a scratch folder and start

The agent works inside the folder you launch it from, called the working directory. Make one with nothing in it:

```bash
mkdir ~/claude-practice
cd ~/claude-practice
```

Now start Claude Code. For your first session I recommend Manual mode, which asks you before it edits a file or runs a command:

```bash
claude --permission-mode manual
```

Why the flag: on a current version of Claude Code, sessions start in **auto mode** by default. In auto mode a second model, a classifier, reviews each action instead of you, and most edits and commands run without a prompt. That's great once you know what you're looking at. On day one you want to see every step, so turn the prompts on. The status bar under the prompt shows `manual mode on` when it worked.

Above the prompt you'll see the version, the current model, and the working directory. Confirm it says `claude-practice`. If it doesn't, exit and `cd` into the right folder first.

## Step 2: ask a read-only question

You talk to it in plain English. No syntax. Type:

```text
What files are in this folder?
```

It'll say the folder is empty. That's the point. It didn't guess. It used a tool to look, and you can see the tool call in the output. Reading files inside the working directory doesn't need your permission, even in Manual mode.

## Step 3: give it a small task

```text
Create a file called notes.txt with three things a beginner should remember about Claude Code.
```

Watch what happens, in order:

1. **A short plan.** It says what it's about to do.
2. **A tool call.** A request to write `notes.txt`, with the contents shown.
3. **A permission prompt.** Because you're in Manual mode, it stops and asks. Read what it's about to write, then choose **Yes**.
4. **The result.** It writes the file and confirms.

Now check that it really happened:

```text
Show me what's in notes.txt
```

It reads the file back. You just ran the whole loop: a goal in English, the agent picked tools, asked before acting, did the work, and you verified the result on disk. Everything else in these docs is that loop with more tools and fewer prompts.

## Step 4: a few controls worth knowing

| Key or command | What it does |
|---|---|
| `Esc` | Stops the current response or tool call so you can redirect. Work done so far is kept. On a permission prompt it means No. |
| `Shift+Tab` | Cycles the permission mode for this session |
| `/help` | Lists available commands |
| `/status` | Shows version, model, and which account is signed in |
| `/clear` | Starts a fresh conversation in the same session |
| `/exit` | Leaves Claude Code (so does `Ctrl+D` pressed twice) |

`Esc` is the one to build a reflex for. If the plan in step 1 isn't what you meant, stop it there instead of waiting for it to finish the wrong thing.

## Step 5: exit, then come back

Type `/exit`. The session closes.

Look in the folder. `notes.txt` is still there, because it's a file. The conversation isn't. That's the lesson in one move: **the chat evaporated, the file survived.**

You can pick a conversation back up. From the same folder:

```bash
claude -c
```

That continues your most recent conversation in this directory. `claude -r` lets you choose an older one. Ask "what did we just do?" and it'll know about the notes file.

## What the session forgets

Honest read: resuming is handy, but don't build on it. A conversation is a fragile place to keep anything that matters. Context windows fill up and get summarized, sessions end, and the next agent you start won't have read your old chat at all.

The fix is simple and it's the most important habit in these docs: anything that has to outlast a session goes in a file. Decisions, rules, progress, what's left to do. The agent reads files on demand, so a good file beats a long conversation every time. My own system runs on that rule. Agent sessions get replaced constantly; the files, tables and logs they write are what make the organization remember. [Files as state](/docs/fundamentals/files-as-state/) covers it properly.

**Next:** [The working directory and your first edit](/docs/start-here/your-first-edit/)
