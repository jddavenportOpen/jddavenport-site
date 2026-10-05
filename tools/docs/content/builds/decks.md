---
title: "AI decks that don't look like AI"
description: "Eight failed python-pptx attempts, then a design system and a render, read, critique, fix loop. Where deck generation stands now."
section: builds
group: "Research and content"
order: 60
updated: 2026-10-05
sources: ["learn/tier-3/f2-deck-architect-v4.mdx", "building-ai-os/arch-deck-architect.mdx", "articles/why-your-ai-slides-suck.mdx"]
---

AI slides look AI-generated for two reasons, and a better prompt fixes neither. The model is placing boxes by coordinate, and it never sees the result. The fix is a design system it can't wander outside of, plus a loop where it has to look at the rendered slide before it's allowed to call the deck done. It took me from April to June 2026 to learn that, and I blamed the wrong thing for most of it.

## What you'll learn

- Why eight attempts in one evening produced eight bad decks
- What changed when the layout decisions moved out of the model's hands
- The render, read, critique, fix loop, and the bug that quietly broke it
- How my decks get built today, and the rules that make them look intentional

## April: eight attempts, eight rejections

In early April I spent an evening asking an agent to build a professional PowerPoint deck with `python-pptx`, the standard Python library for writing .pptx files. The agent wrote code, the code wrote a deck, I opened it and winced. Eight times.

- Versions 1 to 3: wrong backgrounds, wrong colors, amateur type.
- Version 4: the right background image, still a group project.
- Versions 5 to 7: accent lines under titles, gradients, "professional" layouts. Each one worse.
- Version 8: stripped back to orange and white. My note to myself at the time: worse than what the plain Claude chat app produced.

At the time I decided the library was the problem. `python-pptx` places boxes and sets fonts, but it's a file-format library, not a design tool, and it makes shadows, rounded corners and gradients awkward. I switched to [PptxGenJS](https://github.com/gitbrent/PptxGenJS), a JavaScript library with better primitives, and added a design system: a small set of tested palettes, a library of layout patterns with exact coordinates, typography rules and a list of things never to do.

The output got dramatically better. The deck that came after was accepted on the first try.

## The list of things never to do

This part has outlived every engine change, so it's worth copying as is:

- No accent line under the title. It's the single most recognizable tell of a generated slide.
- No more than six bullets on a slide. Fewer is better.
- Left-align body text. Center only titles.
- No clip art, no stock icons.
- No more than two type sizes per slide.

## June: let the model write content, not layout

The next versions split the job. A planner turns the brief into a structured content plan: one entry per slide with an action title, a narrative type (statement, chart, three columns, quote), the content, and a chart spec. Templates own the layout. The model fills slots; it never writes coordinates.

Then a visual QA loop, up to three rounds:

```text
render the .pptx to images
  -> a vision model reads each slide image
  -> critique: title collisions, overlapping numbers, text overflow, broken charts
  -> fix the source, re-render
```

### The bug that broke the loop

On June 8, 2026 the QA polish pass on a 21-slide deck failed. The cause sat one layer down, in my shared LLM client. Vision calls normally went through a third-party router that speaks the OpenAI message format, where an image is an `image_url` block. That day the router was out of credits, so calls fell back to Anthropic's API directly. Anthropic's API wants a different image block, with a base64 `source` and a media type, and the fallback path never translated one into the other. So whenever the fallback fired, the critic never actually saw the slides.

The fix was one small function that converts OpenAI-style image blocks into Anthropic image blocks on the direct path. It merged the same day, and it fixed QA for every deck after it, because every deck shared that client.

The lesson is broader than slides: a fallback path that nobody exercises is a fallback path that doesn't work. Test the degraded route on purpose.

With the critic able to see again, the next run on the flagship deck caught real breakage: a chart rendered as scattered dots instead of bars, two title collisions, and a number overlapping its label. All fixed before the deck went out. One more catch from that day: the research behind the deck had inflated figures about my own system, so every number was re-checked against the actual files and the research numbers were thrown out. A deck about real work can't carry a number nobody verified.

## How decks get built today

Today the work runs through two designer agents, each paired with a skill: one in my own brand, Warm Graphite (the dark, amber-accented design system this site uses), and one built on an employer's official brand. The employer-branded one came first, on June 10, 2026. The Warm Graphite one followed on June 28, re-themed from it.

And here's the part April me would not have predicted: both are built on `python-pptx` again.

The difference is that the design system is now code. Each skill ships a small builder library of components (title slide, section break, statement, KPI row, card grid, layer stack, timeline, table, screenshot frame, code box, takeaway) plus a branding spec. The agent doesn't place boxes. It picks components.

The process is fixed, and steps four and five are never skipped:

1. **Content first.** Turn the source into a slide plan. Each slide is one assertion (the action title) plus one visual. Lists become card grids, numbers become KPI cards, sequences become timelines, comparisons become bars.
2. **Read the branding spec.**
3. **Write a build script** against the component library, with speaker detail in the notes.
4. **Render.** A short script converts the .pptx to PDF with LibreOffice in headless mode, then splits it into one PNG per slide.
5. **Read every PNG.** The agent looks at each slide image and fixes overflow, collisions, orphan whitespace and uneven cards, then re-renders until it's clean.

```bash
soffice --headless --convert-to pdf deck.pptx --outdir /tmp/render
pdftoppm -png -r 96 /tmp/render/deck.pdf deck_render/slide
```

Claude Code can read images, so step five needs no special vision plumbing: the agent opens the PNG the same way it opens a text file. That's the render, read, critique, fix loop with the bug class from June removed entirely.

### The design rules that do the work

- One saturated color, used sparingly. Everything else stays muted.
- Action titles that carry the argument, so someone skimming titles gets the story.
- Never two consecutive slides built from the same component.
- Three KPI cards beat five. Four cards beat six.
- Cut content before you shrink type, and never go below 10 point.
- Every number on a slide matches a live source, checked before the deck ships.

A 22-slide webinar deck at the end of June went through exactly this loop. The work decks follow the same process.

## What it still can't do

The engine is typographic, not photographic. There's no image generation step, by choice: a model generating images for slides opens the same IP questions my [merch store](/docs/builds/ip-safety-gate/) has a whole gate for. When a slide needs a picture, it uses a real screenshot of the product, which is better evidence anyway.

Honest read: in April I said the library capped quality. The library was maybe a third of it. The rest was letting the model make layout decisions it had no taste for, and never making it look at what it built. Give it components and eyes, and the boring library works fine.

**Next:** [Socrates: the X autopilot](/docs/builds/socrates-x/)
