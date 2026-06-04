#!/usr/bin/env python3
"""Generate ADU cost satellite post and update ADU category index."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADU = ROOT / "adu"
SCRIPTS = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS))

from adu_cluster import (  # noqa: E402
    PILLAR_SLUG,
    apply_contextual_links,
    build_cluster_intro,
    build_read_also,
    strip_read_also,
)
SLUG = "how-much-does-an-adu-cost"
POST_DIR = ADU / SLUG
TEMPLATE = ADU / PILLAR_SLUG / "index.html"
CONTENT_FILE = SCRIPTS / "adu-cost-content.html"
POST_TITLE = "How Much Does an ADU Cost? Complete Pricing Guide for Homeowners"
POST_EXCERPT = (
    "Discover how much it costs to build an Accessory Dwelling Unit, what factors influence the price, "
    "and how to estimate the investment required for your project."
)
CANONICAL = f"https://jrhconstructions.com/adu/{SLUG}/"
PILLAR_CANONICAL = f"https://jrhconstructions.com/adu/{PILLAR_SLUG}/"
OG_IMAGE = "https://jrhconstructions.com/services/images/accessory-dwelling-unit-service-scaled.webp"
PUBLISHED = "2026-06-04"
PILLAR_TITLE = "What Is an Accessory Dwelling Unit (ADU)? The Complete Homeowner's Guide"
PILLAR_EXCERPT = (
    "Learn what an Accessory Dwelling Unit is, the different types available, "
    "the benefits of building one, and why ADUs have become one of the most popular "
    "ways to increase living space and property value in the United States."
)


def build_post_page(article_html: str) -> str:
    html = TEMPLATE.read_text(encoding="utf-8")

    html = re.sub(
        r"<title>.*?</title>",
        f"<title>{POST_TITLE} | JRH Constructions ADU</title>",
        html,
        count=1,
    )
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{POST_EXCERPT}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta name="keywords" content="[^"]*">',
        '<meta name="keywords" content="ADU cost, how much does an ADU cost, ADU pricing, Massachusetts ADU cost, garage conversion ADU cost, detached ADU cost, JRH Constructions">',
        html,
        count=1,
    )
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{CANONICAL}">', html, count=1)
    html = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{POST_TITLE}">', html, count=1)
    html = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{POST_EXCERPT}">',
        html,
        count=1,
    )
    html = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{CANONICAL}">', html, count=1)
    html = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{POST_TITLE}">', html, count=1)
    html = re.sub(
        r'<meta name="twitter:description" content="[^"]*">',
        f'<meta name="twitter:description" content="{POST_EXCERPT}">',
        html,
        count=1,
    )

    schema = (
        '{"@context":"https://schema.org","@graph":[{"@type":"BlogPosting","@id":"'
        + CANONICAL
        + '#article","headline":"'
        + POST_TITLE.replace('"', '\\"')
        + '","description":"'
        + POST_EXCERPT.replace('"', '\\"')
        + '","url":"'
        + CANONICAL
        + '","image":"'
        + OG_IMAGE
        + '","datePublished":"'
        + PUBLISHED
        + '","dateModified":"'
        + PUBLISHED
        + '","author":{"@type":"Organization","name":"JRH Constructions"},"publisher":{"@type":"Organization","name":"JRH Constructions","logo":{"@type":"ImageObject","url":"https://jrhconstructions.com/adu/images/logo-jrh-constructions.webp"}},"mainEntityOfPage":{"@type":"WebPage","@id":"'
        + CANONICAL
        + '"},"inLanguage":"en-US","isPartOf":{"@id":"https://jrhconstructions.com/adu/#webpage"},"about":{"@type":"Article","@id":"'
        + PILLAR_CANONICAL
        + '#article","name":"What Is an Accessory Dwelling Unit (ADU)?"}}]}'
    )
    html = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        f'<script type="application/ld+json">{schema}</script>',
        html,
        count=1,
        flags=re.DOTALL,
    )

    html = html.replace(PILLAR_TITLE, POST_TITLE)
    html = html.replace(PILLAR_EXCERPT, POST_EXCERPT)
    html = html.replace(PILLAR_CANONICAL, CANONICAL)

    article_body = strip_read_also(article_html.strip())
    article_body = apply_contextual_links(SLUG, article_body)
    article_body += build_read_also(SLUG)
    article_html = build_cluster_intro(SLUG) + article_body

    html = re.sub(
        r"(<div class=\"jrh-blog-article\">).*?(</div>\s*\n\t\t\t\t</div>\s*\n\t\t\t\t</div>)",
        r"\1\n" + article_html + r"\n\t\t\t\t\t\2",
        html,
        count=1,
        flags=re.DOTALL,
    )

    html = html.replace(
        "Homeowners in Lynn, Massachusetts, and surrounding communities who are considering an Accessory Dwelling Unit should work with experienced contractors familiar with local regulations and construction requirements. Professional guidance can help transform an idea into a valuable long-term investment.",
        'Homeowners in Lynn, Massachusetts, and surrounding communities who are considering an '
        '<a href="../../services/accessory-dwelling-unit-adu-service/">Accessory Dwelling Unit</a> should work with experienced contractors familiar with local regulations and construction requirements. '
        'Professional guidance from <a href="../../contact-us/">JRH Constructions</a> can help transform an idea into a valuable long-term investment.',
        1,
    )

    html = html.replace('<meta name="jrh-blog-contextual-links" content="1">', "")
    return html


def update_blog_index() -> None:
    import subprocess
    import sys

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sync-blog-index.py")],
        check=True,
    )


def link_pillar_to_satellite() -> None:
    pillar_path = ADU / PILLAR_SLUG / "index.html"
    html = pillar_path.read_text(encoding="utf-8")
    old = "<h2>How Much Does an ADU Cost?</h2>"
    new = f'<h2><a href="../{SLUG}/">How Much Does an ADU Cost?</a></h2>'
    if new in html or old not in html:
        return
    html = html.replace(old, new, 1)
    pillar_path.write_text(html, encoding="utf-8")


def main() -> None:
    raw_html = CONTENT_FILE.read_text(encoding="utf-8")
    raw_html = strip_read_also(raw_html)
    CONTENT_FILE.write_text(raw_html, encoding="utf-8")

    article_html = raw_html
    POST_DIR.mkdir(parents=True, exist_ok=True)
    (POST_DIR / "index.html").write_text(build_post_page(article_html), encoding="utf-8")
    update_blog_index()
    link_pillar_to_satellite()

    import subprocess

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "apply-adu-cluster-links.py")],
        check=True,
    )
    print(f"Created {POST_DIR / 'index.html'}")
    print("Updated ADU index, pillar cross-link, and cluster links")


if __name__ == "__main__":
    main()
