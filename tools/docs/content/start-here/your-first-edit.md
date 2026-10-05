---
title: "The working directory and your first edit"
description: "How Claude Code reads and writes files in your project, and how to review a change before you accept it."
section: start-here
order: 50
updated: 2026-10-05
sources: ["learn/tier-0/05-working-directory-and-first-edits.mdx"]
---

Most real work isn't creating files. It's changing ones that already exist: a line, a value, a function. This page explains the box the agent works in, then walks one edit from request to reviewed diff, with git as your undo button.

## The working directory is the agent's world

When you run `claude` from a folder, that folder is the working directory. The agent reads freely inside it and its subfolders. Reading outside it, editing files, and running commands are what the permission system governs (next page).

What follows from that:

- **Start in the project you mean.** Launch from your home folder and the agent's world is your whole home folder. Launch from one project and it's that project. Narrower is safer and gets better answers.
- **You don't have to list files for it.** Ask "where's the config file?" and it searches. Pasting paths is optional.
- **It reads on demand.** It doesn't load your whole project up front. It opens what it needs, which is why it handles big projects fine.

> **Tip:** One folder per project, and `cd` into it before you type `claude`. It's the cheapest safety measure you'll ever adopt.

## Commit before you let an agent edit

Before the edit, make the folder a git repository and commit what's there. Git is the real undo button. Any change the agent makes becomes a diff you can inspect, keep, or throw away with one command.

```bash
mkdir ~/edit-practice
cd ~/edit-practice
printf 'Hello, World\nThis is my first project.\n' > hello.txt
git init
git add hello.txt
git commit -m "starting point"
```

You now have one file, two lines, and a saved starting point. (If git asks who you are, it prints the two `git config` commands to run. Run them, then commit again.)

## Make the edit

Start a session in Manual mode so you see the prompt:

```bash
claude --permission-mode manual
```

Have it read before it writes:

```text
What does hello.txt say right now?
```

Then ask for a specific, fenced change:

```text
In hello.txt, change "Hello, World" to "Hello, Claude Code". Leave the second line alone.
```

"Leave the second line alone" is doing real work in that sentence. Narrow asks get small diffs. Small diffs are easy to review. "Clean up this file" invites a rewrite of things you liked.

## Read the diff before you say yes

The agent doesn't silently overwrite the file. It shows you a diff: the line it wants to remove and the line it wants to add, with untouched lines around them for context. Then it waits.

Check three things:

1. **Right file.** It's editing `hello.txt`, not something else.
2. **Only what you asked.** The second line is untouched. No bonus "improvements."
3. **Correct.** The new text is what you wanted.

All three pass, approve it. If it overreached, choose No and say what was wrong. You can also add a note: highlight Yes or No and press `Tab` to type a comment that goes back to the agent with your answer.

> **Warning:** The most common beginner mistake is approving diffs without reading them. The agent is good, not infallible. Two seconds on the diff catches the wrong file, the unrequested tidy-up, and the misread instruction before they land.

## Verify, then use git to see the truth

After approving, check it outside the agent:

```bash
git diff
```

Git shows exactly what changed since your commit. That's your ground truth, independent of anything the agent tells you. Happy with it? Commit. Not happy? Throw it away:

```bash
git checkout -- hello.txt
```

Inside the session, `/diff` shows the same working-tree changes without leaving Claude Code.

## Rewind exists, but it isn't git

Claude Code also takes automatic checkpoints. Each prompt you send saves the state of the files its edit tools touch, and `/rewind` (or `Esc` twice on an empty prompt) lets you roll code, conversation, or both back to an earlier prompt.

It's useful, with one catch you need to know now: checkpoints only track edits made by Claude's file editing tools. If the agent changes files by running shell commands (`rm`, `mv`, `cp`, a script), rewind can't undo it. Changes from sub-agents usually aren't captured either. Git catches all of it. Use rewind for quick takebacks and git for anything you'd be upset to lose.

## The habit to keep

Ask for the change you want, fence off the rest, read the diff, check it with git, commit. That loop scales from one typo to a team of agents. When I run build agents in parallel on my own repos, each one works in its own git workspace, and nothing reaches the main branch without passing an automated merge gate. [Git for agents](/docs/fundamentals/git-for-agents/) covers that properly.

**Next:** [Permissions and safety basics](/docs/start-here/permissions-and-safety/)
