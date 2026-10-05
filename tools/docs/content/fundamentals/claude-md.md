---
title: "CLAUDE.md: teaching the agent your rules"
description: "Global vs project CLAUDE.md, what belongs in each, and how to keep it small enough that the agent follows it."
section: fundamentals
group: "How it works"
order: 30
updated: 2026-10-05
sources: ["learn/tier-1/03-claude-md.mdx"]
---

`CLAUDE.md` is a plain Markdown file Claude Code reads at the start of every session. Whatever is in it becomes standing instructions: your build commands, your conventions, your hard limits. It's the cheapest way to stop repeating yourself. It is also context, not enforcement. The model reads it and usually follows it, and "usually" is the whole story of this article.

## Where CLAUDE.md files live

Claude Code looks in several places and loads them from broadest to most specific:

| Scope | Location | Use it for |
|---|---|---|
| Organization | A managed policy file your IT team deploys | Company-wide standards. You don't edit this one. |
| User | `~/.claude/CLAUDE.md` | Your rules for every project on this machine |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team rules for this repo. Commit it. |
| Local | `./CLAUDE.local.md` | Your personal notes for this repo. Keep it out of git. |

A few details that matter in practice:

- **Parent folders load at launch.** Start Claude in `repo/packages/web/` and it picks up `repo/CLAUDE.md` too.
- **Subfolders load on demand.** A `CLAUDE.md` in `repo/packages/api/` loads the first time Claude reads a file there.
- **Imports work.** Write `@docs/git-workflow.md` anywhere in the file and that file loads with it, up to four hops deep. Imports organize a big file. They don't make it cheaper, because imported files load at launch too.
- **Edits mid-session aren't guaranteed to land.** The files load at launch. Compaction re-reads the project-root file from disk, but the reliable way to pick up a change is a fresh session.
- **`AGENTS.md` is supported** if your repo already uses that convention.

Run `/init` in a new repo to generate a starter file from your codebase. Run `/memory` to open and edit what's loaded. Run `/context` to confirm a file actually loaded.

## What goes in the user file

Rules that are true no matter what you're working on:

- Who you are and how you want to be addressed in drafts
- Tool preferences ("use the `gh` CLI for GitHub")
- Hard limits ("confirm before deleting anything outside the repo")
- Engineering habits ("smallest change that fixes the bug")

## What goes in the project file

Rules that are only true here:

- How to build, test and lint, as exact commands
- Where things live
- What not to touch
- How to log work when it ships

Here's a project file I'd hand to a new agent today:

```markdown
# Project: invoice-parser

## Commands
- Install: `uv sync`
- Test: `uv run pytest -q` (run before every commit)
- Lint: `uv run ruff check . --fix && uv run ruff format .`

## Layout
- Parsers: `src/parsers/`, one file per vendor
- Fixtures: `tests/fixtures/`, real (scrubbed) invoices only

## Rules
- Work on a branch. Never commit to main.
- Fix the bug you were asked to fix. Don't refactor neighbors.
- A new parser ships with a fixture test from a real invoice.
- Never print or log a full invoice; they contain customer data.

## When you ship
- Add one line to CHANGELOG.md: what changed and why.
```

Notice what's not in it: no essay about values, no "be helpful", no paragraph the model would agree with and then ignore. Each line is something you could check.

## Write rules you can verify

"Use 2-space indentation" works. "Format code properly" doesn't. "Run `pytest -q` before committing" works. "Test your changes" doesn't. If you can't tell from the diff whether the rule was followed, the model can't tell either.

Contradictions are worse than vagueness. If your user file says one thing and your project file says another, the model may pick either one. Review both every so often. `/doctor prompt-audit` (in recent versions) will look for outdated and conflicting instructions for you and propose edits.

## Keep it small

The docs suggest keeping each CLAUDE.md under about 200 lines. I learned why the hard way.

My main project CLAUDE.md grew one reasonable paragraph at a time. Every incident got a dated write-up. Every new rule got a section with its backstory. In late September 2026 the file hit 122,283 bytes, roughly 30,000 tokens, loaded into every session that started in that repo. Every single append made sense. Nobody looked at the total.

Now a check runs at commit time, not in a weekly report nobody reads:

- A hard ceiling on the file's size (64,000 bytes)
- A cap on how much one commit can grow it (1,500 bytes)
- A refusal when someone pastes a dated incident write-up into it

Incident history moves to an archive folder, and the rule that came out of the incident stays in CLAUDE.md with a one-line pointer to the full record. The file says, at the top, that it's kept small on purpose.

## Put the rule where the agent will load it

This one cost me more than size did. A rule only reaches an agent that loads the file it's written in.

My domain agents each start in their own folder, outside the main repo. They load the user-level file and their own folder's file. They never see the main repo's CLAUDE.md. So rules I'd written there reached the main agent and nobody else, and I kept wondering why a domain agent ignored something I had "already fixed." In August 2026 one of those agents was asked to do a routine task, had no idea the capability existed, and silently did nothing.

Now the rules every agent must follow live in the user-level file, and several of them open with a note explaining that they live there on purpose. The same thing bit me from another direction in September: a rule lived in a context file my sessions load at startup, but the loader truncated that file above the section where the rule sat. A rule below a truncation point is not a rule.

Ask of every rule: which agent needs this, and does that agent load this file?

## Prose rules fade. Important rules get a hook.

A CLAUDE.md rule competes with everything else in the context window. Early in a session it's fresh. Ninety minutes and 300K tokens later, it's one paragraph among thousands. Under pressure, a model will skip a rule it would have followed in turn one.

So the rules where a miss is expensive get a second layer. In my system "never raw-restart the session supervisor" is written in CLAUDE.md, and a PreToolUse hook also blocks the command. The prose explains why. The hook makes sure. The official docs say the same thing directly: to block an action regardless of what the model decides, use a hook.

The split I use:

| Mechanism | What it's for |
|---|---|
| CLAUDE.md | Context, conventions, commands, the reasons behind rules |
| Skill | A procedure you only need sometimes, loaded on demand |
| Hook | Anything that must happen, or must never happen, every time |
| Settings | Permissions: what's allowed, asked or denied |

> **Note:** If a rule matters only for one part of the repo, a path-scoped rule in `.claude/rules/` or a nested CLAUDE.md keeps it out of every other session's context.

**Next:** [Tools 101](/docs/fundamentals/tools/)
