---
title: "settings.json and permissions config"
description: "The settings hierarchy, allow and deny rules, env vars, hooks wiring, and what goes in user, project and local files."
section: fundamentals
group: "Extending Claude Code"
order: 90
updated: 2026-10-05
sources: ["learn/tier-1/09-settings-json.mdx"]
---

`CLAUDE.md` talks to the model. `settings.json` configures the harness around it: what the agent may do without asking, what it must never do, which hooks run, which environment variables are set. The model can ignore a sentence in CLAUDE.md. It can't ignore a deny rule. This article covers where settings live, how they combine, a safe starter file, and the one lesson that cost me the most: every setting needs exactly one owner.

## Where settings live

Five levels, highest precedence first:

| Level | Where | Who it's for |
|---|---|---|
| Managed | A policy your organization deploys | Everyone it's deployed to. You can't override it. |
| Command line | Flags like `--model`, or `--settings <json>` | This one session |
| Project local | `.claude/settings.local.json` | You, in this project. Kept out of git. |
| Project shared | `.claude/settings.json` | Everyone in the repo. Commit it. |
| User | `~/.claude/settings.json` | You, in every project |

A key set at a higher level wins over the same key set lower down. Lists are different: `permissions.allow` and friends merge across files, so your user file and the project file can each add rules without erasing each other.

A few practical notes:

- Settings files are strict JSON. A comment or a trailing comma is a syntax error, and Claude Code reports it at the next start.
- When Claude Code creates `settings.local.json` itself, it adds it to your global git excludes. If you create it by hand, add it to `.gitignore` yourself.
- `/status` shows which settings files loaded. `/config` edits common settings interactively. `/permissions` shows and edits rules by scope.

## Permission rules

Rules are written as `Tool(specifier)` and sorted into three lists:

- **allow**: runs without asking
- **ask**: always asks, even if something else would allow it
- **deny**: never runs

They're evaluated deny first, then ask, then allow. The first match wins, and a more specific rule doesn't jump the queue. So a deny always beats an allow.

Some rule shapes:

| Rule | Matches |
|---|---|
| `Bash(npm run test *)` | Any `npm run test ...` command |
| `Bash(git push *)` | Any push (put it in `ask`) |
| `Read(./.env)` | Reading `.env` in the project root |
| `Edit(src/**)` | Edits to files under `src/` |
| `WebFetch(domain:docs.python.org)` | Fetches from that domain |
| `Bash` | Every shell command (a bare name in `deny` removes the tool entirely) |

Two traps worth knowing:

1. **Path rules only use `Read(...)` and `Edit(...)`.** `Edit` rules cover every built-in tool that changes files, including `Write`. A path rule written as `Write(...)` is accepted and then never consulted.
2. **Bash rules match the command text, not the program.** `Bash(rm *)` in deny stops `rm -rf build/`. It doesn't stop `/bin/rm -rf build/`. Treat Bash deny rules as guardrails for the commands the agent normally writes, not as a security boundary. For hard guarantees, use a hook, the sandbox, or a gate in your own code.

## Permission modes

The mode decides what happens when no rule matches:

| Mode | Behavior |
|---|---|
| `default` | Asks for anything that needs permission |
| `acceptEdits` | Accepts file edits automatically, still asks for other actions |
| `plan` | Reads and plans, makes no changes until you approve |
| `auto` | A classifier decides most prompts for you |
| `dontAsk` | Anything that would prompt is denied; only pre-approved tools run |
| `bypassPermissions` | Skips prompts. Only for sandboxes you're willing to lose. |

Set the starting mode with `permissions.defaultMode` or `--permission-mode`. `dontAsk` plus a tight allow list is the right combination for scripts and scheduled jobs, where nobody is around to click yes. The [build your first agent](/docs/fundamentals/build-your-first-agent/) tutorial uses exactly that.

## A safe starter project file

Placeholders only. Change the commands to your stack.

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ],
    "ask": [
      "Bash(git push *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(git push --force *)"
    ]
  },
  "env": {
    "NODE_ENV": "development"
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git push *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/no-force-push.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

The `$schema` line gives you autocomplete and validation in most editors. The deny list keeps secrets out of the agent's reads. The `ask` on push means nothing leaves your machine without a look. The hook is the belt to the deny rule's suspenders, for the force-push variants a text match would miss. The [hooks article](/docs/fundamentals/hooks/) has the script.

## What goes where

| What | Where |
|---|---|
| Rules, conventions, the reasons behind them | `CLAUDE.md` |
| Commands the agent may run without asking | `permissions.allow` |
| Commands that always need a look | `permissions.ask` |
| Things that must never happen | `permissions.deny`, plus a hook if it really matters |
| Hooks | `hooks` |
| Non-secret environment variables | `env` |
| Your personal overrides for one project | `.claude/settings.local.json` |
| Secrets | Your shell environment or a secrets manager. Never a committed settings file. |

## One setting, one owner

This lesson cost me the most, and it has nothing to do with syntax.

From August 8 to September 4, 2026, two of my scripts both managed the same setting: the default effort level in my settings files. One was an integrity guard that every 15 minutes made sure the value matched what I'd chosen. The other was a usage throttle that lowered effort when plan usage ran hot and raised it again later. Each had the "right" value hardcoded, and the two values were different.

So they fought. The throttle wrote its value, the guard put its own back, the throttle wrote again. 30 to 70 times a day, for almost four weeks. Each script's log looked healthy. Each one was doing its job. The setting itself was never stable.

The fix was ownership: the value now lives in one registry key, both scripts read it, and neither has a literal of its own. If you want to change the setting, there's exactly one place to do it.

I've since applied the same rule to the Claude Code binary itself. One pipeline owns upgrades: it tests a new release, swaps it in atomically and rolls back automatically if checks fail. Every settings file disables the CLI's own auto-updater, using documented environment variables, so no running session updates itself underneath that pipeline:

```json
{
  "env": {
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

Before you add a script that writes to a settings file, ask: does something else already write this key? If yes, one of them has to stop.

**Next:** [Git discipline for agents](/docs/fundamentals/git-for-agents/)
