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
    "adu-permits-and-requirements-in-massachusetts": {
        "title": "ADU Permits and Requirements in Massachusetts: The Complete 2026 Guide",
        "excerpt": (
            "Since February 2, 2025, every Massachusetts city and town must allow one ADU by right on "
            "single-family lots. Here is what permits you need and how to get approved without a zoning battle."
        ),
        "content_file": "adu-permits-content.html",
        "role": "satellite",
    },
    "how-to-finance-an-adu-in-massachusetts": {
        "title": "How to Finance an ADU in Massachusetts: HELOC, Refinance, Construction Loans, and State Programs",
        "excerpt": (
            "An ADU in Massachusetts typically costs $150,000 to $400,000. Here are the five real financing "
            "paths homeowners use, what each costs, and which fits your equity, income, and timeline."
        ),
        "content_file": "adu-financing-content.html",
        "role": "satellite",
    },
    "can-you-build-an-adu-on-your-massachusetts-property": {
        "title": "Can You Build an ADU on Your Massachusetts Property? Lot and Zoning Requirements Explained",
        "excerpt": (
            "Under Massachusetts by-right ADU law, most single-family lots qualify. Whether yours does depends "
            "on five filters: zoning, dimensions, septic, overlays, and private restrictions."
        ),
        "content_file": "adu-lot-zoning-content.html",
        "role": "satellite",
    },
    "how-to-choose-an-adu-builder-in-massachusetts": {
        "title": "How to Choose an ADU Builder in Massachusetts: Criteria, Questions, and Red Flags",
        "excerpt": (
            "An ADU is a $150,000 to $400,000 project governed by a law most contractors have never worked under. "
            "Here is how to vet licensing, compare quotes, and spot red flags before you sign."
        ),
        "content_file": "adu-builder-content.html",
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
    if slug == "adu-permits-and-requirements-in-massachusetts":
        return "ADU Permits Guide"
    if slug == "how-to-finance-an-adu-in-massachusetts":
        return "ADU Financing Guide"
    if slug == "can-you-build-an-adu-on-your-massachusetts-property":
        return "Lot & Zoning Guide"
    if slug == "how-to-choose-an-adu-builder-in-massachusetts":
        return "ADU Builder Guide"
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
        (
            "<p><strong>Topic Cluster Opportunity:</strong> ADU Permits</p>",
            f'<p><strong>Topic Cluster Opportunity:</strong> '
            f'<a href="{href("adu-permits-and-requirements-in-massachusetts")}">ADU Permits in Massachusetts</a></p>',
        ),
        (
            "<h2>Permits and Inspections</h2>",
            f'<h2><a href="{href("adu-permits-and-requirements-in-massachusetts")}">Permits and Inspections</a></h2>',
        ),
        (
            "and financing options, see our <a href=\"../how-much-does-an-adu-cost/\">complete ADU cost guide</a>",
            f'and <a href="{href("how-to-finance-an-adu-in-massachusetts")}">financing options</a>, see our '
            f'<a href="{href("how-much-does-an-adu-cost")}">complete ADU cost guide</a>',
        ),
        (
            "<p><strong>Topic Cluster Opportunity:</strong> ADU Zoning Requirements</p>",
            f'<p><strong>Topic Cluster Opportunity:</strong> '
            f'<a href="{href("can-you-build-an-adu-on-your-massachusetts-property")}">ADU Lot and Zoning Requirements</a></p>',
        ),
        (
            "<h2>How to Choose an ADU Builder</h2>",
            f'<h2><a href="{href("how-to-choose-an-adu-builder-in-massachusetts")}">How to Choose an ADU Builder</a></h2>',
        ),
        (
            "Experience and transparency are critical factors when selecting an ADU builder.",
            f'Experience and transparency are critical factors when '
            f'<a href="{href("how-to-choose-an-adu-builder-in-massachusetts")}">selecting an ADU builder</a>.',
        ),
        (
            "<p><strong>Topic Cluster Opportunity:</strong> How to Choose an ADU Builder</p>",
            f'<p><strong>Topic Cluster Opportunity:</strong> '
            f'<a href="{href("how-to-choose-an-adu-builder-in-massachusetts")}">How to Choose an ADU Builder</a></p>',
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
            f'<p>Explore <a href="{href("how-to-finance-an-adu-in-massachusetts")}">ADU financing options</a> and learn how ADUs create value in our '
            f'<a href="{href(PILLAR_SLUG)}">main ADU guide</a>. '
            f"Many homeowners view ADUs as long-term investments.",
        ),
        (
            "Labor costs, permitting requirements, and material prices",
            f'Labor costs, <a href="{href("adu-permits-and-requirements-in-massachusetts")}">permitting requirements</a>, and material prices',
        ),
        (
            "<p>Zoning requirements and permit rules vary by municipality.",
            f'<p><a href="{href("adu-permits-and-requirements-in-massachusetts")}">Zoning requirements and permit rules</a> vary by municipality.',
        ),
        (
            "<h3>Choosing Contractors Based Only on Price</h3>",
            f'<h3><a href="{href("how-to-choose-an-adu-builder-in-massachusetts")}">Choosing Contractors Based Only on Price</a></h3>',
        ),
        (
            "Choosing the right team can make the process smoother and more rewarding.",
            f'<a href="{href("how-to-choose-an-adu-builder-in-massachusetts")}">Choosing the right ADU builder</a> can make the process smoother and more rewarding.',
        ),
    ],
    "adu-permits-and-requirements-in-massachusetts": [
        (
            "</em></p>\n\n<h2>Do You Need a Permit to Build an ADU in Massachusetts? The Short Answer</h2>",
            f'</em></p>\n\n<p>Not sure your lot qualifies? Run our '
            f'<a href="{href("can-you-build-an-adu-on-your-massachusetts-property")}">lot and zoning eligibility checklist</a> first.</p>\n\n'
            f'<p>New to ADUs? Start with our '
            f'<a href="{href(PILLAR_SLUG)}">complete ADU guide</a> before diving into permits.</p>\n\n'
            f"<h2>Do You Need a Permit to Build an ADU in Massachusetts? The Short Answer</h2>",
        ),
        (
            "approval path for a compliant ADU now looks like any other residential construction project",
            f'approval path for a compliant <a href="{href(PILLAR_SLUG)}">ADU</a> now looks like any other residential construction project',
        ),
        (
            "<h2>How Much Do ADU Permits Cost in Massachusetts?</h2>\n\n<p>Permitting is a small share",
            f'<h2>How Much Do ADU Permits Cost in Massachusetts?</h2>\n\n'
            f'<p>For full construction budgets beyond permit fees, see our '
            f'<a href="{href("how-much-does-an-adu-cost")}">complete ADU cost guide</a>.</p>\n\n'
            f"<p>Permitting is a small share",
        ),
        (
            "<h2>Getting Your ADU Permitted Right the First Time</h2>",
            f'<h2>Getting Your ADU Permitted Right the First Time</h2>\n\n'
            f'<p>Compare total project investment in our '
            f'<a href="{href("how-much-does-an-adu-cost")}">ADU cost guide</a> and review ADU basics in our '
            f'<a href="{href(PILLAR_SLUG)}">main ADU overview</a>.</p>',
        ),
        (
            "The order is fixed: feasibility, permits, financing, construction.",
            f'The order is fixed: feasibility, permits, '
            f'<a href="{href("how-to-finance-an-adu-in-massachusetts")}">financing</a>, '
            f'<a href="{href("how-to-choose-an-adu-builder-in-massachusetts")}">choosing a builder</a>, construction.',
        ),
    ],
    "how-to-finance-an-adu-in-massachusetts": [
        (
            "</em></p>\n\n<h2>How Do Homeowners Actually Pay for an ADU? The Short Answer</h2>",
            f'</em></p>\n\n<p>New to ADUs? Start with our '
            f'<a href="{href(PILLAR_SLUG)}">complete ADU guide</a> and our '
            f'<a href="{href("how-much-does-an-adu-cost")}">ADU cost guide</a> before choosing financing.</p>\n\n'
            f"<h2>How Do Homeowners Actually Pay for an ADU? The Short Answer</h2>",
        ),
        (
            "An ADU in Massachusetts typically costs $150,000 to $400,000",
            f'An <a href="{href(PILLAR_SLUG)}">ADU</a> in Massachusetts typically costs '
            f'<a href="{href("how-much-does-an-adu-cost")}">$150,000 to $400,000</a>',
        ),
        (
            "applications are designed to come <strong>after local permits are secured</strong>",
            f'applications are designed to come <strong>after '
            f'<a href="{href("adu-permits-and-requirements-in-massachusetts")}">local permits are secured</a></strong>',
        ),
        (
            "The pattern repeats from the permitting article:",
            f'The pattern repeats from our '
            f'<a href="{href("adu-permits-and-requirements-in-massachusetts")}">ADU permitting guide</a>:',
        ),
        (
            "<h3>Mistake 2: Financing Before Feasibility</h3>\n\n<p>Locking a loan amount before confirming",
            f'<h3>Mistake 2: Financing Before Feasibility</h3>\n\n'
            f'<p>Run our <a href="{href("can-you-build-an-adu-on-your-massachusetts-property")}">lot eligibility checklist</a> first. '
            f"Locking a loan amount before confirming",
        ),
        (
            "<h2>Financing Is Now the Easy Part, If You Sequence It Right</h2>",
            f'<h2>Financing Is Now the Easy Part, If You Sequence It Right</h2>\n\n'
            f'<p>Confirm <a href="{href("can-you-build-an-adu-on-your-massachusetts-property")}">lot and zoning eligibility</a> first, then review the '
            f'<a href="{href("adu-permits-and-requirements-in-massachusetts")}">Massachusetts ADU permit process</a>, '
            f'<a href="{href("how-to-choose-an-adu-builder-in-massachusetts")}">builder selection criteria</a>, and '
            f'<a href="{href("how-much-does-an-adu-cost")}">construction cost ranges</a> before you apply for a loan.</p>',
        ),
        (
            "signed construction contract</strong> with a licensed contractor",
            f'signed construction contract</strong> with a '
            f'<a href="{href("how-to-choose-an-adu-builder-in-massachusetts")}">licensed ADU contractor</a>',
        ),
    ],
    "can-you-build-an-adu-on-your-massachusetts-property": [
        (
            "</em></p>\n\n<h2>The Short Answer: Most Single-Family Lots Now Qualify</h2>",
            f'</em></p>\n\n<p>New to ADUs? Start with our '
            f'<a href="{href(PILLAR_SLUG)}">complete ADU guide</a>. Once your lot checks out, see our '
            f'<a href="{href("adu-permits-and-requirements-in-massachusetts")}">Massachusetts ADU permit guide</a>.</p>\n\n'
            f"<h2>The Short Answer: Most Single-Family Lots Now Qualify</h2>",
        ),
        (
            "regulated under <strong>760 CMR 71.00</strong>",
            f'regulated under <strong>760 CMR 71.00</strong> (detailed in our '
            f'<a href="{href("adu-permits-and-requirements-in-massachusetts")}">ADU permits guide</a>)',
        ),
        (
            "The by-right zoning law explicitly leaves Title 5 untouched.",
            f'The by-right zoning law explicitly leaves <a href="{href("adu-permits-and-requirements-in-massachusetts")}">Title 5</a> untouched.',
        ),
        (
            "The smaller number is your <strong>by-right maximum ADU size</strong>.",
            f'The smaller number is your <strong>by-right maximum ADU size</strong> (see the '
            f'<a href="{href("adu-permits-and-requirements-in-massachusetts")}">full size rule</a>).',
        ),
        (
            "<h2>From \"Can I?\" to \"How Should I?\": Your Next Step</h2>",
            f'<h2>From "Can I?" to "How Should I?": Your Next Step</h2>\n\n'
            f'<p>After eligibility, review <a href="{href("how-much-does-an-adu-cost")}">ADU construction costs</a>, '
            f'<a href="{href("how-to-choose-an-adu-builder-in-massachusetts")}">how to choose an ADU builder</a>, and '
            f'<a href="{href("how-to-finance-an-adu-in-massachusetts")}">financing options</a> for your project.</p>',
        ),
    ],
    "how-to-choose-an-adu-builder-in-massachusetts": [
        (
            "</em></p>\n\n<h2>What Separates a Good ADU Builder: The Short Answer</h2>",
            f'</em></p>\n\n<p>New to ADUs? Start with our '
            f'<a href="{href(PILLAR_SLUG)}">complete ADU guide</a>. Confirm '
            f'<a href="{href("can-you-build-an-adu-on-your-massachusetts-property")}">lot eligibility</a> and review '
            f'<a href="{href("adu-permits-and-requirements-in-massachusetts")}">Massachusetts ADU permits</a> before you interview builders.</p>\n\n'
            f"<h2>What Separates a Good ADU Builder: The Short Answer</h2>",
        ),
        (
            "An ADU is a $150,000 to $400,000 project governed",
            f'An ADU is a <a href="{href("how-much-does-an-adu-cost")}">$150,000 to $400,000 project</a> governed',
        ),
        (
            "<strong>by-right provisions of the Affordable Homes Act</strong>",
            f'<a href="{href("adu-permits-and-requirements-in-massachusetts")}"><strong>by-right provisions of the Affordable Homes Act</strong></a>',
        ),
        (
            "(feasibility, Title 5, zoning, permits)",
            f'(<a href="{href("can-you-build-an-adu-on-your-massachusetts-property")}">feasibility</a>, '
            f'<a href="{href("adu-permits-and-requirements-in-massachusetts")}">Title 5, zoning, permits</a>)',
        ),
        (
            "and an appraisal and financing ecosystem that is still maturing.",
            f'and an appraisal and <a href="{href("how-to-finance-an-adu-in-massachusetts")}">financing ecosystem</a> that is still maturing.',
        ),
        (
            "someone still has to do the local permitting.",
            f'someone still has to do the <a href="{href("adu-permits-and-requirements-in-massachusetts")}">local permitting</a>.',
        ),
        (
            "<h2>The Builder Decision Is the Project Decision</h2>",
            f'<h2>The Builder Decision Is the Project Decision</h2>\n\n'
            f'<p>Before signing, compare normalized bids using our '
            f'<a href="{href("how-much-does-an-adu-cost")}">ADU cost guide</a> and confirm your '
            f'<a href="{href("how-to-finance-an-adu-in-massachusetts")}">financing path</a> matches the contract structure.</p>',
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
