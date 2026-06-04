#!/usr/bin/env python3
"""Move ADU articles from /blog/ to /adu/ category and update references."""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
ADU = ROOT / "adu"
CATEGORY = "adu"
CATEGORY_NAME = "ADU"
CATEGORY_DESC = (
    "Guides about Accessory Dwelling Units — types, costs, regulations, and planning "
    "for homeowners in Massachusetts and Greater Boston."
)

ARTICLES = [
    {
        "slug": "how-much-does-an-adu-cost",
        "title": "How Much Does an ADU Cost? Complete Pricing Guide for Homeowners",
        "excerpt": (
            "Discover how much it costs to build an Accessory Dwelling Unit, what factors influence the price, "
            "and how to estimate the investment required for your project."
        ),
    },
    {
        "slug": "what-is-an-accessory-dwelling-unit-adu",
        "title": "What Is an Accessory Dwelling Unit (ADU)? The Complete Homeowner's Guide",
        "excerpt": (
            "Learn what an Accessory Dwelling Unit is, the different types available, "
            "the benefits of building one, and why ADUs have become one of the most popular "
            "ways to increase living space and property value in the United States."
        ),
    },
]

OLD_BLOG_PREFIX = "https://jrhconstructions.com/blog/"
NEW_ADU_PREFIX = f"https://jrhconstructions.com/{CATEGORY}/"


def article_listing_html(base_href: str = "./") -> str:
    items = []
    for art in ARTICLES:
        items.append(
            f'''\t\t\t\t\t\t<article class="jrh-blog-list-item">
\t\t\t\t\t\t\t<h2 class="jrh-blog-list-title"><a href="{base_href}{art["slug"]}/">{art["title"]}</a></h2>
\t\t\t\t\t\t\t<p class="jrh-blog-list-excerpt">{art["excerpt"]}</p>
\t\t\t\t\t\t\t<p class="jrh-blog-list-link"><a href="{base_href}{art["slug"]}/">Read article</a></p>
\t\t\t\t\t\t</article>'''
        )
    return "\n\n".join(items)


def category_listing_html() -> str:
    return f'''\t\t\t\t\t\t<article class="jrh-blog-list-item jrh-blog-category-item">
\t\t\t\t\t\t\t<h2 class="jrh-blog-list-title"><a href="../{CATEGORY}/">{CATEGORY_NAME}</a></h2>
\t\t\t\t\t\t\t<p class="jrh-blog-list-excerpt">{CATEGORY_DESC}</p>
\t\t\t\t\t\t\t<p class="jrh-blog-list-link"><a href="../{CATEGORY}/">View category</a></p>
\t\t\t\t\t\t</article>'''


