#!/usr/bin/env python3
"""Inject shared contact form handler script into pages with Elementor forms."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_TAG = '<script src="/assets/scripts/contact-form.js" defer></script>'


def main() -> None:
    updated = 0
    skipped = 0

    for path in sorted(ROOT.rglob("index.html")):
        if ".git" in path.parts:
            continue

        html = path.read_text(encoding="utf-8")
        if 'class="elementor-form"' not in html:
            continue
        if "/assets/scripts/contact-form.js" in html:
            skipped += 1
            continue

        if "</body>" not in html:
            continue

        html = html.replace("</body>", f"{SCRIPT_TAG}\n</body>", 1)
        path.write_text(html, encoding="utf-8")
        updated += 1
        print(f"updated: {path.relative_to(ROOT)}")

    print(f"Done. Updated {updated} pages, skipped {skipped} already patched.")


if __name__ == "__main__":
    main()
