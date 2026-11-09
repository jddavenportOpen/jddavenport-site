---
title: "Scheduled agents and watchers"
description: "Run an agent on a schedule, or until a condition fires, without it running forever or failing in silence. Built on foundry-builder-kit."
section: marketplace
group: "Workflows"
order: 50
updated: 2026-11-09
sources: ["https://github.com/ai-foundry-byu/foundry-marketplace/tree/main/plugins/foundry-builder-kit"]
---

A promise like "check back on this tomorrow" is lost the moment the chat closes. Put it in a machine loop instead. Pick the loop by its shape, and give every loop a way to stop and a way to tell you it died.

## What you install

```
claude plugin marketplace add ai-foundry-byu/foundry-marketplace
claude plugin install foundry-builder-kit@ai-foundry
```

`scheduled-agents` writes the job: a cron line, a macOS launchd plist, a Linux systemd timer or a Windows scheduled task, plus a runner that calls Claude Code headless.

## The steps

1. **Name the shape.** A fixed cadence forever is a schedule. "When the reply lands" is a watcher: it checks a condition and pings once when it fires. A one-off on a date is a dated reminder.
2. **Give it an off switch.** Every loop gets an expiry, a fire-once rule, or an owner who turns it off.
3. **Change-gate the output.** Only notify when something changed. A loop that sends the same list six times a day gets muted, and then it is worse than nothing.
4. **Add a deadman.** A second, dumb check that alerts when the job has not run on time. A job that stops running makes no noise on its own.

## Check your work

Kill the job on purpose once. The deadman should tell you within one missed run.

## Limits

`scheduled-agents` is labeled beta: the generated config and runner are unit-tested, and its deadman fixes have not been re-run live. Run the job yourself once before you trust it. The patterns are in [Watchers](/docs/patterns/watchers/) and the [Loops doctrine](/docs/patterns/loops-doctrine/).
