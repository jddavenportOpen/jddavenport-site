---
title: "Root cause first, never bandaids"
description: "Diagnose, fix the process, backfill, add a regression guard, then patch the symptom. In that order, with three real incidents."
section: patterns
group: "Shipping"
order: 110
updated: 2026-10-05
sources: ["learn/tier-2/11-root-cause-first.mdx"]
---

A bandaid fixes the bug you saw. A root-cause fix stops the process that made it. With agents writing code all day, the difference compounds fast: a bandaid gets re-applied every time the same class of bug shows up in a new file, and agents are very good at producing new files. So since May 22, 2026 the rule in my system is: fix the process so this never happens again, not just this one issue.

## The five steps, in order

1. **Diagnose the root cause.** Ask why until you hit a process gap, not a line of code. "The script crashed" is a symptom. "Nothing stops any script from doing this" is a root cause.
2. **Fix the process.** The hook, the schema, the gate, the convention: whatever generated this class of bug must stop generating it.
3. **Backfill.** Find every existing instance of the bug class and fix them in one automated pass. Not a list of follow-up tickets.
4. **Add a regression guard.** A test, a check, a detector or a sweep that fails loudly if the class comes back.
5. **Patch the symptom you noticed.** Usually step 3 already did. That's by design.

The order matters. If you start at step 5, you'll usually stop at step 5.

## Three real ones

### One restart killed every session (July 1, 2026)

**Symptom:** every live agent session died in the same two seconds. Twelve of them, including the one that caused it.

**The tempting bandaid:** restart the sessions, tell agents to be more careful.

**Root cause:** at the time, every session ran as a child process of one supervising service. An agent restarted that service with a raw process-manager command instead of the guarded reload script, and the operating system killed the whole process group. The real gap wasn't the command. The safety check lived inside one script, on the honor system, and nothing stopped an agent from going around it.

**Process fix:** a hook that runs before every tool call and blocks raw restarts of protected services outright.

**Backfill:** the reload scripts now refuse to run while sessions are live, and print the list of casualties if someone forces it.

**Guard:** a detector that checks every five minutes for a cluster of session deaths, pages me, and names the session and command responsible.

The full write-up is Failure 1 in [the teardown](https://jddavenport.com/teardown).

### The kernel-panic loop (September 2026)

**Symptom:** the main machine kept panicking and rebooting. Six reboots on September 7 alone.

**What I got wrong first:** my first diagnosis said "not memory." I had read memory stats from a freshly rebooted machine, which of course looked fine. The panic reports themselves said otherwise. Once I read the primary evidence, the cause was plain: the memory compressor's segment table was filling up. A 12 GB local model was being loaded many times a day, on top of browser and Node swarms, and the gates that admitted new work trusted a "free memory" reading that said 87% free on a machine that was nearly full.

**Process fix:** a memory gauge that reports what's actually available, wired into every gate that admits new work. Heavy local models are now refused on that machine by policy.

**Backfill:** agent launch sites were put into their own process groups so they can be killed cleanly, and boot-time job storms were broken up.

**Guards:** a breaker that kills verified process groups when real available memory drops through set floors, a boot governor, and an alert route fix. That last one stung: none of the panics had paged me, because the alert routing silently dropped them. The full story is in [Watchdogs](/docs/safety-and-operations/watchdogs/).

Lesson inside the lesson: step 1 is only as good as the evidence you read. Read the crash report, not the dashboard.

### Fake people in memory (August and September 2026)

**Symptom:** my contacts database kept growing entries for people who don't exist. "Site Map." "Oracle Database." "Warden Nightly," which is a scheduled job.

**The tempting bandaid:** delete the junk entries.

**Root cause:** a hook that looks up names in every prompt was treating text the system had injected into the prompt (recalled memories, carried-over context, pipeline prompts) as if I had typed it. Anything in Title Case looked like a person.

**Process fix:** injected regions are stripped before name lookup, headless pipeline runs set a flag the hook respects, and a provenance check refuses to treat hook-created stubs as real contacts. Title Case no longer counts as evidence of a person.

**Backfill:** one pass quarantined 135 fake entries and pruned them from the vector and graph stores. Nothing was deleted, so the pass is reversible.

**Guard:** the weekly contacts health check gained new violation classes, and a weekly invariant sweep checks the hook's provenance rule.

## When someone asks for the bandaid

Sometimes the person asking is me, in a hurry. The script I gave my agents, and that they're expected to use on me:

> The bandaid is 5 minutes. The root-cause fix is 30. The bandaid will recur. I recommend the 30-minute fix.

Then they do the 30-minute fix unless I explicitly say "bandaid this one, root cause later." If I do say that, the agent opens a tracked loop for the root-cause fix before it moves on. A bandaid without a loop becomes a permanent fixture, and six months later nobody remembers why the manual workaround exists.

## Put it in the prompt

Most agents default to step 5. They fix what you pointed at and report done. If you want root-cause work, ask for it in so many words:

```text
Fix this bug using root-cause-first:
1. Diagnose why the system allowed this class of bug. Read primary evidence (logs, crash reports), not summaries.
2. Fix the process that generates it.
3. Find and fix every existing instance in one pass.
4. Add a regression guard that fails if the class returns.
5. Then patch the original symptom.
If you can only do step 5 now, open a tracked loop for steps 1 to 4 and say so in your report.
```

## Surgical is not the opposite

My instruction files also say "make surgical changes." That's about scope, not depth. A root-cause fix is surgical when it's the smallest change that stops the bug class from coming back. A hook that blocks one dangerous command is small. Rewriting the supervisor because you're annoyed is not.

Honest read: root-cause-first costs more on every individual bug and less on the system over time. I'd make the same trade again. The fires I fought in April are not the fires I fight now, and that's the only scoreboard that matters.

**Next:** [Ship to prod: review the product, not the diff](/docs/patterns/ship-to-prod/)
