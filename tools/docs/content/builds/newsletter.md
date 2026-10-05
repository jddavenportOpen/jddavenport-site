---
title: "The newsletter pipeline"
description: "A news sweep, a build-log-first draft grounded in receipts, an approval bound to the exact email, and three names in one summer."
section: builds
group: "Research and content"
order: 90
updated: 2026-10-05
sources: ["learn/tier-3/f5-newsletter-agent.mdx"]
---

My newsletter pipeline drafts an issue every week and sends nothing until I approve that exact issue. The drafting is the boring part. The useful part is that the pipeline has been rebuilt twice after audits found it barely worked, and that it changed names twice in three weeks. Both stories are below, because they're more useful than the diagram.

## The pipeline today

```text
daily AI news sweep -> dated digest with real source links
weekly drafter (Tuesday morning)
  -> build log first: what I shipped, with receipts
  -> a short news sweep: a few items, each with its link
  -> grounding guards: refuse a draft that can't trace its claims
preview email + approval card to me
  -> approve: send to confirmed subscribers only
  -> skip, or silence: nothing is sent
delivery sweep -> record what was delivered, flip hard bounces
```

**The news sweep** runs daily, pulls recent AI news from search, dedupes it, and writes a dated digest with a real source URL for every item. Its job is to give the drafter something true and recent to stand on.

**The drafter** leads with the build log: what I actually shipped that week, pulled from my project logs with receipts. News comes second and is capped. A guard refuses any draft whose build log can't be traced to real entries, or whose numbers don't trace to a file. If the guard fails, no draft, no card.

**The approval** is bound to the bytes. The card I get carries an issue id and a short hash of the exact email that would be sent. When I approve, the gate recomputes the hash at send time, so a regenerated draft voids the old approval. If more than one issue is waiting and I send a bare "yes," the gate fails closed and asks which one. It's the same idea as my system-wide [send gate](/docs/safety-and-operations/the-send-gate/): approve the thing, not a description of the thing.

**Silence is a no.** If I don't decide, I get one reminder, then nothing. When the next week's draft lands, the undecided one is skipped and logged as "skip by silence."

**Only confirmed people get mail.** A subscriber is sendable only if they're active and have clicked a confirmation link. No exceptions, no backfills.

## History, part one: the June audit

On June 6, 2026 an audit of the newsletter found it had sent 4 of 26 drafted issues, the last one on May 22. Two causes:

- **Nothing sent automatically.** The "Friday send" job in the schedule was a stub. It existed, it ran, and it did nothing.
- **What did send landed in spam,** for four stacked reasons: an unsubscribe link that returned 404 (a legal problem, not just a deliverability one), no `List-Unsubscribe` header, an image-heavy template served from raw storage URLs, and a From address that didn't align with the sending domain.

The rebuild landed the same day: a text-only template that works in light and dark mode and on phones, a real unsubscribe handler plus the one-click header, test addresses pruned out of the list, the approval gate restored (it had been lost in a cleanup and was found because the project's runbook still referenced it), and a real send. The next issue went to 11 real subscribers that same day.

A second problem was in the content. The "AI news" section had been written from the model's memory, which means news that could be six to twelve months stale. The fix was the daily sweep: the drafter now picks items from real dated digests with links, instead of recalling what happened.

## History, part two: three names

- **The Agent Brief** was the original name.
- **The Agent Operator** replaced it in July 2026.
- **Raising Clawd** was picked on August 11, 2026, with a new build-log-first format, and the relaunch went out under it.

"Clawd" is what I call my agent system. Renaming a newsletter twice in three weeks isn't a strategy I'd recommend. It's here because it happened.

## History, part three: the August audit

On August 30, 2026 a full audit found the pipeline was broken in a new way:

- Seven drafts had been rotting since mid-July. Nobody had decided on them.
- The approval pings had been muted by a notification policy change, and the morning briefing never mentioned the newsletter. So I never saw the drafts.
- Of 358 subscriber rows, **zero** had confirmed their address. Most of the list came from a signup flood: bots had pushed hundreds of addresses through the form.
- The opt-in check in the send path had never been committed, and the confirmation flow didn't exist, so approving an issue would have mailed nobody.
- No open or click had ever been tracked.

The rebuild, over the next two days:

1. **List surgery.** The flood rows were suppressed (reversibly, not deleted) and the real people who had signed up organically were kept.
2. **Double opt-in with bot defenses.** A time trap that rejects the flood's exact submission shape, filters for disposable and gateway addresses, the same neutral response whether or not an address already exists (so the form can't be used to probe or to mail-bomb someone), single-use confirmation tokens, and no welcome email anywhere in the flow.
3. **A rebuilt approval surface** with the hash binding described above, plus a pending-approvals view so nothing waiting on me can hide.
4. **The build-log-first format,** with the grounding guards.

On September 1, 2026 the relaunch issue went out to a small, confirmed list: every address delivered, none failed. It was the first send since July and the first ever through the rebuilt path. Three days later the first organic signup arrived through the new form.

## One more trap, found in October

On October 5, 2026 a full end-to-end check of the signup funnel (form, pending row, confirmation email, click, active, in the next send's audience) passed, and turned up two unsubscribe bugs:

- The one-click unsubscribe that mail clients call was returning 403, blocked by the web framework's origin check.
- A plain GET to the unsubscribe link removed the subscriber immediately. That sounds convenient until you remember that corporate email scanners open every link in a message to check it for malware. A scanner could unsubscribe your readers without them ever seeing the email.

Both are fixed. If you build one of these: make the GET show a confirm button, and handle the one-click POST separately.

## Where it honestly stands

The machine works. Every Tuesday it drafts an issue grounded in what I shipped, and the approval card lands. Every weekly draft in September was skipped by silence, because I didn't approve one. That's the gate doing exactly its job, and also the most honest metric on this page: a newsletter pipeline is only as regular as the editor who taps approve.

As of this writing, the signup form still lives on my old docs site.

## What I'd copy

- Never let the model write "recent news" from memory. Ground it in dated sources with links.
- Lead with your own work and refuse drafts that can't cite it.
- Bind approval to a hash of the exact email.
- Double opt-in from day one. A list nobody confirmed isn't a list.
- Make silence a no, with exactly one reminder.
- Never let a GET request change state.

**Next:** [Voice notes into the second brain](/docs/builds/plaud-voice-notes/)
