---
title: "Skills: packaged know-how the agent loads on demand"
description: "What a skill is, how SKILL.md works, when a skill beats a prompt or a rule, and how to build and test one."
section: fundamentals
group: "Extending Claude Code"
order: 70
updated: 2026-10-05
sources: ["learn/tier-1/07-skills.mdx", "tutorials/building-skills.mdx", "articles/unified-skill-registry.mdx"]
---

A skill is a folder with a `SKILL.md` file in it: a short description of when to use it, then the instructions to follow. Claude Code keeps the descriptions in view and loads the full instructions only when a skill is relevant, or when you type `/skill-name`. If you've typed the same multi-step request three times, that's a skill waiting to be written.

## What you'll learn

- How skills load, and why that makes them cheap
- Where skill folders live and what the frontmatter does
- When a skill beats CLAUDE.md, a hook or a plain prompt
- A complete worked example: a GitHub issue triage skill
- How to test one before you trust it

## How a skill works

At session start, Claude Code reads the `description` of every available skill and keeps that short list in context. The body of the skill stays on disk. When your request matches a description ("triage the open issues on this repo"), Claude loads that skill's full instructions and follows them. You can also call one directly with `/name`.

That two-step loading is the point. A CLAUDE.md rule costs context in every session. A skill costs one line until the moment you need it. So procedures you need sometimes, like how to cut a release or how to write a weekly report, belong in skills, not in CLAUDE.md.

Custom slash commands have been folded into skills. A file at `.claude/commands/deploy.md` still works and still creates `/deploy`, but a skill folder can also hold scripts, templates and reference files next to the instructions.

## Where skills live

| Scope | Location | Who gets it |
|---|---|---|
| Personal | `~/.claude/skills/<name>/SKILL.md` | You, in every project on this machine |
| Project | `.claude/skills/<name>/SKILL.md` | Everyone working in this repo (commit it) |
| Nested | `<subfolder>/.claude/skills/<name>/SKILL.md` | Loads when Claude works in that subfolder |
| Plugin | Inside an installed plugin | Wherever the plugin is enabled, as `/plugin:name` |

Run `/skills` in a session to see what's available and how much context each one costs.

## The frontmatter that matters

```yaml
---
name: release-notes
description: Draft release notes from merged PRs since the last tag. Use when asked for release notes, a changelog for a version, or "what shipped since v1.4".
argument-hint: "[since-tag]"
allowed-tools: Bash(git log *) Bash(gh pr list *)
disable-model-invocation: false
---
```

- **`description`** is the most important line you'll write. It's how Claude decides to use the skill. Put the main use case first, then the phrasings people actually use.
- **`allowed-tools`** pre-approves specific tools while the skill runs, so a read-only skill doesn't stop to ask permission for every command.
- **`disable-model-invocation: true`** means only you can trigger it with `/name`. Use it for anything with side effects you want to start on purpose, like a deploy.
- **`argument-hint`** shows up in autocomplete. Inside the body, `$ARGUMENTS` holds what you passed, and `${CLAUDE_SKILL_DIR}` points at the skill's own folder so it can call its own scripts.

Everything is optional except that you really want a description. A field name that doesn't match exactly is silently ignored, so copy names from the docs.

## When a skill is the right tool

| You want | Use |
|---|---|
| A fact or rule true in every session ("tests run with `pytest -q`") | CLAUDE.md |
| A procedure you need sometimes ("how we triage issues") | A skill |
| Something that must happen, or must never happen, every time | A hook |
| A new capability the agent doesn't have (a database, an API with OAuth) | An MCP server or a CLI |
| A one-off request | Just ask |

## Worked example: a GitHub issue triage skill

The old version of this tutorial built the same thing for a different harness, with hand-rolled curl scripts and a registry file. On Claude Code it's one folder and the `gh` CLI. You need `gh` installed and signed in (`gh auth status` should say so).

### 1. Make the folder

```bash
mkdir -p .claude/skills/triage-issues
```

### 2. Write SKILL.md

Save this as `.claude/skills/triage-issues/SKILL.md`:

