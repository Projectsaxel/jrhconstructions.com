#!/usr/bin/env python3
"""Generate ADU blog post and update blog index."""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADU = ROOT / "adu"
SLUG = "what-is-an-accessory-dwelling-unit-adu"
POST_DIR = ADU / SLUG
CONTENT_FILE = Path(__file__).parent / "adu-guide-content.html"

ARTICLE_HTML = CONTENT_FILE.read_text(encoding="utf-8").strip()

POST_TITLE = "What Is an Accessory Dwelling Unit (ADU)? The Complete Homeowner's Guide"
POST_EXCERPT = (
    "Learn what an Accessory Dwelling Unit is, the different types available, "
    "the benefits of building one, and why ADUs have become one of the most popular "
    "ways to increase living space and property value in the United States."
)
CANONICAL = f"https://jrhconstructions.com/adu/{SLUG}/"
OG_IMAGE = "https://jrhconstructions.com/services/images/accessory-dwelling-unit-service-scaled.webp"


def build_post_page() -> str:
    template = (ROOT / "blog" / "index.html").read_text(encoding="utf-8")

    html = template
    html = re.sub(r"<title>.*?</title>", f"<title>{POST_TITLE} | JRH Constructions ADU</title>", html, count=1)
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{POST_EXCERPT}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta name="keywords" content="[^"]*">',
        '<meta name="keywords" content="ADU, Accessory Dwelling Unit, ADU guide, Massachusetts ADU, backyard cottage, in-law suite, JRH Constructions">',
        html,
        count=1,
    )
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{CANONICAL}">', html, count=1)
    html = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{POST_TITLE}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{POST_EXCERPT}">',
        html,
        count=1,
    )
    html = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{CANONICAL}">', html, count=1)
    html = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG_IMAGE}">', html, count=1)
    html = re.sub(
        r'<meta property="og:image:secure_url" content="[^"]*">',
        f'<meta property="og:image:secure_url" content="{OG_IMAGE}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta name="twitter:title" content="[^"]*">',
        f'<meta name="twitter:title" content="{POST_TITLE}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta name="twitter:description" content="[^"]*">',
        f'<meta name="twitter:description" content="{POST_EXCERPT}">',
        html,
        count=1,
    )
    html = re.sub(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{OG_IMAGE}">', html, count=1)

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
        + '","datePublished":"2026-06-04","dateModified":"2026-06-04","author":{"@type":"Organization","name":"JRH Constructions"},"publisher":{"@type":"Organization","name":"JRH Constructions","logo":{"@type":"ImageObject","url":"https://jrhconstructions.com/blog/images/logo-jrh-constructions.webp"}},"mainEntityOfPage":{"@type":"WebPage","@id":"'
        + CANONICAL
        + '"},"inLanguage":"en-US","isPartOf":{"@id":"https://jrhconstructions.com/adu/#webpage"}}]}'
    )
    html = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        f'<script type="application/ld+json">{schema}</script>',
        html,
        count=1,
        flags=re.DOTALL,
    )

    # menu paths one level deeper
    html = html.replace('href="../"', 'href="../../"')
    html = html.replace('href="../about-us/"', 'href="../../about-us/"')
    html = html.replace('href="../contact-us/"', 'href="../../contact-us/"')
    html = html.replace('href="../services/', 'href="../../services/')
    html = html.replace('href="../boston-jrh-constructions/"', 'href="../../boston-jrh-constructions/"')
    html = html.replace('href="../quincy-jrh-constructions/"', 'href="../../quincy-jrh-constructions/"')
    html = html.replace('href="../cambridge-jrh-constructions/"', 'href="../../cambridge-jrh-constructions/"')
    html = html.replace('href="../sommerville-jrh-constuctions/"', 'href="../../sommerville-jrh-constuctions/"')
    html = html.replace('href="../peabody-jrh-constructions/"', 'href="../../peabody-jrh-constructions/"')
    html = html.replace('href="../malden-jrh-constructions/"', 'href="../../malden-jrh-constructions/"')
    html = html.replace('href="../newton-bathroom-kitchen-tile/"', 'href="../../newton-bathroom-kitchen-tile/"')
    html = html.replace('href="../other-cities-served/"', 'href="../../other-cities-served/"')
    html = html.replace('href="../privacy-policy/"', 'href="../../privacy-policy/"')
    html = html.replace('href="../terms-of-use/"', 'href="../../terms-of-use/"')

    html = html.replace(
        'current-menu-item page_item current_page_item menu-item-blog"><a href="./" aria-current="page" class="elementor-item elementor-item-active">Blog</a>',
        'menu-item-blog"><a href="../../blog/" class="elementor-item">Blog</a>',
    )
    html = html.replace(
        'current-menu-item page_item current_page_item menu-item-blog"><a href="./" aria-current="page" class="elementor-item elementor-item-active" tabindex="-1">Blog</a>',
        'menu-item-blog"><a href="../../blog/" class="elementor-item" tabindex="-1">Blog</a>',
    )

    html = html.replace(
        '<h1 class="elementor-heading-title elementor-size-default">Blog</h1>',
        f'<h1 class="elementor-heading-title elementor-size-default">{POST_TITLE}</h1>',
    )
    html = html.replace(
        "<p>Remodeling tips, project guides, and construction insights for homeowners in Boston and Greater Boston.</p>",
        f"<p>{POST_EXCERPT}</p>",
    )

    article_block = f'''\t\t\t\t\t\t<div class="elementor-element elementor-element-blog-article exad-sticky-section-no exad-glass-effect-no elementor-widget elementor-widget-text-editor">
\t\t\t\t<div class="elementor-widget-container">
\t\t\t\t\t<div class="jrh-blog-article">
{ARTICLE_HTML}
\t\t\t\t\t</div>
\t\t\t\t</div>
\t\t\t\t</div>'''

    html = re.sub(
        r'<div class="elementor-element elementor-element-blog-intro.*?<div class="elementor-widget-container">\s*<p>Our blog is coming soon.*?</div>\s*</div>',
        article_block,
        html,
        count=1,
        flags=re.DOTALL,
    )

    return html


