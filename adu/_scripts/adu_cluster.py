"""ADU topic cluster registry and link helpers."""

from __future__ import annotations

import re

PILLAR_SLUG = "what-is-an-accessory-dwelling-unit-adu"
CATEGORY = "adu"
BLOG_CATEGORY_HREF = f"../../blog/?category={CATEGORY}"

ARTICLES: dict[str, dict[str, str]] = {
    PILLAR_SLUG: {
        "title": "What Is an Accessory Dwelling Unit (ADU)? The Complete Homeowner's Guide",
        "excerpt": (
            "Learn what an Accessory Dwelling Unit is, the different types available, "
            "the benefits of building one, and why ADUs have become one of the most popular "
            "ways to increase living space and property value in the United States."
        ),
        "content_file": "adu-guide-content.html",
        "role": "pillar",
    },
    "how-much-does-an-adu-cost": {
        "title": "How Much Does an ADU Cost? Complete Pricing Guide for Homeowners",
        "excerpt": (
            "Discover how much it costs to build an Accessory Dwelling Unit, what factors influence the price, "
            "and how to estimate the investment required for your project."
        ),
        "content_file": "adu-cost-content.html",
        "role": "satellite",
    },
}

READ_ALSO_MARKER = '<div class="jrh-blog-read-also">'
SERVICE_CTA_MARKER = '<div class="jrh-adu-service-cta">'
SERVICE_PAGE_HREF = "../../services/accessory-dwelling-unit-adu-service/"


def href(slug: str) -> str:
    return f"../{slug}/"


def related_slugs(current: str) -> list[str]:
    if current == PILLAR_SLUG:
        return [slug for slug in ARTICLES if slug != PILLAR_SLUG]
    others = [slug for slug in ARTICLES if slug != current]
    return [PILLAR_SLUG] + [slug for slug in others if slug != PILLAR_SLUG]


def build_cluster_intro(slug: str) -> str:
    meta = ARTICLES[slug]
    parts = [f'<a href="{BLOG_CATEGORY_HREF}">ADU</a>']

    if meta["role"] == "satellite":
        parts.append(
            f'<a href="{href(PILLAR_SLUG)}">Complete ADU Guide</a>'
        )

    related = related_slugs(slug)
    if related:
        guide_links = ", ".join(
            f'<a href="{href(s)}">{short_title(s)}</a>' for s in related
        )
        label = "Related guides" if len(related) > 1 else "Related guide"
        parts.append(f"{label}: {guide_links}")

    return f'<p class="jrh-blog-cluster-link">{" · ".join(parts)}</p>\n'


def short_title(slug: str) -> str:
    title = ARTICLES[slug]["title"]
    if slug == "how-much-does-an-adu-cost":
        return "ADU Cost Guide"
    if slug == PILLAR_SLUG:
        return "What Is an ADU?"
    return title.split("|")[0].strip()[:60]


def build_read_also(slug: str) -> str:
    items = []
    for related in related_slugs(slug):
        meta = ARTICLES[related]
        items.append(
            f'<li><a href="{href(related)}">{meta["title"]}</a> — {meta["excerpt"]}</li>'
        )
    if not items:
        return ""
    return (
        f"\n{READ_ALSO_MARKER}\n"
        f"<h2>Read Also</h2>\n"
        f"<ul>\n" + "\n".join(items) + "\n</ul>\n</div>\n"
    )


def strip_read_also(html: str) -> str:
    start = html.find(READ_ALSO_MARKER)
    if start == -1:
        return html.rstrip()
    return html[:start].rstrip()


def strip_service_cta(html: str) -> str:
    while SERVICE_CTA_MARKER in html:
        start = html.find(SERVICE_CTA_MARKER)
        end = html.find("</div>", start)
        if end == -1:
            break
        html = (html[:start] + html[end + len("</div>") :]).strip()
    return html


def build_service_cta() -> str:
    return f"""{SERVICE_CTA_MARKER}
<p class="jrh-adu-service-cta-title">Planning an ADU on your property?</p>
<p class="jrh-adu-service-cta-text">JRH Constructions offers complete Accessory Dwelling Unit services in Massachusetts and Greater Boston — from design and permits to construction for garage conversions, attached units, and detached backyard ADUs.</p>
<p class="jrh-adu-service-cta-link"><a href="{SERVICE_PAGE_HREF}">Explore our ADU construction service</a></p>
</div>
"""


def insert_service_cta_after_second_h2(html: str) -> str:
    html = strip_service_cta(html)
    h2_matches = list(re.finditer(r"<h2\b", html, flags=re.IGNORECASE))
    if len(h2_matches) < 3:
        return html
    insert_at = h2_matches[2].start()
    return html[:insert_at] + build_service_cta() + "\n\n" + html[insert_at:]


