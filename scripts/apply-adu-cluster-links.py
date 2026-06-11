#!/usr/bin/env python3
"""Apply ADU cluster internal links to content sources and published pages."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADU = ROOT / "adu"
SCRIPTS = ADU / "_scripts"
sys.path.insert(0, str(SCRIPTS))

from adu_cluster import (  # noqa: E402
    ARTICLES,
    apply_contextual_links,
    build_cluster_intro,
    build_read_also,
    insert_service_cta_after_second_h2,
    strip_read_also,
    strip_service_cta,
)

LIVE_PATCHES: dict[str, list[tuple[str, str]]] = {
    "what-is-an-accessory-dwelling-unit-adu": [
        (
            "For homeowners considering an ADU project in Massachusetts, working with experienced professionals",
            'For homeowners considering an <a href="../../services/accessory-dwelling-unit-adu-service/">ADU project in Massachusetts</a>, working with experienced professionals',
        ),
        (
            "<p><strong>JRH Constructions</strong>, located at",
            '<p><strong><a href="../../contact-us/">JRH Constructions</a></strong>, located at',
        ),
        (
            "remodeling, and custom ADU projects designed to maximize",
            'remodeling, and <a href="../../services/accessory-dwelling-unit-adu-service/">custom ADU projects</a> designed to maximize',
        ),
    ],
    "how-much-does-an-adu-cost": [
        (
            "who are considering an Accessory Dwelling Unit should work with experienced contractors",
            'who are considering an <a href="../../services/accessory-dwelling-unit-adu-service/">Accessory Dwelling Unit</a> should work with experienced contractors',
        ),
        (
            "Professional guidance can help transform an idea into a valuable long-term investment.",
            'Professional guidance from <a href="../../contact-us/">JRH Constructions</a> can help transform an idea into a valuable long-term investment.',
        ),
    ],
    "adu-permits-and-requirements-in-massachusetts": [
        (
            "work with a team that has already carried ADU projects through Massachusetts building departments",
            'work with a team that has already carried <a href="../../services/accessory-dwelling-unit-adu-service/">ADU projects</a> through Massachusetts building departments',
        ),
        (
            '<a href="../../services/accessory-dwelling-unit-adu-service/">Explore JRH Constructions ADU construction services</a>',
            '<a href="../../services/accessory-dwelling-unit-adu-service/">Explore our ADU construction services</a>',
        ),
    ],
    "how-to-finance-an-adu-in-massachusetts": [
        (
            "if you want the feasibility, permitting, and lender package handled as one workflow",
            'if you want the <a href="../../services/accessory-dwelling-unit-adu-service/">feasibility, permitting, and construction</a> package handled as one workflow',
        ),
        (
            '<a href="../../services/accessory-dwelling-unit-adu-service/">explore JRH Constructions ADU construction services</a>',
            '<a href="../../services/accessory-dwelling-unit-adu-service/">explore our ADU construction services</a>',
        ),
    ],
    "can-you-build-an-adu-on-your-massachusetts-property": [
        (
            "That study is where experienced ADU builders earn their keep before construction even starts",
            'That study is where <a href="../how-to-choose-an-adu-builder-in-massachusetts/">experienced ADU builders</a> earn their keep before construction even starts',
        ),
        (
            '<a href="../../services/accessory-dwelling-unit-adu-service/">explore our ADU construction services</a>',
            '<a href="../../services/accessory-dwelling-unit-adu-service/">explore our ADU construction services</a>',
        ),
    ],
    "how-to-choose-an-adu-builder-in-massachusetts": [
        (
            "with a feasibility study first and contract transparency as policy",
            'with a <a href="../../services/accessory-dwelling-unit-adu-service/">feasibility study first</a> and contract transparency as policy',
        ),
    ],
    "which-adu-type-is-best-for-your-massachusetts-home": [
        (
            "That walkthrough is the entire purpose of a feasibility assessment",
            'That walkthrough is the entire purpose of a <a href="../../services/accessory-dwelling-unit-adu-service/">feasibility assessment</a>',
        ),
    ],
    "basement-adu-conversion-in-massachusetts": [
        (
            "Those calls are exactly what a professional feasibility walkthrough resolves",
            'Those calls are exactly what a professional <a href="../../services/accessory-dwelling-unit-adu-service/">basement feasibility walkthrough</a> resolves',
        ),
    ],
    "adu-floor-plans-for-massachusetts": [
        (
            "that is a feasibility conversation before it is a design contract",
            'that is a <a href="../../services/accessory-dwelling-unit-adu-service/">feasibility and design consultation</a> before it is a design contract',
        ),
    ],
    "how-long-does-it-take-to-build-an-adu-in-massachusetts": [
        (
            "That backward plan is a standard part of a professional feasibility assessment",
            'That backward plan is a standard part of a professional <a href="../../services/accessory-dwelling-unit-adu-service/">feasibility assessment with a timeline plan</a>',
        ),
    ],
    "adu-roi-in-massachusetts": [
        (
            "the feasibility walkthrough that anchors them to your actual lot, are the first step that costs nothing.",
            'the <a href="../../services/accessory-dwelling-unit-adu-service/">feasibility walkthrough with a rental projection</a> that anchors them to your actual lot, are the first step that costs nothing.',
        ),
    ],
}


def apply_live_patches(slug: str, html: str) -> str:
    for old, new in LIVE_PATCHES.get(slug, []):
        if old in html and new not in html:
            html = html.replace(old, new, 1)
    return html


def append_cluster_css() -> None:
    css_path = ROOT / "blog" / "styles.css"
    css = css_path.read_text(encoding="utf-8")
    additions = []

    if ".jrh-blog-read-also" not in css:
        additions.append("""
