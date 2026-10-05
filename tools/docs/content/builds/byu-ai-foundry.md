---
title: "The BYU AI Foundry"
description: "The program I co-founded at BYU Marriott where student builders ship production AI for real clients, and the systems behind it."
section: builds
group: "School and work"
order: 130
updated: 2026-10-05
sources: ["learn/tier-3/i2-byu-ai-foundry.mdx"]
---

The BYU AI Foundry is the program I co-founded at BYU Marriott so students get real reps building and shipping with AI agents instead of only studying them. It's an experiential learning program of the business school: student builders take on real projects and ship production software. The public site is [aifoundry.byu.edu](https://aifoundry.byu.edu), and its tagline says it plainly: student-built, production-grade, AI-native.

This page covers what the Foundry is, what's public, and the parts of my own system that support it. It stays inside what the Foundry's site already says. The people and the client work belong to the program, not to these docs.

## What the program does

The Foundry's [about page](https://aifoundry.byu.edu/about) describes about 30 students from a range of disciplines as of October 2026, working in small "velocity pods" matched to what a project needs. I'm the Managing Director.

The work falls into three kinds, per the site:

| Kind | What it means |
|---|---|
| Full-stack applications | New web and mobile apps, customer-facing or internal |
| AI integration and orchestration | Agents and copilots on a client's own data, automations across the tools they already use, document processing |
| AI enablement and training | Teaching a client's team to build this way, with Claude Code, Codex and other agent tooling, then handing off |

Every engagement gets a written scope, a cost estimate and a delivery timeline before anyone builds. The [work page](https://aifoundry.byu.edu/work) lists reference builds that are shipped and running, from an open-source build spec for an AI-native feedback widget to an agentic grading tool where the instructor keeps the final say on every grade.

The values on the site are the part I'd point a new member to first. The first one reads: "We are judged by what we ship: whether it works, and whether someone would pay for it." That's the whole culture in one line.

## The public surfaces

Three things are public, and they're the parts of the Foundry most worth copying if you're starting something similar.

### The site

The site's source is public at [github.com/ai-foundry-byu/website](https://github.com/ai-foundry-byu/website). It carries the proposal form ("tell us what you want built") and a network form where alumni and builders opt into events, a periodic AI digest, access to the cohort for hiring, or submitting a project. Both write to the program's own database.

### The roadmap that counts itself

The [roadmap page](https://aifoundry.byu.edu/roadmap) lays out three phases (foundation, community, programs) and shows live numbers next to each item: how many leaders have earned the Claude Architect certification, how many advisors are confirmed, how many people are in the network. The page says the counts are read from the program's own systems each time it loads.

That's deliberate. A number typed into a slide is wrong the week after you type it. This is the same rule I follow on my own site: exact numbers only where a generator produced them, durable floors everywhere else. More on that in [The system documents itself](/docs/safety-and-operations/ground-truth/).

### The jobs board

The [jobs board](https://aifoundry.byu.edu/jobs) aggregates startup roles from venture portfolio companies. On October 5, 2026 it listed more than 47,000 roles across more than 900 companies, refreshed twice a day. When it launched in late July 2026 it had around 10,000.

Most of it is ordinary deterministic code an agent wrote: an ingest job that pulls postings from portfolio boards and company applicant-tracking systems, dedupes them on the apply URL, and retires postings that disappear. The AI part is resume matching. At launch that was a single LLM call that scored a resume against a posting, which I extracted and open-sourced as [resume-grader](/docs/builds/resume-grader/). The board's code is public too, at [jddavenportOpen/vc-job-board](https://github.com/jddavenportOpen/vc-job-board).

## What my system does for it

The Foundry is one of the domains in my own agent system. A persistent domain agent owns it: applicant intake from the site's forms, cohort milestones, and site operations. It keeps a status report current so my daily summary can say where things stand without me opening five tabs. See [Domain agents](/docs/nerve-center/domain-agents/) for how those work.

One rule matters more than the rest: nothing goes out to a cohort member, applicant, partner or advisor without my yes. The agents draft emails, update trackers and prepare materials. A human sends. That's the [send gate](/docs/safety-and-operations/the-send-gate/), and it applies here like everywhere else.

## A lesson from the first site: make it safe for non-developers

In June 2026 a teammate who isn't a developer needed to update the original program site. Instead of handing over the keys and hoping, I set up three things first:

1. **Branch protection on main.** Nobody pushes directly. Changes go through a pull request.
2. **A CI check that must pass.** Build and lint run on every pull request. Red means it can't merge.
3. **A plain-English guide in the repo.** How to make a change, open a pull request, wait for green, and merge it yourself.

Every pull request also got a preview URL, and every merge to main deployed to production. Setup took about an hour. The principle: if someone who has never heard of CI can be trusted with your production site, it's because the gates make the mistake impossible, not because you trusted them harder.

Honest read: the Foundry's tech is the easy part. The hard part is the same as any program: finding builders who ship, finding clients with real problems, and keeping the promises you make to both. The agents help with the paperwork around that. They don't do the trust part.

**Next:** [Build your own resume grader](/docs/builds/resume-grader/)
