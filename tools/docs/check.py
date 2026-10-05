#!/usr/bin/env python3
"""Gate for jddavenport.com/docs. Python 3 standard library only.

    python3 tools/docs/check.py                  # fail on any problem
    python3 tools/docs/check.py --allow-planned  # links to PLAN.json articles not yet written are warnings

Checks the Markdown sources (tools/docs/content, sections.json) and the
generated tree (docs/):

  - no em dash or en dash, no emoji, in any source or generated file
  - no "/Users/" path anywhere
  - every article has title + description (and the rest of the front matter contract)
  - no MDX / JSX / HTML remnants in Markdown prose
  - every internal /docs/ link resolves (in sources: to an article or section;
    in generated HTML: to a file that exists under docs/)
  - the generated tree is current: one page per source article
  - no unconverted Markdown in generated HTML (literal ](...) or ** outside code)

Exit 0 when clean, 1 when anything fails. Prints a summary either way.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402  (same directory; reuses the front matter parser and paths)

ROOT = build.ROOT
OUT = build.OUT
CONTENT = build.DEFAULT_CONTENT
SECTIONS = build.DEFAULT_SECTIONS
PLAN = HERE / "PLAN.json"

DASH_RE = re.compile("[–—]")
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U0001F1E6-\U0001F1FF☀-➿⬀-⯿️⌚⌛⏩-⏳⏸-⏺‍⃣]")
USERS_RE = re.compile(r"/Users/")
MDX_PATTERNS = [
    (re.compile(r"^\s*import\s+[\w{*]"), "import line"),
    (re.compile(r"^\s*export\s+(const|default|function|let)\b"), "export line"),
    (re.compile(r"</?[A-Za-z][\w.-]*(\s[^<>]*)?/?>"), "HTML/JSX tag"),
    (re.compile(r"\{/\*|\*/\}"), "JSX comment"),
    (re.compile(r"^\s*:::"), "admonition fence (:::)"),
    (re.compile(r"\bclassName="), "className="),
    (re.compile(r"^\s*<!--"), "HTML comment"),
]


class Report:
    def __init__(self):
        self.fail: list[str] = []
        self.warn: list[str] = []

    def f(self, where, msg):
        self.fail.append(f"{where}: {msg}")

    def w(self, where, msg):
        self.warn.append(f"{where}: {msg}")


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def scan_text(path: Path, text: str, r: Report):
    for n, line in enumerate(text.split("\n"), 1):
        if DASH_RE.search(line):
            r.f(f"{rel(path)}:{n}", "em/en dash: " + line.strip()[:90])
        if EMOJI_RE.search(line):
            ch = EMOJI_RE.search(line).group(0)
            r.f(f"{rel(path)}:{n}", f"emoji U+{ord(ch):04X}: " + line.strip()[:90])
        if USERS_RE.search(line):
            r.f(f"{rel(path)}:{n}", "local /Users/ path")


def prose_lines(body: str):
    """Yield (line_no_offset, text) for Markdown body lines outside code fences, inline code removed."""
    in_fence, fence = False, ""
    for n, line in enumerate(body.split("\n"), 1):
        m = re.match(r"^\s*(`{3,}|~{3,})", line)
        if m:
            if not in_fence:
                in_fence, fence = True, m.group(1)[0] * len(m.group(1))
            elif line.strip().startswith(fence):
                in_fence = False
            continue
        if in_fence:
            continue
        yield n, re.sub(r"(`+).+?\1", "", line)


def check_sources(r: Report, plan_urls: set[str], allow_planned: bool):
    sections = json.loads(SECTIONS.read_text())
    sec_ids = {s["id"] for s in sections}
    scan_text(SECTIONS, SECTIONS.read_text(), r)
    articles: dict[str, Path] = {}
    files = sorted(CONTENT.glob("**/*.md"))
    for p in files:
        if len(p.relative_to(CONTENT).parts) == 2:
            articles[f"/docs/{p.parent.name}/{p.stem}/"] = p
    valid = set(articles) | {f"/docs/{s}/" for s in sec_ids} | {"/docs/"}
    for p in files:
        text = p.read_text(encoding="utf-8")
        scan_text(p, text, r)
        where = rel(p)
        if len(p.relative_to(CONTENT).parts) != 2:
            r.f(where, "must live at content/<section>/<slug>.md")
            continue
        try:
            meta, body = build.parse_front_matter(text)
        except build.SourceError as e:
            r.f(where, str(e))
            continue
        fm_lines = text.split("\n---", 1)[0].count("\n") + 2
        for k in ("title", "description"):
            if not str(meta.get(k) or "").strip():
                r.f(where, f"missing {k}")
        for k in ("section", "order", "updated"):
            if meta.get(k) in (None, ""):
                r.f(where, f"missing {k}")
        extra = set(meta) - build.ALLOWED_KEYS
        if extra:
            r.f(where, f"unknown front matter keys {sorted(extra)}")
        if meta.get("section") != p.parent.name:
            r.f(where, f"section {meta.get('section')!r} does not match folder {p.parent.name!r}")
        if p.parent.name not in sec_ids:
            r.f(where, f"folder {p.parent.name!r} is not a section in sections.json")
        if not build.SLUG_RE.match(p.stem):
            r.f(where, "slug is not lowercase-kebab")
        if not isinstance(meta.get("order"), int):
            r.f(where, "order is not an integer")
        d = str(meta.get("description") or "")
        if len(d) >= 160:
            r.f(where, f"description is {len(d)} chars (must be under 160)")
        if not build.DATE_RE.match(str(meta.get("updated", ""))):
            r.f(where, "updated is not YYYY-MM-DD")
        for n, line in prose_lines(body):
            ln = n + fm_lines
            for pat, label in MDX_PATTERNS:
                if pat.search(line):
                    r.f(f"{where}:{ln}", f"{label}: {line.strip()[:90]}")
            if re.match(r"^#\s", line):
                r.f(f"{where}:{ln}", "'#' heading in body (the title is the h1; use ##)")
            for m in re.finditer(r"\]\((/[^)\s]*)\)", line):
                url = m.group(1).split("#", 1)[0]
                if not url.startswith("/docs"):
                    r.f(f"{where}:{ln}", f"site-relative link outside /docs/: {url} (use a full https URL)")
                    continue
                if not url.endswith("/"):
                    r.f(f"{where}:{ln}", f"internal link must end with '/': {url}")
                    url += "/"
                if url in valid:
                    continue
                if url in plan_urls and allow_planned:
                    r.w(f"{where}:{ln}", f"links planned article not written yet: {url}")
                else:
                    r.f(f"{where}:{ln}", f"internal link does not resolve: {url}")
            if re.search(r"\]\((?!https?://|/|#|mailto:)[^)]+\)", line):
                r.f(f"{where}:{ln}", "relative link (use /docs/... or a full https URL)")
            if re.search(r"\]\(http://", line):
                r.w(f"{where}:{ln}", "http:// link (prefer https)")
    return articles


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[int, str]] = []
        self.ids: set[str] = set()
        self.text_outside_code: list[tuple[int, str]] = []
        self._code = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("code", "pre", "script", "style"):
            self._code += 1
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k):
                self.links.append((self.getpos()[0], a[k]))

    def handle_endtag(self, tag):
        if tag in ("code", "pre", "script", "style") and self._code:
            self._code -= 1

    def handle_data(self, data):
        if not self._code and data.strip():
            self.text_outside_code.append((self.getpos()[0], data))


def resolve_docs_url(url: str) -> bool:
    path = url.split("#", 1)[0].split("?", 1)[0]
    if not path.startswith("/docs"):
        return True
    target = ROOT / path.lstrip("/")
    if path.endswith("/"):
        return (target / "index.html").is_file()
    return target.is_file() or (target / "index.html").is_file()


def check_generated(r: Report, articles: dict[str, Path], plan_urls: set[str], allow_planned: bool):
    if not OUT.is_dir():
        r.f("docs/", "generated tree missing: run python3 tools/docs/build.py")
        return 0
    pages = 0
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix not in (".html", ".css", ".js", ".json"):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        scan_text(p, text, r)
        if p.suffix != ".html":
            continue
        pages += 1
        lp = LinkParser()
        lp.feed(text)
        for ln, href in lp.links:
            if href.startswith("/docs") and not resolve_docs_url(href):
                if allow_planned and href.split("#", 1)[0] in plan_urls:
                    r.w(f"{rel(p)}:{ln}", f"links planned article not written yet: {href}")
                else:
                    r.f(f"{rel(p)}:{ln}", f"internal link does not resolve: {href}")
            if href.startswith("#") and len(href) > 1 and href[1:] not in lp.ids:
                r.f(f"{rel(p)}:{ln}", f"in-page anchor has no target: {href}")
        for ln, data in lp.text_outside_code:
            if re.search(r"\]\(\S+\)", data):
                r.f(f"{rel(p)}:{ln}", f"unconverted Markdown link: {data.strip()[:80]}")
            if "**" in data:
                r.w(f"{rel(p)}:{ln}", f"literal ** in text: {data.strip()[:80]}")
            if re.search(r"(^|\s)#{2,3}\s", data):
                r.w(f"{rel(p)}:{ln}", f"literal heading marker in text: {data.strip()[:80]}")
        if build.GENERATED_MARK in text:
            for tag in ("<title>", 'name="description"', 'rel="canonical"', 'property="og:title"'):
                if tag not in text:
                    r.f(rel(p), f"missing {tag}")
    for url, src in articles.items():
        page = ROOT / url.lstrip("/") / "index.html"
        if not page.is_file():
            r.f(rel(src), f"no generated page at {url} (run build.py, or fix the source error it reports)")
    for page in OUT.glob("*/*/index.html"):
        url = "/" + str(page.parent.relative_to(ROOT)) + "/"
        if url not in articles:
            r.f(rel(page), "generated page has no source article (run build.py to prune it)")
    return pages


def check_sitemap(r: Report, articles: dict[str, Path]):
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    for url in articles:
        if build.SITE + url not in locs:
            r.f("sitemap.xml", f"missing {url}")
    if build.SITE + "/docs/" not in locs:
        r.f("sitemap.xml", "missing /docs/")


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for jddavenport.com/docs")
    ap.add_argument("--allow-planned", action="store_true",
                    help="links to PLAN.json articles that are not written yet warn instead of fail")
    ap.add_argument("--quiet-warnings", action="store_true")
    args = ap.parse_args()
    r = Report()
    plan_urls = set()
    if PLAN.exists():
        plan_urls = {f"/docs/{a['id']}/" for a in json.loads(PLAN.read_text())["articles"]}
    articles = check_sources(r, plan_urls, args.allow_planned)
    pages = check_generated(r, articles, plan_urls, args.allow_planned)
    check_sitemap(r, articles)

    if r.warn and not args.quiet_warnings:
        print(f"Warnings ({len(r.warn)}):")
        for w in r.warn:
            print(f"  WARN  {w}")
    if r.fail:
        print(f"Failures ({len(r.fail)}):")
        for f in r.fail:
            print(f"  FAIL  {f}")
    print(f"check: {len(articles)} source articles · {pages} generated pages · "
          f"{len(r.fail)} failures · {len(r.warn)} warnings · {'FAIL' if r.fail else 'PASS'}")
    return 1 if r.fail else 0


if __name__ == "__main__":
    sys.exit(main())
