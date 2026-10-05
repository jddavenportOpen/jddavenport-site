---
title: "Install Claude Code"
description: "Install the CLI on macOS, Linux or Windows, confirm it works with claude --version, and keep it updated."
section: start-here
order: 20
updated: 2026-10-05
sources: ["learn/tier-0/02-install-claude-code.mdx"]
---

This page gets the `claude` command onto your machine and proves it works. You need a terminal and an internet connection. You don't need Node.js, Python, or anything else for the recommended installer.

Every command here was checked against Anthropic's official setup page on October 5, 2026. If something on your screen disagrees with this page, trust the [official setup docs](https://code.claude.com/docs/en/setup). Install details move faster than articles.

## What you need

- **A terminal.** On macOS, open Terminal (Cmd + Space, type "Terminal"). On Windows, open PowerShell. On Linux, your usual terminal app. Never used one? Anthropic has a short [terminal guide](https://code.claude.com/docs/en/terminal-guide).
- **A supported system.** macOS 13 or later, Windows 10 (1809) or later, or a recent Ubuntu, Debian or Alpine. 4 GB of RAM or more.
- **A paid Claude account.** Pro, Max, Team, Enterprise, or a Console account with API credits. The free plan doesn't include Claude Code. You'll sign in on the next page.

## Install it

The native installer is the recommended path. Copy the line for your system, paste it, press Enter.

macOS, Linux, or WSL:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://claude.ai/install.ps1 | iex
```

On native Windows, install [Git for Windows](https://git-scm.com/downloads/win) too if you can. With it, Claude Code runs shell commands through Git Bash. Without it, Claude Code uses PowerShell instead. WSL doesn't need it.

> **Tip:** If PowerShell says `'irm' is not recognized`, you're in CMD, not PowerShell. Your prompt shows `PS C:\` when you're in PowerShell.

### Prefer a package manager?

Homebrew (macOS or Linux):

```bash
brew install --cask claude-code
```

WinGet (Windows):

```powershell
winget install Anthropic.ClaudeCode
```

There's also a global npm package. It needs Node.js 22 or later, and the official docs warn against installing it with `sudo`. If you don't already live in npm, skip it.

## Check that it worked

Open a **new** terminal window, then run:

```bash
claude --version
```

You should see a version number followed by `(Claude Code)`. That's a working install.

If the shell says `command not found: claude`, the install folder isn't on your PATH yet. Close the terminal completely, open a fresh one, and try again. Still broken? Run the diagnostic:

```bash
claude doctor
```

`claude doctor` prints install health, settings errors, and suggested fixes without starting a session. The [troubleshooting page](https://code.claude.com/docs/en/troubleshoot-install) matches most error messages to a fix.

## Keeping it updated

How updates work depends on how you installed:

| Install method | Updates |
|---|---|
| Native installer | Updates itself in the background. New versions take effect the next time you start Claude Code. |
| Homebrew | Manual: `brew upgrade claude-code` |
| WinGet | Manual: `winget upgrade Anthropic.ClaudeCode` |
| npm | Manual: `npm install -g @anthropic-ai/claude-code@latest` |

There are two release channels. **Latest** (the default for the native installer) gets new versions as soon as they ship. **Stable** runs about a week behind and skips releases with major regressions. On Homebrew the channel is the cask name: `claude-code` tracks stable, `claude-code@latest` tracks latest. On the native installer you can switch with `/config` inside a session.

To update right now instead of waiting, run `claude update`.

Honest read: if you're learning, take the native installer and let it update itself. Thinking about update channels before you've run a single session is a good way to never run one.

> **Note:** My own machine works differently, and a failure taught me why. In September two separate setups on it kept reinstalling the CLI on their own schedules, and each reinstall briefly deleted `claude`, which made a live agent turn fail. Now no session updates itself. One pipeline owns the CLI: it follows the stable channel, installs each release next to the old one, runs a contract test suite against it, swaps it in atomically, and rolls back on its own if anything breaks. Major versions wait for my approval. You won't need any of that for a while.

## You haven't signed in yet

Installing the tool and signing in are separate steps. Right now you have the `claude` command, but it doesn't know which account to bill. The choice between a subscription and an API key changes how you pay, so it gets its own page.

**Next:** [Sign in: subscription or API key](/docs/start-here/plans-and-api-keys/)
