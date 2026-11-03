#!/usr/bin/env python3
"""Build /work and /work/<slug> from tools/work/work.json.

Stdlib only, deterministic (no timestamps, stable ordering), re-runnable:

    python3 tools/work/build_work.py

Writes work.html and work/<slug>.html (one per case study) at the repo root.
Cards are rendered server-side so the page reads fine with JS off; the inline
script only filters them.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "tools", "work", "work.json")
SITE = "https://jddavenport.com"
FILTER_CHIP_MIN = 2  # a tag needs at least this many items to get a filter chip

ACTION = {
    "live-product": "Visit site",
    "open-source": "View repo",
    "case-study": "Read case study",
}
KIND_LABEL = {
    "live-product": "Live product",
    "open-source": "Open source",
    "case-study": "Case study",
}


def esc(s):
    return html.escape(s or "", quote=True)


# ---------- tiny markdown: ## headings, paragraphs, - lists, **bold** ----------
def md_inline(text):
    out = esc(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)


def md_to_html(md):
    lines = (md or "").replace("\r\n", "\n").split("\n")
    out, para, items = [], [], []

    def flush():
        if para:
            out.append("<p>" + md_inline(" ".join(para)) + "</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join("<li>" + md_inline(i) + "</li>" for i in items) + "</ul>")
            items.clear()

    for raw in lines:
        line = raw.strip()
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if not line:
            flush()
        elif m:
            flush()
            level = min(len(m.group(1)) + 0, 4)
            level = max(level, 2)  # page owns h1
            out.append("<h%d>%s</h%d>" % (level, md_inline(m.group(2)), level))
        elif re.match(r"^[-*]\s+", line):
            if para:
                flush()
            items.append(re.sub(r"^[-*]\s+", "", line))
        else:
            if items:
                flush()
            para.append(line)
    flush()
    return "\n".join(out)


# ---------- shared chrome (matches index.html) ----------
CSS = r"""
:root{
  --f-serif:"Newsreader",Georgia,"Times New Roman",serif;
  --f-sans:"Geist",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --f-mono:"Geist Mono",ui-monospace,"SF Mono",Menlo,monospace;
  --coral:#FF8A5C;
  --gutter:16px;
  --max:1120px;
}
[data-stage=dawn]  {--bg:#FFFBF6;--ink:#1A2236;--muted:#566079;--blue:#0358F7;--on-blue:#FFFFFF;--sun:#A3481F;--line:rgba(26,34,54,.16);--card:#FFFFFF}
[data-stage=night] {--bg:#090D18;--ink:#F6EFE8;--muted:#A3AEC8;--blue:#8DB0FF;--on-blue:#090D18;--sun:#FFA27A;--line:rgba(246,239,232,.16);--card:#0F1524}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;background:#FFFBF6}
body{margin:0;background:#FFFBF6;color:#1A2236;font:400 17px/1.6 var(--f-sans);-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,svg{max-width:100%}
img{display:block}
a{color:var(--blue);text-underline-offset:.18em;text-decoration-thickness:1px}
a:hover{text-decoration-thickness:2px}
:focus-visible{outline:2px solid var(--blue);outline-offset:3px;border-radius:3px}
.skip{position:absolute;left:-9999px;top:8px;background:#1A2236;color:#fff;padding:12px 14px;z-index:50}
.skip:focus{left:var(--gutter)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.tap{display:inline-flex;align-items:center;min-height:44px}
section[data-stage],footer[data-stage],header[data-stage],main[data-stage]{background:var(--bg);color:var(--ink)}
.wrap{max-width:var(--max);margin:0 auto;padding:0 var(--gutter)}
@media (min-width:720px){:root{--gutter:32px}}
h1,h2,h3{margin:0;font-weight:400}
h2{font:400 clamp(1.85rem,1.3rem + 2.2vw,2.9rem)/1.1 var(--f-serif);letter-spacing:-.012em;max-width:24ch;text-wrap:balance}
.lede{color:var(--muted);max-width:62ch;margin:16px 0 0;font-size:1.0625rem}
/* header */
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;padding-top:6px;padding-bottom:0}
.mark{font:500 19px/1 var(--f-serif);color:var(--ink);text-decoration:none;letter-spacing:-.01em;white-space:nowrap}
.top nav ul{display:flex;gap:10px;list-style:none;margin:0;padding:0;font-size:16px}
.top nav a{color:var(--ink);text-decoration:none}
.top nav a:hover,.top nav a[aria-current]{text-decoration:underline}
.top nav a.cv{min-height:36px;margin:4px 0;padding:0 10px;border:1px solid var(--ink);border-radius:999px}
.top nav a.cv:hover{background:var(--ink);color:var(--bg);text-decoration:none}
@media (min-width:720px){.top{padding-top:18px}.top nav ul{gap:28px}}
@media (max-width:479px){.top{flex-wrap:wrap;row-gap:0}.top nav ul{gap:16px}}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:48px;padding:0 20px;border-radius:999px;font:500 16px/1.2 var(--f-sans);text-decoration:none;border:1px solid transparent;cursor:pointer}
.btn.sun{background:var(--coral);color:#090D18;border-color:var(--coral);font-weight:600;justify-self:start}
.btn.sun:hover{background:#FFA27A;border-color:#FFA27A}
/* footer */
.sub-strip{padding-top:72px;padding-bottom:72px;display:grid;gap:26px}
@media (min-width:860px){.sub-strip{grid-template-columns:1fr auto;align-items:end;gap:64px;padding-bottom:100px}}
.sub-strip h2{max-width:20ch}
.foot{border-top:1px solid var(--line);padding-top:26px;padding-bottom:40px;display:grid;gap:18px;font-size:16px;color:var(--muted)}
@media (min-width:860px){.foot{grid-template-columns:1fr auto;align-items:start}}
.foot ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:0 22px}
.foot a{color:var(--ink);text-decoration:none}
.foot a:hover{text-decoration:underline}
.foot .who{color:var(--ink);font:400 22px/1.2 var(--f-serif)}
.foot p{margin:6px 0 0}
h1{font:400 clamp(2.45rem,1.4rem + 4.4vw,4.9rem)/1.03 var(--f-serif);letter-spacing:-.024em;color:var(--ink);max-width:18ch;text-wrap:balance}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important;animation:none!important}}
"""

LIST_CSS = r"""
.hero{padding-top:28px;padding-bottom:12px}
@media (min-width:720px){.hero{padding-top:56px}}
.hero .lede{font:400 clamp(1.125rem,1rem + .55vw,1.45rem)/1.42 var(--f-serif);color:var(--ink);max-width:48ch;margin-top:16px}
.controls{margin-top:28px;display:grid;gap:14px}
.controls[hidden]{display:none}
.search label{display:block;font-weight:500;font-size:16px;margin-bottom:6px}
.search input{width:100%;max-width:560px;min-height:48px;padding:0 16px;font:400 17px/1.2 var(--f-sans);color:var(--ink);background:#FFFFFF;border:1px solid #6B7389;border-radius:999px}
.search input:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;border:0;min-width:0}
.chips legend{font-weight:500;font-size:16px;margin-bottom:6px;padding:0;width:100%}
.chip{min-height:44px;padding:0 14px;border-radius:999px;border:1px solid var(--ink);background:transparent;color:var(--ink);font:500 15px/1 var(--f-sans);cursor:pointer}
.chip:hover{background:#EAF2FF}
.chip[aria-pressed=true]{background:var(--ink);color:#FFFBF6}
.chip .n{opacity:.8;margin-left:4px;font-variant-numeric:tabular-nums}
.count{margin:18px 0 0;font-size:16px;color:var(--muted)}
.cards{list-style:none;margin:16px 0 0;padding:0;display:grid;gap:16px}
@media (min-width:720px){.cards{grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}}
@media (min-width:1040px){.cards{grid-template-columns:repeat(3,minmax(0,1fr))}}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;display:flex;flex-direction:column;overflow:hidden;min-width:0}
.card[hidden]{display:none}
.thumb{display:block;aspect-ratio:8/5;background:#EAF2FF;border-bottom:1px solid var(--line);overflow:hidden}
.thumb img{width:100%;height:100%;object-fit:cover;object-position:top}
.card .in{padding:18px 20px 16px;display:flex;flex-direction:column;flex:1;min-width:0}
.card .kind{margin:0 0 6px;font-size:15px;color:var(--sun);font-weight:500}
.card h3{font:400 1.35rem/1.25 var(--f-serif);letter-spacing:-.005em;color:var(--ink);overflow-wrap:anywhere}
.card p.d{margin:8px 0 0;font-size:16px;color:var(--ink)}
.card p.r{margin:8px 0 0;font-size:15px;color:var(--muted)}
.card p.r b{font-weight:600;color:var(--ink)}
.card p.w{margin:4px 0 0;font-size:15px;color:var(--muted)}
.tags{list-style:none;margin:12px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:6px}
.tags li{font-size:14px;line-height:1;padding:6px 9px;border-radius:999px;background:#F2EDE6;color:#3E475E}
.card .go{margin-top:auto;padding-top:14px}
.card .go a{font-weight:500}
.card .go .arr{margin-left:.35em}
.empty{margin:24px 0 0;padding:24px;border:1px dashed var(--line);border-radius:6px;background:var(--card)}
.empty[hidden]{display:none}
.empty p{margin:0 0 12px}
.reset{min-height:44px;padding:0 16px;border-radius:999px;border:1px solid var(--ink);background:transparent;color:var(--ink);font:500 16px/1 var(--f-sans);cursor:pointer}
.reset:hover{background:var(--ink);color:#FFFBF6}
.listing{padding-bottom:64px}
"""

CASE_CSS = r"""
.article{max-width:760px;padding-top:28px;padding-bottom:64px}
@media (min-width:720px){.article{padding-top:56px}}
.back{font-size:16px}
.kicker{margin:18px 0 10px;font-size:15px;color:var(--sun);font-weight:500}
.article h1{font-size:clamp(2.1rem,1.4rem + 3vw,3.6rem);max-width:22ch}
.meta{margin:18px 0 0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:4px 22px;font-size:16px;color:var(--muted)}
.meta b{color:var(--ink);font-weight:600}
.summary{font:400 clamp(1.125rem,1rem + .45vw,1.35rem)/1.45 var(--f-serif);color:var(--ink);margin:22px 0 0}
.callout{margin:26px 0 0;padding:14px 16px;border:1px solid var(--line);border-left:4px solid var(--sun);border-radius:4px;background:#FFFFFF;font-size:16px;color:var(--ink)}
.callout b{font-weight:600}
.body h2{font-size:clamp(1.5rem,1.2rem + 1vw,2rem);margin:40px 0 0}
.body h3{font:600 1.1rem/1.3 var(--f-sans);margin:28px 0 0}
.body p{margin:14px 0 0;max-width:68ch}
.body ul{margin:14px 0 0;padding-left:22px;max-width:68ch}
.body li{margin:8px 0}
.pn{margin:56px 0 0;padding:20px 0 0;border-top:1px solid var(--line);display:grid;gap:14px}
@media (min-width:720px){.pn{grid-template-columns:1fr 1fr}}
.pn a{display:block;padding:14px 16px;border:1px solid var(--line);border-radius:6px;background:#FFFFFF;text-decoration:none;color:var(--ink)}
.pn a:hover{border-color:var(--ink)}
.pn .lbl{display:block;font-size:14px;color:var(--muted)}
.pn .t{display:block;font:400 1.15rem/1.3 var(--f-serif);color:var(--blue)}
.pn .nx{text-align:right}
@media (max-width:719px){.pn .nx{text-align:left}}
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@500;600'
    '&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap" rel="stylesheet">'
)
ANALYTICS = (
    "<script>if(location.protocol!=='file:'){var va=document.createElement('script');va.defer=true;"
    "va.src='/_vercel/insights/script.js';document.head.appendChild(va);}</script>"
)


def head(title, description, path, extra_css):
    url = SITE + path
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{SITE}/images/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{SITE}/images/og-image.png">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta name="theme-color" content="#FFFBF6">
{ANALYTICS}
{FONTS}
<style>{CSS}{extra_css}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header data-stage="dawn">
  <div class="wrap top">
    <a class="mark tap" href="/">JD Davenport</a>
    <nav aria-label="Primary">
      <ul>
        <li><a class="tap" href="/work"{' aria-current="page"' if path == '/work' else ''}>Work</a></li>
        <li><a class="tap" href="/teardown">Teardown</a></li>
        <li><a class="tap" href="/newsletter">Newsletter</a></li>
        <li><a class="tap cv" href="/resume.pdf">Resume</a></li>
      </ul>
    </nav>
  </div>
</header>
"""


FOOTER = """
<footer data-stage="night">
  <div class="wrap">
    <div class="sub-strip">
      <div>
        <h2 id="sub-h">Raising Clawd, in your inbox.</h2>
        <p class="lede">My newsletter from inside Nerve Center: what 30+ agents in daily production teach me, what broke, and the guard I added after.</p>
      </div>
      <a class="btn sun" href="/newsletter">Subscribe <span aria-hidden="true">→</span></a>
    </div>
    <div class="foot">
      <div>
        <div class="who">JD Davenport</div>
        <p>Founder &amp; Managing Director, BYU AI Foundry</p>
        <p><a class="tap" href="mailto:me@jddavenport.com">me@jddavenport.com</a></p>
      </div>
      <nav aria-label="Footer">
        <ul>
          <li><a class="tap" href="/resume.pdf">Resume</a></li>
          <li><a class="tap" href="/work">Work</a></li>
          <li><a class="tap" href="/teardown">Teardown</a></li>
          <li><a class="tap" href="/docs/">Docs</a></li>
          <li><a class="tap" href="/newsletter">Newsletter</a></li>
          <li><a class="tap" href="https://www.linkedin.com/in/jd-davenport/">LinkedIn</a></li>
          <li><a class="tap" href="https://github.com/jddavenportOpen">GitHub</a></li>
          <li><a class="tap" href="https://byu-aifoundry.com">BYU AI Foundry</a></li>
        </ul>
        <p>© 2026 JD Davenport</p>
      </nav>
    </div>
  </div>
</footer>
"""


def tag_key(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def card(item):
    kind = item["kind"]
    slug = item["slug"]
    if kind == "case-study":
        href = "/work/" + slug
        ext = ""
    else:
        href = item["url"]
        ext = ' rel="noopener"'
    search = " ".join(
        [item["title"], item["summary"], item.get("role", ""), item.get("collaborator", ""), " ".join(item["tags"])]
    ).lower()
    tags = " ".join(tag_key(t) for t in item["tags"])
    thumb = ""
    if kind == "live-product" and os.path.exists(os.path.join(ROOT, "images", "work", slug + ".png")):
        thumb = (
            f'<a class="thumb" href="{esc(href)}"{ext} tabindex="-1" aria-hidden="true">'
            f'<img src="/images/work/{slug}.png" alt="" width="960" height="600" loading="lazy" decoding="async"></a>'
        )
    collab = f'<p class="w">{esc(item["collaborator"])}</p>' if item.get("collaborator") else ""
    when = f' · {esc(item["year"])}' if kind == "case-study" and item.get("year") else ""
    tag_li = "".join(f"<li>{esc(t)}</li>" for t in item["tags"])
    label = ACTION[kind]
    return f"""    <li class="card" data-kind="{kind}" data-tags="{esc(tags)}" data-search="{esc(search)}">
      {thumb}<div class="in">
        <p class="kind">{KIND_LABEL[kind]}{when}</p>
        <h3>{esc(item["title"])}</h3>
        <p class="d">{esc(item["summary"])}</p>
        <p class="r"><b>Role:</b> {esc(item.get("role", ""))}</p>
        {collab}
        <ul class="tags" aria-label="Tags">{tag_li}</ul>
        <p class="go"><a class="tap" href="{esc(href)}"{ext}>{label}<span class="sr">: {esc(item["title"])}</span><span class="arr" aria-hidden="true">→</span></a></p>
      </div>
    </li>"""


SCRIPT = r"""
<script>
(function(){
  var cards=[].slice.call(document.querySelectorAll('.card'));
  var q=document.getElementById('q'), count=document.getElementById('count'), empty=document.getElementById('empty');
  var kindBtns=[].slice.call(document.querySelectorAll('[data-set-kind]'));
  var tagBtns=[].slice.call(document.querySelectorAll('[data-set-tag]'));
  var state={q:'',kind:'',tag:''};
  var validKinds={}, validTags={};
  kindBtns.forEach(function(b){validKinds[b.getAttribute('data-set-kind')]=1;});
  tagBtns.forEach(function(b){validTags[b.getAttribute('data-set-tag')]=1;});
  function read(){
    var p=new URLSearchParams(location.search);
    state.q=p.get('q')||'';
    state.kind=validKinds[p.get('kind')]?p.get('kind'):'';
    state.tag=validTags[p.get('tag')]?p.get('tag'):'';
  }
  function write(){
    var p=new URLSearchParams();
    if(state.q)p.set('q',state.q);
    if(state.kind)p.set('kind',state.kind);
    if(state.tag)p.set('tag',state.tag);
    var s=p.toString();
    try{history.replaceState(null,'',location.pathname+(s?'?'+s:'')+location.hash);}catch(e){}
  }
  function apply(){
    var terms=state.q.toLowerCase().split(/\s+/).filter(Boolean), n=0;
    cards.forEach(function(c){
      var ok=(!state.kind||c.getAttribute('data-kind')===state.kind)
        &&(!state.tag||(' '+c.getAttribute('data-tags')+' ').indexOf(' '+state.tag+' ')>-1);
      if(ok){var hay=c.getAttribute('data-search');for(var i=0;i<terms.length;i++){if(hay.indexOf(terms[i])<0){ok=false;break;}}}
      c.hidden=!ok; if(ok)n++;
    });
    count.textContent=n===cards.length?'Showing all '+n+' items':'Showing '+n+' of '+cards.length+' items';
    empty.hidden=n!==0;
    kindBtns.forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-set-kind')===state.kind));});
    tagBtns.forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-set-tag')===state.tag));});
  }
  read();
  q.value=state.q;
  document.getElementById('controls').hidden=false;
  q.addEventListener('input',function(){state.q=q.value.trim();write();apply();});
  kindBtns.forEach(function(b){b.addEventListener('click',function(){state.kind=b.getAttribute('data-set-kind');write();apply();});});
  tagBtns.forEach(function(b){b.addEventListener('click',function(){var t=b.getAttribute('data-set-tag');state.tag=state.tag===t?'':t;write();apply();});});
  document.getElementById('reset').addEventListener('click',function(){state={q:'',kind:'',tag:''};q.value='';write();apply();q.focus();});
  window.addEventListener('popstate',function(){read();q.value=state.q;apply();});
  apply();
})();
</script>
"""


def build_list(data):
    items = data["items"]
    kinds = data["kinds"]
    order = ["live-product", "open-source", "case-study"]
    kind_counts = {k: sum(1 for i in items if i["kind"] == k) for k in order}
    tag_counts = {}
    tag_label = {}
    for i in items:
        for t in i["tags"]:
            k = tag_key(t)
            tag_counts[k] = tag_counts.get(k, 0) + 1
            tag_label.setdefault(k, t)
    chip_tags = sorted((k for k, n in tag_counts.items() if n >= FILTER_CHIP_MIN), key=lambda k: (-tag_counts[k], k))

    kind_chips = [f'<button type="button" class="chip" data-set-kind="" aria-pressed="true">All<span class="n">{len(items)}</span></button>']
    for k in order:
        kind_chips.append(
            f'<button type="button" class="chip" data-set-kind="{k}" aria-pressed="false">{esc(kinds[k])}'
            f'<span class="n">{kind_counts[k]}</span></button>'
        )
    tag_chips = [
        f'<button type="button" class="chip" data-set-tag="{k}" aria-pressed="false">{esc(tag_label[k])}'
        f'<span class="n">{tag_counts[k]}</span></button>'
        for k in chip_tags
    ]
    desc = "Products I built or helped build, open source, and case studies for work under NDA."
    page = head("Work · JD Davenport", desc, "/work", LIST_CSS)
    page += f"""
<main id="main" data-stage="dawn">
  <section class="wrap hero" aria-labelledby="work-h">
    <h1 id="work-h">Work</h1>
    <p class="lede">Products I built or helped build, open source, and case studies for work under NDA.</p>
    <div class="controls" id="controls" hidden>
      <div class="search" role="search">
        <label for="q">Search work</label>
        <input id="q" type="search" autocomplete="off" spellcheck="false" placeholder="Try “evals”, “Siemens” or “safety”" aria-describedby="count">
      </div>
      <fieldset class="chips">
        <legend>Kind</legend>
        {''.join(kind_chips)}
      </fieldset>
      <fieldset class="chips">
        <legend>Topic</legend>
        {''.join(tag_chips)}
      </fieldset>
    </div>
  </section>
  <section class="wrap listing" aria-label="All work">
    <p class="count" id="count" role="status" aria-live="polite">Showing all {len(items)} items</p>
    <ul class="cards">
{chr(10).join(card(i) for i in items)}
    </ul>
    <div class="empty" id="empty" hidden>
      <p>Nothing matches that search. Try a broader word, or clear the filters.</p>
      <button type="button" class="reset" id="reset">Clear search and filters</button>
    </div>
  </section>
</main>
"""
    page += FOOTER + SCRIPT + "</body>\n</html>\n"
    return page


def build_case(item, prev_item, next_item):
    path = "/work/" + item["slug"]
    page = head(item["title"] + " · JD Davenport", item["summary"], path, CASE_CSS)
    meta = [f'<li><b>Role</b> {esc(item["role"])}</li>', f'<li><b>Dates</b> {esc(item["year"])}</li>']
    pn = []
    if prev_item:
        pn.append(
            f'<a href="/work/{prev_item["slug"]}" rel="prev"><span class="lbl">← Previous case study</span>'
            f'<span class="t">{esc(prev_item["title"])}</span></a>'
        )
    else:
        pn.append("<span></span>")
    if next_item:
        pn.append(
            f'<a class="nx" href="/work/{next_item["slug"]}" rel="next"><span class="lbl">Next case study →</span>'
            f'<span class="t">{esc(next_item["title"])}</span></a>'
        )
    page += f"""
<main id="main" data-stage="dawn">
  <article class="wrap article">
    <a class="back tap" href="/work?kind=case-study">← All case studies</a>
    <p class="kicker">Case study</p>
    <h1>{esc(item["title"])}</h1>
    <ul class="meta">{''.join(meta)}</ul>
    <p class="summary">{esc(item["summary"])}</p>
    <p class="callout"><b>Confidentiality.</b> {esc(item.get("confidentiality_note", ""))}</p>
    <div class="body">
{md_to_html(item.get("body_md", ""))}
    </div>
    <nav class="pn" aria-label="More case studies">{''.join(pn)}</nav>
    <p><a class="back tap" href="/work">← Back to all work</a></p>
  </article>
</main>
"""
    page += FOOTER + "</body>\n</html>\n"
    return page


SERVED = ("slug", "title", "kind", "role", "summary", "tags", "url", "collaborator", "year",
          "confidentiality_note", "body_md")
NEVER_SERVED = ("jd_needs_to_confirm", "receipts", "status")


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    # Site rule (CLAUDE.md): no em/en-dashes and no emoji in visible copy.
    bad = re.findall(r"[\u2013\u2014\U0001F300-\U0001FAFF\u2600-\u27BF]", json.dumps(data, ensure_ascii=False))
    assert not bad, f"work.json has forbidden characters (dashes or emoji): {sorted(set(bad))}"
    seen = set()
    for i in data["items"]:
        assert i["slug"] not in seen, "duplicate slug " + i["slug"]
        seen.add(i["slug"])
        assert i["kind"] in ACTION, i["slug"]
        for k in NEVER_SERVED:
            assert k not in i, f"{i['slug']}: field {k} must not be in work.json"
        assert set(i) <= set(SERVED), f"{i['slug']}: unexpected fields {set(i) - set(SERVED)}"
        if i["kind"] != "case-study":
            assert i.get("url", "").startswith("https://"), i["slug"]
    with open(os.path.join(ROOT, "work.html"), "w", encoding="utf-8") as f:
        f.write(build_list(data))
    cases = [i for i in data["items"] if i["kind"] == "case-study"]
    os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
    for n, item in enumerate(cases):
        prev_item = cases[n - 1] if n > 0 else None
        next_item = cases[n + 1] if n + 1 < len(cases) else None
        with open(os.path.join(ROOT, "work", item["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(build_case(item, prev_item, next_item))
    print(f"wrote work.html ({len(data['items'])} items) and {len(cases)} case-study pages")


if __name__ == "__main__":
    main()
