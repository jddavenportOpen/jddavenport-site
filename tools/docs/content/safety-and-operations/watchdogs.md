---
title: "Watchdogs: liveness is work completed"
description: "Catch-up after reboots, stale-job alerts, death-cluster detection, auto-unwedging, and the memory breaker that ended a kernel-panic loop."
section: safety-and-operations
group: "Keeping it running"
order: 50
updated: 2026-10-05
sources: ["learn/tier-2/08-cron-catchup-and-resilience.mdx", "building-ai-os/arch-cron.mdx"]
---

The most dangerous state in an agent system isn't down. It's alive and wedged: the process is up, the port answers, the health check is green, and no work is happening. Uptime checks are blind to that state by construction. So every watchdog in my system asks one question: did you do work? Not: are you running?

The watchdog layer is designed on the assumption that every layer above it will eventually lie about its own health. This page is the set of detectors I run, the incident behind each one, and the pattern you can copy.

## What you'll learn

- How to catch up on jobs a reboot made you miss, without double-sending
- Stale-job alerts, and why the alerter needs its own watcher
- Detecting session death clusters and wedged sessions
- The kernel-panic loop, and why the memory reading lied
- Why an alert path must be tested like any other code

## Catch-up after reboots

Cron has no memory. If the machine is asleep or rebooting at 7:00 when the morning briefing is scheduled, that run just doesn't happen, and the next one is tomorrow.

My catch-up job runs twice an hour. (Its schedule line says `*/47`, which I meant as every 47 minutes and cron reads as minutes 0 and 47; the trap is in [Schedules as a heartbeat](/docs/patterns/heartbeats/).) For each job on a short list, it checks the last successful run. If the job missed its window, it replays it with `CATCHUP=1` in the environment, and jobs that talk to me honor that flag by producing their output without the notification.

The list is opt-in, and that was learned the hard way. The first version replayed everything unless a job was marked disruptive. In June 2026 an evening email went out twice, once on schedule and once as a "catch-up" at 3:30 in the morning. Now a job replays only if it's explicitly marked safe to catch up, and new jobs default to not replayed. Two more rails:

- **Skip window:** don't catch up if the job is due to run normally in the next 30 minutes.
- **Once per day:** if a catch-up already ran today for this job, don't run it again. A broken script shouldn't loop.

And as of September, the catch-up job checks the kill ledger before replaying anything. If I killed a job, a missed run is not a reason to bring it back.

## Stale-job alerts

A job that fails silently is invisible. Its log fills with errors that nobody reads, and everything downstream keeps assuming it worked. The 90-day school API token I mention in [The loops doctrine](/docs/patterns/loops-doctrine/) went dead for 12 weeks exactly this way.

The alerter is deliberately dumb. For each watched job, it compares the last successful run against the expected cadence. Past twice the expected interval, the job is stale. The alerter pages on state changes only: once when a job goes stale, once when it recovers, and silence while the same set stays broken. Before that change it re-paged on a timer, which is how you train yourself to ignore a pager.

The same rule applies when I read status: a health file older than twice its writer's cadence is **unknown**, never green, and unknown is never grounds for telling anyone the system is healthy.

### Who watches the watcher

In August 2026 the cron layer itself died for about a day. The stale-job alerter ran on cron. So it died too, and nobody was paged for roughly 24 hours. The alerter couldn't report the exact failure it exists to catch.

The fix is a cross-scheduler deadman. The alerter moved to launchd. A tiny cron job, with no Python and no network beyond the notifier so it can run on a sick machine, watches the alerter's log:

```text
cron dies     -> the launchd alerter sees cron-fed jobs go stale -> pages
launchd dies  -> the cron deadman sees a stale alerter log      -> pages
both die      -> the machine is down; that's a different, louder problem
```

Neither scheduler is trusted to report its own death.

## Death clusters

On July 1, 2026, one bad restart killed every live session at once. All my agent sessions run as children of one supervising service, and an agent restarted it with a raw command that took the whole process group down. The full story is in [Root cause first](/docs/patterns/root-cause-first/).

Besides the hook that now blocks raw restarts, a detector runs every five minutes looking for clusters: four or more sessions dying within two minutes. When it finds one, it pages me and names the session and command responsible, pulled from the transcripts. One session dying is normal. Several at once is an incident, and a detector that names the culprit turns a mystery into a five-minute fix.

