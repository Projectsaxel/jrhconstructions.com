#!/usr/bin/env python3
"""Sync blog index listing from blog_registry."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
sys.path.insert(0, str(BLOG / "_scripts"))

from blog_registry import build_listing_html  # noqa: E402

LISTING_START = '<div class="jrh-blog-list">'
SCRIPT_TAG = '<script src="/blog/blog-filter.js"></script>'


def sync_blog_index() -> None:
    index_path = BLOG / "index.html"
    html = index_path.read_text(encoding="utf-8")

    html = re.sub(
        r'<div class="jrh-blog-list">.*?</div>\s*(?=</div>\s*</div>\s*</div>\s*\n\t\t</div>\s*\n\t\t\t\t\t</div>\s*\n\t\t</section>)',
        build_listing_html() + "\n\t\t\t\t",
        html,
        count=1,
        flags=re.DOTALL,
    )

    if SCRIPT_TAG not in html:
        html = html.replace(
            '<script src="/blog/script.js"></script>',
            '<script src="/blog/script.js"></script>\n' + SCRIPT_TAG,
        )

    index_path.write_text(html, encoding="utf-8")


def redirect_adu_index() -> None:
    adu_index = ROOT / "adu" / "index.html"
    adu_index.write_text(
        """<!DOCTYPE html>
<html lang="en">
<head>
\t<meta charset="utf-8">
\t<meta name="robots" content="noindex, follow">
\t<link rel="canonical" href="https://jrhconstructions.com/blog/?category=adu">
\t<meta http-equiv="refresh" content="0; url=/blog/?category=adu">
\t<script>location.replace("/blog/?category=adu");</script>
\t<title>Redirecting…</title>
</head>
<body><p><a href="/blog/?category=adu">View ADU articles on the blog</a></p></body>
</html>
""",
        encoding="utf-8",
    )


def append_filter_css() -> None:
    css_path = BLOG / "styles.css"
    css = css_path.read_text(encoding="utf-8")
    if ".jrh-blog-filters" in css:
        return
    css += """

.jrh-blog-filters{display:flex;flex-wrap:wrap;gap:.5rem;margin:0 0 1.75rem;padding:0 0 1.25rem;border-bottom:1px solid #eee}
.jrh-blog-filter{font-family:"Sora",Sans-serif;font-size:14px;line-height:1.2;padding:.55rem 1rem;border:1px solid #ddd;border-radius:999px;background:#fff;color:var(--e-global-color-6939b83);cursor:pointer;transition:background .15s ease,border-color .15s ease,color .15s ease}
.jrh-blog-filter:hover{border-color:#bbb}
.jrh-blog-filter.is-active{background:var(--e-global-color-6939b83, #111);border-color:var(--e-global-color-6939b83, #111);color:#fff}
.jrh-blog-list-meta{margin:0 0 .5rem}
.jrh-blog-list-category{display:inline-block;font-family:"Sora",Sans-serif;font-size:12px;font-weight:600;letter-spacing:.02em;text-transform:uppercase;color:#666}
.jrh-blog-list-item[hidden]{display:none}
"""
    css_path.write_text(css, encoding="utf-8")


def main() -> None:
    sync_blog_index()
    redirect_adu_index()
    append_filter_css()

    import subprocess

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate-sitemap-blog.py")],
        check=True,
    )
    print(f"Updated {BLOG / 'index.html'}")
    print("Redirected /adu/ to /blog/?category=adu")


if __name__ == "__main__":
    main()
