#!/usr/bin/env python3
"""python3 tools/metrics/test_refresh_snapshot.py  (standard library only, no network)"""
import copy
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import refresh_snapshot as rs

REPO = Path(__file__).resolve().parents[2]
FEED = {
    "as_of": "2099-01-02",
    "stats": {"agents": 51, "skills": 60, "automations": 300, "domains": 9, "ships_last_30d": 1234},
    "metrics": {
        "turns_yesterday": 7777,
        "usd_equivalent_yesterday": 999.5,
        "tokens_yesterday": {"total": 5},
        "tokens_30d_sparkline": [{"d": "2099-01-01", "total": 10}, {"d": "2099-01-02", "total": 20}],
    },
    "structure": {
        "agents_by_kind": {"orchestrator": 1, "domain": 14, "python-package": 30, "skill-backed": 2, "unclassified": 4},
        "skills_by_scope": {"system": 50, "global": 10},
        "jobs_by_category": {"self-heal / watchdog": 70, "other": 230},
        "ships_per_day": [1, 2, 3],
    },
}


class Refresh(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        for name in ("brain.html", "showcase.html"):
            shutil.copy(REPO / name, self.dir / name)

    def pages(self):
        return (self.dir / "brain.html").read_text("utf-8"), (self.dir / "showcase.html").read_text("utf-8")

    def test_rewrites_every_block_in_both_pages(self):
        rs.refresh(FEED, self.dir)
        brain, showcase = self.pages()
        for page in (brain, showcase):
            self.assertIn("Snapshot · 2099-01-02</span>", page)
            self.assertIn("the snapshot from 2099-01-02", page)
        self.assertIn('<b data-k="spec">36</b>', brain)  # python-package + skill-backed + unclassified
        self.assertIn('<b data-k="jobs">300</b>', brain)
        self.assertIn('<b data-k="turns">7,777</b>', brain)
        self.assertIn('<span>Self-healing watchdogs</span><b>70</b>', brain)
        snap = json.loads(re.search(r"^ var SNAP=(.*);$", brain, re.M).group(1))
        self.assertEqual(snap["as_of"], "2099-01-02")
        self.assertIn('<b data-k="watchdogs">70</b>', showcase)
        # Counting rule: showcase states 30+ / 100+ in copy, never a live agent count.
        self.assertNotIn('data-k="agents"', showcase)
        self.assertIn("30+ agents in daily production", showcase)
        self.assertIn('live={"agents": 51, "automations": 300, "watchdogs": 70, "ships": 1234};', showcase)
        self.assertEqual(re.search(r'id="spark"[^>]*>(.*?)</svg>', showcase, re.S).group(1).count("<rect"), 3)

    def test_no_dollar_field_survives(self):
        rs.refresh(FEED, self.dir)
        for page in self.pages():
            self.assertNotIn("usd", page.lower())
            self.assertNotRegex(page, r"\$\s?\d")
        self.assertNotIn("tokens_yesterday", json.dumps(rs.snapshot(FEED)))

    def test_rerun_is_a_no_op(self):
        rs.refresh(FEED, self.dir)
        first = self.pages()
        self.assertIn("already current", rs.refresh(FEED, self.dir))
        self.assertEqual(first, self.pages())

    def assert_kept(self, feed):
        before = self.pages()
        with self.assertRaises(rs.Keep):
            rs.refresh(feed, self.dir)
        self.assertEqual(before, self.pages())

    def test_missing_or_bad_fields_keep_the_old_snapshot(self):
        for mutate in (
            lambda f: f.pop("as_of"),
            lambda f: f["stats"].pop("agents"),
            lambda f: f["metrics"].pop("turns_yesterday"),
            lambda f: f["structure"].pop("agents_by_kind"),
            lambda f: f["structure"]["jobs_by_category"].pop("self-heal / watchdog"),
            lambda f: f["stats"].update(agents=0),
            lambda f: f["stats"].update(agents="48"),
            lambda f: f.update(as_of="2001-01-01"),
        ):
            feed = copy.deepcopy(FEED)
            mutate(feed)
            self.assert_kept(feed)

    def test_a_page_missing_a_block_changes_neither_page(self):
        p = self.dir / "showcase.html"
        p.write_text(p.read_text("utf-8").replace('id="chip-text"', 'id="other"'), "utf-8")
        self.assert_kept(FEED)

    def test_counting_rule_refuses_a_precise_count_in_prose(self):
        p = self.dir / "brain.html"
        p.write_text(p.read_text("utf-8").replace("<h1>The live brain</h1>", "<h1>48 agents</h1>"), "utf-8")
        self.assert_kept(FEED)
        p.write_text(p.read_text("utf-8").replace("<h1>48 agents</h1>", "<h1>30+ agents</h1>"), "utf-8")
        rs.refresh(FEED, self.dir)

    def test_a_dollar_figure_in_a_page_refuses(self):
        p = self.dir / "showcase.html"
        p.write_text(p.read_text("utf-8").replace("<h2>Open source", "<h2>$5 Open source"), "utf-8")
        self.assert_kept(FEED)

    def test_failed_fetch_exits_zero_and_writes_nothing(self):
        import os
        os.environ["SNAPSHOT_METRICS_URL"] = "file:///nonexistent/metrics.json"
        self.addCleanup(os.environ.pop, "SNAPSHOT_METRICS_URL")
        import sys
        argv, sys.argv = sys.argv, ["refresh_snapshot.py", "--dry-run"]
        self.addCleanup(setattr, sys, "argv", argv)
        self.assertEqual(rs.main(), 0)


if __name__ == "__main__":
    unittest.main()