def update_blog_index() -> None:
    import subprocess
    import sys

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sync-blog-index.py")],
        check=True,
    )


def append_post_styles() -> None:
    css_path = ROOT / "blog" / "styles.css"
    css = css_path.read_text(encoding="utf-8")
    marker = "/* Blog post article */"
    if marker in css:
        return
    css += """

/* Blog post article */
.jrh-blog-article{font-family:"Sora",Sans-serif;color:var(--e-global-color-6939b83);font-size:16px;line-height:1.75;max-width:820px;margin:0 auto;text-align:left}
.jrh-blog-article h1{font-size:2rem;line-height:1.25;margin:0 0 1rem;font-weight:600}
.jrh-blog-article h2{font-size:1.5rem;line-height:1.3;margin:2rem 0 .75rem;font-weight:600}
.jrh-blog-article h3{font-size:1.25rem;line-height:1.35;margin:1.5rem 0 .5rem;font-weight:600}
.jrh-blog-article h4{font-size:1.05rem;line-height:1.4;margin:1rem 0 .35rem;font-weight:600}
.jrh-blog-article p{margin:0 0 1rem}
.jrh-blog-article ul,.jrh-blog-article ol{margin:0 0 1rem 1.25rem;padding:0}
.jrh-blog-article li{margin-bottom:.35rem}
.jrh-blog-article table{width:100%;border-collapse:collapse;margin:0 0 1.25rem;font-size:.95rem}
.jrh-blog-article th,.jrh-blog-article td{border:1px solid #e5e5e5;padding:.6rem .75rem;text-align:left;vertical-align:top}
.jrh-blog-article thead th{background:#f7f7f7;font-weight:600}
.jrh-blog-article em{font-style:italic}
.jrh-blog-article strong{font-weight:600}

.jrh-blog-list{max-width:820px;margin:0 auto;text-align:left}
.jrh-blog-list-item{padding:1.5rem 0;border-bottom:1px solid #eee}
.jrh-blog-list-title{font-family:"Sora",Sans-serif;font-size:1.35rem;line-height:1.35;margin:0 0 .75rem;font-weight:600}
.jrh-blog-list-title a{color:inherit;text-decoration:none}
.jrh-blog-list-title a:hover{text-decoration:underline}
.jrh-blog-list-excerpt{font-family:"Sora",Sans-serif;font-size:15px;line-height:1.65;margin:0 0 .75rem;color:var(--e-global-color-6939b83)}
.jrh-blog-list-link{margin:0;font-family:"Sora",Sans-serif}
.jrh-blog-list-link a{font-weight:600;text-decoration:none}
.jrh-blog-list-link a:hover{text-decoration:underline}

@media(max-width:767px){
.jrh-blog-article h1{font-size:1.6rem}
.jrh-blog-article h2{font-size:1.3rem}
.jrh-blog-article table{display:block;overflow-x:auto;-webkit-overflow-scrolling:touch}
}
"""
    css_path.write_text(css, encoding="utf-8")


def main() -> None:
    POST_DIR.mkdir(parents=True, exist_ok=True)
    (POST_DIR / "index.html").write_text(build_post_page(), encoding="utf-8")
    update_blog_index()
    append_post_styles()
    print(f"Created {POST_DIR / 'index.html'}")
    print(f"Updated {ROOT / 'blog' / 'index.html'}")


if __name__ == "__main__":
    main()
