#!/usr/bin/env python3
"""Build /projects (projects.html + projects.json) from the vendored project catalog.

Stdlib only, deterministic, re-runnable. Two modes:

    # 1. refresh the vendored inputs from the audit catalog (run when the catalog changes)
    python3 tools/projects/build_projects.py --refresh \
        --catalog <catalog.json> --decisions <library-decisions.json> --shots <screenshot dir>

    # 2. build the page from what is vendored here (the normal case)
    python3 tools/projects/build_projects.py

--refresh keeps only the entries library-decisions.json ships, and only their public
fields, and applies overrides.json BEFORE writing catalog.json, so the vendored file
holds exactly the copy that ships: nothing internal (notes, evidence paths, sensitivity,
pre-edit text) ever lands in this public repo. The build re-checks that every override
is already in catalog.json and fails if one is not (re-run --refresh). Excluded slugs are stored as sha256 hashes in denylist.json: the guard test
can prove none of them leaked without the repo naming them. It also copies the
screenshots into images/projects/.

The page is rendered server-side (it reads fine with JS off); the inline script only
searches, filters and sorts. Shared chrome comes from tools/work/build_work.py.
"""
import argparse
import hashlib
import html
import json
import os
import re
import shutil
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "work"))
import build_work as bw  # noqa: E402  shared CSS, fonts, nav and footer

CATALOG = os.path.join(HERE, "catalog.json")
OVERRIDES = os.path.join(HERE, "overrides.json")
DENYLIST = os.path.join(HERE, "denylist.json")
IMG_DIR = os.path.join(ROOT, "images", "projects")
SITE = bw.SITE
FILTER_CHIP_MIN = 2  # same rule as /work: a category or status needs 2+ items for a chip

PUBLIC_FIELDS = ("slug", "title", "owner", "track", "category", "status", "one_liner",
                 "details", "tech", "links", "highlight_score")
SERVED_FIELDS = ("slug", "title", "owner", "track", "category", "status", "one_liner",
                 "details", "tech", "links", "thumb", "image")

# PLAN.md section 1, in order. The plan's client build is not cleared, so its first
# alternate (app-feedback-loop) takes the slot; the newsletters use the same ten.
TOP10 = ["siemens-spark-ai", "ai-foundry-program", "foundry-marketplace", "app-feedback-loop",
         "nerve-center", "recruit-copilot", "clawdling", "speedprep", "deckboard", "agenttree-merch"]

# Screenshots that show a GitHub repo page get a text card instead (PLAN.md section 6).
SKIP_SHOTS = {"app-feedback-loop", "clawdling"}

OWNERS = [  # (catalog owner, url key, chip label)
    ("JD", "jd", "JD"),
    ("AI Foundry", "foundry", "AI Foundry"),
    ("JD at Siemens", "siemens", "JD at Siemens"),
    ("John Davenport + JD", "john-davenport", "With John Davenport"),
]
OWNER_KEY = {o: k for o, k, _ in OWNERS}
OWNER_LABEL = {o: lbl for o, _, lbl in OWNERS}
DAD = "John Davenport + JD"

# client-project in the catalog covers JD's own past roles once client builds are removed,
# and those link to /work case studies, so the public label is "Case study".
CATEGORY_KEY = {"client-project": "case-study"}
CATEGORY_LABEL = {
    "tool": "Tool", "app": "App", "plugin": "Plugin", "research": "Research", "agent": "Agent",
    "website": "Website", "case-study": "Case study", "harness": "Harness", "skill": "Skill",
    "course": "Course", "newsletter": "Newsletter", "program": "Program", "milestone": "Milestone",
    "business": "Business",
}
STATUS_LABEL = {"live": "Live", "beta": "Beta", "built": "Built", "shipped": "Shipped", "archived": "Archived"}
STATUS_ORDER = ["live", "beta", "built", "shipped", "archived"]

DASH_RE = re.compile("[–—]")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def esc(s):
    return html.escape(s or "", quote=True)


