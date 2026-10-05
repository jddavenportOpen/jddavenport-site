---
title: "Agent evals: the short version"
description: "What top PM roles pay for agent evals, what an eval actually is, and the kit you can use tonight."
section: ai-core-skills
group: "#1 Agent evals"
order: 10
updated: 2026-10-05
sources: ["ai-roles-skills-series/day-01-agent-evals"]
---

This is day one of my AI Core Skills series. Each skill gets the same treatment: what the market pays for it, where it came from, how to do it with AI, how to check you did it right, and a kit you can actually use: prompts, agents, a Claude Code skill, a repo, and practice builds.

**The kit for this skill:** https://github.com/jddavenportOpen/agent-evals-starter
- `.claude/skills/agent-evals/`: an agent eval skill for Claude Code
- `.claude/agents/`: two agents (a task auditor and a judge writer)
- `prompts/PROMPTS.md`: ten prompts for building evals with AI
- `practice/README.md`: seven practice builds with "done when" checks
- A working support agent with 24 eval tasks, four grader types and three control agents. Runs offline in five minutes.

---

- **Top PM roles ask for it.** Anthropic's "Product Manager, Claude Science" posts $305,000 to $385,000 base and requires that you "Have personally built evals or benchmarks for model capabilities, ideally agentic or scientific ones." (Checked on Anthropic's live job board, 5 Oct 2026.) The same labs pay the same bands to PMs whose postings don't mention evals, so this is a ticket into the room, not a premium.
- **It came from a very old idea.** Since at least 1931, people have tested models on data held back from training. Agents broke the old version: you didn't train the model, it takes actions over many steps, and it answers differently every run.
- **An agent eval is not a dataset.** It's a set of tasks, each run several times in a clean environment, graded on what actually happened. Did the refund land in the database, not did the bot say "refund processed."
- **AI can build most of it.** It can draft test inputs, cluster failures, write tasks, wire graders and draft judges. Two things stay human: reading the first transcripts and labeling the examples that check the judge.
- **You validate it by trying to fool it.** The known-good answers must score 100%. An agent that does nothing, and one that does whatever it's told, must fail wherever that behavior breaks the rules. Your judge must agree with labels a person wrote.

## Read it in order

1. [What top PM roles pay](/docs/ai-core-skills/agent-evals-pay/)
2. [Where evals came from, and what they mean](/docs/ai-core-skills/agent-evals-origins/)
3. [How to build one with AI](/docs/ai-core-skills/agent-evals-build/)
4. [How to validate it](/docs/ai-core-skills/agent-evals-validate/)
5. [The kit](/docs/ai-core-skills/agent-evals-kit/)
6. [Reference](/docs/ai-core-skills/agent-evals-reference/)