```markdown
---
name: triage-issues
description: Triage open GitHub issues for a repo and draft replies. Use when asked to triage, sort, summarize or check open issues, or "what's open on <repo>".
argument-hint: "[owner/repo]"
allowed-tools: Bash(gh issue list *) Bash(gh issue view *) Bash(gh auth status)
---

# Triage open issues

Repo: $ARGUMENTS. If empty, use the repo in the current directory.

## Steps
1. Run `gh auth status`. If it fails, stop and say gh needs `gh auth login`.
2. List open issues:
   `gh issue list --repo <repo> --state open --limit 50 --json number,title,labels,createdAt,comments`
3. For each issue with no labels, read it: `gh issue view <number> --repo <repo>`.
4. Put each one in exactly one bucket: bug, feature request, question, needs info, duplicate.
5. For "needs info" and "question," draft a short reply. Don't post it.
6. Write the report to `triage/<today>.md` in the format below.

## Output format
- One table: number, title, bucket, one-line reason.
- Under it, each drafted reply with its issue number.
- Last line: counts per bucket.

## Rules
- Never comment, label, assign or close. Draft only.
- If there are more than 50 open issues, say so and triage the newest 50.
- If there are none, write one line saying so and stop.
- If an issue might be a security report, don't summarize its details. Flag it for a human.
```

Notice the rules section. The skill can read freely (those commands are pre-approved) but it can't change anything on GitHub. If you later say "post the reply on #42," Claude will ask permission for `gh issue comment`, because that command isn't in `allowed-tools`. Reading is automatic. Writing to someone else's tracker needs a yes.

### 3. Try it three ways

1. **Directly:** `/triage-issues your-org/your-repo`
2. **By description:** "what's open on your-org/your-repo?" Check that Claude picks up the skill instead of improvising.
3. **On an edge case:** a repo with zero open issues, and one with more than 50. A skill that falls apart on missing data is worse than no skill.

Then read the report it wrote. If the buckets are wrong, the fix is almost always in the instructions: a sharper definition of "needs info," an example of a borderline case.

### 4. Add a script when the steps get mechanical

If step 2 grows into filtering and sorting, move it into `scripts/` inside the skill folder, make the script print JSON, and call it as `${CLAUDE_SKILL_DIR}/scripts/open-issues.sh`. Agents parse structured output more reliably than prose, and a script can be tested on its own.

## Writing skills that hold up

- **Say what done looks like.** "Write the report to `triage/<date>.md`" beats "summarize the issues."
- **Name the files and commands.** "Run `gh issue list ...`" beats "look at the issues."
- **Write down the edge cases.** Missing auth, empty results, too many results, stale data.
- **Keep side effects behind a human.** Draft, then ask. Or set `disable-model-invocation: true`.
- **Write it for a smart new hire.** If a step is ambiguous, the agent will guess, and it will guess confidently.

## A short history: the registry I don't run anymore

In April 2026 I built a unified skill registry: one YAML file meant to index every capability across OpenClaw (an open-source agent framework I was experimenting with at the time), Claude Code and my MCP servers, so any orchestrator could discover any skill. It was a reasonable idea while I was bridging several harnesses. Then I retired the OpenClaw bridge in June 2026 (my system had always run on Claude Code), and the hand-maintained index went stale the way every hand-maintained list does.

What replaced it is better: the public [capabilities showcase](https://nerve-center-showcase.vercel.app) regenerates every day from the live system, skills included. Nobody edits it. If a skill exists, it shows up. If it's deleted, it disappears. Generate your inventories from what exists.

## Skills you can copy

- [context-kit](https://github.com/jddavenportOpen/context-kit) ships skill files for a personal setup: keeping a file per person, tracking open loops, watchers, a morning briefing and a session digest, plus four personal context templates.
- [agent-evals-starter](https://github.com/jddavenportOpen/agent-evals-starter) includes an agent eval skill in `.claude/skills/agent-evals/` that walks the [agent evals](/docs/ai-core-skills/agent-evals/) method step by step and stops at the human gates on its own.

**Next:** [Hooks: rules the model cannot forget](/docs/fundamentals/hooks/)
