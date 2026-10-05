---
title: "MCP: giving the agent new senses"
description: "What the Model Context Protocol is, how to add a server, and how to choose between an MCP server, a CLI and a skill."
section: fundamentals
group: "Extending Claude Code"
order: 60
updated: 2026-10-05
sources: ["learn/tier-1/06-mcp-basics.mdx", "building-ai-os/arch-mcp-servers.mdx"]
---

The built-in tools work on your files and your terminal. They can't query your database, read a calendar or open a pull request on their own. MCP, the Model Context Protocol, is how you give the agent those senses without writing a custom tool into the harness. You run a small server that declares some tools, Claude Code connects to it, and the agent calls those tools like any other.

## What you'll learn

- What an MCP server is, in one paragraph
- How to add one with `claude mcp add`, and which scope to pick
- How to keep secrets out of a shared config
- The kinds of servers I actually run, and the one I mostly stopped using
- When an MCP server is the wrong answer and a CLI or a skill is better

## What MCP is

MCP is an open protocol, published by Anthropic, for connecting agents to tools and data. An MCP server is a process (local, or remote over HTTP) that says "here are my tools, here are their inputs." The agent calls a tool by name, the server does the work, and the result comes back into the conversation.

From the agent's side, an MCP tool looks like a built-in one. It just has a longer name: `mcp__<server>__<tool>`, like `mcp__github__list_prs`. That name is also what you use in permission rules and hook matchers.

## Adding a server

Use the CLI. A remote server over HTTP:

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

A local server that runs as a process (stdio). Everything after `--` is the command that starts the server:

```bash
claude mcp add --transport stdio --env API_KEY=your-key example -- npx -y @example/mcp-server
```

Then check it:

```bash
claude mcp list          # every configured server and its status
claude mcp get example   # one server's details
```

Inside a session, `/mcp` shows connection status and handles OAuth sign-in for servers that need it.

## Pick a scope

Where the config is stored decides who gets the server:

| Scope | Flag | Loads in | Shared? | Stored in |
|---|---|---|---|---|
| Local (default) | `--scope local` | This project only | No, just you | Your user config file |
| Project | `--scope project` | This project | Yes, via git | `.mcp.json` at the repo root |
| User | `--scope user` | All your projects | No, just you | Your user config file |

In an interactive session, a project-scoped server from a cloned repo waits until you approve it, so a commit alone can't start a server on your machine. Headless runs are different: `claude -p` shows no trust dialog and no approval prompt, and the docs say it connects a repo's `.mcp.json` servers (and runs its project hooks) even in a folder you've never trusted. Read a repo's `.claude/` folder and `.mcp.json` before you point a headless run at it.

## Keep secrets out of `.mcp.json`

`.mcp.json` is meant to be committed. Your API keys are not. Claude Code expands environment variables in it, so the shared file names the variable and each person's environment holds the value:

```json
{
  "mcpServers": {
    "tickets": {
      "command": "npx",
      "args": ["-y", "@example/tickets-mcp"],
      "env": {
        "TICKETS_API_KEY": "${TICKETS_API_KEY}",
        "TICKETS_URL": "${TICKETS_URL:-https://tickets.example.com}"
      }
    }
  }
}
```

> **Warning:** An MCP server runs with whatever credentials you hand it. A server holding a database key with write access can write to your whole database. Scope every credential to what the server actually needs, the same way you'd scope a key you gave a contractor.

## Context cost is lower than it used to be

Older versions loaded every connected server's full tool definitions into the context window at startup, so ten servers meant a noticeably heavier session before you typed anything. Current Claude Code defers MCP tool definitions by default: only the names and server instructions load, and a tool's full definition loads when the agent goes to use it. `/context` shows what's actually loaded.

That doesn't make servers free. Each one is a live process with its own auth and network dependencies. When one is down, its tools fail, and the agent may quietly work around the gap.

## What I run, by kind

I'm not going to give you an inventory with a count. The count changes every few weeks, and the old inventory on this site went stale fast. What's stable is the kinds:

- **Memory.** My own memory layer (a knowledge graph plus a vector store) exposed as search and recall tools, so any session can ask "what do we know about X" instead of re-reading files.
- **The school LMS.** Read-only: courses, assignments, due dates, announcements.
- **A browser.** Playwright, for pages that need clicking rather than fetching.
- **The database.** Query and inspect the Postgres tables where durable state lives.
- **GitHub.** Repos, PRs, issues, code search.
- **A notes vault and web search.** Reading my notes; searching the web.
- **A code-intelligence graph.** Indexes a codebase into a graph of functions, calls and modules.

That last one gets its own section.

## The code graph cost more than grep

A code graph sounds like an obvious upgrade over text search: ask "who calls this function" and get a precise answer instead of grep noise. On my repos, measured, it cost more than plain search and reading, and it was never more complete. Grep found everything the graph found.

So the rule now is narrow: use it for what grep can't do, like tracing a call path across modules, getting an architecture overview, or cross-repo edges. Verify any caller list it gives you with a plain search. Don't reach for it by default. Honest read: a fancier tool is only better if you measured it on your own work.

## Credentials expire quietly

MCP servers rarely crash. They go quiet when a credential expires.

My school's LMS caps API tokens at 90 days. In June 2026 one expired and nothing told me. For 12 weeks the agents that depended on it were working blind on coursework, and nothing in the system treated that as an outage. Now a weekly job renews the token and a health check pages me if renewal stops.

Two lessons. Know the expiry of every credential a server holds. And make an empty result look different from a failed one, because an agent will treat "the server returned nothing" as "there is nothing."

## MCP server, CLI or skill?

Not everything should be a server.

| Use | When | Example |
|---|---|---|
| An existing CLI | A good command-line tool already exists and the agent can run it with `Bash` | `gh` for GitHub, `psql` for Postgres |
| A skill | The agent already has the tools; it needs know-how, a procedure or a checklist | "How we cut a release," "how to triage an issue" |
| An MCP server | You need structured tools with typed inputs, a stateful or authenticated connection, or the same capability across several agents and apps | Memory search, a third-party API with OAuth |

My Google services are a real example of the first row. I use a command-line client for mail, calendar and docs instead of the MCP servers, because the MCP servers' OAuth kept breaking and the CLI was easier to keep alive. Boring and working beats elegant and flaky.

## Shipping your own server

If you build one, ship it with a way to prove it works. My public example is [mcp-judge](https://github.com/jddavenportOpen/mcp-judge): a calibrated, multi-persona LLM-as-judge that scores any document against any rubric, exposed as an MCP server so any agent can call it, with an eval harness that measures whether the calibration actually holds. The server is the easy part. The harness is the part that makes it trustworthy.

**Next:** [Skills: packaged know-how the agent loads on demand](/docs/fundamentals/skills/)
