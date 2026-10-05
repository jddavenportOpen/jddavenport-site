---
title: "Hooks: rules the model cannot forget"
description: "PreToolUse, Stop and the other hook events, why infrastructure beats instructions, and three real hooks worth copying."
section: fundamentals
group: "Extending Claude Code"
order: 80
updated: 2026-10-05
sources: ["learn/tier-1/08-hooks.mdx"]
---

A hook is a command Claude Code runs automatically at a point in a session's life: before a tool call, after one, when the model finishes a turn, when a session starts. It doesn't depend on the model remembering anything. It fires because the event happened. That's why the rules that matter most in my system are hooks, not paragraphs: prose rules don't survive contact with autonomous agents, and machine enforcement does.

## What you'll learn

- The hook events you'll actually use, and which ones can block
- How to wire a hook in settings and write one that denies a command
- Three hooks from my production system and the failures behind them
- The limit nobody mentions: what a hook can't see

## Why instructions aren't enough

A CLAUDE.md rule is text competing with everything else in the context window. In turn one it's fresh. Two hours and a few hundred thousand tokens later, it's one paragraph among thousands, and the model is focused on the task in front of it. It doesn't defy the rule. It just stops weighing it.

For most rules that's fine. For the ones where a single miss is expensive (a destructive command, a message sent to the wrong person, a restart that kills everything), "the model usually remembers" is not good enough. Ask of every important rule: what happens the one time it's skipped? If the answer hurts, it belongs in a hook.

## The events you'll use

Claude Code has a long list of hook events. These are the ones that come up most, checked against the hooks reference in October 2026:

| Event | Fires | Can it block? |
|---|---|---|
| `SessionStart` | When a session starts or resumes | No (it can add context) |
| `UserPromptSubmit` | When you submit a prompt, before Claude sees it | Yes |
| `PreToolUse` | Before a tool call runs | Yes: this is the enforcement hook |
| `PermissionRequest` | When a tool call needs a permission decision | Through its decision output |
| `PostToolUse` | After a tool call succeeds | No (the tool already ran) |
| `Stop` | When Claude finishes responding | Yes: it can make Claude keep going |
| `SubagentStop` | When a subagent finishes | Yes |
| `PreCompact` | Before context compaction | Yes |
| `Notification` | When Claude Code sends a notification | No |
| `SessionEnd` | When a session ends | No |

A handler is usually a shell command, but it can also be an HTTP call, an MCP tool, a prompt to a model, or a small agent. Start with commands.

## Wiring one

Hooks live in the `hooks` key of a settings file. This one runs a script before any `Bash` call whose command starts with `git push`:

```json
{
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

The `matcher` narrows by tool name. The `if` narrows further using permission-rule syntax, so the script only spawns when both match.

The hook receives the tool call as JSON on stdin. To deny, print a decision:

```bash
#!/bin/bash
# .claude/hooks/no-force-push.sh
cmd=$(jq -r '.tool_input.command')
if echo "$cmd" | grep -qE 'git push.*(--force|-f( |$))'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Force push is blocked. Ask the human to do it."
    }
  }'
fi
exit 0
```

Make it executable (`chmod +x`), install `jq`, and run `/hooks` in a session to confirm it's registered. The other way to block is exit code 2: on events that can block, exit 2 blocks the action and shows your stderr to Claude, so write a reason it can act on.

> **Tip:** Hooks run as real processes with your permissions, and a slow one stalls the session. Keep them fast, test them on their own with a sample JSON payload, and log what they decide so you can audit them later.

## Three hooks from my system

### 1. Voice replies that never get forgotten (Stop)

My main agent talks to me over Telegram. When it sends a long summary, it should also send a spoken version I can listen to on my phone. That rule lived in CLAUDE.md and the agent followed it for a few turns. Then sessions got long, and voice replies started going missing.

So I stopped rewording the paragraph and wrote a `Stop` hook. After every turn it reads the session transcript, finds the last message sent to me, and checks whether it's summary-class: 300 characters or more, or it contains a heading, or it contains a list. If voice mode is on and the reply doesn't carry an explicit opt-out token, the hook generates the audio with a local text-to-speech model and sends it. Short acknowledgements stay text. Long replies go through a small, cheap model first, so the spoken version keeps the numbers and decisions instead of just the first and last paragraphs.

Since May 2026 the model doesn't have to remember to do this at all. The CLAUDE.md entry now just explains the behavior and tells the agent not to send voice itself, because the hook already will.

### 2. The restart guard (PreToolUse)

Every agent session in my system runs as a child of one supervising service. On July 1, 2026, a single raw restart of that service killed every live session at once: 12 of them, mid-work.

A rule saying "don't do that" already existed. What exists now is a `PreToolUse` hook that blocks raw restart commands for that service and points the agent to a reload script. The reload script refuses to run while live sessions exist and prints the list of sessions it would kill if forced. A separate detector watches for clusters of session deaths and names the session and command responsible.

The hook has grown since. It now guards several commands that must go through a wrapper instead of being typed raw, like deploying the cockpit to production and re-enabling a scheduled job I deliberately turned off. That last one fails closed: if the hook can't check, the command doesn't run.

### 3. The GitHub governor (PreToolUse)

I want agents shipping fixes without me. I don't want them doing anything on someone else's GitHub repo that I'd be embarrassed by.

So pushes and PRs to my own repos go straight through. Anything touching a repo I don't own (a fork, a PR, a Discussion) goes to a governor that judges reputation risk. A genuine, on-topic, single bug-fix PR to a project I use passes. Self-promotion, star-farming, adding my project to someone's awesome list, and templated or mass outreach get denied. If the judge fails or times out, the answer is deny. And my explicit approval overrides it, so I'm never stuck arguing with my own guard.

The governor only ever denies or steps aside, and every decision goes to a log.

## The limit: a hook only sees the tool layer

This is the part that most hook tutorials skip, and it's the most important.

A `PreToolUse` hook sees tool calls. It sees `Bash(python send_report.py)`. It doesn't see what that Python script does once it's running. If the script sends an email, the hook has no idea.

I found this out with my own policy hook, a `PreToolUse` gate meant to block irreversible or outward-facing actions. An audit in early September 2026 found it had logged tens of thousands of allow decisions and zero blocks. It wasn't broken. Real sends in my system happen inside Python code, out of its sight, so it was guarding a door nobody used.

What actually enforces is a gate in the code itself: one send chokepoint that every outbound message must pass through, with single-use approvals bound to the exact message, and a CI check that fails the build if any code path sends around it. That chokepoint has recorded hundreds of denials. It's covered in [the send gate](/docs/safety-and-operations/the-send-gate/).

Honest read: hooks are the right tool for anything the agent does directly through its tools. For anything your own code does, put the gate in the code. Use both, and know which one is doing the work.

> **Note:** A related limit applies to permission rules. A rule like `Bash(rm *)` matches the command text, so `/bin/rm` or `bash -c 'rm ...'` can slip past it. A hook that parses the command more carefully, or a sandbox, closes more of that gap. Neither replaces a gate in code.

**Next:** [settings.json and permissions config](/docs/fundamentals/settings-and-permissions/)
