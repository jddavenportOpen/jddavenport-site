#!/usr/bin/env python3
"""Guard for /projects. Stdlib only. Run one file per process:

    python3 tools/projects/test_build_projects.py            # full, includes live link checks
    PROJECTS_SKIP_NET=1 python3 tools/projects/test_build_projects.py   # offline checks only

Rebuilds projects.html + projects.json first, then fails if any of these reach the output
(the phrase, editorial, slug and dash checks also run over the vendored tools/projects/*.json,
because tools/ ships to the public GitHub repo even though .vercelignore keeps it off the site):
  - a slug the audit excluded or marked private (checked by sha256, see denylist.json)
  - a forbidden phrase from PLAN.md (unconfirmed numbers, NDA and sponsor terms), checked
    by sha256 against forbidden.json so this public repo never prints them; only generic
    patterns (internal host, Slack archive links, local paths) stay in plain text
  - an audit-lane editorial note ("newsletter material", "candidate for", ...)
  - a link to github.com/JDDavenport (404 to every logged-out visitor)
  - an em or en dash
  - an email address in the project data or the page body (the site footer's contact
    address sits outside <main> and is allowed)
  - a link that does not answer 200 to an anonymous request (redirects count as failures,
    except a bare trailing-slash or http-to-https hop, because a redirect is how a retired
    page kept answering 200 in the audit)
"""
import glob
import hashlib
import html as htmllib
import json
import os
import re
import subprocess
import sys
import unittest
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

FORBIDDEN = ["cockpit.jddavenport.com", "slack.com/archives", "/Users/"]  # generic patterns only
EDITORIAL_RE = re.compile(r"newsletter material|candidate for|MBA audience|MBA-facing|thread of the newsletter"
                          r"|per the public page|registry (?:status|lists)", re.I)
