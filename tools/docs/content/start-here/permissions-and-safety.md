---
title: "Permissions and safety basics"
description: "Permission prompts, allow rules, permission modes, what skipping permissions really means, and why destructive actions get a human yes."
section: start-here
order: 60
updated: 2026-10-05
sources: ["learn/tier-0/06-permissions-and-safety.mdx"]
---

An agent that can edit files and run commands can also delete files and run the wrong command. The permission system decides which actions happen on their own and which stop and ask you. This page covers the prompt, the modes, the rules, and the one rule I run my whole system on: anything destructive gets a human yes, and a machine enforces that.

## The prompt

In Manual mode, when the agent wants to edit a file, run a command, or fetch from the web, it stops and shows you a prompt: what it wants to do, and your options. For a shell command it looks roughly like this:

```text
Bash command
  npm test
  Run the test suite

Do you want to proceed?
  1. Yes
  2. Yes, and don't ask again for: npm test *
  3. Yes, and switch to auto mode
  4. No
```

- **Yes** approves this one action.
- **Yes, and don't ask again** saves an allow rule so the same kind of action runs without a prompt next time.
- **Switch to auto mode** approves it and hands future checks to the classifier (more below). Not every prompt offers it.
- **No** (or `Esc`) declines. Press `Tab` on Yes or No to add a comment the agent will see.

Decide by reversibility. Reading a file is free. Writing a new file is cheap. Deleting something or changing system state deserves a slow, careful look. When unsure, approve once instead of "don't ask again."

## Permission modes

The mode sets the baseline for what runs without asking. Press `Shift+Tab` to cycle modes during a session, and watch the status bar to see which one you're in. Names and behavior below are from the [official docs](https://code.claude.com/docs/en/permission-modes) as of October 5, 2026.

| Mode | Runs without asking | Use it for |
|---|---|---|
| Manual (`default`) | Reads only | Learning, sensitive work, unfamiliar code |
| `acceptEdits` | Reads, file edits, basic file commands | Iterating on code you're watching |
| `plan` | Reads; no edits until you approve a plan | Exploring before changing anything |
| `auto` | Most things, with a classifier model reviewing each action | Longer tasks where you trust the direction |
| `dontAsk` | Only pre-approved tools; everything else is denied | Locked-down scripts and CI |
| `bypassPermissions` | Everything | Isolated containers and VMs only |

On current versions, auto mode is the default starting mode in the terminal. Anthropic's own warning on it is worth repeating: auto mode reduces prompts but does not guarantee safety. Use Manual while you learn what normal looks like.

## What "skip permissions" really means

`bypassPermissions` (the `--dangerously-skip-permissions` flag) turns the prompts off almost entirely, including for writes to protected folders like `.git`. The official guidance is to use it only inside a container or VM where the agent can't damage anything that matters. That's the right guidance. The name has "dangerously" in it for a reason.

If you ever run unattended, the order of safety is: an isolated environment first, a version-controlled folder second, a narrow working directory third, and permissions turned down only after all three.

## Rules: allow, ask, deny

Modes are the baseline. Rules are the exceptions you write down. Open `/permissions` to see and edit them.

- **Allow** rules let a specific tool or command run without a prompt, for example `Bash(npm run build)`.
- **Ask** rules always prompt, even in modes that normally wouldn't.
- **Deny** rules block, in every mode, including bypass.

They're checked in a fixed order: deny, then ask, then allow. A broad deny like `Bash(rm *)` beats a narrow allow, every time.

You can also write rules into a settings file, which is how they end up in a project's repo where everyone gets them. This `.claude/settings.json` lets the agent build and commit without asking, and blocks every push:

```json
{
  "permissions": {
    "allow": ["Bash(npm run *)", "Bash(git commit *)"],
    "deny": ["Bash(git push *)"]
  }
}
```

[settings.json and permissions config](/docs/fundamentals/settings-and-permissions/) covers where these files live and which one wins.

The single most useful sentence in the official permissions docs: permission rules are enforced by Claude Code, not by the model. Writing "never delete anything" in your instructions shapes what the agent tries. A deny rule decides what it can actually do.

On macOS, Linux and WSL2 there's also a built-in sandbox for shell commands (`/sandbox`) that limits which files and network hosts a command can reach. It's a second wall behind the permission rules, and it works with any mode.

## The rule I run on

Confirm before anything destructive: deleting files, force-pushing git, dropping a database table, restarting something other work depends on. Reversible mistakes cost you a redo. Irreversible ones cost you the data.

The part that took me a while to learn: a rule written in prose is a wish. In July 2026 one of my agents restarted the service that supervises every agent session with a raw command instead of the guarded reload script. Every live session died in the same two seconds, a dozen of them, including the one that ran the command. The guarded script existed. Using it was on the honor system, and nothing stopped the agent from going around it.

The fix was a hook: a small script Claude Code runs before every tool call, which blocks that command outright no matter what the model believes it's allowed to do. Reload scripts now refuse to run while sessions are live, and a detector pages me if several sessions die at once. Hooks are how you turn a rule into a guarantee. [Hooks](/docs/fundamentals/hooks/) shows how to write one.

> **Note:** The same principle runs my whole system. Agents can draft anything. Nothing goes out to another person, and no money moves, without my explicit yes, and that's enforced by code, not by instructions.

## Two safety nets you already have

1. **The working directory.** Start the agent in the right project and a lot of damage is impossible by construction.
2. **Git.** Commit before the agent edits and every change is reviewable and reversible.

Keep the prompts on while you learn. Earn your way to fewer of them: tight folder, version control, deny rules for the things that bite, and a way to see what happened afterward.

**Next:** [Reading the output](/docs/start-here/reading-the-output/)
