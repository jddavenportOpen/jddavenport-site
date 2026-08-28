#!/usr/bin/env python3.12
"""Render tools/og-card.html to images/og-image.png at exactly 1200x630.

Usage:
    python3.12 tools/render-og.py

Why this exists: the previous og-image was a hand-made file from a previous
generation of the design (green accent, an old title, an orphaned agent count).
Nobody noticed for months, because the card is the one surface you never look
at while working on the site: it is what other people see when the link is
pasted into a Slack channel. Keeping the card as source that renders from the
same tokens as the site means it can be regenerated in one command instead of
redrawn, so it cannot silently fall a generation behind again.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "tools" / "og-card.html"
OUTPUT = ROOT / "images" / "og-image.png"
WIDTH, HEIGHT = 1200, 630


def main() -> int:
    if not SOURCE.exists():
        print(f"missing source: {SOURCE}", file=sys.stderr)
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=1,
        )
        page.goto(SOURCE.as_uri(), wait_until="networkidle")
        # Geist comes from Google Fonts; without this the card renders in the
        # system fallback and looks like a different brand.
        page.wait_for_function("document.fonts.ready.then(() => true)")
        page.wait_for_timeout(400)
        page.screenshot(
            path=str(OUTPUT),
            clip={"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT},
        )
        browser.close()

    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes, {WIDTH}x{HEIGHT})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
