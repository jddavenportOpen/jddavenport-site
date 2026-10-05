---
title: "Voice in and out"
description: "Spoken summaries that fire without the model remembering, local text-to-speech, a read-aloud button in the cockpit, and dictation that doesn't invent words."
section: nerve-center
group: "Interfaces and tools"
order: 190
updated: 2026-10-05
sources: ["learn/tier-2/10-voice-in-out.mdx"]
---

A long reply is hard to read while you're walking across campus, so the system talks. Summary-length answers on Telegram and iMessage arrive with a voice note, every reply in the cockpit has a read-aloud button, and I can dictate into the cockpit instead of typing. The speech is generated on my own machine with a small open model; nothing goes to a cloud text-to-speech service.

Almost every lesson here is the same lesson: voice fails *silently*. A missing voice note doesn't throw an error. It just doesn't arrive, and you notice a week later.

## Out: spoken summaries

### Stop making the model remember

For weeks I had to ask "and the voice?" after summary replies. The rule was in the instructions, and the model followed it early in a session and forgot it as the context filled up. Any rule that has to compete with everything else in a long context loses eventually.

So on May 8 the job moved out of the model's memory and into a Stop hook: code that runs at the end of every turn, whether the model remembers or not. [Hooks](/docs/fundamentals/hooks/) covers the mechanism.

The gates, in order:

1. **Is voice mode on?** A global switch: `/voice on`, `/voice off`, or `/voice once` (one voice note, then off).
2. **Is the reply summary-class?** At least 300 characters, or it has a Markdown header, or it has two or more list items. Short acks stay text.
3. **Opt-out token?** If the reply contains the literal token `[no-voice]`, skip. That's the per-reply escape hatch for things like a big table that reads terribly out loud.
4. **Already spoken?** A dedup ledger keyed on the reply's message id prevents double-fires.

The text is cleaned before it's spoken: code blocks and headers are stripped, and anything over about 700 characters is cut to the first paragraph plus a closing summary.

### Then the hook went quiet

In July the Telegram side was rebuilt as a headless transport ([the full story](/docs/nerve-center/phone-and-messaging/)). The voice hook's trigger looked for a reply-tool call in the session transcript. In the new design the *transport* sends the reply, so that call never appears. The hook would run after every turn and do nothing, forever, without an error.

That got caught during the rebuild's testing, and the same gates were moved into the transport, running on the confirmed outbound text. Lesson: when you change who sends a message, check every hook that keyed on the old sender.

## The voice itself: local Kokoro

The first voice used a cloud text-to-speech API. When its key went dead, the fallback was the built-in macOS voice, which is serviceable and sounds like a GPS from 2009.

In early June I replaced it with Kokoro-82M, a small open neural text-to-speech model under the MIT license that runs offline on Apple Silicon. Kokoro is the voice now and the macOS voice is the fallback. The old cloud API is still wired in, but only runs with a working key, and it doesn't have one.

Two silent failures came with it:

**The kill switch that killed the fallback.** The Stop hook had a gate: if the cloud API key wasn't set, skip voice entirely. That made sense when the cloud API was the only engine. When the key expired, it silently turned off voice for everything, including the local fallback. The fix was to delete the gate and let the engine order handle fallback. A guard that was right when written became wrong when the architecture changed underneath it.

**The model that lived in a cache.** On June 11 the voice suddenly went robotic. The Kokoro model files had been sitting in a cache folder, and a disk cleanup did exactly what cleanups do to caches. Nothing errored; it fell back to the macOS voice. The model now lives in a protected folder, the voice code re-downloads it in the background if it's ever missing, and a daily check confirms it's there.

> **Tip:** Anything your system can't run without doesn't belong in a folder whose name tells cleanup tools it's disposable.

Kokoro needed a newer numerical library than the rest of my Python tools, so it runs in its own virtual environment. The build agent caught the conflict and isolated it instead of upgrading the shared environment and breaking the analytics stack. Isolate over break is the right default.

## Read-aloud in the cockpit

Since August 24 every assistant reply in the cockpit has a speaker button. The audio is synthesized on my own machine with the same Kokoro voice, because the hosted web app has no model and a short request time limit. A warm server mode loads the model once instead of per chunk, which brought a warm request to about 0.45 seconds.

The hard part was making Markdown sound like speech. The first version had a bug that read tables as gibberish: it swapped each table row for a placeholder word, and when the cleanup missed, the placeholder got read out loud, and it collided with real prose that happened to contain the same word. The fix renders each block (code, table, list, quote) straight to prose with no placeholder. Probing that bug class found more: commit hashes read character by character, shell commands read as "slash x dot s h", HTML entities read as "ampersand a m p semicolon." Small tables are now read as "header: value" pairs; big ones are summarized.

If my machine is unreachable, the button falls back to the browser's built-in speech and says so, instead of pretending.

## In: dictation that doesn't invent words

The cockpit's microphone button works the way Telegram's does since August: tap, talk, tap send. The recording streams to my machine while I talk and is transcribed locally with Whisper, so the wait after I hit send stays flat instead of growing with the length of the take. The message sends itself when the transcript lands.

Whisper has a known habit: given silence, it hallucinates. Two versions of that shipped as my words before they were caught:

- A silent recording came back as "You You You You You." Fix: measure the audio's peak level *before* transcription and refuse to transcribe silence.
- A loud recording with no human voice in it (phone noise) came back as "Thank you." The loudness gate passed it. Fix: a second, independent check for how much of the audio is actually in the human voice range.

In September an audit diffed every take against fresh re-decodes and found the small model was mangling my vocabulary, so it moved to a larger, faster Whisper variant. The model name had been typed by hand in three separate places, one of them on a model already known to be bad. All three now ask one shared resolver.

## Voice on iMessage

Since late September, the assistant's iMessage channel follows the same rules: summary answers get a voice note after the text (the text always goes first, and a voice failure never blocks it), `[no-voice]` works, and `/voice on|off|once` is the same global switch as Telegram. Voice memos I send are transcribed locally before the assistant sees them.

For a voice agent you can *call* on the phone, see [VoiceClaw](/docs/builds/voiceclaw/).

## What to copy

1. Put the trigger in code that runs every turn, not in instructions the model has to remember.
2. Test the silent path. Disable each engine and confirm the next one speaks.
3. Keep model files out of cache folders.
4. Gate transcription on whether there's a human voice, not just whether there's sound.
5. Render structure to prose directly. Never round-trip it through a magic placeholder word.

**Next:** [The agent browser](/docs/nerve-center/agent-browser/)
