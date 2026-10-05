---
title: "Reading the output: plans, tool calls, results"
description: "How to read what a session shows you, spot when the agent is stuck or guessing, and step in before it wastes an hour."
section: start-here
order: 70
updated: 2026-10-05
sources: ["learn/tier-0/07-reading-the-output.mdx"]
---

The text scrolling past in a session is the agent narrating its plan, the tools it calls, and what came back. Once you can read it, you supervise the agent instead of hoping it lands. This page teaches the four parts of the stream, the signs of trouble, and the one habit that saves the most time: decide what proof of "done" you'll accept before you accept it.

## The four things you'll see

A session is a loop of four kinds of output, repeated until the task is finished.

**1. The plan.** Before acting, the agent usually says what it's going to do: "I'll find the config file, then change the timeout." This is your cheapest moment to catch a misunderstanding. If the plan is wrong, press `Esc` and redirect now.

**2. The tool call.** The agent reaching for a tool: read a file, search, edit, run a command, fetch a page. It names the target, so you can see which file or which command. Actions that change things are where permission prompts appear.

**3. The result.** What came back: the file contents, the search matches, the command output, the error. This is the most information-dense part of the stream, because it's ground truth. The agent's next move should follow from it.

**4. The next step or the final summary.** Another tool call, or a summary of what it did. Then it stops and waits for you.

Long results get collapsed to keep the screen readable. Press `Ctrl+O` to open the transcript viewer, which shows every tool call and its full output, with a timestamp and model on each message. When something seems off, that's where you look.

## What a healthy run looks like

You ask: "The site won't build. Find out why and fix it."

1. Plan: "I'll run the build first to see the error."
2. Tool call: runs the build.
3. Result: an import error on line 12 of one file.
4. Plan: "That import is misspelled. I'll open the file."
5. Tool call: reads the file. Result confirms the typo.
6. Tool call: edits the import.
7. Tool call: runs the build again. Result: success.
8. Summary: "Fixed a misspelled import on line 12. The build passes."

Every step follows from the last result, not from a guess. And notice step 7: it proved the fix by running the build again instead of just announcing it.

## Signs it's stuck or guessing

| What you see | What it usually means | Your move |
|---|---|---|
| The same command, the same error, three times | It's looping without a new idea | Stop it. Paste the real error, or point it at the right file. |
| Edits to files you didn't mention | It filled a vague request with its own goal | Stop it. Restate the task narrowly. |
| "I can't find" or "I don't have access" | A missing file, tool, or permission | Give it the path or the context. Usually it's a gap, not a dead end. |
| A claim with no tool call behind it | It's reasoning from memory, not from your files | Ask "show me where you saw that." |
| "Done" with no proof in the stream | It believes the task is finished | Ask for the evidence (next section). |

The last row costs beginners the most, because it's quiet. The agent isn't lying. It genuinely believes it finished, based on what it saw. Your defense is a habit, not vigilance.

## Decide what "done" means before you start

Before you accept "done," know which evidence you'd accept. Better, say it in the request:

```text
Fix the failing login test. Done means: the test suite passes, and you show me the output.
```

Good evidence is something you can check without trusting the agent's summary:

- **A test that passes**, with the output in the stream.
- **A file** you can open and read.
- **A URL that loads** and shows the change.
- **A git diff** that contains only what you asked for.

Bad evidence is the agent's own sentence saying it worked.

On my own system this stopped being a habit and became a rule in July 2026. "Done" now has a machine definition for anything user-facing: the live site has to report the exact git commit that was merged, and a browser test has to click through the real user journey on the live site and pass. If either check fails, or can't run, nobody gets to say "it's live." [Ship to prod](/docs/patterns/ship-to-prod/) covers how that gate works.

## When to step in

You don't have to wait for a bad run to finish.

- **Press `Esc`** to stop the current step. The work so far is kept, and you can type a correction.
- **Type while it works.** Messages you send mid-turn get queued and delivered to the agent, so you can add a fact without stopping it.
- **Narrow the task.** "Just fix the failing test in auth.js. Don't touch anything else."
- **Rewind.** If it went down the wrong path entirely, `/rewind` rolls back to an earlier prompt.

## The supervisor's job

You're not writing the code or running the commands. Your job is to read the plan, sanity-check the tool calls, glance at the results, and verify the outcome against evidence you chose in advance. Do that and you catch the rare wrong turn while it's still cheap.

**Next:** [Where to go next: learning paths](/docs/start-here/learning-paths/)
