---
title: "Personal context files"
description: "Four files that tell every agent who you are, how you decide, how you write and what you never do. Plus five skills."
section: nerve-center
group: "Memory and context"
order: 130
updated: 2026-10-05
sources: ["learn/tier-3/c4-pca-personal-context-artifacts.mdx", "articles/personal-ai-os.mdx"]
---

An agent can have every tool and every file it needs and still produce the wrong thing for you: a draft in the wrong voice, a recommendation that contradicts how you think about risk, an action you'd never have approved. It has the tools. It doesn't know you. Four Markdown files fix most of that, and I've published starter templates for them.

I call them personal context artifacts. Every agent in my system that decides or drafts on my behalf loads them.

## What you'll learn

- The four files and the one question each answers
- Why they're four files and not one
- How agents load them without blowing the context budget
- What went wrong, and how to start with the public kit

## The four files

| File | Question | What goes in it |
|---|---|---|
| Wiki | Who am I? | Roles, background, the areas of life and work, current projects, the people who matter most right now |
| Mental models | How do I decide? | Priors on money, time, risk, energy and work. The frames you apply when there's no time to think |
| Voice | How do I write? | Real examples of text you'd send, real anti-examples you never would, rules per channel |
| Protocols | What do I never do? | Hard rules. Short on purpose. Breaking one is an error, not a judgment call |

Here's what entries look like. These are invented for illustration, not copied from my files:

```markdown
## Mental models
- Reversible beats perfect. For anything I can undo in a day, ship at 80% now.
- Existing tooling before new tooling. Ask "what do we already have?" first.

## Protocols
- No purchase over a set amount without a 24-hour cooldown.
- Never commit someone else's time without asking them first.
- Nothing goes out under my name without my yes on the exact text.
```

The voice file is the one I've iterated on most, and two of its rules are already public on this site: no em-dashes, and the first sentence carries the point. The format that works is examples, not adjectives. "Write concisely" does nothing. Ten real messages you sent, ten drafts you hated with a one-line reason each, and rules per channel (a text, a cold email, a post) do a lot.

## Why four files, not one

Different agents need different slices, and each file changes at a different rate.

- **The wiki** is broad and factual. The CEO agent and anything that routes work reads it.
- **Mental models** are for agents that recommend. When a recommendation conflicts with a stated prior, the agent should surface the conflict instead of quietly picking a side.
- **Voice** is only for agents that write as me. Loading it for a status check wastes budget.
- **Protocols** are for anything that acts. They stay short because a long list of hard rules isn't a list of hard rules anymore. If it's a preference, it belongs in mental models.

## How agents load them

The instruction file every session reads says the four files are required for any session that drafts as me, decides for me, or surfaces information to me. Rules in a file are only half of it, though. The other half is how the context gets into the prompt.

For the CEO agent, the context is assembled when the session starts. The assembler pulls the wiki, mental models, protocols and a few system files, strips boilerplate (file preambles, restatements of rules that already live elsewhere), and caps the result at about 16,000 characters. The voice file is added only for drafting tasks. The result goes in as system prompt, not as the first chat message, after a July audit found a 12,000-character context dump showing up as the opening "message" in every cockpit chat.

Outbound drafts get a second check. A voice gate runs a deterministic lint first (banned phrases, the em-dash, channel-specific tells like hashtag spam or "hope this finds you well") and then an adversarial model read grounded in the voice file that scores the draft on voice, on-brand, sounds-human and not-dumb. It passes only if every score clears the bar. If the judge model is down or returns something unparseable, the draft doesn't pass on lint alone: it's marked unverified and routed to me. That changed in August, after a lint-only pass let through a draft that invented a delivery date and a budget. A gate that gets more permissive as the model gets weaker is backwards.

## What went wrong

**The voice file was being cut off.** The voice judge loaded the file with a 7,000-character cap. The file had grown past that, so the judge was reading the examples and missing about three quarters of the spec, including every anti-example. It approved drafts the anti-examples exist to catch. Now it loads the whole file. If you cap context, check what falls off the end.

**Placement is part of the rule.** A rule written only in one project's instruction file never reaches an agent started in a different directory. Some of my hard rules had to move into the user-level file that every session loads, with a note saying why they live there. Context that isn't loaded isn't context.

**The files drift.** They're static, and I update them by hand. When a draft sounds wrong, the fix is to diagnose why and add an anti-example, not to correct the draft and move on. In July I harvested a batch of my real sent emails into the voice file as grounded examples. Honest read: the voice file is the only one I maintain well. The wiki goes stale between big life changes.

**Timeline, for the record:** the four skeletons went in on May 25, 2026, as part of the executive assistant build, with gaps marked for me to fill instead of letting an agent invent details only I know. I published the templates as a public kit on July 4.

## Start with the public kit

The templates and five Claude Code skills are open source (MIT) at [jddavenportOpen/context-kit](https://github.com/jddavenportOpen/context-kit). The skills are the working layer on top of the files: CRM everything (a file per person), open loops (capture promises before they become dropped balls), watchers (notify me when a condition is true), morning briefing, and session digest (a summary the next session reads first).

```bash
git clone https://github.com/jddavenportOpen/context-kit.git
cd context-kit
bash scripts/install.sh
```

The installer copies the four templates into `~/.claude/context/` and the skills into `~/.claude/skills/`, then prints next steps. The kit also ships a starter `CLAUDE.md` template. Then reference the files from your `CLAUDE.md` so every session loads them:

```markdown
## Personal context
Read these at session start:
- ~/.claude/context/pca-wiki.md: who I am
- ~/.claude/context/pca-mental-models.md: how I decide
- ~/.claude/context/pca-voice.md: how I write
- ~/.claude/context/pca-protocols.md: my hard rules
```

Fill in the voice file first. It pays back fastest, because you'll stop rewriting every draft. Then write five protocols, not fifty.

**Next:** [Open loops: tracking every promise](/docs/nerve-center/open-loops/)
