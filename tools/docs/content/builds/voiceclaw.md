---
title: "VoiceClaw: a phone agent"
description: "A March 2026 build: a voice agent you call on the phone, wired to personal tools. What worked, what I planned next, and why it's archived."
section: builds
group: "Open source"
order: 190
updated: 2026-10-05
sources: ["articles/voice-ai-self-hosted.mdx"]
---

VoiceClaw was a phone number I could call to talk to an AI that knew my calendar, email, messages and notes. I built it in March 2026 on a hosted voice platform, it worked, and it's archived now. The public repo is [jddavenportOpen/voiceclaw](https://github.com/jddavenportOpen/voiceclaw). The more useful part of this page is why it stopped, because the reason applies to every second channel you bolt onto an agent.

## What it was

Call the number, ask "what's on my schedule today?" or "any important emails?", and hear the answer. The public version's stack:

```text
phone call -> Vapi (telephony, speech-to-text, text-to-speech)
                 |
                 v
            Claude (reasoning and tool calls)
                 |
                 v
            a small Python tools server -> calendar, email, messages, notes, weather, web search
```

- **Vapi** handled the phone line and the speech pipeline, with Deepgram for transcription.
- **Claude** did the reasoning and chose the tools.
- **A FastAPI tools server** on my machine bridged Claude's tool calls to command-line tools for Google services, iMessage and Apple Notes.

Setup was the repo's whole appeal: clone it, add three API keys, run a script that creates the voice assistant on the platform, start the tools server, call the number the platform gives you. I built it during my early-2026 experiments with OpenClaw (a large public open-source agent project I tried before building my own system on Claude Code), and the README still says so.

## What was wrong with it

It worked as a demo. As a daily tool it had four problems, which I wrote down in a v2 spec at the end of March:

| Problem | Why it mattered |
|---|---|
| A separate brain | The voice agent had its own system prompt and its own context. Voice me was talking to a different assistant than text me |
| A small subset of the tools | Voice got a handful of tools while the text side had far more. Voice was the dumber channel |
| No memory between calls | Every call started cold. I repeated myself |
| Slow first words | Responses took noticeably long to start, partly because of how the tool calls were wired |

The first row is the real one. The other three are symptoms of it. A second channel built as a second agent will always lag the first, because every improvement lands in one place and has to be ported to the other.

## The v2 plan: own the pipeline, share the brain

The v2 spec had two goals. Replace the hosted platform with a self-hosted pipeline (Twilio for the line, Deepgram for speech-to-text, Claude, Cartesia for speech, wired together with the open-source Pipecat framework), and make the phone reach the same brain as text, with the same tools and memory.

The latency budget I wrote for it is still the right way to think about voice agents:

```text
silence detection     300 ms   (deciding you've stopped talking)
speech-to-text        150 ms   (streaming)
model first token     280 ms
text-to-speech         90 ms   (first audio chunk)
network                30 ms
total                 850 ms   target: under 800
```

These are planned numbers from March 2026, not measurements. The levers were the useful part:

1. **Detect silence sooner.** Shortening the voice-activity window is the cheapest 300 milliseconds you'll find, at the cost of occasionally cutting someone off.
2. **Load context before the call connects.** Fetch the schedule, recent call summaries and memory while the phone is still ringing, not on the first turn.
3. **Fill tool time with speech.** Say "let me check your calendar" the instant a tool call starts. Dead air on a phone call reads as a dropped call.
4. **Let the caller interrupt.** If the agent keeps talking over you, nothing else matters.

Cross-call memory in the plan was simple: transcribe every call, summarize it, and load the last few summaries into the next call's prompt.

The pricing argument was that a hosted platform adds a per-minute fee on top of the speech, model and telephony costs you'd pay anyway. I never ran v2 long enough to measure what it actually saved, so I won't quote the per-minute numbers from the old version of this page. Check current pricing for each piece if you're doing the math yourself.

> **Note:** The self-hosted v2 pipeline was planned, not shipped. The public repo is the hosted-platform version only.

## Why it's archived

Two things happened.

First, the foundation moved. VoiceClaw v2 was designed to call into my OpenClaw setup, and in the spring I rebuilt everything on Claude Code instead. The project was archived in my registry on April 19, 2026. A plan to call a brain that no longer exists is not a plan.

Second, when I picked phone voice back up in June 2026, I respecified it around the lesson above. The new design put the phone in front of the same Claude Code harness my text channels use (same tools, same memory, same instruction files, a resumed session per caller) with a real-time voice framework handling the call. The brain loop worked off-call, with reads allowed automatically and writes needing confirmation. Telephony stalled on provider setup, and I put the time elsewhere.

Honest read: phone calls turned out to be the wrong shape for how I actually use the system. I talk to it in short bursts through the day, from a phone, and I want a record. Voice in my system today looks like this instead:

- Long replies get a spoken summary automatically, generated by a small text-to-speech model running locally.
- The cockpit has a read-aloud button on any message.
- Voice notes from a recorder and from my phone are transcribed and turned into tasks and notes.

That's in [Voice in and out](/docs/nerve-center/voice/).

## What to keep from it

- **One brain, many channels.** Never build the second interface as a second agent. Put the new channel in front of the same harness, with the same tools and memory.
- **Budget latency per stage.** "It feels slow" is not debuggable. 300 milliseconds of silence detection is.
- **Prefetch on ring.** Anything you can load before the first word, load before the first word.
- **Archive honestly.** The repo is still public because the hosted version is a fine weekend starting point. This page says what it isn't.

**Next:** [Lessons from running agents every day](/docs/field-notes/lessons-from-running-agents/)
