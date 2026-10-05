---
title: "The bridge"
description: "The service between the cockpit and every agent session, and how one careless restart once killed them all."
section: nerve-center
group: "The cockpit"
order: 170
updated: 2026-10-05
sources: ["learn/tier-3/d4-the-bridge.mdx"]
---

The bridge is the Python service on my always-on Mac that sits between the cockpit and every interactive agent session. The cockpit runs on Vercel, the agents run on the Mac, and Vercel can't reach into my Mac. The bridge is the one door between them. For its first months it was also the most dangerous thing to restart in the whole system, and how that stopped being true is most of what this article is about.

## What it does

| Job | Detail |
|---|---|
| Spawn | Starts Claude Code sessions (today through separate worker processes, covered below), each with an allowlisted working directory per agent, so a cockpit request can't start an agent somewhere it shouldn't be |
| Route input | Chat text from the cockpit, plus raw keys for interactive menus and question prompts |
| Stream | Live output and transcript updates to the cockpit, session state to Postgres |
| Resume | Brings a parked or dead session back with `claude --resume`, so the agent continues with its full conversation instead of starting blank |
| Account for itself | An audit log of every spawn, input and kill, which is how incidents get a named culprit |

It sits behind a tunnel with authentication on every request. It is not the control plane. Scheduled jobs, the Telegram transport and the agent bus all keep running if the bridge is down. Only the live cockpit views go dark.

One detail that matters for anyone building on Claude Code: a resumed session keeps the model it was born with. A registry change doesn't reach a live session. So an hourly guard checks running sessions against the registry and switches drifted ones through the cockpit's own model-switch path, and it never overrides a model I picked by hand.

## Failure 1: one restart killed every session

The original architecture was deliberate: every session was a child process of the bridge, which gave one place for lifecycle and one place for policy. The cost of that choice arrived on July 1, 2026.

An agent restarted the bridge with a raw process-manager command instead of the guarded reload script. The OS killed the whole process group. All 12 live sessions died within the same two seconds, including the session that issued the command. Nobody noticed for more than 90 minutes.

The root cause wasn't the command. The safety check lived inside one script, on the honor system, and nothing stopped an agent from going around it. An agent under context pressure with a confused plan will eventually take the shortest path. Prose instructions are not a barrier.

## The fix, in three layers

**1. Block the raw command.** A PreToolUse hook runs before every shell command an agent executes and refuses raw restarts, stops and unloads of any service that hosts sessions. It isn't advice the model can reason its way past. It runs first, deterministically. The same hook now blocks other shortcuts where a guarded wrapper exists, like a raw production deploy of the cockpit or re-enabling a scheduled job I've killed. A human-approved mass restart needs an explicit override token in the command.

**2. Make the sanctioned path safe.** The reload script:

- refuses to run while live sessions would die, and with `--force` prints the casualty list before it does anything;
- refuses more than two restarts in two hours without an override, after a restart storm in early July;
- drains first: it snapshots live panes and waits up to 30 seconds for any mid-turn session to reach a turn boundary, so the restart lands in a quiet gap.

**3. Detect it anyway.** Every session writes a digest when it ends. A detector runs every five minutes and looks for four or more session endings within two minutes. If it finds a cluster, it pages me with the session and the command that caused it.

That detector had its own bug. On July 3 it sent nine false pages: it reported the bridge's start time but never used it. Sessions die independently all the time. They can only die together if their parent died, so the detector now fires only when the parent process actually restarted inside the death window. A detector that pages on noise gets muted, and then it's not a detector.

## Then the architecture moved

Guards made the restart rarer. They didn't make it harmless. So in mid-July the sessions moved out of the web server into a separate worker process. I built it behind a flag on July 13, and it was carrying live sessions within days. The bridge talks to the worker over a local socket. Reloading the bridge's code no longer touches a single session; on July 16 that was proven twice, eight sessions out of eight surviving each time.

Later the worker was split into several shards, because one worker's event loop could only stream about eight to ten busy sessions at once. Each shard reloads through its own drained, casualty-listed script, and a nightly deploy backstop skips any shard holding a pane I've typed into in the last 24 hours.

## And then the machine died

In early September the Mac itself started kernel-panicking (memory pressure, covered in [Watchdogs](/docs/safety-and-operations/watchdogs/)). Session restore after a whole-machine death turned out to fail in both directions at once:

- **Under-restore.** 19 panes were live at one panic. Zero came back. The resume logic trusted each session's status word, but while the machine was dying the bookkeeping kept running and stamped panes "killed" or "crashed", so by the time it rebooted, the records no longer described what I'd had open.
- **Over-restore.** A different revival path brought six panes back in seven seconds with no memory check, into a machine that had just died of memory exhaustion. The next panic followed.

The fix takes its list from the last inventory the worker wrote before the crash (it snapshots its live sessions every 30 seconds), not from status words. Then it restores in stages: wait five quiet minutes after boot, bring panes back in batches of three at least 90 seconds apart, read memory fresh before each batch and defer on pressure, and stop at a hard cap. "Resume everything faster" would have been the wrong fix. It would have restored 19 panes into a box already at the cliff.

## What to take from this

1. One supervisor gives you one place for policy. Until you've moved the sessions out of it, treat its restart as the most dangerous command in the system.
2. Guard the raw command with a hook, not a sentence in an instructions file.
3. Make the safe path print its casualties and wait for a quiet moment.
4. Detect the failure anyway, and gate the detector on the actual cause so it doesn't cry wolf.
5. When guards keep getting tested, move the blast radius. Separating the sessions from the web server did more than every guard combined.

**Next:** [Talking to it from your phone](/docs/nerve-center/phone-and-messaging/)
