#!/usr/bin/env python3
"""Build /projects (projects.html + projects.json) from tools/projects/curated.json.

Stdlib only, deterministic, re-runnable:

    python3 tools/projects/build_projects.py

Since 2026-11-22 /projects is a short, curated page: about 15 items in a few groups,
each with one plain line, who built it, and a working link. curated.json is the one
source. It replaced a 78-item searchable library whose catalog carried counts and
claims the public fact sheet does not
support. Every number in curated.json must have a row in that fact sheet.

Rendered server-side, no script. Shared chrome (head, nav, footer) comes from
tools/work/build_work.py.
"""
import html
import json
import os
import re
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "work"))
import build_work as bw  # noqa: E402  shared CSS, fonts, nav and footer

CURATED = os.path.join(HERE, "curated.json")
IMG_DIR = os.path.join(ROOT, "images", "projects")
SITE = bw.SITE
MAX_ITEMS = 16  # JD 2026-11-22: "cut /projects to about 15"

# JD 2026-11-10: client projects are paid consulting work. Never name a family member,
# never split credit on them. test_build_projects.py checks the output for this too.
FAMILY_RE = re.compile(r"\b(dad|dad's|father|john davenport|john-davenport)\b", re.I)
DASH_RE = re.compile("[–—]")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
# The only agent count allowed in static copy is "100+ agents built" (fact sheet, ruling 3).
COUNT_RE = re.compile(r"\b(?:30\+|50\+|54|55|66|120\+)\s*(?:[a-z-]+\s+)?agents?\b", re.I)


def esc(s):
    return html.escape(s or "", quote=True)


def host(url):
    return urlparse(url).netloc.replace("www.", "")


def ext_attrs(url):
    return "" if url.startswith(SITE + "/") else ' rel="noopener"'


def local(url):
    """Same-site links render relative, so a local preview stays on the local copy."""
    return url[len(SITE):] if url.startswith(SITE + "/") else url


def load():
    with open(CURATED, encoding="utf-8") as f:
        data = json.load(f)
    blob = json.dumps(data, ensure_ascii=False)
    bad = sorted(set(DASH_RE.findall(blob) + EMOJI_RE.findall(blob)))
    assert not bad, f"forbidden characters in public copy (dashes or emoji): {bad}"
    assert not FAMILY_RE.search(blob), "family reference in public copy"
    hit = COUNT_RE.search(blob)
    assert not hit, f"agent count outside the fact sheet: {hit.group(0)!r}"
    seen = set()
    for g in data["groups"]:
        for i in g["items"]:
            assert i["slug"] not in seen, f"duplicate slug {i['slug']}"
            seen.add(i["slug"])
            assert i["links"], f"{i['slug']}: every card needs at least one public link"
            for l in i["links"]:
                assert l["url"].startswith("https://"), f"{i['slug']}: non-https link {l['url']}"
                assert not re.search(r"github\.com/jddavenport(?!open)", l["url"], re.I), \
                    f"{i['slug']}: github.com/JDDavenport is not public"
            if i.get("thumb"):
                p = os.path.join(IMG_DIR, i["thumb"] + "-thumb.webp")
                assert os.path.exists(p), p
    assert len(seen) <= MAX_ITEMS, f"{len(seen)} items; /projects is capped at about 15"
    return data


def card(i):
    first = i["links"][0]["url"]
    if i.get("thumb"):
        face = (f'<a class="thumb" href="{esc(local(first))}"{ext_attrs(first)} tabindex="-1" aria-hidden="true">'
                f'<img src="/images/projects/{i["thumb"]}-thumb.webp" alt="" width="720" height="450" '
                f'loading="lazy" decoding="async"></a>')
    else:
        face = ""  # no screenshot: a text-only card reads cleaner than a tile that repeats the title
    links = "".join(
        f'<li><a class="tap" href="{esc(local(l["url"]))}"{ext_attrs(l["url"])}>{esc(l["label"])}'
        f'<span class="sr">: {esc(i["title"])} ({esc(host(l["url"]))})</span>'
        f'<span class="arr" aria-hidden="true">→</span></a></li>' for l in i["links"])
    return f"""      <li class="card" id="p-{i['slug']}">
        {face}<div class="in">
          <p class="kind">{esc(i['kind'])}</p>
          <h3>{esc(i['title'])}</h3>
          <p class="d">{esc(i['line'])}</p>
          <ul class="go">{links}</ul>
        </div>
      </li>"""