def slug_hash(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def public_text(s):
    """Copy rules for anything printed: JD asked for his dad to appear by name."""
    s = re.sub(r"\bDad's\b", "John Davenport's", s or "")
    s = re.sub(r"\bDad\b", "John Davenport", s)
    return s.strip()


TEXT_OVERRIDES = ("title", "one_liner", "details", "category")


def load_overrides():
    with open(OVERRIDES, encoding="utf-8") as f:
        return {k: v for k, v in json.load(f).items() if not k.startswith("_")}


def apply_overrides(row, o):
    """Public copy fixes: replace text fields, drop or re-point links. Idempotent."""
    for k in TEXT_OVERRIDES:
        if k in o:
            row[k] = o[k]
    drop = set(o.get("drop_links", []))
    fix = o.get("replace_links", {})
    row["links"] = [dict(l, url=fix.get(l["url"], l["url"])) for l in row["links"] if l["url"] not in drop]
    return row


# ---------------------------------------------------------------- refresh
def refresh(catalog_path, decisions_path, shots_dir):
    with open(catalog_path, encoding="utf-8") as f:
        cat = json.load(f)
    with open(decisions_path, encoding="utf-8") as f:
        dec = json.load(f)
    ship = set(dec["included"])
    over = load_overrides()
    excluded = sorted({x["slug"] for x in dec["excluded"]})
    assert not ship & set(excluded), "a slug is both included and excluded"
    entries = []
    for e in cat["entries"]:
        if e["slug"] not in ship:
            continue
        assert e.get("sensitivity") != "private", e["slug"]
        row = {k: e.get(k) for k in PUBLIC_FIELDS}
        # keep only links that answered 200 to an anonymous request during the audit
        row["links"] = [{"label": l["label"], "url": l["url"]} for l in e.get("links") or []
                        if l.get("http_status") == 200]
        entries.append(apply_overrides(row, over.get(e["slug"], {})))
    entries.sort(key=lambda r: r["slug"])
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump({"source": "foundry-audit catalog, shipped entries only, public fields only",
                   "generated": cat.get("generated", ""), "entries": entries}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with open(DENYLIST, "w", encoding="utf-8") as f:
        json.dump({"about": "sha256 of every catalog slug that must never appear on /projects",
                   "sha256": sorted(slug_hash(s) for s in excluded)}, f, indent=1)
        f.write("\n")
    copied = 0
    if shots_dir:
        with open(os.path.join(shots_dir, "manifest.json"), encoding="utf-8") as f:
            manifest = json.load(f)
        os.makedirs(IMG_DIR, exist_ok=True)
        for m in manifest:
            s = m["slug"]
            if not m.get("ok") or s not in ship or s in SKIP_SHOTS:
                continue
            for src, dst in ((m["file"], s + ".webp"), (m["thumb"], s + "-thumb.webp")):
                shutil.copyfile(os.path.join(shots_dir, src), os.path.join(IMG_DIR, dst))
            copied += 1
    print(f"refreshed {len(entries)} entries, {len(excluded)} denylisted slugs, {copied} screenshots")


# ---------------------------------------------------------------- build
def load():
    with open(CATALOG, encoding="utf-8") as f:
        entries = json.load(f)["entries"]
    over = load_overrides()
    by = {e["slug"]: e for e in entries}
    unknown = set(over) - set(by)
    assert not unknown, f"overrides for slugs that are not shipped: {sorted(unknown)}"
    for s, o in over.items():  # catalog.json must already hold the shipped copy
        e = by[s]
        assert apply_overrides(json.loads(json.dumps(e)), o) == e, \
            f"{s}: overrides.json is not applied to catalog.json; re-run --refresh"
    items = []
    for e in entries:
        cat = CATEGORY_KEY.get(e["category"], e["category"])
        status = e["status"]
        assert e["owner"] in OWNER_KEY, f"{e['slug']}: unknown owner {e['owner']!r}"
        assert cat in CATEGORY_LABEL, f"{e['slug']}: unknown category {cat!r}"
        assert status in STATUS_LABEL, f"{e['slug']}: unknown status {status!r}"
        thumb = f"/images/projects/{e['slug']}-thumb.webp"
        image = f"/images/projects/{e['slug']}.webp"
        has_img = os.path.exists(os.path.join(ROOT, image.lstrip("/")))
        items.append({
            "slug": e["slug"],
            "title": public_text(e["title"]),
            "owner": e["owner"],
            "track": e["track"],
            "category": cat,
            "status": status,
            "one_liner": public_text(e["one_liner"]),
            "details": public_text(e["details"]),
            "tech": [public_text(t) for t in (e.get("tech") or [])],
            "links": [dict(l) for l in e["links"]],
            "thumb": thumb if has_img else None,
            "image": image if has_img else None,
            "_score": e.get("highlight_score") or 0,
        })
    items.sort(key=lambda i: (-i["_score"], i["title"].lower()))
    blob = json.dumps(items, ensure_ascii=False)
    bad = sorted(set(DASH_RE.findall(blob) + EMOJI_RE.findall(blob)))
    assert not bad, f"forbidden characters in public copy (dashes or emoji): {bad}"
    for i in items:
        assert i["links"], f"{i['slug']}: every shipped card needs at least one public link"
        for l in i["links"]:
            assert l["url"].startswith("https://"), f"{i['slug']}: non-https link {l['url']}"
    return items


def primary_label(url):
    u = urlparse(url)
    if u.netloc == "github.com":
        return "View repo"
    if u.netloc == "jddavenport.com" and re.match(r"^/(docs|work|teardown)", u.path):
        return "Read the write-up"
    return "Visit site"


def host(url):
    return urlparse(url).netloc.replace("www.", "")


def ext_attrs(url):
    return "" if url.startswith(SITE + "/") else ' rel="noopener"'


def card(i):
    s = i["slug"]
    hay = " ".join([i["title"], i["one_liner"], i["details"], " ".join(i["tech"]),
                    OWNER_LABEL[i["owner"]], CATEGORY_LABEL[i["category"]]]).lower()
    first = i["links"][0]["url"]
    if i["thumb"]:
        face = (f'<div class="thumb"><img src="{i["thumb"]}" alt="" width="720" height="450" '
                f'loading="lazy" decoding="async"></div>')
    else:
        face = (f'<div class="thumb face" aria-hidden="true"><span class="fk">{esc(host(first))}</span>'
                f'<span class="ft">{esc(i["title"].split(":")[0])}</span></div>')
    tags = "".join(f"<li>{esc(t)}</li>" for t in i["tech"][:4])
    tags = f'<ul class="tags" aria-label="Built with">{tags}</ul>' if tags else ""
    links = "".join(
        f'<li><a class="tap" href="{esc(l["url"])}"{ext_attrs(l["url"])}>{esc(public_text(l["label"]))}'
        f'<span class="sr"> ({esc(host(l["url"]))})</span></a></li>' for l in i["links"])
    shot = ""
    if i["image"]:
        shot = (f'<figure class="shot"><img src="{i["image"]}" alt="Screenshot of {esc(i["title"].split(":")[0])}, '
                f'taken from {esc(host(first))} in November 2026" width="1440" height="900" loading="lazy" '
                f'decoding="async"></figure>')
    return f"""    <li class="card" id="p-{s}" data-owner="{OWNER_KEY[i['owner']]}" data-cat="{i['category']}" data-status="{i['status']}" data-score="{i['_score']}" data-title="{esc(i['title'].lower())}" data-search="{esc(hay)}">
      {face}<div class="in">
        <p class="kind"><span>{esc(OWNER_LABEL[i['owner']])}</span> · {esc(CATEGORY_LABEL[i['category']])}</p>
        <h3>{esc(i['title'])}</h3>
        <p class="st st-{i['status']}">{STATUS_LABEL[i['status']]}</p>
        <p class="d">{esc(i['one_liner'])}</p>
        {tags}
        <details>
          <summary class="tap">Details and links<span class="sr">: {esc(i['title'])}</span></summary>
          <p class="more">{esc(i['details'])}</p>
          <ul class="links">{links}</ul>
          {shot}
        </details>
        <p class="go"><a class="tap" href="{esc(first)}"{ext_attrs(first)}>{primary_label(first)}<span class="sr">: {esc(i['title'])}</span><span class="arr" aria-hidden="true">→</span></a></p>
      </div>
    </li>"""


def top_card(n, i):
    img = (f'<img src="{i["thumb"]}" alt="" width="720" height="450" loading="lazy" decoding="async">'
           if i["thumb"] else f'<span class="ft">{esc(i["title"].split(":")[0])}</span>')
    cls = "tthumb" if i["thumb"] else "tthumb face"
    return (f'      <li class="pick"><a href="#p-{i["slug"]}" data-jump="{i["slug"]}">'
            f'<span class="{cls}" aria-hidden="true">{img}</span>'
            f'<span class="tn">{n:02d}</span><span class="tt">{esc(i["title"])}</span>'
            f'<span class="td">{esc(i["one_liner"])}</span></a></li>')


PAGE_CSS = r"""
.hero{padding-top:28px;padding-bottom:8px}
@media (min-width:720px){.hero{padding-top:56px}}
.hero .lede{font:400 clamp(1.125rem,1rem + .55vw,1.45rem)/1.42 var(--f-serif);color:var(--ink);max-width:52ch;margin-top:16px}
.count-line{margin:14px 0 0;font:500 15px/1.4 var(--f-mono);color:var(--muted);letter-spacing:.02em}
.tops{padding-top:28px}
.tops h2,.lib h2,.dad h2{font-size:clamp(1.5rem,1.2rem + 1vw,2rem)}
.tops .lede{margin-top:8px}
.toplist{list-style:none;margin:18px 0 0;padding:0;display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(min(240px,100%),1fr))}
.pick a{display:grid;grid-template-columns:auto 1fr;align-content:start;gap:4px 10px;height:100%;padding:12px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink);text-decoration:none}
.pick a:hover{border-color:var(--ink)}
.tthumb{grid-column:1/-1;display:block;aspect-ratio:8/5;overflow:hidden;border-radius:4px;background:#EAF2FF;margin-bottom:6px}
.tthumb img{width:100%;height:100%;object-fit:cover;object-position:top}
.tthumb.face{display:flex;align-items:flex-end;padding:12px;background:#1A2236;color:#F6EFE8}
.tthumb.face .ft{font:400 1.2rem/1.2 var(--f-serif)}
.tn{font:600 14px/1.5 var(--f-mono);color:var(--sun)}
.tt{font:500 16px/1.35 var(--f-sans)}
.td{grid-column:1/-1;font-size:15px;color:var(--muted);line-height:1.45}
.lib{padding-top:48px}
.controls{margin-top:18px;display:grid;gap:14px}
.controls[hidden]{display:none}
.search label,.sort label{display:block;font-weight:500;font-size:16px;margin-bottom:6px}
.search input{width:100%;max-width:560px;min-height:48px;padding:0 16px;font:400 17px/1.2 var(--f-sans);color:var(--ink);background:#FFFFFF;border:1px solid #6B7389;border-radius:999px}
.sort select{min-height:44px;padding:0 12px;font:400 16px/1.2 var(--f-sans);color:var(--ink);background:#FFFFFF;border:1px solid #6B7389;border-radius:8px}
.search input:focus-visible,.sort select:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;border:0;min-width:0}
.chips legend{font-weight:500;font-size:16px;margin-bottom:6px;padding:0;width:100%}
.chip{min-height:44px;padding:0 14px;border-radius:999px;border:1px solid var(--ink);background:transparent;color:var(--ink);font:500 15px/1 var(--f-sans);cursor:pointer}
.chip:hover{background:#EAF2FF}
.chip[aria-pressed=true]{background:var(--ink);color:#FFFBF6}
.chip .n{opacity:.8;margin-left:4px;font-variant-numeric:tabular-nums}
.count{margin:18px 0 0;font-size:16px;color:var(--muted)}
.cards{list-style:none;margin:16px 0 0;padding:0;display:grid;gap:16px}
@media (min-width:768px){.cards{grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}}
@media (min-width:1040px){.cards{grid-template-columns:repeat(3,minmax(0,1fr))}}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;display:flex;flex-direction:column;overflow:hidden;min-width:0;scroll-margin-top:16px}
.card[hidden]{display:none}
.card:target{outline:2px solid var(--blue);outline-offset:2px}
.thumb{display:block;aspect-ratio:8/5;background:#EAF2FF;border-bottom:1px solid var(--line);overflow:hidden}
.thumb img{width:100%;height:100%;object-fit:cover;object-position:top}
.thumb.face{display:flex;flex-direction:column;justify-content:flex-end;gap:6px;padding:18px 20px;background:#1A2236;color:#F6EFE8}
.thumb.face .fk{font:500 13px/1 var(--f-mono);color:#FFA27A;letter-spacing:.04em;overflow-wrap:anywhere}
.thumb.face .ft{font:400 1.6rem/1.15 var(--f-serif);overflow-wrap:anywhere}
.card .in{padding:18px 20px 16px;display:flex;flex-direction:column;flex:1;min-width:0}
.card .kind{margin:0 0 6px;font-size:15px;color:var(--sun);font-weight:500}
.card h3{font:400 1.3rem/1.25 var(--f-serif);letter-spacing:-.005em;color:var(--ink);overflow-wrap:anywhere}
.st{display:inline-block;align-self:flex-start;margin:10px 0 0;padding:4px 10px;border-radius:999px;font:500 13px/1.2 var(--f-mono);border:1px solid currentColor}
.st-live{color:#2C6E3F}.st-beta,.st-built{color:#1F5F82}.st-shipped{color:#566079}.st-archived{color:#6B7389}
.card p.d{margin:10px 0 0;font-size:16px;color:var(--ink)}
.tags{list-style:none;margin:12px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:6px}
.tags li{font-size:14px;line-height:1;padding:6px 9px;border-radius:999px;background:#F2EDE6;color:#3E475E}
.card details{margin-top:12px;border-top:1px solid var(--line)}
.card summary{cursor:pointer;font-weight:500;font-size:16px;color:var(--blue);list-style-position:inside}
.card details[open] summary{margin-bottom:4px}
.card p.more{margin:4px 0 0;font-size:15px;line-height:1.55;color:var(--ink)}
.links{list-style:none;margin:8px 0 0;padding:0;display:flex;flex-direction:column}
.links a{font-size:15px;overflow-wrap:anywhere}
.shot{margin:10px 0 4px}
.shot img{width:100%;height:auto;border:1px solid var(--line);border-radius:4px}
.card .go{margin-top:auto;padding-top:10px}
.card .go a{font-weight:500}
.card .go .arr{margin-left:.35em}
.empty{margin:24px 0 0;padding:24px;border:1px dashed var(--line);border-radius:6px;background:var(--card)}
.empty[hidden]{display:none}
.empty p{margin:0 0 12px}
.reset{min-height:44px;padding:0 16px;border-radius:999px;border:1px solid var(--ink);background:transparent;color:var(--ink);font:500 16px/1 var(--f-sans);cursor:pointer}
.reset:hover{background:var(--ink);color:#FFFBF6}
.dad{margin-top:56px;scroll-margin-top:16px}
.dad[hidden]{display:none}
.listing{padding-bottom:64px}
"""

SCRIPT = r"""
<script>
(function(){
  var cards=[].slice.call(document.querySelectorAll('.card'));
  var lists=[].slice.call(document.querySelectorAll('.cards'));
  var q=document.getElementById('q'),count=document.getElementById('count'),empty=document.getElementById('empty');
  var sortSel=document.getElementById('sort'),dad=document.getElementById('john-davenport');
  var groups={owner:[],cat:[],status:[]},valid={owner:{},cat:{},status:{}};
  [].slice.call(document.querySelectorAll('[data-f]')).forEach(function(b){
    var g=b.getAttribute('data-f');groups[g].push(b);valid[g][b.getAttribute('data-v')]=1;});
  var state;
  function blank(){return {q:'',owner:[],cat:[],status:[],sort:'featured'};}
  function read(){
    var p=new URLSearchParams(location.search);state=blank();
    state.q=p.get('q')||'';
    ['owner','cat','status'].forEach(function(g){
      state[g]=(p.get(g)||'').split(',').filter(function(v){return valid[g][v];});});
    state.sort=p.get('sort')==='az'?'az':'featured';
  }
  function write(push){
    var p=new URLSearchParams();
    if(state.q)p.set('q',state.q);
    ['owner','cat','status'].forEach(function(g){if(state[g].length)p.set(g,state[g].join(','));});
    if(state.sort!=='featured')p.set('sort',state.sort);
    var s=p.toString(),url=location.pathname+(s?'?'+s:'')+location.hash;
    try{if(push&&url!==location.pathname+location.search+location.hash)history.pushState(null,'',url);else history.replaceState(null,'',url);}catch(e){}
  }
  function sortCards(){
    lists.forEach(function(ul){
      var lis=[].slice.call(ul.children);
      lis.sort(function(a,b){
        if(state.sort==='az')return a.getAttribute('data-title')<b.getAttribute('data-title')?-1:1;
        var d=(+b.getAttribute('data-score'))-(+a.getAttribute('data-score'));
        return d||(a.getAttribute('data-title')<b.getAttribute('data-title')?-1:1);
      });
      lis.forEach(function(li){ul.appendChild(li);});
    });
  }
  function apply(){
    var terms=state.q.toLowerCase().split(/\s+/).filter(Boolean),n=0;
    cards.forEach(function(c){
      var ok=true;
      ['owner','cat','status'].forEach(function(g){
        if(ok&&state[g].length&&state[g].indexOf(c.getAttribute('data-'+g))<0)ok=false;});
      if(ok){var hay=c.getAttribute('data-search');for(var i=0;i<terms.length;i++){if(hay.indexOf(terms[i])<0){ok=false;break;}}}
      c.hidden=!ok;if(ok)n++;
    });
    dad.hidden=!dad.querySelector('.card:not([hidden])');
    count.textContent=n===cards.length?'Showing all '+n+' projects':'Showing '+n+' of '+cards.length+' projects';
    empty.hidden=n!==0;
    ['owner','cat','status'].forEach(function(g){groups[g].forEach(function(b){
      b.setAttribute('aria-pressed',String(state[g].indexOf(b.getAttribute('data-v'))>-1));});});
    sortSel.value=state.sort;
  }
  function openHash(){
    var m=/^#p-([a-z0-9-]+)$/.exec(location.hash);if(!m)return;
    var c=document.getElementById('p-'+m[1]);if(!c)return;
    if(c.hidden){state=blank();q.value='';write(false);sortCards();apply();}
    var d=c.querySelector('details');if(d)d.open=true;
    c.scrollIntoView({block:'start'});
  }
  read();q.value=state.q;
  document.getElementById('controls').hidden=false;
  q.addEventListener('input',function(){state.q=q.value.trim();write(false);apply();});
  ['owner','cat','status'].forEach(function(g){groups[g].forEach(function(b){
    b.addEventListener('click',function(){
      var v=b.getAttribute('data-v'),k=state[g].indexOf(v);
      if(k>-1)state[g].splice(k,1);else state[g].push(v);
      write(true);apply();});});});
  sortSel.addEventListener('change',function(){state.sort=sortSel.value==='az'?'az':'featured';write(true);sortCards();apply();});
  document.getElementById('reset').addEventListener('click',function(){state=blank();q.value='';write(true);sortCards();apply();q.focus();});
  window.addEventListener('popstate',function(){read();q.value=state.q;sortCards();apply();});
  window.addEventListener('hashchange',openHash);
  sortCards();apply();openHash();
})();
</script>
"""


def chips(group, values, label_of, counts, always=False):
    out = []
    for v in values:
        n = counts.get(v, 0)
        if n == 0 or (not always and n < FILTER_CHIP_MIN):
            continue
        out.append(f'<button type="button" class="chip" data-f="{group}" data-v="{v}" aria-pressed="false">'
                   f'{esc(label_of(v))}<span class="n">{n}</span></button>')
    return "".join(out)


def build_page(items):
    by = {i["slug"]: i for i in items}
    missing = [s for s in TOP10 if s not in by]
    assert not missing, f"top ten names slugs that are not shipped: {missing}"
    tops = [by[s] for s in TOP10]
    n = len(items)
    owner_counts, cat_counts, status_counts = {}, {}, {}
    for i in items:
        k = OWNER_KEY[i["owner"]]
        owner_counts[k] = owner_counts.get(k, 0) + 1
        cat_counts[i["category"]] = cat_counts.get(i["category"], 0) + 1
        status_counts[i["status"]] = status_counts.get(i["status"], 0) + 1
    owner_label = {k: lbl for _, k, lbl in OWNERS}
    cats = sorted(cat_counts, key=lambda c: (-cat_counts[c], CATEGORY_LABEL[c]))
    owner_chips = chips("owner", [k for _, k, _ in OWNERS], owner_label.get, owner_counts, always=True)
    cat_chips = chips("cat", cats, CATEGORY_LABEL.get, cat_counts)
    status_chips = chips("status", STATUS_ORDER, STATUS_LABEL.get, status_counts)
    main_cards = "\n".join(card(i) for i in items if i["owner"] != DAD)
    dad_items = [i for i in items if i["owner"] == DAD]
    dad_cards = "\n".join(card(i) for i in dad_items)
    desc = (f"A searchable library of {n} projects: my own builds, BYU AI Foundry, Spark AI at Siemens, "
            "and the products I build with my dad, John Davenport.")
    page = bw.head("Projects · JD Davenport", desc, "/projects", PAGE_CSS)
    page += f"""
<main id="main" data-stage="dawn">
  <section class="wrap hero" aria-labelledby="proj-h">
    <h1 id="proj-h">Everything we've built.</h1>
    <p class="lede">My own builds, the BYU AI Foundry's work, Spark AI at Siemens, and the products I build with my dad, John Davenport. Every card links to the real thing.</p>
    <p class="count-line" id="total">{n} projects</p>
  </section>
  <section class="wrap tops" aria-labelledby="top-h">
    <h2 id="top-h">Start with these</h2>
    <p class="lede">Our top ten, picked so a stranger can click every one.</p>
    <ol class="toplist">
{chr(10).join(top_card(k, i) for k, i in enumerate(tops, 1))}
    </ol>
  </section>
  <section class="wrap lib listing" aria-labelledby="lib-h">
    <h2 id="lib-h">The library</h2>
    <div class="controls" id="controls" hidden>
      <div class="search" role="search">
        <label for="q">Search projects</label>
        <input id="q" type="search" autocomplete="off" spellcheck="false" placeholder="Try “evals”, “SpeedPrep” or “Siemens”" aria-describedby="count">
      </div>
      <fieldset class="chips"><legend>Who built it</legend>{owner_chips}</fieldset>
      <fieldset class="chips"><legend>Kind</legend>{cat_chips}</fieldset>
      <fieldset class="chips"><legend>Status</legend>{status_chips}</fieldset>
      <div class="sort"><label for="sort">Sort</label>
        <select id="sort"><option value="featured">Featured first</option><option value="az">A to Z</option></select>
      </div>
    </div>
    <p class="count" id="count" role="status" aria-live="polite">Showing all {n} projects</p>
    <ul class="cards">
{main_cards}
    </ul>
    <section class="dad" id="john-davenport" aria-labelledby="dad-h">
      <h2 id="dad-h">Built with my dad, John Davenport</h2>
      <p class="lede">Co-built with my dad, John Davenport, a career engineer. He owns the product and the code; I work on go-to-market and build alongside him.</p>
      <ul class="cards">
{dad_cards}
      </ul>
    </section>
    <div class="empty" id="empty" hidden>
      <p>Nothing matches that search. Try a broader word, or clear the filters.</p>
      <button type="button" class="reset" id="reset">Clear search and filters</button>
    </div>
  </section>
</main>
"""
    page += bw.FOOTER + SCRIPT + "</body>\n</html>\n"
    return page


def build():
    items = load()
    page = build_page(items)
    with open(os.path.join(ROOT, "projects.html"), "w", encoding="utf-8") as f:
        f.write(page)
    served = [{k: i[k] for k in SERVED_FIELDS} for i in items]
    with open(os.path.join(ROOT, "projects.json"), "w", encoding="utf-8") as f:
        json.dump({"count": len(served), "projects": served}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    dad = sum(1 for i in items if i["owner"] == DAD)
    imgs = sum(1 for i in items if i["image"])
    print(f"wrote projects.html and projects.json: {len(items)} projects ({dad} with John Davenport, "
          f"{imgs} with screenshots); top row {len(TOP10)} of 10")
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refresh", action="store_true", help="re-vendor catalog.json, denylist.json and screenshots")
    ap.add_argument("--catalog")
    ap.add_argument("--decisions")
    ap.add_argument("--shots")
    a = ap.parse_args()
    if a.refresh:
        if not (a.catalog and a.decisions):
            ap.error("--refresh needs --catalog and --decisions")
        refresh(a.catalog, a.decisions, a.shots)
    build()


if __name__ == "__main__":
    main()
