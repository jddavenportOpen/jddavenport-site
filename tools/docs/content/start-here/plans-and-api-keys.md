---
title: "Sign in: subscription or API key"
description: "Pro, Max, Team or a Console API key: which to pick, how billing differs, and the stray-key mistake that quietly costs money."
section: start-here
order: 30
updated: 2026-10-05
sources: ["learn/tier-0/03-authenticate.mdx"]
---

Claude Code needs to know whose account pays for the work. You have two real choices: a Claude subscription with a flat monthly price, or a Console API key billed per use. Pick on purpose. The wrong one shows up later as either a usage wall in the middle of a task or a bill you didn't watch grow.

## The two options

| | Claude subscription | Console API key |
|---|---|---|
| What it is | The same plan you use for the Claude app (Pro, Max, Team, Enterprise) | Prepaid credits on the Claude Console, billed per token |
| How you pay | Fixed price per month or per seat | Per use. Every task costs something. |
| Limits | Usage limits that reset on a schedule | You keep going while credit lasts |
| Best for | Daily hands-on work, learning | Scripts, CI, and workloads you meter yourself |

Prices on [claude.com/pricing](https://claude.com/pricing) as of October 5, 2026: Pro is $20 a month ($17 a month billed annually), Max starts at $100 a month with a 5x or 20x usage tier, and a Team standard seat is $25 a month ($20 billed annually). All three include Claude Code. The free plan doesn't. Prices change, so check the page before you buy.

Honest read: if you're learning, start on Pro. It's the cheapest way in and the usage limits rarely bite on the kind of work in these docs. Move to Max when you notice you're waiting on resets. I run on Max plans because I have many sessions going all day.

## First sign-in

Start a session:

```bash
claude
```

On first launch Claude Code opens a browser window. Sign in with your Claude account, approve it, and the terminal shows `Login successful`. If the browser can't hand back to the terminal (common over SSH or in WSL2), it shows a code instead. Paste that code into the terminal prompt.

Your credentials are stored locally (in the macOS Keychain on a Mac), so you sign in once. To switch accounts later, type `/login` inside a session. To sign out, type `/logout`.

## Using an API key instead

An API key comes from the [Claude Console](https://platform.claude.com/). You'd choose it when you want to pay exactly for what you use, or when a script needs to run Claude Code without a browser.

The simplest way: choose the Console option at the `/login` prompt and sign in there. Claude Code can do that without you ever copying a key. The other way is to set the key in your shell as `ANTHROPIC_API_KEY` before you start `claude`. When it sees that variable, Claude Code skips the browser login and asks you once whether to use the key.

Treat a key like a card number. Never paste it into a chat, never commit it to a repo, and set a spend limit on your workspace in the Console so a runaway loop has a ceiling.

> **Warning:** A key that bills per use has no natural stopping point. An agent stuck in a loop at 2 AM keeps going until something stops it. Put the ceiling in place before you need it.

## The stray-key mistake

This one catches people who have both a subscription and a key.

When more than one credential is present, Claude Code picks by a fixed precedence, and an `ANTHROPIC_API_KEY` in your environment sits above your subscription login. In an interactive session you approve the key once and the choice is remembered. In non-interactive mode (`claude -p`, used by scripts), the key is always used when it's present.

So here's how it goes wrong. You set a key months ago for some experiment. It's still exported in your shell profile. You think you're on your flat-rate plan. Your scripts are quietly billing the key instead.

The check takes five seconds. Inside a session, run:

```text
/status
```

It shows which account and login method are active, and when both a login and a key are configured it marks the one that isn't in use. If you meant to use your subscription, remove the key:

```bash
unset ANTHROPIC_API_KEY
```

Then delete the `export` line from your shell profile so it doesn't come back next time. In my own system, the scripts that launch headless workers unset the key before they start Claude Code, so every background agent runs on the plan it's supposed to. "I thought I was on the plan" is not a fun thing to discover from an invoice.

## A note on the numbers I publish

Elsewhere in these docs and on my site you'll see token figures from my system. Those are work volume, list-price equivalent: what the tokens would cost at published API rates. They are not my bill and they are not plan consumption. Those are three different measurements, and I've watched people (and agents) mix them up and reach the wrong conclusion.

## Confirm you're in

Run `claude`. If it drops you at a prompt without asking you to sign in, you're authenticated. Type `/help` to see what's available, and `/exit` to leave.

**Next:** [Your first session](/docs/start-here/your-first-session/)