The detector had its own bug, which is worth knowing about. It looked up a worker process by searching its command line, but the operating system only keeps the first part of a very long command line, and the token it searched for was past the cutoff. So it reported the worker as not running and fired on every cluster. Reading the full argument list fixed it. Watchdogs need tests too.

## Wedged sessions

Teardown Failure 3: the CLI under one daemon hit a usage limit and popped a confirmation dialog. The daemon sat waiting on a prompt no human would ever see, and inbound messages queued silently for four and a half hours. Nothing crashed, so nothing alerted.

The fix had two parts: a watchdog that detects that stuck state and confirms the dialog automatically, and liveness checks that measure output (messages processed, work completed, state advanced) instead of process health.

The same shape showed up elsewhere. On June 30, 2026 the relay that carries every outbound message wedged on a half-open database connection after a network blip. The process stayed up, wrote no logs, and sent nothing for about 12 hours. A manual restart drained the whole backlog in two seconds. The watchdog built that day doesn't read the relay's logs, because a wedged process goes quiet. It reads the queue: if a row for a provider that normally sends in under three seconds has been waiting far longer, and isn't in a deliberate backoff, the relay is wedged and gets restarted. Anything that can wedge now has a detector that checks whether work moved, measured at the source of truth.

The general recipe:

1. Pick the unit of work: a message handled, a row processed, a file written.
2. Record a timestamp every time one completes.
3. Alert when the gap between completions exceeds what's normal **while there is work waiting**. An idle queue with no completions is fine. A full queue with no completions is wedged.

## The kernel-panic loop (September 2026)

In early September the main machine started panicking and rebooting. Six reboots on September 7 alone.

**The first diagnosis was wrong, and mine.** I read memory stats from a freshly rebooted machine, saw plenty free, and wrote "not memory." The panic reports themselves said otherwise: the memory compressor's segment table was at 100% when it went down. I fixed a real but secondary problem first (a boot herd of jobs all starting at once) and called it solved. Within the hour, a closer read of the panic files proved me wrong.

**The real cause:** a 12 GB local model was being loaded many times a day, on top of browser and Node swarms, on a 36 GB machine. The gates that admitted new work trusted a standard "memory free" reading. Side by side, that reading said 84% free while truly available memory was under 9 GB. The gates were letting work in because the gauge lied.

**The fix, landed and verified on September 9:**

- A memory-truth gauge that reports what's actually available, used by every gate that admits new work.
- Heavy local models refused on that machine by policy. It now serves only small models.
- A compressor breaker that kills in verified process groups when available memory drops through set floors, with a flight recorder of what it killed and why. Agent launches were tagged with their own process groups so the breaker can kill cleanly, and the core supervising service is protected.
- A boot governor so restarts don't stampede.

One more detail that matters: the fix landed on main at 18:07, but the running breaker had started at 15:41. Merged code isn't running code. The last step was restarting the breaker and confirming in its log that the new version was the one ticking.

## The alarm that couldn't ring

The worst finding from the panic audit: none of the panics had paged me. My alert routing had an allowlist for what reaches my main channel, and panic alerts weren't on it. They were delivered to a lane that was switched off.

It went further. The stale-job alerter has a line that reports when its own alerts fail to deliver. That line was itself being dropped by the same allowlist. The alerting system could not report its own death.

I fixed it narrowly: outage-class alerts (panics, a stuck shipping pipeline, delivery failures) now always reach the main channel. Not every alert, because a flood of alarms is how you got blind in the first place. And for pagers whose trigger is a disaster, a probe now fires the real sending path end to end and checks the message arrived, because a pager you've never fired is a pager you're guessing about.

## A watchdog checklist

| Detector | Asks | Catches |
|---|---|---|
| Catch-up | Did the scheduled run happen? | Runs lost to sleep and reboots |
| Stale-job alert | When did this last succeed? | Silent failures |
| Cross-scheduler deadman | Is the alerter itself alive? | The watcher dying with what it watches |
| Death-cluster detector | Did several sessions die together? | Mass kills, with the culprit named |
| Unwedger plus output liveness | Did work move while work was waiting? | Alive-but-stuck processes |
| Memory-truth gauge and breaker | What's actually available? | A gauge that lies, then a panic |
| Alert-path live fire | Does the page actually arrive? | Alerts dropped in transit |

Honest read: none of these is clever. Each one exists because I believed a green light that wasn't true. Build the detector for the lie, not for the outage.

**Next:** [Durable state: Postgres as the system of record](/docs/safety-and-operations/durable-state/)