def redirect_html(target_path: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
\t<meta charset="utf-8">
\t<meta name="robots" content="noindex, follow">
\t<link rel="canonical" href="https://jrhconstructions.com{target_path}">
\t<meta http-equiv="refresh" content="0; url={target_path}">
\t<script>location.replace("{target_path}");</script>
\t<title>Redirecting…</title>
</head>
<body><p><a href="{target_path}">Continue to the updated page</a></p></body>
</html>
"""


def fix_article_html(html: str, slug: str) -> str:
    html = html.replace(OLD_BLOG_PREFIX, NEW_ADU_PREFIX)
    html = re.sub(
        r"\| JRH Constructions Blog</title>",
        f"| JRH Constructions {CATEGORY_NAME}</title>",
        html,
        count=1,
    )

    category_breadcrumb = f'<a href="../">{CATEGORY_NAME}</a>'
    if "jrh-blog-cluster-link" in html:
        html = re.sub(
            r'(<p class="jrh-blog-cluster-link">)',
            rf'\1{category_breadcrumb} · ',
            html,
            count=1,
        )
    else:
        html = re.sub(
            r'(<div class="jrh-blog-article">)',
            rf'\1\n<p class="jrh-blog-cluster-link">{category_breadcrumb}</p>\n',
            html,
            count=1,
        )

    html = html.replace(
        'isPartOf":{"@id":"https://jrhconstructions.com/blog/#webpage"}',
        f'isPartOf":{{"@id":"https://jrhconstructions.com/{CATEGORY}/#webpage"}}',
    )
    return html


def build_category_index() -> str:
    html = (BLOG / "index.html").read_text(encoding="utf-8")

    html = re.sub(r"<title>.*?</title>", f"<title>{CATEGORY_NAME} | JRH Constructions</title>", html, count=1)
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{CATEGORY_DESC}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{NEW_ADU_PREFIX}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{CATEGORY_NAME} | JRH Constructions">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{CATEGORY_DESC}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{NEW_ADU_PREFIX}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta name="twitter:title" content="[^"]*">',
        f'<meta name="twitter:title" content="{CATEGORY_NAME} | JRH Constructions">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta name="twitter:description" content="[^"]*">',
        f'<meta name="twitter:description" content="{CATEGORY_DESC}">',
        html,
        count=1,
    )

    html = html.replace(
        '<h1 class="elementor-heading-title elementor-size-default">Blog</h1>',
        f'<h1 class="elementor-heading-title elementor-size-default">{CATEGORY_NAME}</h1>',
    )
    html = html.replace(
        "<p>Remodeling tips, project guides, and construction insights for homeowners in Boston and Greater Boston.</p>",
        f"<p>{CATEGORY_DESC}</p>",
    )

    html = html.replace(
        'current-menu-item page_item current_page_item menu-item-blog"><a href="./" aria-current="page" class="elementor-item elementor-item-active">Blog</a>',
        'menu-item-blog"><a href="../blog/" class="elementor-item">Blog</a>',
    )
    html = html.replace(
        'current-menu-item page_item current_page_item menu-item-blog"><a href="./" aria-current="page" class="elementor-item elementor-item-active" tabindex="-1">Blog</a>',
        'menu-item-blog"><a href="../blog/" class="elementor-item" tabindex="-1">Blog</a>',
    )

    listing = f"""<div class="jrh-blog-list">
<p class="jrh-blog-cluster-link"><a href="../blog/">Blog</a> · {CATEGORY_NAME}</p>
{article_listing_html("./")}
\t\t\t\t\t</div>"""

    html = re.sub(
        r'<div class="jrh-blog-list">.*?</div>\s*</div>\s*</div>',
        f'<div class="elementor-widget-container">\n\t\t\t\t\t{listing}\n\t\t\t\t</div>\n\t\t\t\t</div>',
        html,
        count=1,
        flags=re.DOTALL,
    )

    schema = (
        '{"@context":"https://schema.org","@graph":[{"@type":"CollectionPage","@id":"'
        + NEW_ADU_PREFIX
        + '#webpage","name":"'
        + CATEGORY_NAME
        + '","description":"'
        + CATEGORY_DESC.replace('"', '\\"')
        + '","url":"'
        + NEW_ADU_PREFIX
        + '","inLanguage":"en-US","isPartOf":{"@id":"https://jrhconstructions.com/blog/#webpage"}}]}'
    )
    html = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        f'<script type="application/ld+json">{schema}</script>',
        html,
        count=1,
        flags=re.DOTALL,
    )
    return html


def update_blog_index() -> None:
    index_path = BLOG / "index.html"
    html = index_path.read_text(encoding="utf-8")

    listing = f"""<div class="jrh-blog-list">
{category_listing_html()}
\t\t\t\t\t</div>"""

    html = re.sub(
        r'<div class="jrh-blog-list">.*?</div>\s*</div>\s*</div>',
        f'<div class="elementor-widget-container">\n\t\t\t\t\t{listing}\n\t\t\t\t</div>\n\t\t\t\t</div>',
        html,
        count=1,
        flags=re.DOTALL,
    )
    index_path.write_text(html, encoding="utf-8")


def move_articles() -> None:
    ADU.mkdir(parents=True, exist_ok=True)

    for art in ARTICLES:
        slug = art["slug"]
        src = BLOG / slug / "index.html"
        dst_dir = ADU / slug
        dst_dir.mkdir(parents=True, exist_ok=True)

        html = fix_article_html(src.read_text(encoding="utf-8"), slug)
        (dst_dir / "index.html").write_text(html, encoding="utf-8")

        redirect = redirect_html(f"/{CATEGORY}/{slug}/")
        (BLOG / slug / "index.html").write_text(redirect, encoding="utf-8")


def move_scripts() -> None:
    src_scripts = BLOG / "_scripts"
    dst_scripts = ADU / "_scripts"
    if dst_scripts.exists():
        shutil.rmtree(dst_scripts)
    shutil.copytree(src_scripts, dst_scripts)

    for name in ("generate-adu-post.py", "generate-adu-cost-post.py"):
        path = dst_scripts / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace('BLOG = ROOT / "blog"', f'ADU = ROOT / "{CATEGORY}"')
        text = text.replace("BLOG / SLUG", "ADU / SLUG")
        text = text.replace("BLOG / PILLAR_SLUG", "ADU / PILLAR_SLUG")
        text = text.replace('BLOG / "index.html"', 'ROOT / "blog" / "index.html"')
        text = text.replace("update_blog_index()", "update_adu_index()")
        text = text.replace("def update_blog_index", "def update_adu_index")
        text = text.replace("index_path = BLOG /", "index_path = ADU /")
        text = text.replace(
            f"https://jrhconstructions.com/blog/{CATEGORY}/",
            NEW_ADU_PREFIX,
        )
        text = text.replace("https://jrhconstructions.com/blog/", NEW_ADU_PREFIX)
        text = text.replace(
            '"isPartOf":{"@id":"https://jrhconstructions.com/blog/#webpage"}',
            f'"isPartOf":{{"@id":"{NEW_ADU_PREFIX}#webpage"}}',
        )
        text = text.replace(
            f'CANONICAL = f"https://jrhconstructions.com/blog/{{SLUG}}/"',
            f'CANONICAL = f"https://jrhconstructions.com/{CATEGORY}/{{SLUG}}/"',
        )
        text = text.replace(
            f'PILLAR_CANONICAL = f"https://jrhconstructions.com/blog/{{PILLAR_SLUG}}/"',
            f'PILLAR_CANONICAL = f"https://jrhconstructions.com/{CATEGORY}/{{PILLAR_SLUG}}/"',
        )
        text = text.replace("| JRH Constructions Blog</title>", f"| JRH Constructions {CATEGORY_NAME}</title>")
        path.write_text(text, encoding="utf-8")


def update_apply_internal_links() -> None:
    path = ROOT / "scripts" / "apply-internal-links.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        'blog_href = "../blog/what-is-an-accessory-dwelling-unit-adu/"',
        f'blog_href = "../{CATEGORY}/what-is-an-accessory-dwelling-unit-adu/"',
    )
    text = text.replace(
        'blog_href = "../../blog/what-is-an-accessory-dwelling-unit-adu/"',
        f'blog_href = "../../{CATEGORY}/what-is-an-accessory-dwelling-unit-adu/"',
    )
    text = text.replace(
        'post = ROOT / "blog/what-is-an-accessory-dwelling-unit-adu/index.html"',
        f'post = ROOT / "{CATEGORY}/what-is-an-accessory-dwelling-unit-adu/index.html"',
    )
    text = text.replace(
        'print("linked: blog/what-is-an-accessory-dwelling-unit-adu/index.html")',
        f'print("linked: {CATEGORY}/what-is-an-accessory-dwelling-unit-adu/index.html")',
    )
    path.write_text(text, encoding="utf-8")


def append_category_css() -> None:
    css_path = BLOG / "styles.css"
    css = css_path.read_text(encoding="utf-8")
    if ".jrh-blog-category-item" in css:
        return
    css += """

.jrh-blog-category-item{border-bottom:1px solid #eee}
"""
    css_path.write_text(css, encoding="utf-8")


def main() -> None:
    move_articles()
    (ADU / "index.html").write_text(build_category_index(), encoding="utf-8")
    update_blog_index()
    move_scripts()
    update_apply_internal_links()
    append_category_css()
    print(f"Created {ADU}/ with {len(ARTICLES)} articles")
    print(f"Updated {BLOG}/index.html with ADU category")
    print("Old /blog/<slug>/ URLs now redirect to /adu/<slug>/")


if __name__ == "__main__":
    main()