PAGE_CSS = r"""
.hero{padding-top:28px;padding-bottom:8px}
@media (min-width:720px){.hero{padding-top:56px}}
.hero .lede{font:400 clamp(1.125rem,1rem + .55vw,1.45rem)/1.42 var(--f-serif);color:var(--ink);max-width:52ch;margin-top:16px}
.jump{list-style:none;margin:18px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:4px 22px;font-size:16px}
.grp{padding-top:44px;scroll-margin-top:16px}
.grp h2{font-size:clamp(1.5rem,1.2rem + 1vw,2rem)}
.grp .lede{margin-top:8px;max-width:64ch}
.cards{list-style:none;margin:20px 0 0;padding:0;display:grid;gap:16px}
@media (min-width:720px){.cards{grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}}
@media (min-width:1040px){.cards{grid-template-columns:repeat(3,minmax(0,1fr))}}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;display:flex;flex-direction:column;overflow:hidden;min-width:0;scroll-margin-top:16px}
.card:target{outline:2px solid var(--blue);outline-offset:2px}
.thumb{display:block;aspect-ratio:8/5;background:#EAF2FF;border-bottom:1px solid var(--line);overflow:hidden}
.thumb img{width:100%;height:100%;object-fit:cover;object-position:top}
.thumb.face{display:flex;flex-direction:column;justify-content:flex-end;gap:6px;padding:18px 20px;background:#1A2236;color:#F6EFE8}
.thumb.face .fk{font:500 13px/1 var(--f-mono);color:#FFA27A;letter-spacing:.04em;overflow-wrap:anywhere}
.thumb.face .ft{font:400 1.6rem/1.15 var(--f-serif);overflow-wrap:anywhere}
.card .in{padding:18px 20px 14px;display:flex;flex-direction:column;flex:1;min-width:0}
.card .kind{margin:0 0 6px;font-size:15px;color:var(--sun);font-weight:500}
.card h3{font:400 1.3rem/1.25 var(--f-serif);letter-spacing:-.005em;color:var(--ink);overflow-wrap:anywhere}
.card p.d{margin:10px 0 0;font-size:16px;color:var(--ink)}
.card .go{list-style:none;margin:auto 0 0;padding:12px 0 0;display:flex;flex-wrap:wrap;gap:0 20px}
.card .go a{font-weight:500;font-size:16px}
.card .go .arr{margin-left:.35em}
.listing{padding-bottom:64px}
"""


def build_page(data):
    items = [i for g in data["groups"] for i in g["items"]]
    n = len(items)
    jump = "".join(f'<li><a class="tap" href="#{g["id"]}">{esc(g["title"])}</a></li>' for g in data["groups"])
    sections = []
    for g in data["groups"]:
        cards = "\n".join(card(i) for i in g["items"])
        sections.append(f"""  <section class="wrap grp" id="{g['id']}" aria-labelledby="{g['id']}-h">
    <h2 id="{g['id']}-h">{esc(g['title'])}</h2>
    <p class="lede">{esc(g['lede'])}</p>
    <ul class="cards">
{cards}
    </ul>
  </section>""")
    desc = ("Projects by JD Davenport: my own builds on Claude Code, BYU AI Foundry products, "
            "Spark AI at Siemens, and client work. Each links to the live thing.")
    page = bw.head("Projects · JD Davenport", desc, "/projects", PAGE_CSS)
    page += f"""
<main id="main" data-stage="dawn">
  <section class="wrap hero" aria-labelledby="proj-h">
    <h1 id="proj-h">Projects</h1>
    <p class="lede">My own builds, BYU AI Foundry client work, and Spark AI at Siemens. Each card says who built it and links to the live thing.</p>
    <ul class="jump" aria-label="Groups on this page">{jump}</ul>
  </section>
{chr(10).join(sections)}
  <div class="wrap listing"><p class="lede">My jobs are written up as case studies on <a href="/work">Work</a>. Everything I keep public on GitHub is at <a href="https://github.com/jddavenportOpen" rel="noopener">github.com/jddavenportOpen</a>.</p></div>
</main>
"""
    page += bw.FOOTER + "</body>\n</html>\n"
    return page, n


def build():
    data = load()
    page, n = build_page(data)
    with open(os.path.join(ROOT, "projects.html"), "w", encoding="utf-8") as f:
        f.write(page)
    served = []
    for g in data["groups"]:
        for i in g["items"]:
            served.append({"slug": i["slug"], "group": g["title"], "title": i["title"], "kind": i["kind"],
                           "line": i["line"], "links": i["links"],
                           "thumb": f"/images/projects/{i['thumb']}-thumb.webp" if i.get("thumb") else None})
    with open(os.path.join(ROOT, "projects.json"), "w", encoding="utf-8") as f:
        json.dump({"projects": served, "count": len(served)}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"wrote projects.html and projects.json: {n} projects in {len(data['groups'])} groups")
    return data


if __name__ == "__main__":
    build()
