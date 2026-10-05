---
title: "Worktree isolation: the hard lesson"
description: "Why parallel agents need their own git worktrees, the incidents that proved it, and the machine-enforced fix that replaced a prose rule."
section: patterns
group: "Agents"
order: 40
updated: 2026-10-05
sources: ["learn/tier-2/03-worktree-isolation.mdx"]
---

Two agents sharing one git checkout will eventually move the branch out from under each other. Neither will notice. Give every agent that can touch git its own worktree, and enforce it with hooks and watchdogs, because a sentence in an instruction file did not survive contact with parallel agents in my system. I tried.

## What you'll learn

- What went wrong in May and June 2026
- What a git worktree is, in one command
- The nested-repo trap that isolation flags don't cover
- The machine enforcement that replaced the prose rule
- What Claude Code now does natively

## What went wrong

A git checkout has exactly one current branch. Every process working in that directory shares it. So when agent B runs `git checkout fix-b`, agent A's half-finished edits are now sitting on `fix-b`. Agent A doesn't know. Its next commit lands on the wrong branch, or its files silently revert to whatever `fix-b` had.

This happened on my cockpit repo on May 22, May 26 and May 27, 2026. Each recovery took 15 minutes or more of reading `git reflog` and cherry-picking commits back where they belonged. The fix landed May 28 (more on it below).

Then it happened again, in a worse shape. On June 8 one agent ran `git reset --hard` on a shared checkout. It wiped another agent's uncommitted edits and rewound the live code on disk to a stale version. Committed work survived. The uncommitted edits didn't. The changelog logged it as the third occurrence of the same bug class and said it plainly: "honor-system prompts proven insufficient, machine enforcement required."

Every one of those agents had been told to use a worktree. Telling wasn't the problem. An instruction is read once and competes with everything else in the context window. A hook runs every time.

## What a worktree is

`git worktree add` creates a second directory that shares the repository's history but has its own working files and its own current branch:

```bash
git worktree add ../myrepo-feat-login -b feat/login origin/main
cd ../myrepo-feat-login       # edit, test, commit here
git worktree list             # see every checkout of this repo
git worktree remove ../myrepo-feat-login
```

Agent A in one worktree and agent B in another can switch branches, reset, and commit all day without touching each other. They share commits, not working files.

## The nested-repo trap

My cockpit is its own git repository, and it lives inside the folder of my larger agent repository. When an agent got "worktree isolation," it got a worktree of the outer repo. The inner cockpit repo was still one shared checkout, used by every agent that touched it.

So isolation was on, and the incidents kept happening. If you nest repositories, check which one your isolation actually covers. It's almost always the outer one.

## The machine fix

Here's what replaced the prose rule, in the order an agent hits it:

1. **A preflight that refuses to guess.** Before any isolated agent edits anything, it runs a script that confirms which repo it's in. A session rooted in several directories at once can hand an agent a worktree of the wrong repo. The preflight prints the right worktree path, creating one if needed, and exits with an error if it can't tell. Blind is a failure, never a pass.
2. **A per-agent worktree wrapper.** One command creates a worktree for a named branch inside the nested repo, prints the path, and is safe to run twice. It refuses a base that's more than 25 commits behind `origin/main`, because a stale base produces merge pain later. The fix is to rebase, not to override.
3. **A pre-commit hook on the shared checkout.** It refuses commits made there; commits from a worktree pass. Even an agent that ignores everything above gets stopped at the commit.
4. **A watchdog every five minutes.** If the shared checkout has sat on a branch other than `main` for five minutes, it stashes any uncommitted work (saved, not deleted), puts the checkout back, and pages me with the stash reference.

The outer repo had the same problem at a larger scale: around ten sessions run from its one shared checkout. It got its own set of guards:

- **No branch switching on the shared root.** Since June 26, 2026 no session may switch that checkout's branch; anything that needs another branch gets a worktree. A watchdog puts the root back on the live branch after five minutes of drift.
- **A checkout log.** A post-checkout hook records every branch switch on the shared root and the process chain that caused it, so the next incident comes with a culprit.
- **Lossless sync.** Since September 2, the shared root updates itself only when that can't clobber local work, and any edit left untouched for 24 hours gets parked on a local branch with a ticket saying where it went.

One small habit belongs here too. When many sessions share an index, `git add mine && git commit` can sweep in files someone else staged. Use:

```bash
git commit --only -- path/to/my-file.ts path/to/my-test.ts
```

### A guard that silently never fires

After the cockpit was renamed in June, its folder became a symlink to the old physical path. The hook installer compares the repo's top-level path against the expected one, and git reports the physical path, not the symlink. So a fresh install of the hook would never fire. Nothing errors. It just doesn't stop anything. My instructions now say not to reinstall it until that comparison resolves real paths.

> **Warning:** Test that a guard fires, not just that it installs. A hook that never triggers looks exactly like a hook with nothing to catch.

## What Claude Code does natively now

When I built this, isolation was mostly my own scaffolding. As of October 2026, Claude Code has worktrees built in ([docs](https://code.claude.com/docs/en/worktrees)):

- `claude --worktree feature-auth` starts a session in a new worktree under `.claude/worktrees/`, on a new branch.
- A custom sub-agent with `isolation: worktree` in its front matter always gets its own temporary worktree, removed automatically if it made no changes.
- While a session is isolated, Claude Code blocks edits that target the main checkout, commands whose working directory is the main checkout, and git redirected into it (`git -C`, `GIT_DIR` and similar).
- New worktrees branch from your default branch unless you set `worktree.baseRef` to `"head"`.
- A `.worktreeinclude` file copies gitignored files like `.env` into each new worktree.

Start there. It covers the common case with zero scripts. My reading of the docs is that the checks apply to the repository you launched from and the checkout a linked worktree comes from. A separate repo nested inside it is still yours to handle, which is exactly where my incidents came from.

## The finding that surprised me

My fleet supervisor, worktree plus tmux for parallel Claude Code instances, landed on April 29, 2026. Then it went largely unused: only a handful of worktree-agent branches merged in the following two months. Parallel work took off in June, and so did the collisions.

Building the capability wasn't the bottleneck. Adopting it was, and adoption is what exposed every place the isolation leaked. Expect your incidents to start when parallelism becomes routine, not when you first build it.

## Checklist before you run agents in parallel

- Every agent that may write files or run git gets its own worktree. Read-only research agents can skip it.
- Each prompt says: "You are in a worktree. Confirm with `pwd`. Don't touch other branches."
- Nested repos get their own per-agent worktrees.
- A hook refuses commits on the shared checkout, and you've watched it refuse one.
- Each agent commits in its own worktree; the parent integrates with `git merge --ff-only <branch>` or a PR, never by checking out the agent's branch in the shared directory.

[Git discipline for agents](/docs/fundamentals/git-for-agents/) covers the everyday habits around this.

**Next:** [Orchestration: delegate down, verify up](/docs/patterns/orchestration/)