CONTEXTUAL_LINKS: dict[str, list[tuple[str, str]]] = {
    PILLAR_SLUG: [
        (
            "<h2>How Much Does an ADU Cost?</h2>",
            f'<h2><a href="{href("how-much-does-an-adu-cost")}">How Much Does an ADU Cost?</a></h2>',
        ),
        (
            "One of the first questions homeowners ask is how much it costs to build an",
            f'One of the first questions homeowners ask is <a href="{href("how-much-does-an-adu-cost")}">how much it costs to build</a> an',
        ),
        (
            "<p><strong>Topic Cluster Opportunity:</strong> ADU Cost</p>",
            f'<p><strong>Topic Cluster Opportunity:</strong> <a href="{href("how-much-does-an-adu-cost")}">ADU Cost</a></p>',
        ),
        (
            "Understanding these cost drivers allows homeowners to establish realistic expectations",
            f'For detailed pricing tables, Massachusetts estimates, and financing options, see our '
            f'<a href="{href("how-much-does-an-adu-cost")}">complete ADU cost guide</a>. '
            f"Understanding these cost drivers allows homeowners to establish realistic expectations",
        ),
        (
            "<h3>How much does an ADU cost?</h3>\n<p>Costs typically range",
            f'<h3>How much does an ADU cost?</h3>\n<p>See our '
            f'<a href="{href("how-much-does-an-adu-cost")}">ADU cost guide</a> for a full breakdown by type, '
            f"size, and construction phase. Costs typically range",
        ),
        (
            "<h2>Return on Investment and Rental Income</h2>",
            f'<h2>Return on Investment and Rental Income</h2>\n\n'
            f'<p>Explore projected costs and rental returns in our '
            f'<a href="{href("how-much-does-an-adu-cost")}">ADU cost and ROI guide</a>.</p>',
        ),
    ],
    "how-much-does-an-adu-cost": [
        (
            "</em></p>\n\n<h2>How Much Does an ADU Cost?</h2>",
            f'</em></p>\n\n<p>New to ADUs? Start with our '
            f'<a href="{href(PILLAR_SLUG)}">complete ADU guide</a> before estimating your budget.</p>\n\n'
            f"<h2>How Much Does an ADU Cost?</h2>",
        ),
        (
            "building an <strong>Accessory Dwelling Unit (ADU)</strong> varies",
            f'building an <a href="{href(PILLAR_SLUG)}"><strong>Accessory Dwelling Unit (ADU)</strong></a> varies',
        ),
        (
            "<h2>Is Building an ADU Worth the Investment?</h2>\n\n<p>For many homeowners, an ADU is more",
            f'<h2>Is Building an ADU Worth the Investment?</h2>\n\n<p>For many homeowners, an '
            f'<a href="{href(PILLAR_SLUG)}">ADU</a> is more',
        ),
        (
            "<h2>Detached ADUs vs Garage Conversions</h2>\n\n<p>Detached ADUs offer",
            f"<h2>Detached ADUs vs Garage Conversions</h2>\n\n"
            f'<p>Compare <a href="{href(PILLAR_SLUG)}">different types of ADUs</a> in our overview guide. '
            f"Detached ADUs offer",
        ),
        (
            "<h2>Understanding the True Cost of an ADU</h2>\n\n<p>The cost of an ADU depends",
            f'<h2>Understanding the True Cost of an ADU</h2>\n\n'
            f'<p>If you are still learning what an ADU is and how it works, read '
            f'<a href="{href(PILLAR_SLUG)}">What Is an Accessory Dwelling Unit (ADU)?</a> first. '
            f"The cost of an ADU depends",
        ),
        (
            "<h2>Can an ADU Pay for Itself?</h2>\n\n<p>Many homeowners view ADUs as long-term investments.",
            f"<h2>Can an ADU Pay for Itself?</h2>\n\n"
            f'<p>Learn how ADUs create value beyond construction costs in our '
            f'<a href="{href(PILLAR_SLUG)}">main ADU guide</a>. '
            f"Many homeowners view ADUs as long-term investments.",
        ),
    ],
}


def apply_contextual_links(slug: str, html: str) -> str:
    for old, new in CONTEXTUAL_LINKS.get(slug, []):
        if old in html and new not in html:
            html = html.replace(old, new, 1)
    return html


def prepare_article_html(slug: str, html: str) -> str:
    html = apply_contextual_links(slug, html)
    html = strip_read_also(html)
    html = insert_service_cta_after_second_h2(html)
    return html + build_read_also(slug)
