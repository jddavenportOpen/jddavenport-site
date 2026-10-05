---
title: "The executive assistant"
description: "Inbox triage, calendar merge, draft-first replies through the send gate, a pull-based Needs-you view, weekly planning, and an iMessage channel."
section: nerve-center
group: "Orchestration"
order: 90
updated: 2026-10-05
sources: ["learn/tier-3/g4-executive-assistant.mdx", "building-ai-os/story-automation.mdx"]
---

The executive assistant layer runs the daily operations of my life: it triages the inbox, merges calendars, drafts replies, tracks what I owe people, closes the day, and runs a weekly planning session with me. It drafts as me all the time. It sends as me never, not without my yes on the exact text.

The most useful thing it taught me wasn't a feature. It was that a morning briefing I didn't read was worse than no briefing at all.

## Two agents, one layer

| Agent | Owns |
|---|---|
| Donna, the daily-operations agent | Inbox triage, calendar merge, the voice-note and health-summary pipelines, open loops, the end-of-day debrief, the iMessage channel |
| The executive-assistant agent | Weekly planning, follow-up and relationship nudges, and calibrating how much it's allowed to do without asking. Most of its scheduled pushes are paused as of October |

Donna is just the name I gave the daily-operations agent, and she's the one I actually talk to. The split is by cadence: Donna is daily, the EA agent is weekly and strategic.

## Draft-first, always

Every message that would go out as me follows the same path:

1. The agent drafts it.
2. The draft lands in an approval queue with the exact recipients, subject and body.
3. I approve, edit or kill it.
4. Approval mints a single-use token bound to a hash of that exact content. Change one word and the token dies.
5. The [send gate](/docs/safety-and-operations/the-send-gate/) transmits only with a valid token.

Reads, searches, calendar lookups and drafting are free. Sending isn't. That rule is the only reason I was willing to give it my inbox at all.

## The standup I killed

In June I collapsed every scheduled morning message into one: a 7 AM standup from Donna. Calendar, inbox highlights, open loops, overnight alerts, system health. It was the one earned morning push, and it got more thorough every month, which is a polite way of saying longer.

I stopped reading it. On September 11 I killed it. Nine days later an audit found it had been sending daily anyway: a liveness job that watched the assistant had kept firing it again. A deadman switch can't tell "it broke" from "I turned it off on purpose."

So on September 20 it died for real, and the off state became a recorded decision: an off-switch manifest names the job, who turned it off and when, and every path that could revive it (a schedule, a deadman, a catch-up after reboot, a monitor). A standing invariant check fails if any of those paths could bring it back.

> **Tip:** When you turn something off, record it as a decision with an owner and a date. Otherwise your own reliability tooling will turn it back on.

## What replaced it: pull, not push

The replacement is a **Needs you** tab on the cockpit's Today page, on desktop and phone. It shows:

- One sentence on whether the assistant's sources are healthy.
- The one ask: the oldest high-priority item that's blocked on me, plus how many approvals are waiting.
- The urgent items, each with Done and Snooze buttons that write receipts.

I look when I want to. Nothing pings me to tell me there's nothing new.

The day still has one push, at the end instead of the start: an evening debrief at 8:30 that closes the day in three short beats and asks for a braindump of tomorrow. If I braindump priorities in any chat ("tomorrow the most important things are..."), they go to the top of the Today list and everything else moves down. Nothing gets deleted.

## Inbox triage and calendar merge

Donna reads the inboxes I point her at and sorts by what needs me, what needs a reply, and what's noise. Replies become drafts in the queue above.

Calendar merge sounds trivial. It wasn't. In September an agent asked for my free time over the next six weeks and got almost none. Most of the events in that window were phantoms: recurring blocks from old template calendars I'd stopped using. Unioning every calendar produced a schedule with zero free time. The fix was choosing which calendars count, not merging harder.

## Left-on-read, and the noise lesson

I built a detector for threads where I sent the last message and never got a reply. The first test run in May found 78 of them. About 50 were mailing-list threads where I was a recipient and nobody expected an answer.

I didn't schedule it until it had a sender blocklist and a noise score. Even then, a digest of stale threads every few hours was noise, and I turned the push version off. The idea lives on as a follow-ups view I pull up when I want it.

The general rule, which I learned on this one and then relearned on the standup: if the first run is mostly false positives, fix the filter before you add the schedule. An alert that's wrong half the time trains you to ignore the one that's right.

## Weekly planning: the Sunday Sync

Weekly planning is one artifact and one ritual:

1. **Saturday, 8 PM:** a prep pack is built from real data: proposed wins, what carried over from last week with a proposed action for each, upcoming deadlines, decisions waiting on me, and a short scorecard. Stale sources are flagged, not faked.
2. **Sunday:** a live, facilitated session in a chat. Hard cap of 25 minutes, five phases, at most three big priorities. The agent proposes first and asks "ok, change, or skip?" one item per turn, so I'm reacting, not authoring. Delegations go straight onto the agent bus.
3. **The result** is written as a weekly plan record that the daily layer reads all week.

It runs inline in a live session, not as a background job, because it needs real back-and-forth.

## iMessage: text it like a person

Since September 25 I can text Donna over iMessage. Summary answers also arrive as a short voice note. The trust model matters more than the feature: every inbound message is verified with the messaging gateway before any turn runs, only my own handles in one-to-one iMessage become turns, and the gateway's secrets are never visible inside a turn. [Talking to it from your phone](/docs/nerve-center/phone-and-messaging/) has the details.

Voice recordings feed the same layer: they're transcribed and turned into tasks and contact notes daily. That pipeline is its own build: [voice notes into the second brain](/docs/builds/plaud-voice-notes/).

## What I'd do if I started over

1. Make it pull-first. Push one thing a day at most, and measure whether you read it.
2. Fix the filter before the schedule.
3. Draft everything, send nothing without a content-bound approval.
4. Record every off switch as a decision so your own tooling respects it.
5. Choose your sources deliberately. More inputs is not more truth.

**Next:** [The second brain: logs, rollups, journals](/docs/nerve-center/the-second-brain/)
