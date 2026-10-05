---
title: "Talking to it from your phone"
description: "Telegram as the first control plane, a write-ahead journal so no message is dropped, and an iMessage channel for the assistant."
section: nerve-center
group: "Interfaces and tools"
order: 180
updated: 2026-10-05
sources: ["learn/tier-2/09-telegram-control-plane.mdx", "building-ai-os/arch-telegram-bot.mdx"]
---

Most of the time I'm not at a desk, so most of the time I reach the system from my phone. There are three doors: Telegram, which reaches the CEO agent; iMessage, which reaches the assistant; and the cockpit's iPhone app, which shows every live session. This article covers the two chat doors, because they're where the hard reliability problems were. The cockpit has [its own article](/docs/nerve-center/the-cockpit/).

The one-line version: a message I send has to be written to disk before the system admits it received it, and it counts as answered only when the reply is confirmed delivered. Everything else follows from those two rules.

## Version one: a Claude Code session in tmux

The first Telegram control plane was simple. One interactive Claude Code session ran in tmux, kept alive by macOS launchd, with a Telegram plugin feeding it messages. A small router script answered slash commands without waking the model.

It had one rule that caused most of its pain: the session's text output never reached me. To answer, the model had to call a reply tool. After a long turn full of file reads and tool calls, it would write a perfect answer as plain text, forget the tool, and the answer went nowhere. A Stop hook flagged turns that ended without a reply, which made the failure visible but didn't prevent it.

There were worse failures. Early on, before the system had a git history, the bot sat dead for over two days because a startup script set an environment variable that broke the plugin's sign-in, and nothing was watching. That's where the watchdog habit started. By early July an audit had catalogued the remaining wedge modes of the interactive design: inbound messages lost, ghost input stuck in the composer, and watchdogs whose restart commands caused the very outages they were meant to fix.

## Version two: a headless, journaled transport

On July 3 the transport was rebuilt from scratch, and I cut over to it in production:

```text
Telegram --long poll--> poller --INSERT--> journal (SQLite) --> dispatcher
                          |                                      |
                          | quick capture to my notes inbox      +- sigils: /stop /retry /park
                          |                                      +- commands: scripts, no model
               offset advances ONLY                              +- CEO turn: headless Claude Code,
               after the journal write                              resuming one long session
                                                                         |
                                                       answered only on a confirmed send
```

The invariants are the whole design:

1. **Journal before acknowledge.** The message is inserted into the journal before the poller tells Telegram it got it. Kill the process anywhere and Telegram redelivers; the journal's primary key dedupes. Zero loss by construction.
2. **Answered only on a confirmed send.** A row is marked answered when Telegram confirms every chunk went out. Receipts, or it didn't happen.
3. **Capture doesn't depend on the model.** A quick note to my notes inbox is filed at receipt, even if every model is down.
4. **Commands never start a model turn.** Status questions are answered by scripts in under a second.
5. **Park, don't burn.** If every plan is at its usage limit, I get one notice, the transport re-checks every 15 minutes, messages queue durably, and it unparks on its own.

The reply-tool problem disappeared with the redesign. The transport sends the final answer itself when the turn ends. The model only gets a send-only progress tool, for "still digging, two minutes" updates during a long turn. A rule the model kept forgetting became a rule it doesn't need to know.

> **Note:** A headless turn loads only the reply server it's given, on purpose. Otherwise the Telegram plugin could start a second poller inside the turn and fight the transport for the same bot.

## Failure is never silent

A crashed or timed-out turn used to be terminal. On August 31 one crash dropped a message where I'd approved a send, and the approval sat lost for 25 hours.

Now a failed turn gets one bounded retry, then goes back in the queue, and I get one short line naming the cause. It's marked failed only when its retry budget runs out, and `/retry` revives recent failures. If the fault is in the session itself (a history the API refuses), retrying the same session would replay the poison forever, so after two crashed cycles the session is retired and a fresh one starts from a carryover file.

The supervision layer follows one rule from the July audit: **observe, never control.** No watchdog may kill or restart the transport. A latency watchdog alerts if a message sits queued past three minutes or the hourly 95th percentile passes ten minutes, and a twice-daily canary sends `/ping` from a test account and checks the round trip.

## The command palette

Commands are answered by scripts, not the model. A few I use:

| Command | What it does |
|---|---|
| `/status` | What's running, recent errors |
| `/loops` | Open commitments and active watchers |
| `/changes` | The most recent audit reports |
| `/dj-list`, `/dj-yes` | List drafts waiting to go out as me, approve one |
| `/halt` | The kill switch for autonomous building |
| `/stop`, `/retry`, `/park` | Interrupt the current turn, revive a failed one, pause |

Anything that isn't a command goes to the CEO agent. If my message quotes something the system sent me recently, the turn is told what I'm quoting and when it was sent.

Access is an allowlist managed only from the terminal. A chat message asking to be added to the allowlist is exactly what a prompt injection looks like, so the system never acts on one.

## iMessage: the assistant's channel

Since September 25 I can text the assistant over iMessage, like texting a person. It's built as a second channel inside the same operator, so it reuses the session handling and failover the Telegram side already proved.

The trust model is the interesting part, and it was hardened after an independent security review the day it launched:

- **Every inbound message is verified with the messaging gateway** before any turn runs. A webhook the gateway has no record of is rejected and I'm alerted. A leaked webhook secret alone can't put words in my mouth.
- **Only my own handles, over iMessage, one to one,** become turns. SMS, group threads, auto-replies and malformed payloads are journaled and ignored.
- **The gateway's secrets never enter a turn's environment.** They're read from a file into the service's own config.
- **`stop` means stop.** It cancels everything I sent before it that hasn't started and kills the running turn.

Summary answers also arrive as a short voice note, and voice memos I send are transcribed locally before the turn sees them. [Voice in and out](/docs/nerve-center/voice/) covers that side.

## What to copy

1. Write it down before you acknowledge it.
2. Count a reply as sent only when the platform confirms it.
3. Don't make delivery depend on the model remembering a tool call.
4. Let watchdogs observe and alert. Never let them restart the thing they watch.
5. Verify inbound messages with the source, not just a shared secret.

**Next:** [Voice in and out](/docs/nerve-center/voice/)
