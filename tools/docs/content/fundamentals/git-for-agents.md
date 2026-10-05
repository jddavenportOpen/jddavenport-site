---
title: "Git discipline for agents"
description: "Branch first, commit small, never force-push, and why parallel agents on one checkout will eventually wreck each other's work."
section: fundamentals
group: "Working habits"
order: 100
updated: 2026-10-05
sources: ["learn/tier-1/10-git-discipline.mdx"]
---

Agents use git the way a fast, tireless, slightly reckless developer would. They commit wherever they're standing, write "fix stuff" as a message, and never feel bad about a force-push. With one agent that's a review problem. With several agents in the same checkout it's a correctness problem: one agent's `git checkout` moves the ground under another one mid-edit. This article covers the single-agent rules, then the setup I use to keep about ten concurrent sessions from wrecking each other.

## The single-agent rules

Put these in your CLAUDE.md, and back the important ones with settings.

1. **Branch first.** No edit happens on `main`. If the agent does something wrong on a branch, you delete the branch. If it does it on `main`, you're untangling it under pressure.
2. **Test before you commit.** The commit is a claim that the change works. Run the tests first.
3. **Commit small.** One logical change per commit: the fix, then the test, then the docs. A three-hour session in one commit can't be reviewed or partly reverted.
4. **Write the why.** The diff shows what changed. The message has to say why.
5. **Never force-push.** It rewrites history that someone else (or another agent) may have built on. Deny it in settings and back it with a hook.
6. **Stage by path, not by `git add -A`.** You want to commit what you changed, not everything that happens to be in the folder.

A commit message format that holds up:

```text
fix(orders): ship to the shipping address, not the billing address

The webhook copied order.billing_address into the shipment, so the
print vendor rejected orders with a blank line1. Use shipping_address
and add a fixture test from the failing order.
```

A type prefix, a short summary, then a body with the root cause. Agents will write this happily if your CLAUDE.md shows them an example.

## A minimal flow for one agent

```bash
git switch main && git pull
git switch -c fix/shipping-address

# agent edits files

uv run pytest -q                       # prove it
git add src/orders/webhook.py tests/test_webhook.py
git commit -m "fix(orders): ship to the shipping address"
git push -u origin fix/shipping-address
```

Who merges is a choice. When you're starting out, you review and merge. In my system I don't review diffs at all. I review the product in production. Agents open the PR, separate reviewer agents review it (one of them is told to try to reject it), CI gates run, and the orchestrating session merges, deploys and smoke-tests prod before telling me what to click. That's a later step, covered in [ship to prod](/docs/patterns/ship-to-prod/). Start with you merging.

## The parallel-agent problem

Here's the race. Two agents work in the same folder. Agent A runs `git switch feat/a` and starts editing. Agent B, on a different task, runs `git switch feat/b`. The working tree changes under A. A's next edits land on B's branch, or A's uncommitted work gets carried along to a branch it was never meant for.

Nothing errors. Git did exactly what it was told. You find out later, by reading the reflog and cherry-picking commits back to where they belong.

This happened to me in May 2026, with several sessions sharing one checkout of my cockpit repo (the web app I use to run my agents). By May 28, per-agent worktrees on that checkout were machine-enforced, not a guideline.

## Worktrees fix it

A git worktree is a second working folder attached to the same repository, with its own checked-out branch. Switching branches in one worktree doesn't touch any other.

```bash
git worktree add ../myrepo-fix-shipping -b fix/shipping-address
cd ../myrepo-fix-shipping
```

Claude Code has this built in:

```bash
claude --worktree fix-shipping
```

That creates a worktree under `.claude/worktrees/fix-shipping/` on a new branch and starts the session inside it. Subagents can get the same isolation with `isolation: worktree` in their definition. Add `.claude/worktrees/` to `.gitignore`.

One rule makes the rest work: **the main checkout stays on its branch.** Nobody switches it. Everyone who needs a different branch gets a worktree.

## What my setup adds on top

Worktrees are the core. The rest is guards for the ways agents still got it wrong. Described by what they do:

- **A wrapper that creates the worktree.** An agent asks for a worktree for its branch and gets a path back. If the branch's base is far behind `main`, the wrapper refuses and says to rebase first, instead of letting an agent build on a stale tree.
- **A preflight that refuses to guess.** One session can span several repos. Early on, an agent got handed a worktree of the wrong repo and then every git command it ran was refused. Now the first thing an isolated agent runs is a preflight that confirms which repo it's in, and exits with an error if it can't tell. Blind is a failure, never a pass.
- **Nested repos get their own worktrees.** My cockpit is its own repo, nested inside the main agent repo. A worktree of the outer repo doesn't isolate the inner one, so every agent touching the cockpit still shared one checkout until I added a separate worktree wrapper for it.
- **A pre-commit hook on the shared checkout.** Commits made directly in the shared cockpit checkout are refused. Commits from a worktree pass.
- **A watchdog.** If the shared checkout drifts off its branch for more than about five minutes, a watchdog stashes any work losslessly, puts it back on the right branch, and pages me.
- **Parking for orphaned drafts.** A file left modified and untouched in the shared checkout for a day gets moved to a local holding branch with a ticket saying where it went, instead of sitting there blocking every sync.

## `git commit --only`: don't sweep up someone else's work

Worktrees isolate the working tree. They don't help when several sessions commit small changes directly on the shared main branch, which my system does for low-risk edits. Those sessions share one index (the staging area).

So this is dangerous:

```bash
git add notes/my-change.md && git commit -m "docs: update notes"
```

If another session staged its own file a minute ago, your commit just took it. Your message, their change. Use this instead:

```bash
git commit --only -m "docs: update notes" -- notes/my-change.md
```

`--only` commits exactly the paths you name and leaves everything else in the index alone. Then check the file count in the output. If it says three files changed and you touched one, stop and look.

## One more trap: don't rewrite a running script

Bash reads a script as it runs, not all at once. If an agent rewrites a shell script in place (Python's `write_text`, `cat > script.sh`) while that script is running, the running process keeps reading from its old position in the new text and executes misaligned lines. On September 28, 2026 that killed a run of my push pipeline mid-flight: the log shows a "command not found" on a fragment of a word, then a step starting over. Tools that replace the file with a new one (Claude Code's Edit tool, git checkout, write a temp file and `mv` it over) are safe. For scripts that must be edit-proof, wrap the whole body in `{ ... }` ending in `exit`, so bash parses it all before running any of it.

> **Tip:** Put the never-force-push rule in three places: CLAUDE.md (so the agent knows why), a settings deny rule (so the common form is blocked), and a hook (so the variants are blocked too). Then also turn on branch protection for `main` on GitHub, because the server is the last line.

The full story of the isolation setup is in [worktree isolation](/docs/patterns/worktree-isolation/).

**Next:** [Logging and receipts: making agent work inspectable](/docs/fundamentals/logging-and-receipts/)