WORD_RE = re.compile(r"[a-z0-9$][a-z0-9$,.'/_-]*")
GH_PRIVATE_RE = re.compile(r"github\.com/jddavenport(?!open)", re.I)
DASH_RE = re.compile("[–—]")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+")
TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def phrase_hits(text, hashes):
    """Every 1- to 4-word window of the normalized text (plus URL pieces and $-less forms)."""
    t = htmllib.unescape(text).lower().replace("\u2019", "'")
    words = [w.rstrip(".,'/_-") for w in WORD_RE.findall(t)]
    words = [w for w in words if w]
    hits = set()
    for i, w in enumerate(words):
        variants = {w, *w.split("/")}
        variants |= {"/".join(w.split("/")[:k]) for k in range(2, w.count("/") + 2)}
        for v in variants:
            for x in (v, v.lstrip("$")):
                if x and sha(x) in hashes:
                    hits.add(x)
        for n in range(2, 5):
            if i + n <= len(words):
                p = " ".join(words[i:i + n])
                if sha(p) in hashes:
                    hits.add(p)
    return hits


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def status(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with OPENER.open(req, timeout=25) as r:
            return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location")
    except Exception as e:  # noqa: BLE001  network failure is a failure, never a pass
        return 0, str(e)


def benign_redirect(url, loc):
    if not loc:
        return False
    a, b = urlparse(url), urlparse(loc if "://" in loc else f"{urlparse(url).scheme}://{urlparse(url).netloc}{loc}")
    return (a.netloc == b.netloc and a.path.rstrip("/") == b.path.rstrip("/")) or \
        (a.scheme == "http" and b.scheme == "https" and a.netloc == b.netloc)


class BuildOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, os.path.join(HERE, "build_projects.py")], check=True, cwd=ROOT,
                       stdout=subprocess.DEVNULL)
        with open(os.path.join(ROOT, "projects.html"), encoding="utf-8") as f:
            cls.html = f.read()
        with open(os.path.join(ROOT, "projects.json"), encoding="utf-8") as f:
            cls.raw = f.read()
        cls.data = json.loads(cls.raw)
        with open(os.path.join(HERE, "denylist.json"), encoding="utf-8") as f:
            cls.deny = set(json.load(f)["sha256"])
        with open(os.path.join(HERE, "forbidden.json"), encoding="utf-8") as f:
            cls.forbidden = set(json.load(f)["sha256"])
        cls.vendored = {}
        for p in sorted(glob.glob(os.path.join(HERE, "*.json"))):
            if os.path.basename(p) in ("denylist.json", "forbidden.json"):
                continue
            with open(p, encoding="utf-8") as f:
                cls.vendored["tools/projects/" + os.path.basename(p)] = f.read()
        m = re.search(r"<main\b.*?</main>", cls.html, re.S)
        cls.main = m.group(0) if m else ""

    def test_has_projects_and_count_is_computed(self):
        n = self.data["count"]
        self.assertGreater(n, 20)
        self.assertEqual(n, len(self.data["projects"]))
        self.assertIn(f'id="total">{n} projects<', self.html)
        self.assertEqual(self.main.count('class="card"'), n)

    def outputs(self):
        return [(self.html, "projects.html"), (self.raw, "projects.json"), *[(t, w) for w, t in self.vendored.items()]]

    def test_vendored_inputs_are_scanned(self):
        self.assertIn("tools/projects/catalog.json", self.vendored)
        self.assertIn("tools/projects/overrides.json", self.vendored)

    def test_phrase_guard_catches_planted_text(self):
        planted = {sha("zebrafin"), sha("7 purple"), sha("90q"), sha("example.org/secret")}
        hits = phrase_hits("We use Zebrafin. 7 purple hats, $90Q/yr, https://example.org/secret/x", planted)
        self.assertEqual(hits, {"zebrafin", "7 purple", "90q", "example.org/secret"})
        self.assertTrue(self.forbidden, "forbidden.json is empty")

    def test_no_excluded_or_private_slug(self):
        for p in self.data["projects"]:
            self.assertNotIn(hashlib.sha256(p["slug"].encode()).hexdigest(), self.deny, p["slug"])
        for text, _ in self.outputs():
            hits = {t for t in TOKEN_RE.findall(text.lower()) if hashlib.sha256(t.encode()).hexdigest() in self.deny}
            self.assertFalse(hits, f"excluded slug text in output: {sorted(hits)}")

    def test_no_forbidden_strings(self):
        for text, where in self.outputs():
            for s in FORBIDDEN:
                self.assertNotIn(s, text, f"{s!r} in {where}")
            self.assertEqual(phrase_hits(text, self.forbidden), set(), f"forbidden phrase in {where}")
            self.assertIsNone(EDITORIAL_RE.search(text), f"editorial note in {where}: "
                              f"{EDITORIAL_RE.search(text) and EDITORIAL_RE.search(text).group(0)!r}")
        for text, where in ((self.html, "projects.html"), (self.raw, "projects.json")):
            self.assertIsNone(GH_PRIVATE_RE.search(text), f"github.com/JDDavenport link in {where}")

    def test_no_dashes(self):
        for text, where in self.outputs():
            self.assertIsNone(DASH_RE.search(text), f"em or en dash in {where}")

    def test_no_email_addresses(self):
        self.assertEqual(EMAIL_RE.findall(self.raw), [])
        self.assertEqual(EMAIL_RE.findall(self.main), [])

    def test_only_served_fields(self):
        allowed = {"slug", "title", "owner", "track", "category", "status", "one_liner", "details",
                   "tech", "links", "thumb", "image"}
        for p in self.data["projects"]:
            self.assertEqual(set(p), allowed, p["slug"])

    def test_images_exist(self):
        for p in self.data["projects"]:
            for k in ("thumb", "image"):
                if p[k]:
                    path = os.path.join(ROOT, p[k].lstrip("/"))
                    self.assertTrue(os.path.exists(path), path)
                    self.assertLess(os.path.getsize(path), 150_000, path)

    def test_client_section_and_top_row(self):
        self.assertIn('id="client-work"', self.html)
        self.assertIn(">Client work<", self.html)
        self.assertEqual(self.html.count('class="pick"'), 10)
        self.assertNotIn("client says yes", self.html)

    def test_no_family_or_who_did_what(self):
        # JD 2026-11-10: client projects are paid consulting work; never name a family member
        # and never split credit ("he owns the code", "JD's part is").
        who = re.compile(r"\b(dad|dad's|father|john davenport|john-davenport|co-buil\w*)\b"
                         r"|he owns the|jd's part|jd's agents|built it with claude", re.I)
        for where, text in (("projects.html", self.html), ("projects.json", self.raw)):
            self.assertEqual(who.findall(text), [], f"family or credit-split copy in {where}")

    @unittest.skipIf(os.environ.get("PROJECTS_SKIP_NET") == "1", "PROJECTS_SKIP_NET=1")
    def test_every_link_answers_200(self):
        urls = sorted({l["url"] for p in self.data["projects"] for l in p["links"]})
        with ThreadPoolExecutor(max_workers=6) as ex:
            results = list(ex.map(status, urls))
        bad = []
        for u, (code, loc) in zip(urls, results):
            if code == 200:
                continue
            if code in (301, 302, 307, 308) and benign_redirect(u, loc):
                continue
            bad.append(f"{code} {u}" + (f" -> {loc}" if loc else ""))
        self.assertEqual(bad, [], "links that do not answer 200:\n  " + "\n  ".join(bad))


if __name__ == "__main__":
    unittest.main(verbosity=2)
