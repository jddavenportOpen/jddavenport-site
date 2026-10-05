---
title: "harnessview: see your harness"
description: "Scan a project's Claude Code setup (agents, skills, hooks, MCP, settings) and see it as one live graph that flags broken wiring."
section: builds
group: "Open source"
order: 160
updated: 2026-10-05
sources: ["learn/tier-3/a4-harnessview.mdx"]
---

After a few months of building on Claude Code, you can read every config file and still not know what's actually wired. Which sub-agents can call which MCP servers. Which hooks fire on which tools. Whether the command a hook points at still exists. harnessview answers that with a picture: point it at a project and it opens a local graph of the whole harness, with the broken parts drawn in red.

It's public at [jddavenportOpen/harnessview](https://github.com/jddavenportOpen/harnessview), MIT licensed. No account, no config, no cloud. It reads your files off disk and nothing leaves your machine.

New to the word "harness"? It's everything around the model that lets it act: tools, settings, hooks, skills. [What Claude Code is, and what a harness is](/docs/start-here/what-is-claude-code/) covers it.

## What it shows

harnessview walks the Claude Code settings hierarchy at the target path (enterprise, then user, then project, then local overrides) and composes one graph:

| Node | Where it comes from |
|---|---|
| Project | The root, its `CLAUDE.md`, and the merged model and settings |
| Sub-agent | `.claude/agents/*.md`, including the model and tools in each file's front matter |
| MCP server | `.mcp.json` and the `mcpServers` block in settings |
| Skill | `.claude/skills/*.md` and `.claude/skills/*/SKILL.md` |
| Command | `.claude/commands/**/*.md`, namespaced by folder |
| Hook | The `hooks` block in settings, per event and matcher |
| Plugin | Installed plugin marketplaces |

Edges show the wiring: which sub-agents are granted which MCP servers (through their `mcp__server__*` tool grants), and which plugin owns which component.

Two features carry most of the value:

- **Broken-config detection.** A hook or a local MCP server whose command path doesn't exist on disk renders as an error node. You can read a settings file ten times and miss a path that moved in an upgrade. A red box you notice.
- **Live updates.** The local server watches your config files and pushes changes to the page. Edit a settings file or drop in a new agent and the graph redraws without a refresh.

It's read-only. It doesn't run your agents, call a model, or touch a database. Think `tree` for a Claude Code project, except it knows that this file is a hook and that one is an MCP server, and it checks whether they connect.

## Install and run

harnessview isn't on npm. Publishing stalled in July 2026 on creating the npm account, which is a human step I never got to. So the `npx` line in the README won't work yet. Run it from a clone. You need Node 18 or newer.

```bash
git clone https://github.com/jddavenportOpen/harnessview
cd harnessview
npm install
npm run build
node bin/harnessview.mjs /path/to/your/project
```

It starts a small local server and opens your browser. Options:

```bash
node bin/harnessview.mjs .                 # scan the current directory
node bin/harnessview.mjs ../other-project  # scan another project
node bin/harnessview.mjs . --port 8080     # pick a port
node bin/harnessview.mjs . --no-open       # don't open the browser
npm run scan                               # dump the scanned graph as JSON
```

> **Tip:** Run it against your home directory's Claude Code config too. User-level hooks and MCP servers apply to every project, and they're the ones people forget exist.

## How it's built

The interesting decision is the contract between the scanner and the canvas.

- **Adapters scan.** The Claude Code scanner is the default adapter. Each adapter has a `detect()` and a priority, and the tool picks the best match for the folder. Another agent framework needs only a new adapter. The canvas doesn't change.
- **Node kinds are free strings, and styles ship in the payload.** The graph an adapter returns says what each kind looks like. The renderer adapts to whatever an adapter emits, so adding a kind of node never touches the UI code.
- **A tiny Node server** serves the graph, a server-sent events stream for live reload, and the static page.
- **The canvas** is React Flow with elkjs for layered auto-layout: click a node to inspect it, collapse groups you don't care about.

## Where it came from

I built it in one morning on June 9, 2026. It's a generalization of the org chart in my cockpit, which draws my own agents from a backend database and a registry. That version only works for my system. harnessview kept the canvas, threw away the database and the cockpit framework, and put an adapter contract in between, so it runs against any Claude Code project.

Before it went public, the tracked files got a secret and personal-data scan. That was easy here, because the scanner discovers every path at runtime from the target project. Nothing about my machine is baked in.

Two later fixes are worth knowing about if you fork it. The first layout drew every leaf in one enormously wide row, because a root with dozens of direct children is a star, and a layered layout has nothing to layer. Adding a hub node per category gave it a real three-level tree. Then in July it got Playwright smoke tests for four user stories: the graph renders, clicking a node opens the inspector, groups collapse and expand, and the live badge shows.

Honest read: this is a small tool, and that's the point. A harness grows one config file at a time and nobody draws the diagram. If you're running more than a handful of hooks and MCP servers, look at the picture once a month. You'll find something dead.

**Next:** [Clawdling: the open engine](/docs/builds/clawdling/)
