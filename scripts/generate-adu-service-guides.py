#!/usr/bin/env python3
"""Generate ADU guide pages under /services/ (optional). Menus use a flat ADU link."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADU = ROOT / "adu"
SERVICES = ROOT / "services"
sys.path.insert(0, str(ADU / "_scripts"))

from adu_cluster import ARTICLES  # noqa: E402

SERVICE_GUIDE_SLUGS = [
    "can-you-build-an-adu-on-your-massachusetts-property",
    "adu-permits-and-requirements-in-massachusetts",
    "how-to-finance-an-adu-in-massachusetts",
    "how-to-choose-an-adu-builder-in-massachusetts",
]

NESTED_ADU_ITEM = re.compile(
    r'\t<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children menu-item-2328[^"]*">.*?</ul>\n</li>',
    re.DOTALL,
)


FLAT_ADU_ITEM = re.compile(
    r'\t<li class="menu-item menu-item-type-post_type menu-item-object-page(?: current-menu-item page_item page-item-2240 current_page_item)? menu-item-2328">'
    r'<a href="[^"]*"(?: aria-current="page")? class="elementor-sub-item(?: elementor-item-active)?"(?: tabindex="-1")?>'
    r"Accessory Dwelling Unit \(ADU\)</a></li>",
)


def adu_menu_href(page: Path) -> tuple[str, bool]:
    rel = page.relative_to(ROOT)
    if rel.parts[0] == "services" and len(rel.parts) == 3:
        if rel.parts[1] == "accessory-dwelling-unit-adu-service":
            return "./", True
    prefix = adu_href_prefix(page)
    return f"{prefix}accessory-dwelling-unit-adu-service/", False


def menu_context(page: Path) -> tuple[str, bool]:
    return adu_menu_href(page)


def adu_href_prefix(page: Path) -> str:
    rel = page.relative_to(ROOT)
    parts = rel.parts
    if parts == ("index.html",):
        return "services/"
    if parts[0] == "services":
        if len(parts) == 2:
            return ""
        return "../"
    if parts[0] == "adu":
        return "../../services/"
    return "../services/"


def build_flat_adu_menu_item(
    href: str,
    *,
    tabindex: str = "",
    active: bool = False,
) -> str:
    tab = tabindex if tabindex else ""
    if active:
        classes = (
            "menu-item menu-item-type-post_type menu-item-object-page "
            "current-menu-item page_item page-item-2240 current_page_item menu-item-2328"
        )
        link_cls = "elementor-sub-item elementor-item-active"
        attrs = f' aria-current="page" class="{link_cls}"{tab}'
    else:
        classes = "menu-item menu-item-type-post_type menu-item-object-page menu-item-2328"
        link_cls = "elementor-sub-item"
        attrs = f' class="{link_cls}"{tab}' if tab else f' class="{link_cls}"'
    return f'\t<li class="{classes}"><a href="{href}"{attrs}>Accessory Dwelling Unit (ADU)</a></li>'


def restore_flat_adu_menus() -> None:
    updated = 0
    for page in sorted(ROOT.rglob("index.html")):
        if ".git" in page.parts:
            continue
        html = page.read_text(encoding="utf-8")
        if "menu-item-2328" not in html:
            continue

        href, active = menu_context(page)

        def flat_replacer(m: re.Match[str]) -> str:
            tab_attr = ' tabindex="-1"' if 'tabindex="-1"' in m.group(0) else ""
            return build_flat_adu_menu_item(href, tabindex=tab_attr, active=active)

        new_html = NESTED_ADU_ITEM.sub(flat_replacer, html)
        new_html = FLAT_ADU_ITEM.sub(flat_replacer, new_html)
        if new_html != html:
            page.write_text(new_html, encoding="utf-8")
            updated += 1
    print(f"flat ADU menus restored: {updated} files")


def transform_adu_page_to_service(html: str, slug: str) -> str:
    html = html.replace(f"https://jrhconstructions.com/adu/{slug}/", f"https://jrhconstructions.com/services/{slug}/")
    html = html.replace(f"/adu/{slug}/", f"/services/{slug}/")
    html = html.replace(f"/adu/{slug}#", f"/services/{slug}#")

    blog_only_slugs = {"what-is-an-accessory-dwelling-unit-adu", "how-much-does-an-adu-cost"}
    for other in ARTICLES:
        if other == slug or other not in blog_only_slugs:
            continue
        html = html.replace(f'href="../{other}/"', f'href="../../adu/{other}/"')

    html = html.replace(
        'href="../../services/accessory-dwelling-unit-adu-service/"',
        'href="../accessory-dwelling-unit-adu-service/"',
    )
    return html


def generate_service_guides() -> None:
    for slug in SERVICE_GUIDE_SLUGS:
        source = ADU / slug / "index.html"
        if not source.is_file():
            raise FileNotFoundError(source)
        html = transform_adu_page_to_service(source.read_text(encoding="utf-8"), slug)
        out_dir = SERVICES / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"created: services/{slug}/index.html")


def patch_menus() -> None:
    restore_flat_adu_menus()


def main() -> None:
    generate_service_guides()
    restore_flat_adu_menus()


if __name__ == "__main__":
    main()
