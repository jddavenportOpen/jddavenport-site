---
title: "Clawdling: the open engine"
description: "The open-source, bring-your-own-key personal AI OS engine extracted from my private system, and what it leaves out."
section: builds
group: "Open source"
order: 170
updated: 2026-10-05
sources: []
---

Clawdling is the open-source version of the idea behind my private system: a personal AI cockpit you run on your own machine, with your own key, where the agents act on your tasks and memory instead of just chatting. It's at [jddavenportOpen/clawdling](https://github.com/jddavenportOpen/clawdling), licensed AGPL-3.0, and it's the engine under Clawdascended, a hosted product I'm building that is still early.

My private system can't be open-sourced. It runs my actual life and work, and it's wired into my accounts and machines throughout. Clawdling is what you get when you rebuild the useful core so a stranger can run it from a fresh clone. This page covers what's in it, what's deliberately not, and the bugs that only showed up when I tested it as a stranger.

## What you'll learn

- The three ways to use it: chat, cockpit and workers
- What the open engine includes and leaves out
- How to install it and what it costs to run
- Why "extract the core" turned into "rebuild the core"

## Three modes

**Chat mode.** A web cockpit around an agent that can act. Five acting tools are on out of the box: create a task, list tasks, complete a task, remember a fact, recall it later. Everything lives in plain JSON files on your disk. No database, no account. Your Anthropic API key pays for every call, directly. This mode needs nothing but Node.

**Cockpit mode.** Many real Claude Code sessions at once, side by side in one screen. Each pane is an actual `claude` process on your machine, scoped to one area of your life with its own agent prompt and its own working directory. Spawn them, tile them, drive them from your phone. This needs a small local bridge service and the Claude Code CLI, signed in to your own Claude plan.

**Workers.** The same bridge pointed the other way. A pane is a conversation you sit in. A worker is a job you hand off: give it an objective and a domain agent, it runs headless and you read the outcome later.

| | Pane | Worker |
|---|---|---|
| You are | attached, typing | gone |
| It runs | in a terminal | headless |
| It stops when | you close it | it finishes or hits its deadline |
| It writes in | the folder you chose | its own git worktree, on its own branch |
| It remembers the task via | the conversation | a `WORKPLAN.md` on disk |

Every worker choice in that table comes from a failure in my own system. Two agents writing in one checkout share an index and a `HEAD`, and the second one to switch branches destroys the first one's work, so workers get their own worktree. An unattended run outlives its own context window, so the task lives in a file. An unattended run with no deadline is how you end up with a process nobody remembers starting, so there's a 30-minute ceiling by default. And when a folder isn't a git repo, the run says `isolation: none` and why, instead of claiming isolation it didn't get. More on the pattern in [Worktree isolation: the hard lesson](/docs/patterns/worktree-isolation/).

## Install

You need Node 24. The Claude Code panes also need Python 3.10 or newer and the Claude Code CLI.

```bash
git clone https://github.com/jddavenportOpen/clawdling.git && cd clawdling
./install.sh      # checks Node, writes .env, asks for your Anthropic key, installs deps
make run          # starts the cockpit
```

First boot seeds a welcome thread that walks you through the tools. No key yet? Set `ADJUTANT_MOCK=1` in `.env` and chat streams a canned reply at zero cost so you can look around.

For the Claude Code panes, in a second terminal:

```bash
make bridge-install   # once: a Python venv for the bridge
make bridge
make domain ID=health LABEL=Health BLURB="Training, food, and sleep"
```

The last line adds a domain agent with a prompt template you then edit to give it a real scope.

> **Warning:** The bridge can run commands on your machine. By default both the cockpit and the bridge listen on the loopback address only, and single-user mode has no login. Read the remote-access doc's lockdown section before you expose either one to a network.

### What it costs

Nothing is free and nothing phones home. Chat meters against your own Anthropic API key, and you pick the model and effort in `.env`. Panes and workers run the `claude` CLI on your own Claude plan, which is ordinary use of Claude Code by you. The README says it plainly and so will I: don't use it to give other people access to your subscription. For anything beyond your own single-user install, use API keys.

## What it leaves out

Clawdling is the engine only. It doesn't include, and never calls home for:

- **The builder**, the "describe it and it builds and ships it" self-modification loop
- **Billing, usage metering or subscriptions**
- **Hosted, multi-tenant provisioning** with managed sign-in
- **Premium domain packs**, the curated ready-made bundles

Those are the managed layer of the hosted product. The line is deliberate: everything you need to run it yourself is open, and the parts that only make sense as a service are not.

## Extracting the core meant rebuilding it

The first public version went out on July 7, 2026, with a known-issues file and a fresh, leak-scanned history. It worked for chat. Cockpit mode didn't. The interface for panes had shipped with no backend at all, so every pane was dead on arrival.

The obvious fix was to carve the bridge out of my private system. I looked, and the private session route alone pulled in more than 25 internal modules, plus account routing and domain-seat logic a stranger has no use for. Carving it would have dragged most of a very large codebase along. So in mid-September I wrote a new, small bridge instead: one thread per session, bounded fan-out to viewers, a byte ring replayed when you reattach, signed tokens, working-directory containment, no shell, loopback bind, and it refuses a weak secret. Pane history survives a bridge restart, even a hard kill, and resuming a pane restores the model's own context. Nothing is resurrected behind your back: a restored pane comes back as a readable record you choose to resume.

Honest read: "extract the open-source core" is almost always "rebuild a smaller core from scratch, using the private one as a spec." Plan for that from day one and you'll save yourself a summer.

## What testing as a stranger found

Agents that built the code tested it in the environment they built it in. That's how two of these survived.

### A false caveat, public for 70 days

From July to September the README said production builds were blocked by an upstream Next.js bug. It wasn't true. The real cause was `NODE_ENV=development` exported in the shell the agent built from, which makes the static export run against React's development bundle and crash. The control tests that "confirmed" the framework theory all ran in that same shell, so the environment variable was never a suspect. Re-tested on September 16: same tree, same command, unset the variable and the build works. The known-issues file now says what happened, including that the old diagnosis was wrong.

### A child that inherited the wrong identity

A bridge started from inside a Claude Code session inherits that session's environment, including a variable that tells the CLI it's a sub-agent. Every pane then thought it was a sub-agent and saved no transcript at all. The bridge now builds each child's environment explicitly instead of passing its own through.

### The cold-clone pass

On September 29 I tested it the way a stranger would: anonymous clone of the public repo, Node 24, a real browser. It found:

- Live panes showed "Stopped", because the bridge said `running` and the interface expected `live`.
- Loading the whole `.env` into the bridge moved the panes onto the chat API key, and they failed authentication. The bridge now reads only its own settings, so your API key never reaches a pane.
- The README documented chat engines that didn't exist anymore.

All fixed the same day. Before every publish, an export pipeline runs a leak gate over the tree. In September it caught internal system names in public code comments and a few high-entropy test secrets that looked real enough to alarm a scanner. Both were cleaned before they went out.

## Where it stands

Alpha, verified end to end for chat, tools, panes, pane history across a restart, and headless workers, with honest gaps written down. Some domain dashboards aren't wired for a fresh install and render empty. If you want an assistant that does things, keeps its data on your disk, and has you pay Anthropic directly, it's a real starting point. If you want it hosted and managed, that's what Clawdascended is for, when it's ready.

**Next:** [recruit-copilot: a job search as a verification problem](/docs/builds/recruit-copilot/)
