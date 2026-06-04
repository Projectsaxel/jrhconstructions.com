#!/usr/bin/env python3
"""Add contextual internal links inside text-editor content on service pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICES_DIR = ROOT / "services"

SERVICE_CONFIG = {
    "adu": {
        "main": "accessory-dwelling-unit-adu-service",
        "labels": [
            "Accessory Dwelling Unit (ADU)",
            "Accessory Dwelling Unit",
            "Accessory Dwelling Units",
        ],
        "cities": {
            "cambridge": "accessory-dwelling-unit-adu-in-cambridge",
            "sommerville": "accessory-dwelling-unit-adu-in-sommerville",
            "quincy": "accessory-dwelling-unit-adu-in-quincy",
            "peabody": "accessory-dwelling-unit-adu-in-peabody",
            "malden": "accessory-dwelling-unit-adu-in-malden",
            "newton": "accessory-dwelling-unit-adu-in-newton",
        },
        "related": ["home-additions", "full-remodeling", "bathroom", "kitchen"],
    },
    "bathroom": {
        "main": "bathroom-remodeling-service",
        "labels": ["Bathroom Remodeling"],
        "cities": {
            "boston": "bathroom-remodeling-in-boston",
            "cambridge": "bathroom-remodeling-in-cambridge",
            "sommerville": "bathroom-remodeling-in-sommerville",
            "quincy": "bathroom-remodeling-in-quincy",
            "peabody": "bathroom-remodeling-in-peabody",
            "malden": "bathroom-remodeling-in-malden",
        },
        "related": ["kitchen", "full-remodeling", "home-additions", "painting"],
    },
    "kitchen": {
        "main": "kitchen-remodeling-service",
        "labels": ["Kitchen Remodeling"],
        "cities": {
            "boston": "kitchen-remodelin-in-boston",
            "cambridge": "kitchen-remodeling-in-cambridge",
            "sommerville": "kitchen-remodeling-in-sommerville",
            "quincy": "kitchen-remodeling-in-quincy",
            "peabody": "kitchen-remodeling-in-peabody",
            "malden": "kitchen-remodeling-in-malden",
            "newton": "kitchen-remodeling-in-newton",
        },
        "related": ["bathroom", "full-remodeling", "home-additions", "painting"],
    },
    "home-additions": {
        "main": "home-additions-service",
        "labels": ["Home Additions", "Home Addition"],
        "cities": {
            "boston": "home-additions-in-boston",
            "cambridge": "home-additions-in-cambridge",
            "sommerville": "home-additions-in-sommerville",
            "quincy": "home-additions-quincy",
            "peabody": "home-additions-in-peabody",
            "newton": "home-additions-in-newton",
        },
        "related": ["adu", "full-remodeling", "kitchen", "bathroom"],
    },
    "full-remodeling": {
        "main": "full-remodeling-service",
        "labels": ["Full Remodeling"],
        "cities": {
            "boston": "full-remodeling-in-boston",
            "cambridge": "full-remodeling-in-cambridge",
            "sommerville": "full-remodeling-in-sommerville",
            "quincy": "full-remodeling-in-quincy",
            "peabody": "full-remodeling-in-peabody",
            "malden": "full-remodeling-in-malden",
            "newton": "full-remodeling-in-newton",
        },
        "related": ["kitchen", "bathroom", "home-additions", "adu"],
    },
    "painting": {
        "main": "painting-service",
        "labels": ["Painting Services", "Painting"],
        "cities": {
            "boston": "painting-in-boston",
            "cambridge": "painting-in-cambridge",
            "sommerville": "painting-in-sommerville",
            "quincy": "painting-in-quincy",
            "peabody": "painting-in-peabody",
            "malden": "painting-in-malden",
            "newton": "painting-in-newton",
        },
        "related": ["full-remodeling", "kitchen", "bathroom", "home-additions"],
    },
}

CITY_DISPLAY = {
    "boston": "Boston",
    "cambridge": "Cambridge",
    "sommerville": "Somerville",
    "quincy": "Quincy",
    "peabody": "Peabody",
    "malden": "Malden",
    "newton": "Newton",
}

CITY_NAME_TO_KEY = {
    "Boston": "boston",
    "Cambridge": "cambridge",
    "Somerville": "sommerville",
    "Sommerville": "sommerville",
    "Quincy": "quincy",
    "Peabody": "peabody",
    "Malden": "malden",
    "Newton": "newton",
}

TEXT_EDITOR_RE = re.compile(
    r'(<div class="elementor-element[^"]*elementor-widget-text-editor[^"]*"[^>]*>\s*'
    r'<div class="elementor-widget-container">\s*)(.*?)(\s*</div>\s*</div>)',
    re.DOTALL,
)

MARKER = "jrh-contextual-links-applied"


def parse_page_slug(slug: str) -> tuple[str, bool, str | None] | None:
    if slug == "index":
        return None
    for key, cfg in SERVICE_CONFIG.items():
        if slug == cfg["main"]:
            return key, True, None
        for city, city_slug in cfg["cities"].items():
            if slug == city_slug:
                return key, False, city
    return None


def split_anchors(html: str) -> list[str]:
    return re.split(r"(<a\b[^>]*>.*?</a>)", html, flags=re.DOTALL | re.IGNORECASE)


def link_phrase(html: str, phrase: str, href: str, limit: int = 1) -> str:
    if limit <= 0:
        return html
    count = 0
    parts = split_anchors(html)
    out: list[str] = []
    pattern = re.compile(r"(?<![a-zA-Z])" + re.escape(phrase) + r"(?![a-zA-Z])", re.IGNORECASE)
    for part in parts:
        if count >= limit or part.lower().startswith("<a"):
            out.append(part)
            continue

        def repl(match: re.Match[str]) -> str:
            nonlocal count
            if count >= limit:
                return match.group(0)
            count += 1
            return f'<a href="{href}">{match.group(0)}</a>'

        out.append(pattern.sub(repl, part, count=limit - count))
    return "".join(out)


def link_city_names(html: str, service_key: str, current_city: str | None, limit_per_city: int = 1) -> str:
    cfg = SERVICE_CONFIG[service_key]
    for display, city_key in CITY_NAME_TO_KEY.items():
        if city_key not in cfg["cities"]:
            continue
        if current_city == city_key:
            continue
        slug = cfg["cities"][city_key]
        html = link_phrase(html, display, f"../{slug}/", limit=limit_per_city)
    return html


def related_phrases(service_key: str) -> list[tuple[str, str]]:
    phrases: list[tuple[str, str]] = []
    for rel in SERVICE_CONFIG[service_key]["related"]:
        rel_cfg = SERVICE_CONFIG[rel]
        for label in rel_cfg["labels"]:
            phrases.append((label, rel_cfg["main"]))
    phrases.sort(key=lambda x: len(x[0]), reverse=True)
    return phrases


def append_service_area_links(html: str, service_key: str, is_main: bool, current_city: str | None) -> str:
    if MARKER in html:
        return html

    cfg = SERVICE_CONFIG[service_key]
    needles = [
        "Our Construction company in Massachusetts serves",
        "Our Construction company in Massachusetts services",
        "Our Construction company in Massachusetts provides",
        "To hire a company for your",
        "To hire a company for ",
        "To hire the right partner for your",
        "When looking to hire a",
    ]
    target_needle = next((n for n in needles if n in html), None)
    if not target_needle or "We also offer" in html or "We also provide" in html:
        return html

    other_cities = [(k, s) for k, s in cfg["cities"].items() if k != current_city]
    if not other_cities and is_main:
        other_cities = list(cfg["cities"].items())

    city_bits = [
        f'<a href="../{slug}/">{CITY_DISPLAY[key]}</a>' for key, slug in other_cities[:4]
    ]
    rel_bits = []
    for label, slug in related_phrases(service_key)[:2]:
        rel_bits.append(f'<a href="../{slug}/">{label.lower()}</a>')

    service_label = cfg["labels"][0]
    extra = f' <!-- {MARKER} -->'
    if city_bits and rel_bits:
        sentence = (
            f" We also offer {service_label.lower()} in {', '.join(city_bits)}, "
            f"and related services such as {' and '.join(rel_bits)}."
        )
    elif city_bits:
        sentence = f" We also offer {service_label.lower()} in {', '.join(city_bits)}."
    elif rel_bits:
        sentence = f" Related services include {' and '.join(rel_bits)}."
    else:
        return html

    idx = html.rfind(target_needle)
    if idx == -1:
        return html
    close = html.find("</p>", idx)
    if close == -1:
        return html
    return html[:close] + sentence + extra + html[close:]


def process_content(html: str, service_key: str, is_main: bool, current_city: str | None, *, allow_append: bool = True) -> str:
    if MARKER in html and not allow_append:
        return html

    cfg = SERVICE_CONFIG[service_key]
    own_main = f"../{cfg['main']}/"

    if not is_main:
        for label in sorted(cfg["labels"], key=len, reverse=True):
            html = link_phrase(html, label, own_main, limit=1)
            if own_main in html:
                break
        html = link_city_names(html, service_key, current_city, limit_per_city=1)
    else:
        html = link_city_names(html, service_key, current_city, limit_per_city=1)

    own_labels = set(cfg["labels"])
    for label, slug in related_phrases(service_key):
        if label in own_labels and is_main:
            continue
        html = link_phrase(html, label, f"../{slug}/", limit=1)

    if service_key == "adu" and is_main:
        blog_href = "../adu/what-is-an-accessory-dwelling-unit-adu/"
        if blog_href not in html:
            html = link_phrase(html, "Accessory Dwelling Units", blog_href, limit=1)

    # Contextual links only inside existing copy (no appended blocks).
    return html


def process_file(path: Path) -> bool:
    slug = path.parent.name
    parsed = parse_page_slug(slug)
    if not parsed:
        return False

    service_key, is_main, current_city = parsed
    text = path.read_text(encoding="utf-8")
    already = MARKER in text

    changed = False

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        prefix, body, suffix = match.group(1), match.group(2), match.group(3)
        if "elementor-widget-container" in body:
            return match.group(0)
        new_body = process_content(body, service_key, is_main, current_city, allow_append=MARKER not in body)
        if service_key == "adu" and not is_main:
            blog_href = "../../adu/what-is-an-accessory-dwelling-unit-adu/"
            if blog_href not in new_body:
                new_body = link_phrase(new_body, "Accessory Dwelling Units", blog_href, limit=1)
        if new_body != body:
            changed = True
        return prefix + new_body + suffix

    new_text = TEXT_EDITOR_RE.sub(repl, text)
    if changed:
        path.write_text(new_text, encoding="utf-8")
    return changed


def process_blog_post() -> bool:
    post = ROOT / "adu/what-is-an-accessory-dwelling-unit-adu/index.html"
    if not post.exists():
        return False
    text = post.read_text(encoding="utf-8")
    if "jrh-blog-contextual-links" in text:
        return False

    replacements = [
        (
            "<strong>JRH Constructions</strong>, located at",
            '<strong><a href="../../contact-us/">JRH Constructions</a></strong>, located at',
        ),
        (
            "custom ADU projects designed to maximize",
            '<a href="../../services/accessory-dwelling-unit-adu-service/">custom ADU projects</a> designed to maximize',
        ),
        (
            "For homeowners considering an ADU project in Massachusetts",
            'For homeowners considering an <a href="../../services/accessory-dwelling-unit-adu-service/">ADU project in Massachusetts</a>',
        ),
    ]
    new_text = text
    for old, new in replacements:
        if old in new_text and new not in new_text:
            new_text = new_text.replace(old, new, 1)

    if "home addition" in new_text.lower() and "../../services/home-additions-service/" not in new_text:
        new_text = new_text.replace(
            "A home addition expands the existing residence",
            'A <a href="../../services/home-additions-service/">home addition</a> expands the existing residence',
            1,
        )

    new_text = new_text.replace("</head>", '<meta name="jrh-blog-contextual-links" content="1"></head>', 1)
    if new_text != text:
        post.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> None:
    updated = 0
    for path in sorted(SERVICES_DIR.glob("*/index.html")):
        if path.parent.name == "index":
            continue
        if process_file(path):
            updated += 1
            print("linked:", path.relative_to(ROOT))
    if process_blog_post():
        print("linked: adu/what-is-an-accessory-dwelling-unit-adu/index.html")
        updated += 1
    print(f"Done. Updated {updated} files.")


if __name__ == "__main__":
    main()
