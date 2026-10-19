---
title: "Building and judgment: what Anthropic's hiring data means for MBAs"
description: "Anthropic studied its own hiring. Execution fell and judgment rose. What building and judgment are, what they are not, plus prompts and drills."
section: ai-core-skills
group: "#3 Building and judgment"
order: 10
updated: 2026-10-19
sources: ["anthropic-employment-2026-10-16"]
---

Part of my AI Core Skills series. #1 was [agent evals](/docs/ai-core-skills/agent-evals/) and #2 was [agent tracing](/docs/ai-core-skills/agent-tracing/). This one is less technical and more about careers, and it leans on both. If you want these in your inbox, [join the newsletter](https://jddavenport.com/newsletter).

*By JD Davenport. I'm an MBA student at BYU and the founder of AI Foundry, where MBAs build AI systems for real clients.*

Everyone talks about AI replacing junior engineers. Anthropic just published data on its own workforce, and the bigger story for MBAs is what happened to everyone else. This guide covers what the report says, how much weight to put on it, the two skills it points to (building and judgment), what those skills are and are not, and prompts and drills you can start this week.

---

## 1. What Anthropic published

On October 16, 2026, Anthropic published [How Employment is Changing at Anthropic](https://www.anthropic.com/research/employment-at-anthropic) by Nathan Wilmers, Regina Catipon, Maxim Massenkoff and Peter McCrory. It draws on internal data (employment, AI use, output, surveys, Slack, calendars and hiring scorecards) plus 17 employee interviews.

The numbers that matter if you are early in a business career:

| Finding | Number |
|---|---|
| Junior share of employees in technical departments | 21% to 14% since early 2025 |
| Junior share of technical *hires* | 27% to 9% |
| Technical departments' share of all employees | 61% to 56% in a year |
| Who grew faster | Sales, finance and recruiting hiring outpaced technical hiring |
| Coding-focused agent sessions by non-technical employees | 2 a month (Aug 2025) to 90 a month (May 2026) |
| AI agent hours vs employee hours | 6 to 1 by August 2026 |
| Time a non-technical employee would need to read all their agents' output | Half their work week |
| AI tooling track record noted in non-technical hiring assessments | About 7% in 2024, four times that by 2026 |
| Median employee's time in meetings | Up 20% in a year |

Two quotes from the interviews:

- A sales rep on building a custom dashboard and pipeline: *"a build like this was out of my wheelhouse, especially with the UI, connecting all the tools, the MCPs. But I built this probably in three to four hours, just iterating on it."*
- A non-technical employee on what is left once the routine work is automated: *"that 20% that was strategic becomes 90% of the job."*

And the hiring shift, in the report's words: for non-technical candidates, "customer and mission orientation increased, while discussion of execution skills fell." For technical candidates, the biggest increases were in comments on "autonomy and judgment," while discussion of domain expertise shrank.

The report also names what did not change: "for many non-technical roles, core implementation work is also interpersonal: a sales call, an interview, cross-functional alignment on a complex problem. All of this remains human."

### How much weight to put on it

Read it closely, but read it for what it is.

- **One company, studying itself, at the frontier.** Anthropic adopts AI faster than almost anyone. The authors call it a possible "leading indicator," not a forecast for every employer.
- **The scorecard numbers measure what interviewers wrote about.** An automated coder sorted the comments. "Execution fell" means interviewers wrote about it less. It does not mean they stopped expecting it. Execution is now assumed, and the agent does more of it.
- **Some of the business hiring is just a company scaling sales.** The report says so. Part of the shift may come from coding tools letting non-technical people build software. It does not claim all of it does.
- **Not every non-technical function grew.** Administrative roles that usually scale with headcount did not speed up.

My read: the direction is clear even if the size will differ at your company. Routine execution is moving to agents, and the people who get hired are the ones who decide what the agents should do and whether the output is any good.

---

## 2. The skills, defined: what they are and what they are not

The report points at four things. Two matter most: **building** is becoming the baseline and **judgment** is what separates people. The other two show up in how judgment gets assessed.

### AI building

**What it is:** using a coding agent (Claude Code or something like it) to make a working tool for your own job, such as a dashboard, an agent, an automation or an analysis. You iterate until it does the job, and you own it afterward. The sales rep's dashboard is the model: no engineering ticket, three to four hours, used for real work.

**What it is not:**

- **Not learning to code from scratch.** You need to be able to describe what you want, read what came back, and notice when it is wrong. You do not need a CS degree.
- **Not asking a chatbot for a summary.** That is using AI. Building leaves something running that you did not have yesterday.
- **Not a certificate.** A course badge is not a track record. Hiring managers noted candidates' *track record* with AI tools.
- **Not a demo you never open again.** The test is whether you use it next week.
- **Not writing a spec for engineering and waiting.** If you can't build your own dashboard or agent, you're waiting on someone who can.

| Building | Not building |
|---|---|
| A pipeline dashboard that pulls from your CRM and refreshes daily | A screenshot of a dashboard ChatGPT described |
| An agent that drafts your weekly report from your notes, which you edit and send | Pasting notes into a chat window every Friday |
| A script that cleans the export you used to fix by hand every week | Watching a tutorial on Python for analysts |
| A tool your teammates start using | A side project nobody opens |

### Judgment

**What it is:** deciding what is worth building, what "good" looks like before the agent starts, what to check in what comes back, and what to ship. Agents can produce more than you can read (half a work week, for non-technical staff at Anthropic), so judgment also means choosing where your attention goes.

**What it is not:**

- **Not having opinions.** Judgment shows up as a call you made, the reason for it, and what you checked. If you cannot say what would change your mind, it is a preference.
- **Not seniority.** A first-year associate can show it. Plenty of senior people do not.
- **Not rejecting AI output on reflex, and not accepting it on reflex.** Both skip the step where you look.
- **Not domain trivia.** The report says discussion of domain expertise shrank in technical scorecards. One manager wanted people who are "fungible across domains." Knowing the industry still helps. Memorizing it is not the edge.

| Judgment | Not judgment |
|---|---|
| "I cut 9 of the 14 slides. The decision only needs these 3 claims." | Shipping all 14 because the agent made them |
| "The model says 18% growth. Two assumptions drive it, and one comes from a 2021 report, so I checked it." | Presenting the agent's number because it ran without errors |
| "We can build this, but the customer asked for something else. Here is what they asked for." | Building what is easy to build |
| Writing the eval before the agent starts ([#1](/docs/ai-core-skills/agent-evals/)) | Deciding what "good" means after you see the output |

### The two the report names alongside them

**Creative AI use.** Hiring managers noted a track record with AI tools in about 7% of non-technical assessments in 2024 and four times that in 2026. What it is: "I built X, it replaced Y hours of Z, here is what broke and how I fixed it." What it is not: "Proficient in ChatGPT" in a skills section.

**Customer and mission orientation.** What it is: knowing who the work is for and spending the time AI frees up on them. One account executive said automations let them talk to 30% more customers. What it is not: a sentence about passion in a cover letter.

---

## 3. Where first-year MBA work went

Most first-year MBA work was execution: build the deck, run the model, execute a workstream someone else defined. That is the part interviewers now write about less. Here is how each task splits between the agent and you.

| The old task | What an agent can do now | What you still own |
|---|---|---|
| Build the deck | Draft slides, pull numbers, format | The 3 claims the deck has to land, every number checked, what to cut |
| Run the model | Build the spreadsheet, run scenarios | Which assumptions drive the answer, which scenario you believe, what you would bet |
| Execute a defined workstream | Do the tasks, log progress, draft updates | Scoping it, deciding when it is done, saying what changed |
| Market research | Collect sources, summarize | Which sources to trust, what customers actually said |
| CRM logging and follow-up emails | Draft and log | The conversation itself, and more of them |

The entry-level job is not gone. It moved upstream, to the right-hand column.

---

## 4. Prompts you can use

These are written for Claude Code, but any coding agent works. Replace the bracketed parts.

**1. Build a tool for your own job**

```text
I'm a [role] and every week I [manual task, e.g. pull deals from a CRM export
into a spreadsheet and color-code stalled ones]. Build me a small local tool
that does this. Before you write code, ask me up to 5 questions about my
inputs, what I need to see, and what "done" looks like. Then build the
simplest version that works, show me how to run it, and tell me what it does
NOT handle yet.
```

**2. Scope before you build**

```text
I want to build [tool or analysis]. Don't build anything yet. Interview me
one question at a time to write a one-page spec: who uses it, what decision
it supports, what inputs it gets, what a good output looks like, and 5 test
cases with the answer I'd expect. Push back if I'm describing a solution
before I've described the problem.
```

**3. Check the agent's work**

```text
Here is an analysis an agent produced: [paste or attach]. Act as a skeptical
reviewer. List every number that came from an assumption rather than data,
every claim without a source, and the 3 places this is most likely wrong.
For each, tell me how I would check it myself in under 10 minutes.
```

**4. Protect your attention**

```text
Here is everything my agents produced this week: [paste or attach]. Give me
one screen: the 3 things that need a decision from me, anything that looks
wrong or surprising, and everything else in one line. Do not summarize
things that went as expected.
```

**5. Turn your work into an interview story**

```text
Here are my notes on something I built with AI: [notes]. Help me write a
90-second interview answer: the problem, why it mattered to the customer or
team, what I built and how long it took, a call I made that the agent
couldn't, what broke, and the result in numbers. Ask me for anything
missing. Do not invent results.
```

---

## 5. Training: six drills

Do one a week. The only way to get good at this is time under tension.

**Drill 1: One tool, one evening.** Pick the most annoying recurring task in your week. Use prompt 1 and give yourself 3 hours, about what the Anthropic sales rep needed. *Done when* you use the tool the next time the task comes up.

**Drill 2: Write the spec first.** Before your next build or analysis, use prompt 2 to write a one-page spec with 5 test cases. This is the evals habit from [#1](/docs/ai-core-skills/agent-evals/) applied to your own work. *Done when* you can say whether the output passed without asking anyone.

**Drill 3: Catch the agent.** Take one agent-produced analysis and run prompt 3, then check the top 3 issues yourself. Keep a running log of what your agent gets wrong. *Done when* the log has 10 entries and you can name its two most common mistakes.

**Drill 4: The cut list.** For your next deck or memo, write down what you left out and why, in one line each. *Done when* someone senior reads the cut list and agrees with most of it, or tells you which cut was wrong.

**Drill 5: Spend the time on customers.** Take the hours drills 1 to 3 save and book one more customer, user or stakeholder conversation a week. Write down one thing you learned that no agent could have told you. *Done when* you have 4 of these.

**Drill 6: The story.** Use prompt 5 on your best build. Practice it out loud until it takes 90 seconds. *Done when* you can answer "tell me about a creative way you've used AI" without notes.

---

## 6. How to check you have it

You have the building skill if:

- [ ] You have built at least one tool you still use, without an engineer's help
- [ ] You can explain what it does not handle
- [ ] You can rebuild or change it in an evening

You have the judgment skill if:

- [ ] You write what "good" looks like before the agent starts
- [ ] You can name the assumptions behind any number you present
- [ ] You have a log of what your agent gets wrong
- [ ] You cut things, and can say why
- [ ] You spend some of the time AI saves you with customers or users

---

## 7. How to show it in recruiting

Interviewers noted a track record, so give them one.

**Resume bullets**

| Weak | Strong |
|---|---|
| Proficient in ChatGPT, Claude and AI tools | Built a pipeline dashboard with Claude Code that replaced a 3-hour weekly CRM export; adopted by 4 teammates |
| Used AI to improve team efficiency | Automated client follow-up drafts and logging; spent the saved time on 30% more client calls |
| Passionate about AI | Wrote the evaluation criteria for a client's support agent and caught 2 failure modes before launch |

These are examples of the shape. Use your own numbers, and only numbers you can defend.

**In the interview:** the strongest answers have a call you made that the agent could not make. "The agent built it in an afternoon. The hard part was deciding it should flag stalled deals instead of ranking all of them, because my manager only had time to look at five."

---

## 8. Where AI Foundry fits

This is why we built the [AI Foundry](https://aifoundry.byu.edu) at BYU. Our MBAs work on real systems for real clients: they scope the problem, build the agents, and own what ships. That is the right-hand column of the table in section 3, practiced on work that matters to someone.

You do not need a program to start, though. Drill 1 takes one evening.

---

## Sources

- Wilmers, Catipon, Massenkoff and McCrory, [How Employment is Changing at Anthropic](https://www.anthropic.com/research/employment-at-anthropic), Anthropic, October 16, 2026 ([PDF](https://www-cdn.anthropic.com/72628f1863c53432195db83279252dfd2cb53158/Employment%20at%20Anthropic.pdf)). All numbers and quotes above come from this report.
- The mapping of first-year MBA tasks (section 3), the definitions, prompts, drills and resume examples are mine, not Anthropic's.
