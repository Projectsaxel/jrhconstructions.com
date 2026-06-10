#!/usr/bin/env python3
"""Generate sitemap-blog.xml from blog_registry and update sitemap_index.xml."""
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "blog" / "_scripts"))

from blog_registry import ARTICLES  # noqa: E402

SITE = "https://jrhconstructions.com"
LASTMOD = date.today().isoformat()


def url_entry(loc: str, *, priority: str, changefreq: str) -> str:
    return f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{LASTMOD}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>"""


def generate_blog_sitemap() -> str:
    entries = [
        url_entry(f"{SITE}/blog/", priority="0.8", changefreq="weekly"),
    ]
    for article in ARTICLES:
        entries.append(
            url_entry(
                f"{SITE}{article['path']}",
                priority="0.7",
                changefreq="monthly",
            )
        )
    body = "\n".join(entries)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n"
    )


def update_sitemap_index() -> None:
    index_path = ROOT / "sitemap_index.xml"
    html = index_path.read_text(encoding="utf-8")

    blog_block = f"""  <sitemap>
    <loc>{SITE}/sitemap-blog.xml</loc>
    <lastmod>{LASTMOD}</lastmod>
  </sitemap>"""

    if "sitemap-blog.xml" not in html:
        html = html.replace("</sitemapindex>", blog_block + "\n</sitemapindex>")
    else:
        html = re.sub(
            r"<loc>https://jrhconstructions\.com/sitemap-blog\.xml</loc>\s*<lastmod>[^<]*</lastmod>",
            f"<loc>{SITE}/sitemap-blog.xml</loc>\n    <lastmod>{LASTMOD}</lastmod>",
            html,
            count=1,
        )

    html = re.sub(
        r"(<loc>https://jrhconstructions\.com/sitemap-pages\.xml</loc>\s*<lastmod>)[^<]*(</lastmod>)",
        rf"\g<1>{LASTMOD}\g<2>",
        html,
        count=1,
    )
    index_path.write_text(html, encoding="utf-8")


def main() -> None:
    out = ROOT / "sitemap-blog.xml"
    out.write_text(generate_blog_sitemap(), encoding="utf-8")
    update_sitemap_index()
    print(f"Wrote {out}")
    print(f"Updated {ROOT / 'sitemap_index.xml'}")


if __name__ == "__main__":
    main()