.jrh-blog-read-also{margin:2.5rem 0 0;padding:1.75rem 0 0;border-top:1px solid #eee;max-width:820px}
.jrh-blog-read-also h2{font-family:"Sora",Sans-serif;font-size:1.25rem;line-height:1.35;margin:0 0 .75rem;font-weight:600}
.jrh-blog-read-also ul{margin:0;padding:0 0 0 1.25rem;list-style:disc}
.jrh-blog-read-also li{margin-bottom:.65rem;font-family:"Sora",Sans-serif;font-size:15px;line-height:1.65;color:var(--e-global-color-6939b83)}
.jrh-blog-read-also a{font-weight:600;text-decoration:none;color:inherit}
.jrh-blog-read-also a:hover{text-decoration:underline}""")

    if ".jrh-adu-service-cta" not in css:
        additions.append("""
.jrh-adu-service-cta{margin:2rem 0;padding:1.35rem 1.5rem;border:1px solid #e5e5e5;border-radius:8px;background:#f9f9f9;max-width:820px}
.jrh-adu-service-cta-title{font-family:"Sora",Sans-serif;font-size:1.1rem;line-height:1.35;margin:0 0 .65rem;font-weight:600;color:var(--e-global-color-6939b83)}
.jrh-adu-service-cta-text{font-family:"Sora",Sans-serif;font-size:15px;line-height:1.65;margin:0 0 .85rem;color:var(--e-global-color-6939b83)}
.jrh-adu-service-cta-link{margin:0;font-family:"Sora",Sans-serif;font-size:15px}
.jrh-adu-service-cta-link a{font-weight:600;text-decoration:none}
.jrh-adu-service-cta-link a:hover{text-decoration:underline}""")

    if additions:
        css_path.write_text(css + "\n" + "\n".join(additions), encoding="utf-8")


def prepare_body(slug: str, html: str, *, live_patches: bool = False) -> str:
    html = strip_read_also(strip_service_cta(html))
    html = apply_contextual_links(slug, html)
    if live_patches:
        html = apply_live_patches(slug, html)
    html = insert_service_cta_after_second_h2(html)
    return html + build_read_also(slug)


def sync_content_source(slug: str) -> None:
    meta = ARTICLES[slug]
    path = SCRIPTS / meta["content_file"]
    html = prepare_body(slug, path.read_text(encoding="utf-8"))
    path.write_text(html, encoding="utf-8")


def build_page_body(slug: str) -> str:
    meta = ARTICLES[slug]
    return prepare_body(
        slug,
        (SCRIPTS / meta["content_file"]).read_text(encoding="utf-8"),
        live_patches=True,
    )


def sync_published_page(slug: str) -> None:
    page_path = ADU / slug / "index.html"
    if not page_path.exists():
        return

    source = build_page_body(slug)
    intro = build_cluster_intro(slug)
    page = page_path.read_text(encoding="utf-8")

    page = re.sub(
        r'(<div class="jrh-blog-article">).*?(</div>\s*\n\t\t\t\t</div>\s*\n\t\t\t\t</div>)',
        r"\1\n" + intro + source + r"\n\t\t\t\t\t\2",
        page,
        count=1,
        flags=re.DOTALL,
    )
    page_path.write_text(page, encoding="utf-8")


def main() -> None:
    for slug in ARTICLES:
        sync_content_source(slug)
        sync_published_page(slug)
        print(f"linked: adu/{slug}/")

    append_cluster_css()

    import subprocess
    import sys

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sync-blog-index.py")],
        check=True,
    )
    print("ADU cluster links applied.")


if __name__ == "__main__":
    main()
