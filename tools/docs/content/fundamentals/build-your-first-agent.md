---
title: "Build your first agent"
description: "A small agent that runs on a schedule: a definition, rules, one skill, a memory file, and a hard rule that it drafts but never sends."
section: fundamentals
group: "Capstone"
order: 130
updated: 2026-10-05
sources: ["tutorials/your-first-agent.mdx", "tutorials/build-your-first-openclaw-agent.mdx"]
---

This tutorial puts the whole section together. You'll build a research briefer: every morning it searches the web for what changed on one topic, checks its sources, writes a short brief to a file, and remembers what it already reported so it never repeats itself. It drafts. It never sends. Everything here is plain Claude Code: an agent definition, a CLAUDE.md, one skill, a settings file, a memory file and a scheduler.

## What you'll build

```text
brief-agent/
  CLAUDE.md                          rules and the topic
  .claude/settings.json              what the agent may and may not do
  .claude/agents/briefer.md          the agent definition
  .claude/skills/write-brief/SKILL.md   the procedure and output format
  memory/seen.md                     URLs already reported
  briefings/                         one brief per day
  logs/                              run receipts, written by the runner
  run-brief.sh                       runs the agent headless and logs the result
```

You need Claude Code installed and signed in (see [install Claude Code](/docs/start-here/install-claude-code/)). Budget about 30 minutes, most of it reading the first brief and tuning the skill.

## Step 1: make the workspace

```bash
mkdir -p ~/brief-agent && cd ~/brief-agent
git init
mkdir -p .claude/agents .claude/skills/write-brief memory briefings logs
printf '# Already reported\n' > memory/seen.md
```

`git init` isn't decoration. When the agent edits its memory file badly, `git diff` shows you exactly what it did, and `git checkout` undoes it.

## Step 2: CLAUDE.md, the rules

Create `CLAUDE.md`:

```markdown
# brief-agent

## Topic
AI coding tools: new releases, notable research, and real-world lessons.
(Change this section to your own topic.)

## Files
- `briefings/YYYY-MM-DD.md`: one brief per day. Never edit an old one.
- `memory/seen.md`: every URL already reported, with its date. Read it first. Update it last.
- `logs/`: written by the runner script, not by you.

## Hard rules
- You draft. You never send. No email, no messages, no posts, no form
  submissions, nothing that creates or changes anything outside this folder.
- Only write inside `briefings/` and `memory/`.
- Every item needs a source URL you actually fetched. No fetch, no item.
- If nothing new and worth reading happened, say so in one line. Don't pad.
```

Short, checkable, and the most important rule is first. That's the [CLAUDE.md](/docs/fundamentals/claude-md/) article in practice.

## Step 3: the agent definition

Create `.claude/agents/briefer.md`:

```markdown
---
name: briefer
description: Writes the daily research brief for this folder's topic. Use for "write today's brief" or "run the briefing".
tools: Read, Edit, Write, WebSearch, WebFetch
model: sonnet
skills:
  - write-brief
---

You are a research briefer. You find what changed in the last 24 hours on
one topic, check it, and write a brief a busy person can read in two minutes.

Follow the write-brief skill exactly. Follow the hard rules in CLAUDE.md,
especially this one: you draft, you never send.

Be skeptical. Prefer primary sources (release notes, papers, official docs)
over coverage of them. If two sources disagree, say so instead of picking one.
```

Three choices worth noticing:

- **`tools` has no `Bash`.** No shell means no `curl`, no mail command, no script that could send anything. The agent can read, write files, search and fetch. That's all a briefer needs. Choosing tools is a safety decision before it's anything else.
- **`model: sonnet`.** A daily brief is normal work, not the hardest reasoning you do. Start on the mid tier and move up only if the output is measurably worse. See [cost and model choice](/docs/fundamentals/cost-and-model-choice/).
- **`skills` preloads the procedure.** The full skill is injected at startup, so the agent doesn't have to discover it.

When you run a session as this agent (next steps), its prompt replaces Claude Code's default system prompt, and CLAUDE.md still loads.

## Step 4: the skill, the procedure

Create `.claude/skills/write-brief/SKILL.md`:

