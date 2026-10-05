---
title: "Schedules as a heartbeat"
description: "Scheduled jobs are the system's pulse. Built-in options first, then cron vs launchd, staggered timing, and output that only speaks when something changed."
section: patterns
group: "Loops and schedules"
order: 80
updated: 2026-10-05
sources: ["learn/tier-2/05-crons-as-a-heartbeat.mdx"]
---

Scheduled jobs are what make an agent system a system. Without them, nothing happens until you type. With them, mail gets triaged, state gets synced and broken things get noticed while you sleep. The catch is that a schedule is a promise to do work forever, so you want each one cheap, quiet and easy to kill.

## What you'll learn

- The scheduling Claude Code gives you for free, and when it's enough
- Cron vs launchd on a Mac, and the Keychain gotcha that forces the choice
- Why every schedule gets its own minute
- Why I turned off the hourly agent "heartbeats" the old version of this page was built around

## Start with what's built in

Before you write a crontab line, check whether Claude Code already does the job. As of October 2026 it has three scheduling options, per the [official docs](https://code.claude.com/docs/en/scheduled-tasks):

| | `/loop` | Desktop scheduled task | Routine (cloud) |
|---|---|---|---|
| Runs on | Your machine | Your machine | Anthropic's cloud |
| Needs an open session | Yes | No | No |
| Needs the machine on | Yes | Yes | No |
| Sees your local files | Yes | Yes | No, it gets a fresh clone |
| Shortest interval | 1 minute | 1 minute | 1 hour |
| Lifetime | The session (tasks expire after seven days) | Until you delete it | Until you delete it |

`/loop 5m check whether the deploy finished` is the fastest way to babysit something during a session. Leave out the interval and Claude picks its own pacing, waiting longer when nothing is happening. For anything that has to survive the session closing, use a Desktop task or a routine.

Honest read: if you're starting today, these cover most of what I first built cron for. I built my own because I started before some of them existed and because I wanted every job's output in my own files and tables. You don't need to repeat that.

## When you outgrow them: cron and launchd

On a Mac you have two native schedulers. My rule for picking:

| Use | When |
|---|---|
| **cron** | A script runs, writes something, exits. No secrets from the login Keychain, no GUI session needed. |
| **launchd LaunchAgent** | The job must stay alive (restart on crash), or it needs the logged-in user's session: the Keychain, OAuth tokens stored there, anything that touches the GUI. |

The Keychain line is the one that bites. Cron jobs run outside your login session, so cron can't access the login Keychain. A job that reads a token from it works perfectly in your terminal and fails every time under cron. My crontab still carries a comment from one of those fixes: "Keychain OAuth is unreachable from cron's security session." Worse than failing loudly, a job that reads account state through the Keychain can get an empty answer and conclude everything is dead. The rule now lives in my main instruction file: anything that needs the Keychain is a LaunchAgent limited to the logged-in session, never a cron line.

A minimal LaunchAgent that runs a script every hour looks like this:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.example.inbox-digest</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/path/to/inbox-digest.sh</string>
  </array>
  <key>StartInterval</key><integer>3600</integer>
  <key>LimitLoadToSessionType</key><string>Aqua</string>
  <key>StandardOutPath</key><string>/path/to/logs/inbox-digest.log</string>
  <key>StandardErrorPath</key><string>/path/to/logs/inbox-digest.log</string>
</dict>
</plist>
```

`LimitLoadToSessionType: Aqua` is what ties it to your logged-in session.

### The cron prelude

Cron also hands your script a nearly empty `PATH`. A script that calls `python3.12` from Homebrew finds nothing, or finds a different Python. Every scheduled script in my system starts the same way:

```bash
#!/bin/bash
cd "$HOME/agent-system" || exit 1
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export PYTHONPATH="$HOME/agent-system"
```

If a job works in your terminal and silently does nothing in cron, check this first. `command not found` in the job's log is the tell.

### Never pipe into `crontab -`

In June 2026 an agent edited the crontab with `crontab -l | python -c '...' | crontab -`. The inline Python had a syntax error, printed nothing, and `crontab -` installed that nothing. Every job was gone. Restoring meant a two-day-old backup plus replaying every change since by hand. Two weeks later a `sed` with a delimiter clash piped empty output into `crontab -` and wiped it again, and that time the newest backup was eight days old.

The rule since: write the new crontab to a file, check it, then install the file. And snapshot the crontab daily, so the worst case is one day of loss:

```bash
crontab -l > /tmp/crontab.new
# edit /tmp/crontab.new, then look at the diff
diff <(crontab -l) /tmp/crontab.new
[ -s /tmp/crontab.new ] && crontab /tmp/crontab.new   # never install an empty file
```

And the snapshot itself is one line:

```bash
5 5 * * * crontab -l > "$HOME/backups/crontab-$(date +\%Y\%m\%d).txt"
```

The backslashes matter: cron treats a bare `%` as a newline.

## Give every job its own minute

If ten jobs fire at `:00`, they all compete for CPU, network and model rate limits in the same second, and the slowest one times out. Spread them out: `:03`, `:10`, `:17`.

One trap while you're at it. My catch-up job is scheduled `*/47 * * * *`, which reads like "every 47 minutes." Cron doesn't see it that way. A step in the minute field restarts every hour, so `*/47` means minute 0 and minute 47, and the `:00` run lands right in the hourly crowd I was trying to dodge. If you want a true odd cadence, use a LaunchAgent `StartInterval` in seconds. If you want to stay off the top of the hour, name the minutes: `13,47 * * * *`.

This matters at boot too, which I learned the hard way. In September 2026 the main machine went into a run of kernel panics, six reboots on September 7 alone. The root cause was memory (that story is in [Watchdogs](/docs/safety-and-operations/watchdogs/)), but a boot herd made every panic worse: dozens of LaunchAgents marked run-at-load cold-started at once after each reboot and fought over the disk. I stripped run-at-load from the batch jobs, marked them low-priority background work and made every launchd interval unique.

Then the audit found the run-at-load change had done nothing. launchd caches a job's config when the job is loaded, so editing the plist on disk changes nothing until that job is unloaded and loaded again. If you edit a LaunchAgent, reload it, then ask launchd what it thinks the job is (`launchctl print gui/$(id -u)/<label>`) instead of trusting the file.

## Only speak when something changed

A schedule that sends the same message every time it runs is noise, and noise trains you to stop reading. My number one noise complaint, ever, was an open-loops digest that re-sent the same unchanged list every four hours, six times a day.

Every job that notifies a human should be change-gated: hash the content, compare it to the last one sent, and stay silent if they match. When I ran a twice-daily project digest, its crontab comment carried the whole contract in four words: "identical digest = no send."

```python
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

def send_if_changed(text: str, state_file: Path, send) -> bool:
    digest = sha256(text.encode()).hexdigest()
    last = loads(state_file.read_text()).get("digest") if state_file.exists() else None
    if digest == last:
        return False            # nothing new, say nothing
    send(text)
    state_file.write_text(dumps({"digest": digest}))
    return True
```

## The heartbeats I turned off

The old version of this page described hourly domain heartbeats: every hour, one agent per area of my life (school, work, health and so on) woke up, read its state and wrote a fresh report. It sounded like a pulse. In practice it was one model call per domain per hour, and most of those calls narrated "nothing changed."

On July 21, 2026 I retired them and replaced them with event-driven pulses. A domain's state now updates when something real happens: a project ships, a task completes, an agent posts a result. The pulse appends one line to an event log, refreshes the report, and stamps when it was produced. The old version re-stamped "Last Updated" even when nothing changed, which hid real staleness. The new one only stamps when it writes a new event. In August I turned off the rest of that class. My note at the time: no value out of any of them.

What survived is the useful kind of schedule: cheap, deterministic jobs that sync data, check health and catch missed work. Almost none of them call a model.

Honest read: "the agents check in every hour" is a great line in a demo. Ask what each scheduled run produces that you would miss if it stopped. If the answer is nothing, it's a cost, not a heartbeat.

## A starting set

If you're building your first always-on setup, start with four schedules and add more only when a real need shows up:

1. One sync job per data source you care about (mail, calendar), at the cadence that source actually changes.
2. One daily briefing that reads your state files and tells you what needs you, change-gated.
3. One daily backup of anything you can't rebuild, including the crontab itself.
4. One job that checks the other jobs ran. That's the subject of [Watchdogs](/docs/safety-and-operations/watchdogs/), and it's the one people skip.

**Next:** [The loops doctrine](/docs/patterns/loops-doctrine/)
