#!/usr/bin/env python3
"""Generate ADU financing satellite post and update blog listing."""
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

SLUG = "how-to-finance-an-adu-in-massachusetts"
POST_DIR = ADU / SLUG
TEMPLATE = ADU / PILLAR_SLUG / "index.html"
CONTENT_FILE = SCRIPTS / "adu-financing-content.html"
POST_TITLE = (
    "How to Finance an ADU in Massachusetts: HELOC, Refinance, Construction Loans, and State Programs"
)
POST_EXCERPT = (
    "An ADU in Massachusetts typically costs $150,000 to $400,000. Here are the five real financing "
    "paths homeowners use, what each costs, and which fits your equity, income, and timeline."
)
CANONICAL = f"https://jrhconstructions.com/adu/{SLUG}/"
PILLAR_CANONICAL = f"https://jrhconstructions.com/adu/{PILLAR_SLUG}/"
OG_IMAGE = "https://jrhconstructions.com/services/images/accessory-dwelling-unit-service-scaled.webp"
PUBLISHED = "2026-06-11"
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
        '<meta name="keywords" content="ADU financing Massachusetts, HELOC ADU, MassHousing ADU loan, HomeStyle renovation ADU, FHA 203k ADU, ADU construction loan, JRH Constructions">',
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

    html = html.replace('<meta name="jrh-blog-contextual-links" content="1">', "")
    return html


def main() -> None:
    raw_html = CONTENT_FILE.read_text(encoding="utf-8")
    raw_html = strip_read_also(raw_html)
    CONTENT_FILE.write_text(raw_html, encoding="utf-8")

    POST_DIR.mkdir(parents=True, exist_ok=True)
    (POST_DIR / "index.html").write_text(build_post_page(raw_html), encoding="utf-8")

    subprocess = __import__("subprocess")
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "apply-adu-cluster-links.py")],
        check=True,
    )
    print(f"Created {POST_DIR / 'index.html'}")
    print("Updated cluster links and blog listing")


if __name__ == "__main__":
    main()
