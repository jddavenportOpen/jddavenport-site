---
title: "Voice notes into the second brain"
description: "Recorder to transcript to tasks and CRM notes, the precision problems of version one, and the open-source openplaud."
section: builds
group: "Research and content"
order: 100
updated: 2026-10-05
sources: ["learn/tier-3/g6-plaud-voice-ingest.mdx"]
---

I carry a Plaud voice recorder. When I talk into it, the recording ends up transcribed on my own machine, and the things in it get routed: action items to my task lists, people to my CRM, meeting context to the right area of my notes. I don't type anything after I stop talking.

The routing is the easy part to describe. The hard part was precision. Version one was confidently wrong in ways that polluted long-term memory, and most of this article is about that.

## The pipeline

```text
recorder -> Plaud cloud -> local sync folder
  -> local transcription (Whisper)
  -> extract: my action items, people mentioned, meeting context, domain
  -> route:
       action items  -> backlog (shown on the cockpit's today view) + the domain's task list
       people        -> a note on that person's CRM file
       context       -> a memory note in the right domain, indexed for recall
  -> match against the calendar: which meeting was this?
```

A few design choices that hold the rest together:

- **Dry run by default.** The extractor shows its full routing plan and changes nothing unless it's run in live mode, which only the scheduled job does.
- **Idempotent.** Each action item gets a stable key built from the recording id and its position, so re-running a recording updates rows instead of duplicating them.
- **Pull, not push.** No phone notification per recording. Action items flow into the backlog, and the cockpit's today view surfaces them. Ten recordings shouldn't mean ten pings.
- **Calendar matching.** A matcher pairs each recording with the calendar event it overlaps (with a 15-minute window), so a 2 PM meeting and a 4 PM brain dump land as separate notes with the right context. When there's a meeting on the calendar with no recording, it says so as a gap instead of staying quiet.

## Transcription: the model matters more than you'd think

Everything downstream inherits the transcript's mistakes, so this is where precision starts.

- The smallest English Whisper model garbled names, which turned into wrong CRM keys.
- The next size up fixed most names, but still heard a product name as "in the back," with total confidence.
- On September 25, 2026 it failed in a worse way. On a day of long recordings at a conference, it looped: it repeated the same phrase over and over for most of several recordings. I re-transcribed the day with Whisper's large-v3-turbo model and recovered it.

The machine-wide default is now large-v3-turbo, set in one shared module that every transcription caller imports. The old setup had the model pinned separately in each script, which is exactly how one script stayed on the small model after everything else moved on.

## The precision problems

A June 2026 audit found the first version making three kinds of mistakes, and later ones found more. None of them threw an error. They just wrote wrong things into places I trust.

**Things that aren't people became people.** The extractor created CRM files for "Executive Assistant" (a role) and for a fragment of garbled audio. Later, garbled transcripts minted person files for places and organizations: "Hong Kong," "Utah Jazz," "Salt Lake," "Law School." The fix is a person-name gate with a regression test that lists exactly those strings as must-reject, next to real names that must pass.

**Everyone got filed in the same domain.** One function hardcoded a single domain for every CRM update, so every person from every recording landed in the same bucket regardless of context. That's a one-line bug with a long tail, because every wrong entry had to be found and moved.

**Mis-heard names made duplicates.** A transcription that spelled a known person's name slightly wrong created a new person instead of matching the existing one. One contact ended up with three competing files. The resolver now scores a spoken name against every CRM entry using phonetic similarity and edit distance, prefers the entry with a verified email when two are close, and refuses to guess on a real tie. A tie goes to a confirmation queue.

**Spoken contact details were lost.** People spell their email out loud, letter by letter, with "dot" and "at." Transcription mangles both. A parser now reassembles spoken emails and phone numbers and keeps the exact quote and recording line it came from, so a wrong capture is traceable.

**I became a contact.** In September the extractor created a new person from my own self-introduction in a recording. It was quarantined. Every new person now carries provenance, and a weekly guard checks for the fake-person class across the whole CRM.

The common thread: an extractor that writes to a long-term store needs a filter for "is this actually a person" and a refusal to guess. A bad entry costs more than itself, because every later decision gets made on top of it.

## Captured is not committed

In June the design moved from silently acting on everything to proposing first. The current version keeps that spirit a different way. Action items pulled from recordings land in a "captured" state, not straight on my to-do list. On October 4, 2026 a new intake gate on the shared backlog moved a few hundred auto-captured rows out of "next" and back to "captured," where they belong until someone triages them.

A recording where I say "I should look into that" is not the same as a commitment. The pipeline shouldn't pretend it is.

## Two silent outages

**May 2026: the schedule vanished.** The pipeline's scheduled job was lost and nothing ran for two days. Nothing alerted, because nothing was failing. When it was restored, a backfill processed 99 recordings that had piled up and wrote 88 notes, against zero in the gap. The fix restored the job, corrected a bug in which transcript took precedence when one came back empty, and added a size guard after a stuck recording produced an audio file big enough to run the backfill out of memory. Later, a retry-with-backoff layer added an aging alert: a recording that's still failing 72 hours after its first failure pages me once.

**September 22 to October 4, 2026: extraction went dark.** A crash in the extractor's logging setup stopped processing, and three long recordings got stuck. The fix, shipped October 4, made the job report an honest failure (a nonzero exit and a named failure key) instead of dying quietly, plus a backfill script. The next live run processed the backlog.

Same lesson both times: a job that can fail silently will. Make failure loud and make "nothing processed for too long" its own alarm.

## openplaud: the open-source piece

The part that's general enough to share is public: [jddavenportOpen/openplaud](https://github.com/jddavenportOpen/openplaud), a free, self-hosted manager for Plaud recordings. You don't need Plaud's subscription to use your own recordings.

From its README:

- Watches your Plaud sync folder for new recordings.
- Transcribes with local Whisper (free), Groq (fast) or Deepgram (adds speaker labels), falling back through that chain in order.
- Full-text search across every transcript.
- Audio playback with a waveform and segment navigation.
- Runs with Docker in one command, or with Bun directly.

```bash
git clone https://github.com/jddavenportOpen/openplaud.git
cd openplaud
docker compose up --build
```

Then open the local address the README gives you. Optional API keys for Groq or Deepgram go in a `.env` file; without them it uses local Whisper.

The routing into tasks and a CRM isn't in the public repo. That part is wired into my own [second brain](/docs/nerve-center/the-second-brain/) and [CRM](/docs/nerve-center/the-crm/), and the lessons above are the part worth taking with you.

**Next:** [Course-expert agents](/docs/builds/course-expert-agents/)