```markdown
---
name: write-brief
description: Procedure and format for the daily research brief. Use when writing or checking a brief.
---

# Write the daily brief

1. Read `memory/seen.md`. Anything listed there is already reported.
2. Run 3 to 5 different web searches on the topic, limited to the last 24 hours.
3. Fetch every candidate before you use it. Drop anything you couldn't fetch,
   anything older than 48 hours, and anything already in `memory/seen.md`.
4. Pick at most 5 items. Rank by how much each would change what a
   practitioner does this week.
5. Write `briefings/<today>.md` in the format below.
6. Append every URL you fetched, used or skipped, to `memory/seen.md` as `- <today> <url>`.
7. Delete lines in `memory/seen.md` older than 30 days.

## Format

# Brief: <today>

**Bottom line:** one sentence.

## Items

### <headline in plain words>
Two or three sentences: what happened, and why it matters.
Source: <url>

## Skipped
One line per notable item you dropped, and why.

## Edge cases
- Nothing useful found: write "Nothing new worth your time today." and stop.
- A source is paywalled: don't summarize what you couldn't read.
- Today's file already exists: don't overwrite it. Write `briefings/<today>-2.md`
  and say why at the top.
```

The "Skipped" section is the part people leave out and later wish they had. It's how you see what the agent rejected, and whether it rejected the right things.

## Step 5: settings, the guardrails

Create `.claude/settings.json`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch",
      "Edit(briefings/**)",
      "Edit(memory/**)"
    ],
    "deny": [
      "Bash",
      "Read(./.env)",
      "Edit(CLAUDE.md)",
      "Edit(.claude/**)"
    ]
  }
}
```

The allow list pre-approves exactly what a run needs, so it can work headless. `Edit(...)` rules cover every built-in tool that writes files, including creating new ones. The deny list removes the shell entirely in this folder and stops the agent from editing its own rules, definition or skill. An agent that can rewrite its own instructions doesn't really have instructions.

## Step 6: run it by hand

```bash
cd ~/brief-agent
claude --agent briefer
```

Claude Code will ask whether you trust this folder. Say yes. This step is not optional: until a folder is trusted, Claude Code ignores the allow rules in its `.claude/settings.json`, so a headless run there gets search, fetch and file writes denied.

The startup header shows `@briefer`. Type `write today's brief` and watch. Then read three things:

1. `briefings/<today>.md`: is it useful? Are the sources real and recent?
2. `memory/seen.md`: did it record the URLs it fetched?
3. The transcript: did it fetch before citing, or cite from search snippets?

Your first brief will need tuning. That's expected. Fix the skill, not the brief: tighten the ranking rule, add an example of a good item, add an edge case you hit. Run it again until two runs in a row are good. Then run it a second time on the same day and confirm it doesn't repeat anything. That's the memory file working.

Now run it headless, the way the scheduler will:

```bash
claude -p "Write today's brief." --agent briefer --permission-mode dontAsk --max-turns 40
```

`dontAsk` means anything not pre-approved is denied instead of waiting for a click that will never come. `--max-turns` stops a run that loops.

> **Warning:** When I tested this tutorial on October 5, 2026, I ran the headless command before ever opening the folder interactively. Claude Code printed a warning that it was ignoring the folder's allow rules because the workspace wasn't trusted, every tool it needed (search, fetch, write) was denied, and the agent (correctly) refused to invent a brief. The process still exited 0. That's exactly why the next step's receipt checks for the file instead of the exit code: it logged `FAILED exit=0`.

## Step 7: the runner script, with a receipt

Create `run-brief.sh`:

