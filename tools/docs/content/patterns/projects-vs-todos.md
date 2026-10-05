---
title: "Projects vs. todos"
description: "A project has a goal, an end state and an artifact. Everything else is a todo. The rule that keeps a registry honest."
section: patterns
group: "Running the org"
order: 150
updated: 2026-10-05
sources: ["learn/tier-2/14-projects-vs-domain-todos.mdx"]
---

A project has a goal, an end state, and produces an artifact: code, a deployed app, a published piece, a closed deal. Everything else is a todo. When in doubt, it's a todo. That one rule decides where work lives, and it's what keeps a project registry from filling up with errands.

Get it wrong in one direction and you scaffold a folder, a plan and a changelog for "register the car." Get it wrong in the other and a months-long build lives as a bullet in a task list, with no record of what shipped or why.

## The decision rule

| Ask | Project | Todo |
|---|---|---|
| Is there an end state you could point to? ("deployed", "published") | Yes | No, it's just done or not |
| Does it produce an artifact? | Yes | No |
| Will it take more than one session? | Usually | Usually not |
| Will you want to look back at what shipped, in order? | Yes | No |

If it's a single action ("email the registrar", "renew the domain") or an ongoing chore, it's a todo. Promote a todo to a project when the scope turns real, not when you're speculating that it might.

## What a project gets

Each project gets a folder with four files and a row in a registry:

```text
projects/<slug>/
  README.md       what it is and why it exists
  WORKPLAN.md     milestones, status, what's next, what's blocked
  CHANGELOG.md    what shipped, dated, one line each
  LINKS.md        repos, deploys, docs
registry row      slug, status, domain, owner, links to the four files
```

One command scaffolds the folder and adds the registry row in the same step. That matters more than it sounds: when people (or agents) create the folder by hand, the registry drifts from what's on disk, and then nobody trusts either one.

Status comes from a small fixed vocabulary: idea, planning, active, paused, complete, archived and a couple more. Mark things complete when the artifact shipped and archived when the idea didn't pan out. A registry is only useful if it tells the truth about what's actually alive.

## What a todo gets

One entry in a task list owned by the relevant area of life or work:

```yaml
- id: T-042
  title: "Renew the domain before it lapses"
  status: open
  priority: medium
  project_slug: null     # standalone, not part of a project
```

A todo can optionally attach to a project with `project_slug: <slug>`. That's for small tasks that belong to a project but don't deserve a WORKPLAN milestone of their own. My task lists sync to a database table, so other surfaces can show them without reading the files.

## The logging rule

After shipping anything material on a project, append one line to its changelog:

```bash
bash scripts/clawd-log.sh harnessview "added group collapse to the graph view"
```

That's a small script that appends a timestamped line under today's date in the project's `CHANGELOG.md`. A flag can also tick the matching milestone in the WORKPLAN.

"Material" means anything that changed state: a script written, a bug fixed, a migration run, a decision made. Not pure reading or research. If you wrote code or changed config, log it.

The per-project logs feed a master changelog, regenerated from them every night. Nobody edits the master by hand. If it looks wrong, the fix is to regenerate it, never to patch the file, which means it can't drift from what the projects actually recorded. That master is what I read, and what a fresh session reads, to answer "what did we build?" without trusting anyone's chat memory.

Skip the log and the work is invisible. The next agent to pick up the project has no context, so it either repeats the work or makes a decision that conflicts with what already shipped.

## A worked example: harnessview

[harnessview](https://github.com/jddavenportOpen/harnessview) is a small public tool that visualizes an AI agent harness and its run history. It got a project on June 9, 2026, because it passed every test in the table: a clear artifact (a CLI tool and its repo), an end state, and more than one session of work.

Its WORKPLAN had three milestones. Two shipped: a fix to how the graph laid out a large view, and Playwright tests for four user stories (the graph renders, clicking a node opens the inspector, groups collapse and expand, the live badge shows). The third, publishing to npm, didn't.

Here's why, and it's the useful part. Publishing a public package under my name is outward and irreversible, so it needs my explicit yes and an npm account that only I can set up. In early July a background job kept retrying the publish and paging me with a login link every eight minutes. The fix was to park the milestone with a plain note in the WORKPLAN: needs me, don't retry, don't page, until I say "publish harnessview."

On August 12 an automated pass marked the project complete. The WORKPLAN's own status line still reads two of three milestones done, one parked. Both are true: the code shipped and is public; the package never went to npm. The lesson for your own registry is to decide what "complete" means when a milestone is parked on purpose, and write that down, because otherwise a script will decide for you.

Compare "renew the domain." No folder, no WORKPLAN, no changelog. It needs to get done and get checked off.

## Common mistakes

- **Scaffolding speculation.** A project for an idea you had in the shower. Make it a todo, or an "idea" status row at most.
- **Hiding a real build in a todo.** If you're three sessions in and logging decisions in task comments, it's a project. Promote it.
- **Hand-made folders.** They drift from the registry. Use the scaffold command.
- **A registry nobody prunes.** Mark things complete or archived. An inflated registry creates false confidence about how much is actually running.

**Next:** [Write the rules down, then enforce them](/docs/patterns/governance-charter/)
