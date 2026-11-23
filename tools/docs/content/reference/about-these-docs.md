---
title: "About these docs"
description: "Who writes these, what changed when they moved here in October 2026, and the accuracy rules every article follows."
section: reference
order: 40
updated: 2026-11-22
sources: ["about.mdx"]
---

These docs are how I build and run a production AI organization, written so you can build your own. I'm JD Davenport. My home page, [jddavenport.com](https://jddavenport.com), is the bio; this page is about the docs themselves.

## Who writes them

I do, with agents. Agents draft from my notes, my changelogs and the live system. I set the rules every draft has to pass, and the rules do more of the quality work than any single edit. The voice is mine on purpose: if a page sounds like a brochure, it failed.

## What changed in October 2026

The docs used to live at docs.agenttree.army. In October 2026 they moved here, and every article was rewritten from scratch rather than copied over. The old site had drifted, and some of it was simply wrong:

- **Fiction got cut.** The old pages described agents that never existed (a whole C-suite of them), an origin story built on a framework I tried but didn't build, and frameworks with names that sounded better than they worked.
- **Counts got replaced.** Agent counts had drifted until four different public numbers were live at once, and the cron and server counts were just as stale. A reader who sees two of them stops trusting all of them.
- **Stale facts got updated.** Models, prices, the cockpit, the memory layer and the safety model have all changed since spring. Where an old claim couldn't be verified against the live system, it was cut or labeled as history.
- **Failures stayed.** The parts of the old docs that were honest about what broke were the most useful parts, so those got sharper, not softer.

## The accuracy rules

Every article follows the same rules:

1. **Present tense means true today.** Anything that was true once is written as history, with a date: "in June 2026 I..."
2. **Durable counts only.** The only agent count I use is 100+ agents built. An agent here means a named Claude Code session or scheduled job with its own instructions. I don't type exact live numbers into a page.
3. **Receipts over adjectives.** A date, a file, a command or a measured number beats an adjective every time. Benchmarks need a source; numbers without one get cut.
4. **Autonomy claims keep their asterisk.** By default, sending as me, spending money, identity and anything irreversible need a human yes. I've signed three narrow standing approvals that let some messages go out without a per-message yes. Each has a cap and a kill switch. Any page that implies otherwise is wrong.
5. **Opinions are marked.** I say IMO or I think when it's my opinion and not something I measured.
6. **Public code only.** Every repo link points to something you can open without an account.

For the deeper story of the system these docs describe, read [the teardown](https://jddavenport.com/teardown): the architecture, three documented incidents with root causes, and the constraints I chose on purpose.

## Found a mistake?

Email me@jddavenport.com with the page and what's wrong. A receipt (a link, a command output, a doc) gets it fixed fastest. I'd rather fix a wrong page than leave a confident one up.

**Next:** [Where to go next: learning paths](/docs/start-here/learning-paths/)