```bash
#!/bin/bash
# run-brief.sh: run the briefer once, headless, and log a receipt line.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p logs briefings

# cron runs with a tiny PATH, so use the full path from `command -v claude`
CLAUDE_BIN="/full/path/to/claude"

# macOS cron can't read the login Keychain; use a long-lived token if present
TOKEN_FILE="$HOME/.config/brief-agent/token"
if [ -f "$TOKEN_FILE" ]; then
  export CLAUDE_CODE_OAUTH_TOKEN="$(cat "$TOKEN_FILE")"
fi

today="$(date +%F)"
"$CLAUDE_BIN" -p "Write today's brief." \
  --agent briefer \
  --permission-mode dontAsk \
  --max-turns 40 \
  > "logs/$today.out" 2>&1
code=$?

# the receipt checks for the artifact, not just the exit code
if [ -f "briefings/$today.md" ]; then
  echo "$(date '+%F %T') ok exit=$code file=briefings/$today.md" >> logs/runs.log
else
  echo "$(date '+%F %T') FAILED exit=$code no brief written, see logs/$today.out" >> logs/runs.log
fi
```

```bash
chmod +x run-brief.sh
./run-brief.sh && tail -1 logs/runs.log
```

The last block is the important one. An exit code of 0 means the process ended. It doesn't mean a brief exists. The receipt line checks for the file, because that's the thing you actually wanted. More on that in [logging and receipts](/docs/fundamentals/logging-and-receipts/).

## Step 8: put it on a schedule

Pick the scheduler that matches where the work needs to run:

| Option | Runs where | Good for | Watch out for |
|---|---|---|---|
| cron or launchd running `claude -p` | Your machine | Local files, full control | The machine has to be awake |
| Desktop scheduled tasks | The Claude Code desktop app | If you already use the desktop app | Same: your machine |
| Routines (`/schedule`) | Anthropic's cloud (research preview as of October 2026) | Runs with your laptop closed | Works against a repo, so memory has to be committed there |
| `/loop` | Inside one open session | Testing a cadence | Dies when the session closes |

For cron, add one line with `crontab -e`:

```text
0 7 * * * $HOME/brief-agent/run-brief.sh
```

On Linux that usually just works. On macOS there's one trap that cost me real time: cron jobs can't read your login Keychain, which is where Claude Code keeps your sign-in, so the run fails to authenticate even though it works perfectly from your terminal. Two fixes:

1. Run `claude setup-token` (it needs a Claude subscription), save the token it prints to `~/.config/brief-agent/token`, and run `chmod 600` on that file. The runner script picks it up. Treat that token like a password.
2. Or schedule the script with a launchd LaunchAgent instead of cron, which runs inside your login session. This is what my own system does for any job that needs the Keychain.

Tomorrow morning, check `logs/runs.log` before you open the brief. If the last line says FAILED, the `.out` file next to it says why.

## Done when

- `claude --agent briefer` shows `@briefer` and writes a brief on request
- Two consecutive briefs are good enough that you'd actually read them
- A second run on the same day reports nothing already in `memory/seen.md`
- The headless command finishes without stopping for a permission prompt
- `logs/runs.log` gets an `ok` line after a run, and a `FAILED` line when you break it on purpose (rename `briefings/` and run it)
- The scheduled run fires once while you're not watching, and you can tell from the log alone that it worked

## The safety rule, and why it has three layers

"It drafts, it never sends" is written in CLAUDE.md, enforced by the agent having no tool that can send, and backed by a settings file that denies the shell and blocks edits to its own rules. Any one layer alone would probably hold. I've watched "probably" fail enough times to want three.

There's a quieter reason too. This agent reads untrusted web pages every day. A page can contain text written to manipulate an agent. That's survivable here because the agent has nothing private to leak and no channel to leak it through. The day you give it access to your inbox, keep the inbox and the open web on separate agents, or put a human approval between them and any outbound message. My system routes every outbound message through one gate that needs my yes; see [the send gate](/docs/safety-and-operations/the-send-gate/).

## Where to go from here

- Add a second topic by copying the folder, not by making one agent do two jobs.
- Add a watcher instead of a schedule when the brief should fire on an event ("a new release of X"), not a time.
- Hand the draft to a human-approved send step when you want it in your inbox. Keep the agent itself draft-only.

You now have every primitive from this section working together: files as state, rules in CLAUDE.md, tools chosen on purpose, a skill, settings that enforce, a log that tells the truth, and a model picked for the job. The patterns section is about what happens when you run many of these at once.

**Next:** [Anatomy of an agent](/docs/patterns/anatomy-of-an-agent/)
