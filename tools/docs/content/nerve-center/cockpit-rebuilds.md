---
title: "What the cockpit rebuilds taught me"
description: "Replaying a terminal in a browser broke everything. What replaced it, and why syncing intent beats syncing state."
section: nerve-center
group: "The cockpit"
order: 160
updated: 2026-10-05
sources: ["learn/tier-3/d2-pty-scraping-reckoning.mdx", "learn/tier-3/d3-structured-stream-pivot.mdx", "learn/tier-3/d5-clean-chat-rendering.mdx"]
---

I rebuilt the cockpit's chat surface more than once, and every rebuild came from the same mistake in a new costume: treating something built for human eyes as if it were data. This article is the lessons in the order I learned them, ending with the one I'd put on a poster: sync intent, not state.

## What you'll learn

- Why replaying a terminal in a browser fails, and the five bugs it produced
- The plan I made in May, and what actually stuck
- How to filter Claude Code's transcript into a clean chat view
- The stale-phone-tab bug, and the nightly test suite that killed my real sessions

## Lesson 1: a terminal stream is not an API

Claude Code is an interactive terminal app. It draws colors, spinners, boxes and redraws with ANSI escape codes. The first cockpit attached to each session through a pseudo-terminal, captured the raw byte stream, and replayed it in the browser with a web terminal emulator. You're watching a terminal agent, so put a terminal in the browser. Reasonable. Wrong.

Every reliability bug the cockpit had came from that one choice:

| Symptom | Cause |
|---|---|
| Mangled output on phones | The app drew for the session's column width. The phone's terminal was narrower, so boxes wrapped and broke |
| Garbage after reconnect | Escape codes that move the cursor and overwrite lines replay differently once you've missed some |
| No structure | Bytes don't tell you when a tool call started, what it cost or whether it failed. You'd have to parse the rendering |
| Input races | Keystrokes forwarded as raw bytes collided with output being drawn, and got echoed twice |
| Reboot feel | Every tab sleep or network blip meant replaying everything or showing a blank pane |

On May 29, 2026 I sent three research agents at the question independently. They came back unanimous. My changelog that night put it plainly: the cockpit *"reinvents the wheel by scraping the interactive Claude Code TUI via PTY + replaying raw ANSI in browser xterm,"* and that one choice was the root cause of all of its reliability bugs.

The lesson has nothing to do with Claude Code. If a program has a structured output and a visual output, the visual one was built for the wrong reader. Consume the structured one.

## Lesson 2: the plan and what stuck

The May plan was to move the agent surface to headless runs that emit a stream of typed JSON events (`claude -p --output-format stream-json`), store every event in Postgres, and render a timeline from that. I built it. Headless runs (fleet workers, scheduled jobs) still render that way: tool calls as collapsible cards paired with their results, a "done" divider with the stop reason, a cursor-based API so a reconnecting client resumes from its last event instead of starting over.

The chat panes went a different way. They stayed long-lived interactive Claude Code sessions, and the clean view comes from somewhere better than the terminal: the transcript file Claude Code itself writes for every session, one JSON object per line. The June 1 version was a hybrid:

- **Display:** chat bubbles parsed from the session's own transcript file.
- **Interaction:** the real terminal, kept mounted one tap away, so interactive menus and prompts always have somewhere to go.

That's still the shape in October 2026. What changed is how the clean view stays live:

1. **July 14.** I'd added a live "typing" bubble by tapping the raw terminal stream. It leaked escaped JSON soup into the chat. The replacement streams the transcript itself and deleted the raw tap, with a test that fails if anyone adds it back.
2. **September 22.** Question cards in the clean view could only answer the first tab of a multi-part question, because the transcript only knows what was asked, not which tab the terminal is showing. The fix overlays the live tab parsed from the terminal onto the open question from the transcript. Each source does the one thing it's good at.
3. **October 2.** For speed, raw terminal output now acts as a doorbell: when bytes arrive, the view fetches the new tail of the transcript right away, with a 15-second safety poll behind it. The raw stream says *when*. The transcript says *what*.

Honest read: I expected the headless stream to win everything. It didn't, because an interactive session can do things a one-shot headless run can't, and the transcript gave me structure without giving those up.

## Lesson 3: filter on flags, not on text

A transcript file isn't a conversation. It has Claude Code's own plumbing mixed in: compaction summaries, meta turns, echoes of slash commands. Render all of it and you get a wall of summary text in the middle of the chat.

My first filter was a list of string patterns run against the rendered text. On June 8 a compaction summary leaked straight through it, because by the time the text was extracted, nothing about it looked like plumbing. The fix moved filtering into the parser, where the raw JSON objects still carry their flags:

```python
def is_plumbing(turn: dict) -> bool:
    if turn.get("isCompactSummary") or turn.get("isVisibleInTranscriptOnly"):
        return True                                   # compaction artifacts
    if turn.get("isMeta"):
        return True                                   # system meta turns
    content = (turn.get("message") or {}).get("content") or []
    return any(isinstance(c, dict) and c.get("type") == "text"
               and c.get("text", "").startswith("<command-name>")
               for c in content)                      # slash-command echoes
```

Then a test per artifact: a fixture transcript containing a compaction summary, asserting it never renders. Filter at the schema level, test each thing you filter, and keep a raw view for when you need to see everything.

> **Note:** These are fields in Claude Code's session files as I observed them in 2026, not a documented contract. If you build on them, pin them with tests so a CLI update fails loudly instead of quietly leaking plumbing into your UI.

## Lesson 4: sync intent, not state

This is the [teardown's](https://jddavenport.com/teardown) Failure 2. The cockpit syncs open sessions across devices. A phone tab left open overnight held an old copy of that list, and its writes were last-write-wins on the whole list. So it kept reviving sessions I had already closed. I'd kill them, and the phone would bring them back.

The moment two devices can write the same state, a full-state write is a time machine: the staler device overwrites the newer truth. The fix was to stop syncing state and start syncing intent:

- **Per-entry tombstones.** Closing a session writes a fact that nothing can overwrite.
- **Semantic writes.** A device can add what it knows. It can never erase what it missed.

Later I made the same idea constitutional. A session's desired state (warm, parked or closed) can be written by exactly two actors: me closing or reopening a pane, and me confirming a task is done. Not the reaper, not memory pressure, not a timer. The code raises on any other writer, and a test pins it.

### The sequel: a test suite with my credentials

On September 13 I traced a nightly session massacre. An end-to-end test suite drove the live production cockpit while signed in as me, and in about twenty minutes it issued 61 deletes across 36 sessions, real ones among them. Tombstones did exactly what they were built to do: they kept those sessions dead.

Two fixes. A delete now counts as my decision only with positive proof that it came from a control a human confirmed; anything else is logged but not treated as intent. And typing into a session that was deleted now reopens it instead of returning an error. The suite stays disabled, and the standing rule for build and QA agents got sharper: never touch a live session; use read-only checks or a clearly marked disposable session you delete afterward.

The lesson: once a delete is permanent, the delete path needs proof of *who*. Tombstones make mistakes sticky.

## Copy this

1. Find the structured source before you render anything. Your harness probably writes one.
2. Use the visual stream as a signal, not as content.
3. Filter on flags in the raw objects, with a test per artifact.
4. For anything two devices can write: tombstones, semantic writes, and a short list of who's allowed to write intent.

**Next:** [The bridge](/docs/nerve-center/the-bridge/)
