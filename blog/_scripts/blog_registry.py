"""Blog categories and article registry."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "adu" / "_scripts"))

from adu_cluster import ARTICLES as ADU_CLUSTER  # noqa: E402

CATEGORIES: dict[str, dict[str, str]] = {
    "adu": {
        "name": "ADU",
        "description": (
            "Guides about Accessory Dwelling Units — types, costs, regulations, and planning "
            "for homeowners in Massachusetts and Greater Boston."
        ),
    },
}

# Display order on /blog/ (newest or most specific first).
ADU_DISPLAY_ORDER = [
    "how-to-choose-an-adu-builder-in-massachusetts",
    "can-you-build-an-adu-on-your-massachusetts-property",
    "how-to-finance-an-adu-in-massachusetts",
    "adu-permits-and-requirements-in-massachusetts",
    "how-much-does-an-adu-cost",
    "what-is-an-accessory-dwelling-unit-adu",
]

ARTICLES: list[dict[str, str]] = [
    {
        "slug": slug,
        "category": "adu",
        "title": ADU_CLUSTER[slug]["title"],
        "excerpt": ADU_CLUSTER[slug]["excerpt"],
        "path": f"/adu/{slug}/",
    }
    for slug in ADU_DISPLAY_ORDER
    if slug in ADU_CLUSTER
]


def build_filters_html() -> str:
    buttons = [
        '<button type="button" class="jrh-blog-filter is-active" data-category="all">All</button>'
    ]
    for slug, meta in CATEGORIES.items():
        buttons.append(
            f'<button type="button" class="jrh-blog-filter" data-category="{slug}">{meta["name"]}</button>'
        )
    return (
        '<nav class="jrh-blog-filters" aria-label="Blog categories">\n'
        + "\n".join(f"\t\t\t\t\t\t{btn}" for btn in buttons)
        + "\n\t\t\t\t\t</nav>"
    )


def build_listing_html() -> str:
    items = []
    for article in ARTICLES:
        category = article["category"]
        name = CATEGORIES[category]["name"]
        href = ".." + article["path"]
        items.append(
            f'''\t\t\t\t\t\t<article class="jrh-blog-card" data-category="{category}">
\t\t\t\t\t\t\t<div class="jrh-blog-card-inner">
\t\t\t\t\t\t\t\t<span class="jrh-blog-card-category">{name}</span>
\t\t\t\t\t\t\t\t<h2 class="jrh-blog-card-title"><a href="{href}">{article["title"]}</a></h2>
\t\t\t\t\t\t\t\t<p class="jrh-blog-card-excerpt">{article["excerpt"]}</p>
\t\t\t\t\t\t\t\t<a class="jrh-blog-card-link" href="{href}">Read article</a>
\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t</article>'''
        )
    cards = "\n\n".join(items)
    return (
        f"""\t\t\t\t\t<div class="jrh-blog-list">
{build_filters_html()}
\t\t\t\t\t\t<div class="jrh-blog-grid">
{cards}
\t\t\t\t\t\t</div>
\t\t\t\t\t</div>"""
    )
