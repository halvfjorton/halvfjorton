#!/usr/bin/env python3
"""Generate the Halv Fjorton static site."""

import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
from cms_build import run_cms_build_steps  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT
HOME_SOURCE = ROOT / "scripts/templates/home/index.html"
SITE = "https://halvfjorton.se"
OG = f"{SITE}/assets/img/og.jpg"
# Full-bleed object-fit:cover heroes on portrait phones need far more than 100vw (see alt-hero CSS).
HERO_HOME_COVER_SCALE = 1.35  # mobile Ken Burns peaks ~1.28 on .alt-hero__slide img
SERVICE_HERO_COVER_SCALE_SLIDESHOW = 1.12  # slideshow img scale(1.06)
SERVICE_HERO_COVER_SCALE_STATIC = 1.05


def hero_cover_sizes(img_width: int, img_height: int, cover_scale: float) -> str:
    aspect = round(img_width / img_height, 4)
    return (
        f"(max-width: 900px) calc(max(100vw, 100svh * {aspect}) * {cover_scale}), 100vw"
    )


_HOME_HERO_IMG_TAG = re.compile(
    r"<img([^>]*gallery/halvfjorton-\d+-hero[^>]*)>",
    re.IGNORECASE,
)


def _patch_img_tag_sizes(tag_inner: str, cover_scale: float) -> str:
    width_m = re.search(r'\bwidth="(\d+)"', tag_inner)
    height_m = re.search(r'\bheight="(\d+)"', tag_inner)
    if not width_m or not height_m:
        return f"<img{tag_inner}>"
    sizes = hero_cover_sizes(int(width_m.group(1)), int(height_m.group(1)), cover_scale)
    inner = re.sub(r'\s*sizes="[^"]*"', "", tag_inner)
    return f'<img{inner} sizes="{sizes}">'


def patch_home_hero_src_sizes(html: str) -> str:
    html = _HOME_HERO_IMG_TAG.sub(
        lambda m: _patch_img_tag_sizes(m.group(1), HERO_HOME_COVER_SCALE),
        html,
    )
    first_hero_sizes = hero_cover_sizes(2400, 1600, HERO_HOME_COVER_SCALE)
    html = re.sub(
        r'(<link rel="preload" as="image"[^>]*halvfjorton-01-hero[^>]*imagesizes=")[^"]*(")',
        rf"\g<1>{first_hero_sizes}\2",
        html,
        count=1,
    )
    return html
CLOUDFLARE_WEB_ANALYTICS_TOKEN = "920bacfc410443e3805ce3c92c173af5"
CLOUDFLARE_WEB_ANALYTICS_SNIPPET = (
    "<!-- Cloudflare Web Analytics -->"
    '<script defer src=\'https://static.cloudflareinsights.com/beacon.min.js\' '
    f'data-cf-beacon=\'{{"token": "{CLOUDFLARE_WEB_ANALYTICS_TOKEN}"}}\'></script>'
    "<!-- End Cloudflare Web Analytics -->\n"
)
CLOUDFLARE_ANALYTICS_MARKER = "static.cloudflareinsights.com/beacon.min.js"
ORGANIZATION_JSON = ROOT / "assets/schema/organization.json"
H14_LOGO = ROOT / "assets/img/h14-logo.svg"
BRAND_TITLE = "Halv Fjorton | coverband & bröllopsband i Småland och Skåne"
WEDDING_VIDEO_ID = "V2Nb8jMKUCk"
WEDDING_VIDEO_TITLE = "Signed Sealed Delivered - Halv Fjorton"
TALLY_EMBED_SRC = (
    "https://tally.so/embed/n0xyqQ?alignLeft=1&hideTitle=1&transparentBackground=1&dynamicHeight=1"
)
TALLY_PUBLIC_URL = "https://tally.so/r/n0xyqQ"
OFFERT_URL = f"{SITE}/kontakt/#offert"
SOULFUL_CHRISTMAS_TICKETS = "https://www.nygatan6.se/kalender/a-soulful-christmas/"
SOULFUL_CHRISTMAS_IMG = "/assets/img/events/a-soulful-christmas-2026"
SOULFUL_CHRISTMAS_START = "2026-12-12T00:00:00+01:00"
SOULFUL_CHRISTMAS_END = "2026-12-12T22:00:00+01:00"
SOULFUL_LUCIA_2025_VIDEO_ID = "CFr_XLrILmY"
SOULFUL_LUCIA_2025_IMG = "/assets/img/events/a-soulful-lucia-2025"

CONTACT_USPS = [
    "Vi svarar inom 24 timmar",
    "Skräddarsytt efter era önskemål",
    "En kontakt hela vägen från förfrågan till sista låten",
    "Åttamannaband med blås",
    "Spelar i Småland och Skåne: Växjö, Kalmar, Jönköping, Malmö, Lund, Helsingborg",
    "Sedan 2018",
]

HOME_OFFERT_USPS: list[tuple[str, str]] = [
    ("Svar inom 24 timmar", "check"),
    ("Åttamannaband med blåssektion", "check"),
]

ALT_ICON_CHECK_SVG = (
    '<svg class="alt-facts__icon" width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'aria-hidden="true">'
    '<path d="M5.5 12.5 9.5 16.5 18.5 7.5" stroke="currentColor" stroke-width="1.75" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)

ALT_ICON_PIN_SVG = (
    '<svg class="alt-facts__icon" width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'aria-hidden="true">'
    '<path d="M12 21s7-4.5 7-11a7 7 0 1 0-14 0c0 6.5 7 11 7 11Z" stroke="currentColor" '
    'stroke-width="1.5" stroke-linejoin="round"/>'
    '<circle cx="12" cy="10" r="2.25" stroke="currentColor" stroke-width="1.5"/>'
    "</svg>"
)


def home_alt_facts_block() -> str:
    return f"""      <div class="alt-facts">
        <div class="alt-facts__inner">
          <div class="alt-facts__items">
            <span class="alt-facts__item">{ALT_ICON_CHECK_SVG}Åttamannaband</span>
            <span class="alt-facts__item">{ALT_ICON_CHECK_SVG}Blåssektion</span>
          </div>
          <span class="alt-facts__region alt-facts__item">{ALT_ICON_PIN_SVG}Växjö, Småland</span>
        </div>
      </div>"""


def offert_usp_list_markup(usps: list[tuple[str, str]] | list[str]) -> str:
    lines: list[str] = []
    for item in usps:
        if isinstance(item, tuple):
            label, kind = item
            cls = ' class="list-check__item--pin"' if kind == "pin" else ""
        else:
            label, cls = item, ""
        lines.append(f"            <li{cls}>{esc(label)}</li>")
    return "\n".join(lines)

OFFERT_EMAIL_LINK_TEXT = "Föredrar du e-post? Mejla oss här"

FOOTER_INTEGRITETSPOLICY_HREF = "/integritetspolicy/"


def contact_form_consent_markup() -> str:
    return f"""            <p class="contact-offert__consent">Genom att skicka godkänner du att vi sparar dina uppgifter för att besvara din förfrågan. Läs mer i vår <a href="{FOOTER_INTEGRITETSPOLICY_HREF}">integritetspolicy</a>.</p>"""


def offert_email_mail_markup() -> str:
    return f"""          <p class="contact-offert__mail">
            <a class="alt-btn alt-btn--primary" href="mailto:halvfjorton@gmail.com">{OFFERT_EMAIL_LINK_TEXT}</a>
          </p>
"""


NAV_SERVICES = [
    ("/brollop/", "Bröllop"),
    ("/foretag/", "Företag"),
    ("/fest-och-mingel/", "Fest och mingel"),
]

NAV_PRIMARY = [
    ("/", "Hem"),
    ("/om-oss/", "Om oss"),
    ("/lyssna/", "Lyssna"),
    ("/faq/", "FAQ"),
    ("/kontakt/", "Kontakt"),
]

SITEMAP_PATHS = [
    "/",
    "/brollop/",
    "/foretag/",
    "/julkonsert/",
    "/konserter/",
    "/fest-och-mingel/",
    "/om-oss/",
    "/lyssna/",
    "/faq/",
    "/kontakt/",
]

HOME_NAV_LINKS = [
    ("/konserter/", "Konserter"),
    ("/om-oss/", "Om oss"),
    ("/faq/", "FAQ"),
    ("/lyssna/", "Lyssna"),
    ("/kontakt/", "Kontakt"),
]

LOKAL_TEKNIK_COPY = (
    "Tekniska behov tar vi i offerten utifrån lokal och program. "
    "Vid större saler eller särskilda önskemål har vi kontakter bland uthyrare."
)

BUILD_YEAR = datetime.now(timezone.utc).year

ORG_STREET_ADDRESS = "Fabriksgatan 12"
ORG_POSTAL_CITY_LINE = "342 50 Vislanda"
ORG_POSTAL_ADDRESS_LD = {
    "@type": "PostalAddress",
    "addressLocality": "Växjö",
    "addressRegion": "Kronobergs län",
    "addressCountry": "SE",
}

INSTAGRAM_PROFILE_URL = "https://www.instagram.com/halvfjorton/"
INSTAGRAM_ICON_BTN = """            <svg class="alt-btn__icon" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" stroke-width="1.75"/>
              <circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.75"/>
              <circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>
            </svg>"""

FOOTER_SOCIAL_ICON_SVG = (
    '<svg class="alt-btn__icon" width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{inner}</svg>'
)
FOOTER_INSTAGRAM_ICON = FOOTER_SOCIAL_ICON_SVG.format(
    inner=(
        '<rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" stroke-width="1.75"/>'
        '<circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.75"/>'
        '<circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>'
    )
)
FOOTER_YOUTUBE_ICON = FOOTER_SOCIAL_ICON_SVG.format(
    inner=(
        '<path d="M20.5 7.2a1.6 1.6 0 0 0-1.12-.74C17.7 6.25 12 6.25 12 6.25s-5.7 0-7.38.21a1.6 1.6 0 0 0-1.12.74A16.8 16.8 0 0 0 3 12a16.8 16.8 0 0 0 .5 4.8 1.6 1.6 0 0 0 1.12.74c1.68.21 7.38.21 7.38.21s5.7 0 7.38-.21a1.6 1.6 0 0 0 1.12-.74A16.8 16.8 0 0 0 21 12a16.8 16.8 0 0 0-.5-4.8z" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"/>'
        '<path d="M10.25 15.02V8.98L15.5 12l-5.25 3.02z" fill="currentColor"/>'
    )
)


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def faq_item_markup(question: str, answer: str) -> str:
    return f"""          <details class="alt-faq__item">
            <summary class="alt-faq__question">{esc(question)}</summary>
            <div class="alt-faq__answer">
              <p>{esc(answer)}</p>
            </div>
          </details>"""


def faq_list_two_columns(qa_pairs: list[tuple[str, str]]) -> str:
    """Two-column CSS grid (row order); stable columns + paired row heights when collapsed."""
    items = "\n".join(faq_item_markup(q, a) for q, a in qa_pairs)
    return f"""        <div class="alt-faq__list alt-faq__list--cols" data-faq>
{items}
        </div>"""


def _indent_ld(data: dict) -> str:
    raw = json.dumps(data, indent=2, ensure_ascii=False)
    return "\n".join(f"  {line}" for line in raw.splitlines())


def _ld_fragment_to_dict(fragment: str) -> dict:
    return json.loads(fragment.strip())


def jsonld_graph_markup(fragments: list[str]) -> str:
    graph: list[dict] = []
    for fragment in fragments:
        node = _ld_fragment_to_dict(fragment)
        node.pop("@context", None)
        graph.append(node)
    return _indent_ld({"@context": "https://schema.org", "@graph": graph})


def head_resource_hints() -> str:
    return '  <link rel="preconnect" href="https://static.cloudflareinsights.com" crossorigin>\n'


def music_group_ld() -> str:
    data = json.loads(ORGANIZATION_JSON.read_text(encoding="utf-8"))
    return _indent_ld(data)


def load_org() -> dict:
    return json.loads(ORGANIZATION_JSON.read_text(encoding="utf-8"))


BRAND_MARK_PX = 56

def contact_page_ld() -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "url": f"{SITE}/kontakt/",
        "name": "Kontakta Halv Fjorton",
        "description": "Begär offert till Halv Fjorton | coverband för bröllop, företag och fest i södra Sverige.",
        "mainEntity": {
            "@type": "Organization",
            "name": "Halv Fjorton",
            "url": f"{SITE}/",
            "email": "halvfjorton@gmail.com",
            "address": ORG_POSTAL_ADDRESS_LD,
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "booking",
                "email": "halvfjorton@gmail.com",
                "areaServed": "SE",
                "availableLanguage": ["sv", "en"],
            },
        },
    }
    return _indent_ld(data)


def tally_iframe_markup() -> str:
    return f"""          <iframe
            data-tally-src="{TALLY_EMBED_SRC}"
            loading="lazy"
            title="Offertförfrågan Halv Fjorton"
            width="100%"
            height="420"
            frameborder="0"
            marginheight="0"
            marginwidth="0"
          ></iframe>"""


def integritetspolicy_page_body() -> str:
    return f"""    <section class="section alt-legal-page">
      <div class="alt-svc-wrap alt-legal-page__inner">
        <h1 class="alt-legal-page__title">Integritetspolicy</h1>
        <div class="alt-legal-page__body">
          <p>Denna policy beskriver hur Halv Fjorton behandlar personuppgifter när du kontaktar oss via webbplatsen.</p>
          <h2 class="alt-legal-page__heading">Personuppgiftsansvarig</h2>
          <p>Halv Fjorton, organisationsnummer 769641-5418.<br>
{ORG_STREET_ADDRESS}<br>
{ORG_POSTAL_CITY_LINE}<br>
Kontakt: <a href="mailto:halvfjorton@gmail.com">halvfjorton@gmail.com</a>.</p>
          <h2 class="alt-legal-page__heading">Vad vi samlar in</h2>
          <p>Namn, e-postadress, telefonnummer om du anger det, och meddelandet du skickar i kontaktformuläret.</p>
          <h2 class="alt-legal-page__heading">Kontaktformulär</h2>
          <p>Formuläret för offert och kontakt tillhandahålls av Tally (Tally BV, Belgien, EU), som agerar som personuppgiftsbiträde för Halv Fjorton. De uppgifter du lämnar, bland annat namn, e-postadress och uppgifter om evenemanget, används endast för att besvara din förfrågan. För att formuläret ska fungera sparar Tally viss tekniskt nödvändig information lokalt i din webbläsare. Den används inte för spårning eller marknadsföring. Mer om hur Tally behandlar personuppgifter finns i <a href="https://tally.so/help/privacy-policy">Tallys integritetspolicy</a>.</p>
          <h2 class="alt-legal-page__heading">Varför</h2>
          <p>Vi använder uppgifterna för att besvara din förfrågan och ta fram offert när det behövs.</p>
          <h2 class="alt-legal-page__heading">Hur länge</h2>
          <p>Förfrågningar som inte leder till en bokning raderar vi senast 24 månader efter att de kom in. Uppgifter som hör till en bokning, som avtal och fakturor, sparar vi så länge bokföringslagen kräver.</p>
          <h2 class="alt-legal-page__heading">Delning</h2>
          <p>Vi säljer inte personuppgifter och delar dem inte med tredje part i marknadsföringssyfte.</p>
          <h2 class="alt-legal-page__heading">Webbstatistik</h2>
          <p>Vi använder Cloudflare Web Analytics som räknar besök anonymt utan cookies eller lagring av personuppgifter.</p>
          <h2 class="alt-legal-page__heading">Dina rättigheter</h2>
          <p>Du kan begära tillgång, rättelse eller radering av dina uppgifter. Mejla <a href="mailto:halvfjorton@gmail.com">halvfjorton@gmail.com</a>.</p>
        </div>
      </div>
    </section>"""


def kontakt_page_body() -> str:
    usp_items = offert_usp_list_markup(HOME_OFFERT_USPS)
    return f"""    <section class="alt-contact-page section" id="offert" aria-labelledby="kontakt-rubrik">
      <div class="alt-contact-offert__wrap alt-contact-page__stack">
        <div class="contact-offert__grid">
          <div class="contact-offert__copy">
            <header class="alt-contact-page__intro">
              <h1 id="kontakt-rubrik">Kontakta oss</h1>
              <p class="contact-offert__lead">Fyll i formuläret så återkommer vi, oftast inom 24 timmar. Vi utgår från Växjö och spelar på begäran i hela södra Sverige, till exempel Kalmar, Jönköping, Malmö, Lund och Helsingborg.</p>
            </header>
            <ul class="list-check">
{usp_items}
            </ul>
{offert_email_mail_markup()}
          </div>
          <div class="contact-offert__form-col">
            <div class="contact-offert__form tally-card">
              <noscript>
                <p><a href="{TALLY_PUBLIC_URL}">Öppna offertformuläret på Tally</a> om det inte visas här.</p>
              </noscript>
{tally_iframe_markup()}
            </div>
{contact_form_consent_markup()}
          </div>
        </div>
      </div>
    </section>
    <section class="alt-contact-page__channels section section--tight" aria-label="Direktkontakt">
      <div class="alt-contact-offert__wrap alt-contact-page__channels-inner">
        <a class="alt-contact-page__link" href="mailto:halvfjorton@gmail.com">halvfjorton@gmail.com</a>
        <a class="alt-contact-page__link" href="https://www.instagram.com/halvfjorton/" rel="noopener noreferrer">Instagram @halvfjorton</a>
      </div>
    </section>"""


def contact_offert_section(
    heading: str = "Begär offert",
    lead: str | None = None,
    section_class: str = "contact-offert section",
    wrap_class: str = "wrap contact-offert__grid",
    usps: list[str] | None = None,
    include_mail_button: bool = True,
) -> str:
    usp_source = usps if usps is not None else CONTACT_USPS
    usp_items = offert_usp_list_markup(usp_source[:3])
    lead_html = f'        <p class="contact-offert__lead">{esc(lead)}</p>\n' if lead else ""
    mail_html = offert_email_mail_markup() if include_mail_button else ""
    return f"""    <section class="{section_class}" id="offert" aria-labelledby="offert-rubrik">
      <div class="{wrap_class}">
        <div class="contact-offert__copy">
          <h2 id="offert-rubrik">{esc(heading)}</h2>
{lead_html}          <ul class="list-check">
{usp_items}
          </ul>
{mail_html}        </div>
        <div class="contact-offert__form-col">
          <div class="contact-offert__form tally-card">
            <noscript>
              <p><a href="{TALLY_PUBLIC_URL}">Öppna offertformuläret på Tally</a> om det inte visas här.</p>
            </noscript>
{tally_iframe_markup()}
          </div>
{contact_form_consent_markup()}
        </div>
      </div>
    </section>"""


def font_preloads(asset_root: str = "/assets") -> str:
    root = asset_root.rstrip("/")
    return f"""  <link rel="preload" href="{root}/fonts/InterVariable.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{root}/fonts/Outfit-Variable.woff2" as="font" type="font/woff2" crossorigin>"""


SITE_THEME_COLOR = "#121212"


def favicon_head_links() -> str:
    return f"""  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="{SITE_THEME_COLOR}">"""


def nav_path(href: str, prefix: str = "") -> str:
    if not prefix:
        return href
    return "../" + href.lstrip("/")


def nav_toggle_markup(panel_id: str = "meny") -> str:
    return f"""      <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="{panel_id}" aria-label="Öppna meny">
        <span class="nav-toggle__bars" aria-hidden="true"></span>
      </button>"""


def alt_nav_toggle_markup(panel_id: str = "mobile-menu") -> str:
    return f"""      <button class="nav-toggle alt-nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="{panel_id}" aria-label="Öppna meny">
        <span class="nav-toggle__bars" aria-hidden="true"></span>
      </button>"""


def alt_header_mobile_controls_markup(panel_id: str = "mobile-menu") -> str:
    close = mobile_menu_close_markup().replace(
        'class="mobile-menu__close"',
        'class="mobile-menu__close alt-header__menu-close"',
        1,
    )
    return alt_nav_toggle_markup(panel_id) + "\n" + close


def mobile_menu_close_markup() -> str:
    return """      <button type="button" class="mobile-menu__close" data-nav-close aria-label="Stäng meny">
        <span class="mobile-menu__close-icon" aria-hidden="true"></span>
      </button>"""


def alt_header_scroll_bootstrap_script() -> str:
    return """  <script>
(function () {
  document.documentElement.classList.add("alt-header-state-init");
  var header = document.querySelector(".alt-header");
  if (!header) return;
  if ((window.scrollY || document.documentElement.scrollTop || 0) > 10) {
    header.classList.add("is-solid");
  }
})();
  </script>"""


def nav_services_dropdown(current_path: str, prefix: str = "", menu_id: str = "nav-tjanster") -> str:
    service_paths = {p for p, _ in NAV_SERVICES}
    expanded = "true" if current_path in service_paths else "false"
    items = []
    for href, label in NAV_SERVICES:
        current = ' aria-current="page"' if href == current_path else ""
        items.append(
            f'              <li role="none"><a role="menuitem" href="{nav_path(href, prefix)}"{current}>{label}</a></li>'
        )
    submenu = "\n".join(items)
    return f"""          <li class="nav-item nav-item--dropdown" data-nav-dropdown>
            <button type="button" class="nav-dropdown__trigger" data-nav-dropdown-trigger aria-expanded="{expanded}" aria-controls="{menu_id}" id="{menu_id}-btn">
              Tjänster
              <span class="nav-dropdown__chevron" aria-hidden="true"></span>
            </button>
            <ul class="nav-dropdown__menu" id="{menu_id}" role="menu" aria-labelledby="{menu_id}-btn" data-nav-dropdown-menu>
{submenu}
            </ul>
          </li>"""


def mobile_nav_services_dropdown(current_path: str, prefix: str = "", menu_id: str = "mobile-nav-tjanster") -> str:
    service_paths = {p for p, _ in NAV_SERVICES}
    expanded = "true" if current_path in service_paths else "false"
    items = []
    for href, label in NAV_SERVICES:
        current = ' aria-current="page"' if href == current_path else ""
        items.append(
            f'              <li role="none"><a role="menuitem" href="{nav_path(href, prefix)}"{current}>{label}</a></li>'
        )
    submenu = "\n".join(items)
    return f"""          <li class="nav-item nav-item--dropdown" data-nav-dropdown>
            <button type="button" class="nav-dropdown__trigger" data-nav-dropdown-trigger aria-expanded="{expanded}" aria-controls="{menu_id}" id="{menu_id}-btn">
              Tjänster
              <span class="nav-dropdown__chevron" aria-hidden="true"></span>
            </button>
            <div class="mobile-menu__submenu">
              <div class="mobile-menu__submenu-inner">
                <ul class="nav-dropdown__menu" id="{menu_id}" role="menu" aria-labelledby="{menu_id}-btn" data-nav-dropdown-menu>
{submenu}
                </ul>
              </div>
            </div>
          </li>"""


def render_nav_list(current_path: str, prefix: str = "", include_home: bool = True, menu_id: str = "nav-tjanster") -> str:
    items = []
    if include_home:
        current = ' aria-current="page"' if current_path == "/" else ""
        items.append(f'          <li><a href="{nav_path("/", prefix)}"{current}>Hem</a></li>')
    items.append(nav_services_dropdown(current_path, prefix, menu_id))
    for href, label in NAV_PRIMARY:
        if href == "/":
            continue
        current = ' aria-current="page"' if href == current_path else ""
        items.append(f'          <li><a href="{nav_path(href, prefix)}"{current}>{label}</a></li>')
    return "\n".join(items)


def home_nav_links_markup(
    current_path: str = "/",
    prefix: str = "",
    menu_id: str = "nav-tjanster",
) -> str:
    items = [nav_services_dropdown(current_path, prefix, menu_id)]
    for href, label in HOME_NAV_LINKS:
        current = ' aria-current="page"' if href == current_path else ""
        items.append(f'          <li><a href="{nav_path(href, prefix)}"{current}>{label}</a></li>')
    return "\n".join(items)


def mobile_nav_links_markup(
    current_path: str = "/",
    prefix: str = "",
    menu_id: str = "mobile-nav-tjanster",
) -> str:
    items = [mobile_nav_services_dropdown(current_path, prefix, menu_id)]
    for href, label in HOME_NAV_LINKS:
        current = ' aria-current="page"' if href == current_path else ""
        items.append(f'          <li><a href="{nav_path(href, prefix)}"{current}>{label}</a></li>')
    return "\n".join(items)


def home_nav_block(current_path: str = "/", offert_href: str = "#offert", prefix: str = "") -> str:
    return f"""      <nav class="alt-nav" aria-label="Huvudmeny">
        <ul class="alt-nav__links nav-list" id="alt-meny">
{home_nav_links_markup(current_path, prefix, "nav-tjanster")}
        </ul>
        <a class="alt-btn alt-btn--primary alt-nav__cta-desktop" href="{offert_href}">Begär offert</a>
      </nav>"""


def mobile_menu_block(
    current_path: str = "/",
    offert_href: str = "#offert",
    prefix: str = "",
) -> str:
    return f"""  <div class="mobile-menu" id="mobile-menu" data-mobile-menu hidden aria-hidden="true">
    <nav class="mobile-menu__nav" aria-label="Mobilmeny">
      <ul class="mobile-menu__list nav-list" data-nav-panel>
{mobile_nav_links_markup(current_path, prefix, "mobile-nav-tjanster")}
      </ul>
    </nav>
    <div class="mobile-menu__foot">
      <a class="alt-btn alt-btn--primary mobile-menu__cta" href="{offert_href}">Begär offert</a>
    </div>
  </div>"""


def modern_footer_markup() -> str:
    return f"""  <footer class="site-footer site-footer--columns" aria-label="Sidfot">
    <div class="site-footer__inner">
      <div class="site-footer__columns">
        <div class="site-footer__brand">
          <a class="site-footer__brand-mark" href="/" aria-label="Halv Fjorton">
            <span class="site-footer__title">Halv Fjorton</span>
          </a>
          <p class="site-footer__tagline">Coverband och partyband med rötter i Växjö, Småland.</p>
        </div>
        <div class="site-footer__col">
          <p class="site-footer__col-label">Tjänster</p>
          <ul class="site-footer__links">
            <li><a href="/brollop/">Bröllop</a></li>
            <li><a href="/foretag/">Företag</a></li>
            <li><a href="/fest-och-mingel/">Fest och mingel</a></li>
          </ul>
        </div>
        <div class="site-footer__col">
          <p class="site-footer__col-label">Läs mer</p>
          <ul class="site-footer__links">
            <li><a href="/om-oss/">Om oss</a></li>
            <li><a href="/faq/">FAQ</a></li>
            <li><a href="/lyssna/">Lyssna</a></li>
            <li><a href="/konserter/">Konserter</a></li>
            <li><a href="{FOOTER_INTEGRITETSPOLICY_HREF}">Integritetspolicy</a></li>
          </ul>
        </div>
        <div class="site-footer__col">
          <p class="site-footer__col-label">Följ oss</p>
          <ul class="site-footer__links">
            <li><a class="site-footer__social-link" href="https://www.instagram.com/halvfjorton/" target="_blank" rel="noopener noreferrer">{FOOTER_INSTAGRAM_ICON}<span>Instagram</span></a></li>
            <li><a class="site-footer__social-link" href="https://www.youtube.com/@halvfjorton9292" target="_blank" rel="noopener noreferrer">{FOOTER_YOUTUBE_ICON}<span>YouTube</span></a></li>
          </ul>
        </div>
        <div class="site-footer__col site-footer__col--contact">
          <p class="site-footer__col-label">Kontakt</p>
          <ul class="site-footer__links site-footer__links--plain">
            <li><span class="site-footer__contact-line">Halv Fjorton ek. för.</span></li>
            <li><span class="site-footer__contact-line">Org.nr 769641-5418</span></li>
            <li><a class="site-footer__email" href="mailto:halvfjorton@gmail.com">halvfjorton@gmail.com</a></li>
          </ul>
        </div>
      </div>
      <hr class="site-footer__rule" />
      <p class="site-footer__legal site-footer__legal--bar">
        <span class="site-footer__legal-line">© <span data-footer-year>{BUILD_YEAR}</span> Halv Fjorton</span>
        <span class="site-footer__legal-place">Växjö, Småland</span>
      </p>
    </div>
  </footer>"""


def brand_logo_markup() -> str:
    svg = H14_LOGO.read_text(encoding="utf-8")
    svg = re.sub(
        r'<svg\s+',
        '<svg class="brand-mark" focusable="false" ',
        svg,
        count=1,
    )
    svg = re.sub(r'\bwidth="[^"]*"', f'width="{BRAND_MARK_PX}"', svg, count=1)
    svg = re.sub(r'\bheight="[^"]*"', f'height="{BRAND_MARK_PX}"', svg, count=1)
    return svg


def aeo_answer(text: str) -> str:
    return f'        <p class="aeo-answer">{text}</p>'


def video_facade(
    video_id: str,
    title: str,
    alt: str,
    width: int = 1280,
    height: int = 720,
) -> str:
    return f"""        <div class="embed video-facade" data-video-facade="{video_id}" data-video-title="{esc(title)}">
          <button type="button" class="video-facade__play" aria-label="Spela video: {esc(title)}">
            <img src="https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" alt="{esc(alt)}" width="{width}" height="{height}" loading="lazy" decoding="async">
          </button>
        </div>"""


LYSSNA_VIDEO_MODAL_SCRIPT = (
    '  <script src="/assets/js/lyssna-video-modal.js" defer></script>\n'
)
LYSSNA_REPERTOIRE_JSON = ROOT / "assets/data/lyssna-repertoire.json"
LYSSNA_POSTERS_DIR = ROOT / "assets/img/lyssna-posters"


def lyssna_yt_poster_path(video_id: str) -> str:
    return f"/assets/img/lyssna-posters/{video_id}.webp"


SPOTIFY_REPERTOIRE_PLAYLIST_URL = (
    "https://open.spotify.com/playlist/0q8DLuLfZE25an41tppmvu"
)
SPOTIFY_ICON_BTN = """            <svg class="alt-btn__icon" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 14.36c-.2.32-.62.42-.94.22-2.57-1.57-5.8-1.92-9.62-1.05-.37.08-.74-.16-.82-.53-.08-.37.16-.74.53-.82 4.12-.94 7.7-.55 10.6 1.17.32.2.42.62.22.94zm1.23-2.74c-.25.41-.78.54-1.19.29-2.94-1.81-7.42-2.33-10.9-1.28-.46.14-.95-.12-1.09-.58-.14-.46.12-.95.58-1.09 3.93-1.2 8.82-.62 12.16 1.55.41.25.54.78.29 1.19zm.1-2.86C14.03 8.85 8.16 8.63 4.41 9.76c-.55.17-1.13-.14-1.3-.69-.17-.55.14-1.13.69-1.3 4.28-1.3 10.84-1.05 15.09 1.48.5.3.66.94.36 1.44-.3.5-.94.66-1.44.36z"/>
            </svg>"""

LYSSNA_TILE_PLAY_ICON = """            <svg class="lyssna-video-tile__play-icon" viewBox="8.6 6.9 9.4 10.2" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <path d="M9.15 7.35v9.3l8.7-4.65-8.7-4.65z" fill="currentColor" stroke="currentColor" stroke-width="1.15" stroke-linejoin="round" stroke-linecap="round"/>
            </svg>"""


def _lyssna_poster_srcset(poster: str) -> str:
    if not poster.endswith("-1200w.webp"):
        return ""
    stem = poster[: -len("-1200w.webp")]
    if "/assets/img/gallery/halvfjorton-" in poster:
        return (
            f' srcset="{stem}-480w.webp 480w, {stem}-800w.webp 800w, '
            f'{stem}-1200w.webp 1200w, {stem}-1920w.webp 1920w"'
        )
    if "/assets/img/events/" in poster:
        return (
            f' srcset="{stem}-480w.webp 480w, {stem}-800w.webp 800w, '
            f'{stem}-1200w.webp 1200w"'
        )
    return ""


def lyssna_video_tile(
    video_id: str,
    label: str,
    title: str,
    poster: str,
    start_seconds: int | None = None,
) -> str:
    if not poster.endswith(".webp"):
        raise ValueError(f"lyssna poster must be a local .webp path, got {poster!r}")
    srcset = _lyssna_poster_srcset(poster)
    thumb_src = poster.replace("-1200w.webp", "-800w.webp") if srcset else poster
    sizes = ' sizes="(max-width: 640px) 50vw, (max-width: 900px) 50vw, 36rem"'
    start_attr = f' data-lyssna-start="{start_seconds}"' if start_seconds else ""
    return f"""        <button type="button" class="lyssna-video-tile" data-lyssna-video="{video_id}" data-lyssna-title="{esc(title)}"{start_attr} aria-label="Spela video: {esc(title)}">
          <span class="lyssna-video-tile__media">
            <img class="lyssna-video-tile__thumb" src="{esc(thumb_src)}"{srcset}{sizes} alt="" width="1280" height="720" loading="lazy" decoding="async">
          </span>
          <span class="lyssna-video-tile__meta">
            <span class="lyssna-video-tile__label">{esc(label)}</span>
            <span class="lyssna-video-tile__play" aria-hidden="true">
{LYSSNA_TILE_PLAY_ICON}
            </span>
          </span>
        </button>"""


def lyssna_video_grid(*tiles: str) -> str:
    return "        <div class=\"lyssna-video-grid\">\n" + "\n".join(tiles) + "\n        </div>"


def lyssna_repertoire_song_list_markup() -> str:
    songs = json.loads(LYSSNA_REPERTOIRE_JSON.read_text(encoding="utf-8"))
    items = "\n".join(
        f'            <li><span class="lyssna-song-list__track">{esc(s["title"])}</span> '
        f'<span class="lyssna-song-list__artist">{esc(s["artist"])}</span></li>'
        for s in songs
    )
    return f"""        <ol class="lyssna-song-list" aria-label="Låtar i repertoaren">
{items}
        </ol>"""


def lyssna_spotify_link_markup() -> str:
    return f"""        <div class="lyssna-spotify">
          <a class="alt-btn alt-btn--primary" href="{SPOTIFY_REPERTOIRE_PLAYLIST_URL}" target="_blank" rel="noopener noreferrer">
{SPOTIFY_ICON_BTN}
            <span>Lyssna på Spotify</span>
          </a>
        </div>"""


THE_LICK_VIDEO_URL = "https://www.youtube.com/watch?v=krDxhnaKD7Q"

OM_OSS_MEMBERS = [
    (
        "Adam Blidstål",
        "member-adam.jpg",
        "Sångare och bandets crooner som charmar hela publiken med sin vassa röst. Lärare på dagarna, frontfigur på kvällarna, och ingen i lokalen går säker.",
    ),
    (
        'Gustav "Gema" Kerrolf',
        "member-gustav.jpg",
        "Sångare och slagverkare som sjunger med ena halvan av hjärnan och håller takten med den andra. Ger du honom en bil med släp backar han in i vilken lastficka som helst.",
    ),
    (
        "Edvin Sydmark",
        "member-edvin.jpg",
        "Gitarrist och musiklärare med tajta funkkomp och hjältesolon med dist. Ser du honom lägga ifrån sig gitarren och le: spring. En lek är på väg.",
    ),
    (
        "Ivar Lundin",
        "member-ivar.jpg",
        None,
        (
            "Keyboardist och mångsysslare som lever för fusion och groove. Han hjälper varje treklang på traven "
            f'med några extra ackord och väntar bara på rätt tillfälle att slänga in <a href="{THE_LICK_VIDEO_URL}" '
            'target="_blank" rel="noopener noreferrer">The Lick</a>. Håll utkik!'
        ),
    ),
    (
        "Zacharias Averin",
        "member-zacharias.jpg",
        "Basist som säljer bokföring på dagarna och spelar 32-delar på sin femsträngade på kvällarna. Börjar dansgolvet vibrera är det inte en jordbävning, det är Averin som har satt igång förstärkaren.",
    ),
    (
        "Jonathan Eryd",
        "member-jonathan.jpg",
        "Trummis och bandets äldste som byter cymbaler oftare än vi byter låtordning. Han kan varenda låt och skickar in till Nyacht or Yacht, podden för yachtrocknördar.",
    ),
    (
        'Nils "Nisse" Biström',
        "member-nils.jpg",
        "Trumpetare och ljudtekniker. Ser du en mörk skugga glida längs dansgolvets kant är den inte där för att ta dig. Den är där för att dra ner 3 dB på 250 Hz.",
    ),
    (
        "Olof Ingelsten",
        "member-olof.jpg",
        "Saxofonist vars instrumentsamling börjar likna en liten orkester. Syns inte dansgolvet för rök vet du vem som varit i farten. Olof kör nämligen även ljuset.",
    ),
]


def member_avatar_alt(name: str, line: str) -> str:
    plain = re.sub(r"<[^>]+>", "", line)
    role = plain.split(".", 1)[0]
    if len(role) > 48:
        role = plain.split(",", 1)[0]
    return f"{name}, {role.lower()}"


def member_compact_card(
    name: str = "",
    img_file: str = "",
    line: str = "",
    line_html: str | None = None,
    placeholder: bool = False,
) -> str:
    if placeholder:
        return """          <article class="member-compact-card member-compact-card--placeholder">
            <span class="member-compact-card__avatar member-compact-card__avatar--empty" aria-hidden="true"></span>
            <div class="member-compact-card__body">
              <h3 class="member-compact-card__name">Namn</h3>
              <p class="member-compact-card__line">Instrument</p>
            </div>
          </article>"""
    bio_plain = line if line else re.sub(r"<[^>]+>", "", line_html or "")
    alt = member_avatar_alt(name, bio_plain)
    bio_markup = line_html if line_html is not None else esc(line)
    return f"""          <article class="member-compact-card">
            <img class="member-compact-card__avatar" src="/assets/img/{img_file}" alt="{esc(alt)}" width="160" height="160" loading="lazy" decoding="async">
            <div class="member-compact-card__body">
              <h3 class="member-compact-card__name">{esc(name)}</h3>
              <p class="member-compact-card__line">{bio_markup}</p>
            </div>
          </article>"""


def om_oss_member_card(entry: tuple) -> str:
    name, img, *rest = entry
    if len(rest) == 2 and rest[0] is None:
        return member_compact_card(name, img, line="", line_html=rest[1])
    return member_compact_card(name, img, rest[0])


def members_compact_grid(cards: str) -> str:
    return f"""        <div class="member-compact-grid">
{cards}
        </div>"""


def write_redirect_page(
    path: str,
    target: str,
    *,
    title: str,
    message: str,
    link_label: str,
) -> None:
    canonical = f"{SITE}{target.split('#')[0]}"
    html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta http-equiv="refresh" content="0; url={target}">
  <link rel="canonical" href="{canonical}">
  <title>{esc(title)}</title>
  <meta name="robots" content="noindex,follow">
  <script>location.replace("{target}");</script>
</head>
<body>
  <p>{message} <a href="{target}">Fortsätt till {esc(link_label)}</a>.</p>
</body>
</html>
"""
    segment = unicodedata.normalize("NFC", path.strip("/"))
    dest = OUT_ROOT / segment / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    print("wrote", dest.relative_to(OUT_ROOT), "(redirect)")


SERVICE_HERO_TYPEWRITER_SCRIPT = (
    '  <script src="/assets/js/hero-typewriter.js" defer></script>\n'
)


SERVICE_HERO_TYPEWRITER_PREFIX = "Liveband till "


def service_hero_typewriter_h1(
    h1: str,
    *,
    loop_suffixes: tuple[str, ...] | None = None,
) -> str:
    if loop_suffixes:
        prefix = SERVICE_HERO_TYPEWRITER_PREFIX
        if not h1.startswith(prefix):
            raise ValueError(f"loop hero h1 must start with {prefix!r}: {h1!r}")
        if h1 != f"{prefix}{loop_suffixes[0]}":
            raise ValueError(
                f"hero_h1 must match first loop suffix: {h1!r} vs {prefix}{loop_suffixes[0]!r}"
            )
        longest_suffix = max(loop_suffixes, key=len)
        longest_full = f"{prefix}{longest_suffix}"
        phrases_attr = esc(json.dumps(list(loop_suffixes), ensure_ascii=False))
        first = loop_suffixes[0]
        return f"""        <h1 data-reveal-item data-reveal-i="0">
          <span class="visually-hidden">{esc(h1)}</span>
          <span class="alt-service-hero__h1-stack" aria-hidden="true">
            <span class="alt-service-hero__h1-ghost">{esc(longest_full)}</span>
            <span class="alt-service-hero__h1-live">
              <span class="alt-hero__title-line">{esc(prefix)}</span><span class="alt-hero__typewriter" data-alt-typewriter data-typewriter-phrases="{phrases_attr}">
              <span class="alt-hero__typewriter-ghost">{esc(longest_suffix)}</span>
              <span class="alt-hero__typewriter-live">
                <span class="alt-hero__typewriter-text" data-typewriter-text>{esc(first)}</span><span class="alt-hero__caret" aria-hidden="true"></span>
              </span>
            </span>
            </span>
          </span>
        </h1>"""
    phrases_attr = esc(json.dumps([h1], ensure_ascii=False))
    return f"""        <h1 data-reveal-item data-reveal-i="0">
          <span class="visually-hidden">{esc(h1)}</span>
          <span class="alt-hero__typewriter" data-alt-typewriter data-typewriter-once data-typewriter-phrases="{phrases_attr}" aria-hidden="true">
            <span class="alt-hero__typewriter-ghost">{esc(h1)}</span>
            <span class="alt-hero__typewriter-live">
              <span class="alt-hero__typewriter-text" data-typewriter-text>{esc(h1)}</span><span class="alt-hero__caret" aria-hidden="true"></span>
            </span>
          </span>
        </h1>"""


BROLLOP_FAQS: tuple[tuple[str, str], ...] = (
    (
        "Spelar ni utanför Växjö?",
        "Ja. Vi utgår från Växjö och spelar på bröllop i hela Småland och Skåne. "
        "Längre resor går också bra om vi kommer överens om upplägget.",
    ),
    (
        "Hur långt i förväg behöver vi boka?",
        "För populära datum är det bra att höra av sig ungefär ett år i förväg. "
        "Hör av er så snart ni har datum och lokal klart.",
    ),
    (
        "Kan vi önska låtar?",
        "Ja. Skicka era önskemål i förväg så spelar vi dem om vi kan. Vi har också bra koll på vad som får fart på dansgolvet. "
        "Er första dans ingår alltid, live eller från Spotify genom vårt ljud.",
    ),
    (
        "Spelar ni utomhus?",
        "Det beror på plats, väder och vad som skyddar bandet och utrustningen. "
        "Berätta tidigt om ni vill ha musik utomhus, så kan vi ta ställning till det när ni bokar.",
    ),
    (
        "Samarbetar ni med några bröllopslokaler?",
        "Vi spelar på bröllop i hela Småland och Skåne och återkommer ofta till Asa Herrgård och Norraby gård.",
    ),
)

SERVICE_HERO_SLIDESHOW_KEYS = frozenset({"brollop", "foretag"})
SERVICE_HERO_SLIDESHOW_SCRIPT = (
    '  <script src="/assets/js/service-hero-slideshow.js" defer></script>\n'
)

SERVICE_FAQ_ACCORDION_SCRIPT = (
    '  <script src="/assets/js/faq-accordion.js" defer></script>\n'
)
TALLY_EMBED_SCRIPT = '  <script src="/assets/js/tally-embed.js" defer></script>\n'
FORETAG_PAGE_SCRIPTS = SERVICE_FAQ_ACCORDION_SCRIPT
MINGEL_PAGE_SCRIPTS = SERVICE_FAQ_ACCORDION_SCRIPT

# stem, alt, width, height, object-position per slide (ordered list for CMS Hero-bilder).
SERVICE_HERO_SLIDES: dict[str, list[tuple[str, str, int, int, str]]] = {
    "brollop": [
        (
            "halvfjorton-03-hero",
            "Fest med guldkonfetti och trummor bland gäster vid bord",
            2400,
            1600,
            "center 38%",
        ),
        (
            "halvfjorton-trumpet-barn-wedding",
            "Trumpetare och brudpar på dansgolvet",
            2400,
            1600,
            "center",
        ),
    ],
    "foretag": [
        (
            "halvfjorton-05",
            "Band i rustik lokal med publik i silhuett och blå scenbelysning",
            2400,
            1600,
            "center",
        ),
    ],
    "mingel": [
        (
            "halvfjorton-trumpet-sax-bw-stage",
            "Trumpet och saxofon på scen i rök och scenljus",
            768,
            1024,
            "",
        ),
    ],
}


def _service_hero_img_urls(stem: str) -> tuple[str, str]:
    base = f"/assets/img/gallery/{stem}"
    if stem == "halvfjorton-trumpet-barn-wedding":
        return (
            f"{base}-800w.webp",
            f"{base}.webp 2400w, {base}-800w.webp 800w",
        )
    if stem in GALLERY_STEMS_800_1600:
        return (
            f"{base}-800w.webp",
            f"{base}-800w.webp 800w, {base}-1600w.webp 1600w",
        )
    return (
        f"{base}-800w.webp",
        (
            f"{base}-480w.webp 480w, {base}-800w.webp 800w, "
            f"{base}-1200w.webp 1200w, {base}-1920w.webp 1920w"
        ),
    )


def _service_hero_slide_markup(
    stem: str,
    alt: str,
    width: int,
    height: int,
    position: str,
    *,
    first: bool,
) -> str:
    src, srcset = _service_hero_img_urls(stem)
    pos = f' style="object-position: {position};"' if position else ""
    loading = "eager" if first else "lazy"
    fp = ' fetchpriority="high"' if first else ""
    hero_sizes = hero_cover_sizes(width, height, SERVICE_HERO_COVER_SCALE_SLIDESHOW)
    return f"""          <div class="alt-service-hero__slide">
            <img
              class="alt-service-hero__img"
              src="{src}"
              srcset="{srcset}"
              sizes="{hero_sizes}"
              alt="{esc(alt)}"
              width="{width}"
              height="{height}"
              loading="{loading}"
              decoding="async"{fp}{pos}
            >
          </div>"""


def service_hero_banner(
    service_key: str,
    h1: str,
    description: str,
    *,
    loop_suffixes: tuple[str, ...] | None = None,
) -> str:
    slides = SERVICE_HERO_SLIDES[service_key]
    if service_key in SERVICE_HERO_SLIDESHOW_KEYS:
        slide_html = "\n".join(
            _service_hero_slide_markup(stem, alt, w, h, pos, first=i == 0)
            for i, (stem, alt, w, h, pos) in enumerate(slides)
        )
        return f"""    <header class="alt-service-hero">
      <div class="alt-service-hero__media alt-service-hero__media--slideshow" data-cms-hero="{service_key}" aria-hidden="true">
        <div class="alt-service-hero__carousel">
{slide_html}
        </div>
      </div>
      <div class="alt-service-hero__scrim" aria-hidden="true"></div>
      <div class="alt-service-hero__content" data-reveal-group="hero">
{service_hero_typewriter_h1(h1, loop_suffixes=loop_suffixes)}
        <p class="alt-service-hero__dek" data-reveal-item data-reveal-i="1">{esc(description)}</p>
        <div class="alt-service-hero__actions" data-reveal-item data-reveal-i="2">
          <a class="alt-btn alt-btn--primary" href="/kontakt/#offert">Kontakta oss</a>
        </div>
      </div>
    </header>"""
    stem, alt, width, height, position = slides[0]
    src, srcset = _service_hero_img_urls(stem)
    hero_sizes = hero_cover_sizes(width, height, SERVICE_HERO_COVER_SCALE_STATIC)
    position_attr = f' style="object-position: {position};"' if position else ""
    return f"""    <header class="alt-service-hero">
      <div class="alt-service-hero__media" data-cms-hero="{service_key}" aria-hidden="true">
        <img
          class="alt-service-hero__img"
          src="{src}"
          srcset="{srcset}"
          sizes="{hero_sizes}"
          alt="{esc(alt)}"
          width="{width}"
          height="{height}"
          loading="eager"
          decoding="async"{position_attr}
        >
      </div>
      <div class="alt-service-hero__scrim" aria-hidden="true"></div>
      <div class="alt-service-hero__content" data-reveal-group="hero">
{service_hero_typewriter_h1(h1, loop_suffixes=loop_suffixes)}
        <p class="alt-service-hero__dek" data-reveal-item data-reveal-i="1">{esc(description)}</p>
        <div class="alt-service-hero__actions" data-reveal-item data-reveal-i="2">
          <a class="alt-btn alt-btn--primary" href="/kontakt/#offert">Kontakta oss</a>
        </div>
      </div>
    </header>"""


def service_chapter(title: str, paragraphs: list[str], extra_html: str = "", modifier: str = "") -> str:
    mod = f" alt-svc-chapter--{modifier}" if modifier else ""
    ps = "\n".join(f"          <p>{p}</p>" for p in paragraphs)
    extra = f"\n{extra_html}" if extra_html else ""
    return f"""    <section class="alt-svc-chapter section{mod}" data-reveal>
      <div class="alt-svc-wrap alt-svc-chapter__inner">
        <h2 class="alt-svc-chapter__title">{esc(title)}</h2>
        <div class="alt-svc-chapter__body">
{ps}{extra}
        </div>
      </div>
    </section>"""


def service_addon_figure(
    stem: str,
    alt: str,
    *,
    width: int = 2400,
    height: int = 1600,
    object_position: str = "",
    scale: float | None = None,
) -> str:
    return wedding_figure(
        stem,
        alt,
        "(max-width: 900px) 100vw, min(42vw, 520px)",
        width=width,
        height=height,
        figure_class="alt-svc-addon__figure",
        object_position=object_position,
        scale=scale,
    )


GALLERY_STEMS_800_1600 = frozenset(
    {
        "halvfjorton-band-forest-bw",
        "halvfjorton-band-pink-haze",
        "halvfjorton-barn-purple-stage",
        "halvfjorton-garden-mingel",
        "halvfjorton-acoustic-trio-white-room",
        "halvfjorton-garden-sax-barn",
        "halvfjorton-keys-guitarists-pink",
        "halvfjorton-stage-blue-dining-hall",
        "halvfjorton-stage-from-above-blue",
        "halvfjorton-singer-bw-pointing",
        "halvfjorton-trumpet-sax-bw-stage",
        "halvfjorton-warehouse-green-stage",
    }
)


def _gallery_src_and_srcset(stem: str) -> tuple[str, str]:
    base = f"/assets/img/gallery/{stem}"
    if stem in GALLERY_STEMS_800_1600:
        return (
            f"{base}-800w.webp",
            f"{base}-800w.webp 800w, {base}-1600w.webp 1600w",
        )
    return (
        f"{base}-800w.webp",
        (
            f"{base}-480w.webp 480w, {base}-800w.webp 800w, "
            f"{base}-1200w.webp 1200w, {base}-1920w.webp 1920w"
        ),
    )


def wedding_figure(
    stem: str,
    alt: str,
    sizes: str,
    width: int = 2400,
    height: int = 1600,
    figure_class: str = "alt-wedding-figure",
    loading: str = "lazy",
    object_position: str = "",
    scale: float | None = None,
) -> str:
    src, srcset = _gallery_src_and_srcset(stem)
    style_bits: list[str] = []
    if object_position:
        style_bits.append(f"object-position: {object_position}")
    if scale is not None and scale != 1:
        style_bits.append(f"transform: scale({scale})")
        style_bits.append(f"transform-origin: {object_position or 'center'}")
    style_attr = f' style="{"; ".join(style_bits)};"' if style_bits else ""
    return f"""          <figure class="{figure_class}">
            <img
              src="{src}"
              srcset="{srcset}"
              sizes="{sizes}"
              alt="{esc(alt)}"
              width="{width}"
              height="{height}"
              loading="{loading}"
              decoding="async"{style_attr}
            >
          </figure>"""


def faq_page_ld(qa_pairs: tuple[tuple[str, str], ...]) -> str:
    entities = [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in qa_pairs
    ]
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities,
    }
    return _indent_ld(data)


def wedding_faq_ld() -> str:
    return faq_page_ld(BROLLOP_FAQS)


def wedding_service_ld() -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": "Bröllopsband",
        "description": (
            "Bröllopsband från Växjö med åtta musiker och blås. "
            "Fest, mingel och vigselmusik på bröllop i Småland och Skåne."
        ),
        "url": f"{SITE}/brollop/",
        "areaServed": [
            {"@type": "City", "name": "Växjö"},
            {"@type": "AdministrativeArea", "name": "Småland"},
            {"@type": "AdministrativeArea", "name": "Skåne"},
        ],
        "provider": {
            "@type": "MusicGroup",
            "name": "Halv Fjorton",
            "url": f"{SITE}/",
        },
    }
    return _indent_ld(data)


class ServiceAddon(NamedTuple):
    stem: str
    alt: str
    title: str
    body: str
    width: int = 1280
    height: int = 720
    object_position: str = ""
    scale: float | None = None


class StandardServicePage(NamedTuple):
    service_key: str
    hero_h1: str
    hero_dek: str
    split_title: str
    split_paragraphs: tuple[str, ...]
    split_stem: str
    split_alt: str
    addons: tuple[ServiceAddon, ...]
    faqs: tuple[tuple[str, str], ...]
    closing_text: str
    split_sizes: str = "(max-width: 900px) 100vw, min(46vw, 640px)"
    hero_typewriter_suffixes: tuple[str, ...] | None = None


FORETAG_FAQS: tuple[tuple[str, str], ...] = (
    (
        "Hur länge spelar ni?",
        "På de flesta företagsfester spelar vi två set partymusik. Mingel eller andra delar planeras separat i offerten.",
    ),
    (
        "Kan ni ta mingel och fest samma kväll?",
        "Ja, det är ett av våra vanligaste upplägg. Mingel i mer återhållen stil, sedan två set dans när rummet är redo.",
    ),
    (
        "Ingår ljud och ljus?",
        "Vi kan ordna ljud och ljus om ni saknar leverantör till tillställningen. Har ni redan extern teknik samarbetar vi gärna med dem så att kvällen hänger ihop.",
    ),
    (
        "Kan ni fakturera?",
        "Ja. Vi har F-skatt och skickar faktura.",
    ),
    (
        "Vad behöver ni veta innan offert?",
        "Datum, adress, ungefärligt antal, om det är mingel plus fest, och om lokalen har begränsningar. Resten tar vi i dialogen med er.",
    ),
)

MINGEL_FAQS: tuple[tuple[str, str], ...] = (
    (
        "Kan ni spela både mingel och fest?",
        "Ja. Många väljer att vi tar hela kvällen, från lugnare musik när gästerna kommer till fullt dansgolv senare.",
    ),
    (
        "Kan ni spela under middagen?",
        "Ja, vi spelar gärna någon låt vid utvalda tillfällen under sittningen, eller håller i ett musikquiz med gästerna.",
    ),
    (
        "Måste man boka alla åtta musiker?",
        "När man bokar Halv Fjorton får man hela bandet, alltid. Åtta musiker med full blåssektion ger ett tryck som gör oss till ett coverband utöver det vanliga.",
    ),
    (
        "Spelar ni i hela södra Sverige?",
        "Ja, på förfrågan. Vi spelar ofta i Malmö, Lund, Helsingborg, Växjö, Jönköping, Kalmar, Karlskrona och på Österlen.",
    ),
    (
        "Ingår ljud och ljus?",
        "Det beror på hur stort eventet är. Vi kan ta med egen utrustning eller använda er leverantör, och ser till att ljudet passar lokalen.",
    ),
)


BROLLOP_STANDARD_PAGE = StandardServicePage(
    service_key="brollop",
    hero_h1="Liveband till bröllop",
    hero_dek=(
        "Avsluta dagen på ett storslaget sätt med ett bröllopsband som ger er och era gäster en kväll ni sent glömmer."
    ),
    split_title="Festspelning",
    split_paragraphs=(
        "När middagen är över och första valsen är dansad drar vi igång festen på riktigt. Vi är ett bröllopsband från Växjö med åtta musiker och blåssektion, och vi tar er genom flera genrer under kvällen. Vi har lång erfarenhet av bröllop och vet vad som får dansgolvet att leva.",
    ),
    split_stem="halvfjorton-05",
    split_alt="Band i rustik lokal med publik i silhuett och blå scenbelysning",
    addons=(
        ServiceAddon(
            "halvfjorton-garden-mingel",
            "Musiker som spelar utomhus",
            "Mingelmusik",
            "Före middagen spelar vi lugnare och jazzigare musik medan gästerna minglar. Vi tar med ett eget ljudsystem för detta.",
        ),
        ServiceAddon(
            "halvfjorton-acoustic-trio-white-room",
            "Musikgrupp i ljus lokal med bas, trummor och blås",
            "Vigselmusik",
            "Till vigseln har vi solist och komp, och låtarna väljer vi tillsammans med er. Har ni andra önskemål för vigseln löser vi det efter dem.",
            width=800,
            height=628,
        ),
    ),
    faqs=BROLLOP_FAQS,
    closing_text="Berätta om ert bröllop, så återkommer vi med ett förslag.",
)

FORETAG_STANDARD_PAGE = StandardServicePage(
    service_key="foretag",
    hero_h1="Liveband till företagsfest",
    hero_dek=(
        "Oavsett tillfälle levererar vi en medryckande upplevelse som lyfter stämningen. "
        "Åtta musiker med blåssektion, från första minglet till sista dansen."
    ),
    split_title="Upplägg efter ert program",
    split_paragraphs=(
        "Ni berättar hur kvällen ska löpa: mingel, middag, tal, dans. Vi är flexibla och tar fram ett specialupplägg för just er tillställning, med volym och tider som passar lokalen och gästerna.",
        "Vanligt upplägg är mingel 45 till 90 minuter medan gästerna kommer in, paus under middag och tal, därefter tar vi över och ställer till med ösigt dansgolv!",
    ),
    split_stem="halvfjorton-stage-blue-dining-hall",
    split_alt="Scen med blått ljus i festlokal",
    addons=(
        ServiceAddon(
            "halvfjorton-barn-purple-stage",
            "Scen i lada med lila ljus och rök",
            "Mingelmusik",
            "När gästerna strömmar in spelar vi lugnare musik som låter samtalen flyta. Jazz, soul och svenska visor i en blandning som sätter tonen för kvällen.",
        ),
        ServiceAddon(
            "halvfjorton-01",
            "Band på stor scen med varmt ljus och publik i festsal",
            "Artistkomp",
            "Planerar ni att boka en artist till ert event? Vi har lång erfarenhet av att kompa artister, oavsett genre och sättning, och gör framträdandet komplett.",
            width=1280,
            height=720,
        ),
        ServiceAddon(
            "halvfjorton-warehouse-green-stage",
            "Keyboard på scen i lagerlokal",
            "Middagsunderhållning",
            "Vi spelar gärna en eller två låtar vid utvalda tillfällen under sittningen. Ett uppskattat inslag är ett interaktivt musikquiz med gästerna, som alltid går hem.",
        ),
    ),
    faqs=FORETAG_FAQS,
    closing_text=(
        "Hör av er via formuläret på kontaktsidan. Vi återkommer med upplägg och offert när vi vet plats, tider och vilka delar ni vill boka."
    ),
    hero_typewriter_suffixes=("företagsfest", "personalfest", "kickoff", "jubileum"),
)

MINGEL_STANDARD_PAGE = StandardServicePage(
    service_key="mingel",
    hero_h1="Liveband till fest och mingel",
    hero_dek=(
        "Åttamannaband som sätter stämningen, oavsett om kvällen börjar med skål eller går rakt ut på dansgolvet."
    ),
    split_title="Från första glaset till sista låten",
    split_paragraphs=(
        "Oavsett om det är 50-årsfest, jubileum eller sommarfest på en äng bär vi kvällen hela vägen. "
        "Vi börjar lågmält medan gästerna minglar, och när talen är hållna och borden dukats av drar vi igång festen på riktigt. "
        "Vi är flexibla och anpassar upplägget efter er kväll.",
    ),
    split_stem="halvfjorton-band-pink-haze",
    split_alt="Musiker på scen med ljus och scenrök",
    addons=(
        ServiceAddon(
            "halvfjorton-singer-bw-pointing",
            "Sångare på scen med mikrofon",
            "Festspelning",
            "När det är dags att dansa tar vi över och ställer till med ösigt dansgolv. Två set fullt ös med blåssektion, anpassat efter er publik och kvällens tempo.",
            width=767,
            height=1024,
            object_position="center 15%",
        ),
        ServiceAddon(
            "halvfjorton-stage-from-above-blue",
            "Scen med instrument sett ovanifrån",
            "Middagsunderhållning",
            "Vi spelar gärna en eller två låtar vid utvalda tillfällen under sittningen. Ett uppskattat inslag är ett interaktivt musikquiz med gästerna, som alltid går hem.",
            width=1280,
            height=720,
        ),
        ServiceAddon(
            "halvfjorton-garden-mingel",
            "Musiker som spelar utomhus",
            "Mingel",
            "När gästerna strömmar in spelar vi lugnare musik som låter samtalen flyta. Jazz, soul och svenska visor i en blandning som sätter tonen för kvällen.",
            width=1280,
            height=720,
        ),
    ),
    faqs=MINGEL_FAQS,
    closing_text=(
        "Hör av er via formuläret på kontaktsidan. Vi återkommer med upplägg och offert när vi vet plats, tider och vilka delar ni vill boka."
    ),
    hero_typewriter_suffixes=("fest och mingel", "50-årsfesten", "jubileet", "sommarfesten"),
)


def standard_service_page_body(page: StandardServicePage) -> str:
    hero = service_hero_banner(
        page.service_key,
        page.hero_h1,
        page.hero_dek,
        loop_suffixes=page.hero_typewriter_suffixes,
    )
    split_ps = "\n".join(f"            <p>{esc(p)}</p>" for p in page.split_paragraphs)
    split_figure = wedding_figure(
        page.split_stem,
        page.split_alt,
        page.split_sizes,
        figure_class="alt-svc-inline-figure",
    )
    addon_blocks: list[str] = []
    for addon in page.addons:
        addon_blocks.append(
            f"""          <div class="alt-svc-addon">
{service_addon_figure(addon.stem, addon.alt, width=addon.width, height=addon.height, object_position=addon.object_position, scale=addon.scale)}
            <h3 class="alt-svc-addon__title">{esc(addon.title)}</h3>
            <p>{esc(addon.body)}</p>
          </div>"""
        )
    faq_list = faq_list_two_columns(list(page.faqs))
    addon_grid_class = "alt-svc-addon-grid alt-svc-chapter__body"
    if len(page.addons) >= 3:
        addon_grid_class += " alt-svc-addon-grid--cols-3"
    closing_actions = """          <div class="actions">
            <a class="alt-btn alt-btn--primary" href="/kontakt/">Kontakta oss</a>
          </div>"""
    return f"""{hero}
    <section class="alt-svc-chapter section alt-svc-chapter--split alt-svc-chapter--festspelning" data-reveal>
      <div class="alt-svc-wrap alt-svc-chapter__split alt-svc-chapter__layout--copy-first">
        <div class="alt-svc-chapter__split-copy">
          <h2 class="alt-svc-chapter__title">{esc(page.split_title)}</h2>
          <div class="alt-svc-chapter__body">
{split_ps}
          </div>
        </div>
        <div class="alt-svc-chapter__split-media">
{split_figure}
        </div>
      </div>
    </section>
    <section class="alt-svc-chapter section alt-svc-chapter--addons" data-reveal aria-labelledby="tillaggstjanster">
      <div class="alt-svc-wrap">
        <h2 class="alt-svc-section-label" id="tillaggstjanster">Tilläggstjänster</h2>
        <div class="{addon_grid_class}">
{chr(10).join(addon_blocks)}
        </div>
      </div>
    </section>
    <section class="alt-svc-chapter section" data-reveal>
      <div class="alt-svc-wrap alt-faq">
        <h2 class="alt-svc-chapter__title">Vanliga frågor</h2>
{faq_list}
      </div>
    </section>
    <section class="alt-svc-chapter section alt-svc-chapter--closing" data-reveal>
      <div class="alt-svc-wrap">
        <h2 class="alt-svc-chapter__title">Kontakta oss</h2>
        <div class="alt-svc-chapter__body">
          <p>{esc(page.closing_text)}</p>
{closing_actions}
        </div>
      </div>
    </section>"""


def wedding_page_body() -> str:
    return standard_service_page_body(BROLLOP_STANDARD_PAGE)


def gallery_img(
    stem: str,
    alt: str,
    sizes: str = "(max-width: 900px) 100vw, 46vw",
    width: int = 2400,
    height: int = 1600,
    extra_class: str = "",
) -> str:
    base = f"/assets/img/gallery/{stem}"
    src, srcset = _gallery_src_and_srcset(stem)
    cls = f"content-photo{extra_class}"
    return f"""          <figure class="{cls}">
            <img
              src="{src}"
              srcset="{srcset}"
              sizes="{sizes}"
              alt="{esc(alt)}"
              width="{width}"
              height="{height}"
              loading="lazy"
              decoding="async"
            >
          </figure>"""


def youtube_video_object_ld(
    name: str,
    description: str,
    video_id: str,
    thumbnail_url: str,
    start_seconds: int | None = None,
) -> str:
    embed_url = f"https://www.youtube-nocookie.com/embed/{video_id}"
    content_url = f"https://www.youtube.com/watch?v={video_id}"
    if start_seconds:
        embed_url += f"?start={start_seconds}"
        content_url += f"&t={start_seconds}"
    data = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": name,
        "description": description,
        "thumbnailUrl": thumbnail_url,
        "embedUrl": embed_url,
        "contentUrl": content_url,
        "publisher": {
            "@type": "Organization",
            "name": "Halv Fjorton",
            "url": f"{SITE}/",
        },
    }
    return _indent_ld(data)


def wedding_video_ld() -> str:
    return youtube_video_object_ld(
        WEDDING_VIDEO_TITLE,
        "Livevideo med Halv Fjorton som cover- och bröllopsband i södra Sverige.",
        WEDDING_VIDEO_ID,
        f"https://i.ytimg.com/vi/{WEDDING_VIDEO_ID}/hqdefault.jpg",
    )


def lyssna_page_video_ld() -> list[str]:
    return [
        youtube_video_object_ld(
            "Signed Sealed Delivered - Halv Fjorton 2025",
            "Livefilm med Halv Fjorton från 2025.",
            "V2Nb8jMKUCk",
            f"{SITE}/assets/img/gallery/halvfjorton-01-1200w.webp",
        ),
        youtube_video_object_ld(
            "Halv Fjorton Reel 2022",
            "Kortare klipp från spelningar 2022.",
            "gm5C41wqYuU",
            f"{SITE}{lyssna_yt_poster_path('gm5C41wqYuU')}",
        ),
        youtube_video_object_ld(
            "A Soulful Lucia 2025",
            "Julkonsert med Halv Fjorton, inspelning från lucia 2025.",
            SOULFUL_LUCIA_2025_VIDEO_ID,
            f"{SITE}{SOULFUL_LUCIA_2025_IMG}-1200w.webp",
        ),
        youtube_video_object_ld(
            "A Soulful Christmas 2024 - 8 december, Nygatan 6",
            "Julkonsert A Soulful Christmas 2024 på Nygatan 6 i Växjö.",
            "vV8aavPxYss",
            f"{SITE}{lyssna_yt_poster_path('vV8aavPxYss')}",
        ),
        youtube_video_object_ld(
            "A Soulful Christmas 2023 - 3 december, Nygatan 6",
            "Julkonsert A Soulful Christmas 2023 på Nygatan 6 i Växjö.",
            "UytyTLnKDWQ",
            f"{SITE}{lyssna_yt_poster_path('UytyTLnKDWQ')}",
        ),
    ]


def breadcrumb_ld(items):
    elements = ",\n".join(
        f'''      {{
        "@type": "ListItem",
        "position": {i},
        "name": "{name}",
        "item": "{SITE}{path}"
      }}'''
        for i, (path, name) in enumerate(items, 1)
    )
    return f"""{{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
{elements}
    ]
  }}"""


def service_ld(name, desc, url):
    data = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": name,
        "description": desc,
        "url": f"{SITE}{url}",
        "areaServed": load_org()["areaServed"],
        "provider": {
            "@type": "MusicGroup",
            "name": "Halv Fjorton",
            "url": f"{SITE}/",
        },
    }
    return _indent_ld(data)


def music_event_ld(name: str, start: str, description: str, ticket_url: str, image_path: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "MusicEvent",
        "name": name,
        "description": description,
        "startDate": start,
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "image": f"{SITE}{image_path}-1200w.webp",
        "url": ticket_url,
        "location": {
            "@type": "Place",
            "name": "Nygatan 6",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Nygatan 6",
                "addressLocality": "Växjö",
                "postalCode": "352 33",
                "addressCountry": "SE",
            },
        },
        "performer": {
            "@type": "MusicGroup",
            "name": "Halv Fjorton",
            "url": f"{SITE}/",
        },
        "organizer": {
            "@type": "Organization",
            "name": "Nygatan 6",
            "url": "https://www.nygatan6.se/",
        },
        "offers": {
            "@type": "Offer",
            "url": ticket_url,
            "availability": "https://schema.org/InStock",
        },
    }
    return _indent_ld(data)


def soulful_christmas_event_ld() -> list[str]:
    desc = (
        "Julkonsert med soul, funk, jazz och komiska inslag. Halv Fjorton och gäster på Nygatan 6 i Växjö."
    )
    return [
        music_event_ld(
            "A Soulful Christmas (16:00)",
            "2026-12-12T16:00:00+01:00",
            desc,
            SOULFUL_CHRISTMAS_TICKETS,
            SOULFUL_CHRISTMAS_IMG,
        ),
        music_event_ld(
            "A Soulful Christmas (19:30)",
            "2026-12-12T19:30:00+01:00",
            desc,
            SOULFUL_CHRISTMAS_TICKETS,
            SOULFUL_CHRISTMAS_IMG,
        ),
    ]


def soulful_christmas_ticket_card() -> str:
    base = SOULFUL_CHRISTMAS_IMG
    return f"""        <article
          class="event-ticket"
          data-event-ticket
          data-event-start="{SOULFUL_CHRISTMAS_START}"
          data-event-end="{SOULFUL_CHRISTMAS_END}"
        >
          <div class="event-ticket__grid">
            <div class="event-ticket__poster">
              <div class="event-ticket__status" aria-live="polite">
                <span class="event-ticket__badge" data-event-badge>Kommande</span>
                <span class="event-ticket__countdown" data-event-countdown></span>
              </div>
              <img
                src="{base}-800w.webp"
                srcset="{base}-480w.webp 480w, {base}-800w.webp 800w, {base}-1200w.webp 1200w"
                sizes="(max-width: 767px) 100vw, 38vw"
                alt="Affisch för A Soulful Christmas med Halv Fjorton på Nygatan 6"
                width="1200"
                height="900"
                loading="lazy"
                decoding="async"
              >
            </div>
            <div class="event-ticket__main">
              <h2 class="event-ticket__title">A Soulful Christmas</h2>
              <p class="event-ticket__subtitle">med Halv Fjorton &amp; gäster</p>
              <p class="visually-hidden">Lördag 12 december 2026 · Nygatan 6, Växjö · 16:00 och 19:30</p>
              <p class="event-ticket__when">Lördag 12 december 2026</p>
              <ul class="event-ticket__times">
                <li><span class="event-ticket__chip">16:00</span></li>
                <li><span class="event-ticket__chip">19:30</span></li>
              </ul>
              <p class="event-ticket__place">
                <svg class="event-ticket__pin" width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M12 21s7-4.5 7-11a7 7 0 1 0-14 0c0 6.5 7 11 7 11Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                  <circle cx="12" cy="10" r="2.25" stroke="currentColor" stroke-width="1.5"/>
                </svg>
                <span><a class="event-ticket__venue-link" href="/julkonsert/">Nygatan 6</a>, Växjö</span>
              </p>
              <p class="event-ticket__text">Växjö stad i juleglans, och vad passar då bättre än en julkonsert? Halv Fjorton återvänder och bjuder på svängig julstämning med soul, funk, jazz och komiska inslag. Julklassikerna får en skrud du aldrig hört förut, och kanske smyger sig en och annan sketch in…</p>
              <div class="event-ticket__actions" aria-hidden="true">
                <span class="alt-btn alt-btn--primary event-ticket__cta event-ticket__cta-spacer">Köp biljetter</span>
              </div>
            </div>
          </div>
          <a
            class="event-ticket__stretched-link"
            href="{SOULFUL_CHRISTMAS_TICKETS}"
            target="_blank"
            rel="noopener noreferrer"
          >
            <span class="alt-btn alt-btn--primary event-ticket__cta">Köp biljetter</span>
          </a>
        </article>"""


def page(
    path: str,
    title: str,
    description: str,
    extra_ld: list[str] | None = None,
    body: str = "",
    page_class: str = "",
    outfile: Path | None = None,
    breadcrumb_name: str | None = None,
    extra_scripts: str = "",
    robots_tag: str | None = None,
    include_canonical: bool = True,
):
    canonical = f"{SITE}{path}"
    crumb_label = breadcrumb_name or title.split(" | ")[0].split(", ")[0]
    graphs = [music_group_ld(), breadcrumb_ld([("/", "Hem")] + ([] if path == "/" else [(path, crumb_label)]))]
    if extra_ld:
        graphs.extend(extra_ld)
    jsonld = jsonld_graph_markup(graphs)
    body_class = "alt-page alt-page--inner"
    if page_class:
        body_class = f"{body_class} {page_class}"
    if "alt-page--service-banner" in page_class:
        if "hero-typewriter.js" not in extra_scripts:
            extra_scripts = f"{extra_scripts}{SERVICE_HERO_TYPEWRITER_SCRIPT}"
    nav_block = home_nav_block(path, "/kontakt/")
    mobile_menu = mobile_menu_block(path, "/kontakt/")
    toggle = alt_header_mobile_controls_markup("mobile-menu")
    robots = robots_tag if robots_tag is not None else "index,follow"
    canonical_line = (
        f'  <link rel="canonical" href="{canonical}">\n' if include_canonical else ""
    )
    html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="format-detection" content="telephone=no, date=no, email=no, address=no">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
{canonical_line}  <meta name="robots" content="{robots}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="sv_SE">
  <meta property="og:site_name" content="Halv Fjorton">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{OG}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{OG}">
{favicon_head_links()}
{font_preloads('/assets')}
{head_resource_hints()}  <link rel="stylesheet" href="/assets/css/site.css">
  <script type="application/ld+json">
  {jsonld}
  </script>
</head>
<body class="{body_class}">
  <a class="skip-link" href="#innehall">Hoppa till innehållet</a>
  <header class="alt-header site-header" data-nav>
    <div class="alt-header__inner header-inner">
      <a class="alt-brand brand" href="/" aria-label="Halv Fjorton">
{brand_logo_markup()}
      </a>
{toggle}
{nav_block}
    </div>
  </header>
{alt_header_scroll_bootstrap_script()}
{mobile_menu}
  <main id="innehall" class="alt-inner-main">
{body}
  </main>
{modern_footer_markup()}
  <script src="/assets/js/nav.js" defer></script>
  <script src="/assets/js/header-scroll.js" defer></script>
  <script src="/assets/js/footer-year.js" defer></script>
  <script src="/assets/js/video-facade.js" defer></script>
{extra_scripts}</body>
</html>
"""
    dest = outfile
    if dest is None:
        dest = OUT_ROOT / (path.lstrip("/") + ("index.html" if path.endswith("/") else ""))
        if path == "/":
            dest = OUT_ROOT / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    print("wrote", dest.relative_to(OUT_ROOT))


def write_pages():
    om_oss_member_cards = "\n".join(om_oss_member_card(entry) for entry in OM_OSS_MEMBERS)
    page(
        "/brollop/",
        "Bröllopsband från Växjö | Halv Fjorton",
        "Bröllopsband från Växjö med åtta musiker och blås. Fest, mingel och vigselmusik på bröllop i Småland och Skåne.",
        breadcrumb_name="Bröllop",
        extra_ld=[wedding_service_ld(), wedding_faq_ld()],
        extra_scripts=f"{SERVICE_FAQ_ACCORDION_SCRIPT}{SERVICE_HERO_SLIDESHOW_SCRIPT}",
        body=wedding_page_body(),
        page_class="alt-page--wedding alt-page--service-banner",
    )

    page(
        "/foretag/",
        "Coverband till företagsfest | Halv Fjorton",
        (
            "Personalfest, kickoff och jubileum med åtta musiker och blåssektion. "
            "Mingelmusik, artistkomp och middagsunderhållning i Småland, Skåne och hela södra Sverige."
        ),
        breadcrumb_name="Företag",
        extra_ld=[
            service_ld(
                "Företagsfest och festband",
                "Musikunderhållning till personalfest, kickoff och jubileum. Mingelmusik, artistkomp och middagsunderhållning.",
                "/foretag/",
            ),
            faq_page_ld(FORETAG_FAQS),
        ],
        extra_scripts=f"{FORETAG_PAGE_SCRIPTS}{SERVICE_HERO_SLIDESHOW_SCRIPT}",
        page_class="alt-page--service-banner",
        body=standard_service_page_body(FORETAG_STANDARD_PAGE),
    )

    page(
        "/fest-och-mingel/",
        "Liveband till fest och mingel | Halv Fjorton",
        (
            "Åttamannaband till fest och mingel med blåssektion. "
            "Från lugn stämning till fullt dansgolv i samma kväll."
        ),
        breadcrumb_name="Fest och mingel",
        extra_ld=[
            service_ld(
                "Fest och mingel",
                "Liveband till fest och mingel med mingel, middagsunderhållning och festspelning.",
                "/fest-och-mingel/",
            ),
            faq_page_ld(MINGEL_FAQS),
        ],
        extra_scripts=MINGEL_PAGE_SCRIPTS,
        page_class="alt-page--service-banner",
        body=standard_service_page_body(MINGEL_STANDARD_PAGE),
    )



    page(
        "/julkonsert/",
        "A Soulful Christmas | Halv Fjorton",
        "A Soulful Christmas med Halv Fjorton & gäster, lördag 12 december 2026 på Nygatan 6 i Växjö. Föreställningar 16:00 och 19:30.",
        breadcrumb_name="Julkonsert",
        page_class="alt-page--konserter",
        extra_ld=soulful_christmas_event_ld(),
        extra_scripts='  <script src="/assets/js/event-ticket-card.js" defer></script>\n',
        body=f"""    <div class="wrap alt-konserter-page">
      <div class="event-ticket-wrap alt-konserter-page__tickets">
{soulful_christmas_ticket_card()}
      </div>
    </div>
""",
    )

    page(
        "/konserter/",
        "Konserter | Halv Fjorton",
        "Publik konsert A Soulful Christmas 12 december 2026 på Nygatan 6 i Växjö. Två föreställningar med Halv Fjorton och gäster.",
        breadcrumb_name="Konserter",
        page_class="alt-page--konserter",
        extra_ld=soulful_christmas_event_ld(),
        extra_scripts='  <script src="/assets/js/event-ticket-card.js" defer></script>\n',
        body=f"""    <div class="wrap alt-konserter-page">
      <header class="page-hero compact alt-konserter-page__hero">
        <div class="page-hero-copy">
          <h1>Konserter</h1>
          <p class="lead">Vi spelar inte alltid för privata sammankomster utan gör ibland publika konserter, håll utkik här.</p>
        </div>
      </header>
      <div class="event-ticket-wrap alt-konserter-page__tickets">
{soulful_christmas_ticket_card()}
      </div>
    </div>
""",
    )



    page(
        "/om-oss/",
        "Om Halv Fjorton | coverband från Växjö",
        "Coverband från Växjö. Soul, funk och svenska allsångslåtar med blåssektion. Möt bandet och medlemmarna här.",
        breadcrumb_name="Om oss",
        page_class="alt-page--om-oss",
        extra_scripts='  <script src="/assets/js/om-oss-member-avatar.js" defer></script>\n',
        body=f"""    <header class="page-hero compact">
      <div class="page-hero-split">
        <div class="page-hero-copy">
          <h1>Om Halv Fjorton</h1>
          <p>Vi är åtta musiker från Växjö som älskar att spela tillsammans, och det hörs. Funkigt komp, blås i taket och ett groove som får även de blygsammaste att tappa fotfästet. Målet är en kväll som sitter kvar, så att ni fortfarande nynnar på blåsriffen dagen efter.</p>
        </div>
{gallery_img("halvfjorton-band-forest-bw", "Hela bandet i kostym i skogen, svartvit bild", sizes="(max-width: 900px) 100vw, 50vw", width=1600, height=1112)}
      </div>
    </header>
    <section class="section">
      <div class="wrap">
        <h2 class="om-oss-section-label">Det här kan ni vänta er...</h2>
        <div class="grid-2 om-oss-desc-grid">
          <p>Vår grund är soul och funk, och därifrån tar vi oss vidare till schlager, rock och svenska allsångslåtar. Det viktigaste är att det svänger, och när något gör det spelar vi det. Vi väljer låtar som är roliga att spela och dansa till, och brukar landa i något som både ni och vi kan sjunga med i.</p>
          <p>Vi är ett coverband med blåssektion, så vi spelar gärna låtar med blåsriff och saxofonsolon. Där trivs vi bäst, och där vaknar dansgolvet ofta. Kort och gott: vi har repertoar för både farmor och de yngre.</p>
        </div>
      </div>
    </section>
    <section class="section om-oss-members-section">
      <div class="wrap">
        <h2>Medlemmar</h2>
{members_compact_grid(om_oss_member_cards)}
      </div>
    </section>
""",
    )

    page(
        "/lyssna/",
        "Lyssna | Halv Fjorton",
        (
            "Hör hur det låter när Halv Fjorton spelar på bröllop, företagsfester och julkonserter. "
            "Åtta musiker med egen blåssektion."
        ),
        page_class="alt-page--lyssna",
        extra_scripts=LYSSNA_VIDEO_MODAL_SCRIPT,
        extra_ld=lyssna_page_video_ld(),
        body=f"""    <header class="page-hero compact">
      <div class="page-hero-copy">
        <h1>Lyssna på oss</h1>
        <p class="lead">Filmer från scen och julkonserter, plus en överblick av repertoaren. Samma band som ni bokar till bröllop, företag och mingel.</p>
        <p class="page-hero__actions">
          <a class="alt-btn alt-btn--primary" href="{INSTAGRAM_PROFILE_URL}" target="_blank" rel="noopener noreferrer">
{INSTAGRAM_ICON_BTN}
            <span>Instagram @halvfjorton</span>
          </a>
          <a class="alt-btn alt-btn--ghost" href="#repertoar">Repertoar</a>
        </p>
      </div>
    </header>
    <section class="section" aria-label="Livefilmer">
      <div class="wrap">
{lyssna_video_grid(
    lyssna_video_tile(
        "V2Nb8jMKUCk",
        "Signed Sealed Delivered",
        "Signed Sealed Delivered - Halv Fjorton 2025",
        poster="/assets/img/gallery/halvfjorton-01-1200w.webp",
    ),
    lyssna_video_tile(
        "gm5C41wqYuU",
        "Reel 2022",
        "Halv Fjorton Reel 2022",
        poster=lyssna_yt_poster_path("gm5C41wqYuU"),
    ),
)}
      </div>
    </section>
    <section class="section section-alt">
      <div class="wrap">
        <h2>Lyssna på våra julkonserter</h2>
{lyssna_video_grid(
    lyssna_video_tile(
        SOULFUL_LUCIA_2025_VIDEO_ID,
        "A Soulful Lucia 2025",
        "A Soulful Lucia 2025",
        poster=f"{SOULFUL_LUCIA_2025_IMG}-1200w.webp",
    ),
    lyssna_video_tile(
        "vV8aavPxYss",
        "A Soulful Christmas 2024",
        "A Soulful Christmas 2024 - 8 december, Nygatan 6",
        poster=lyssna_yt_poster_path("vV8aavPxYss"),
    ),
    lyssna_video_tile(
        "UytyTLnKDWQ",
        "A Soulful Christmas 2023",
        "A Soulful Christmas 2023 - 3 december, Nygatan 6",
        poster=lyssna_yt_poster_path("UytyTLnKDWQ"),
    ),
)}
      </div>
    </section>
    <section class="section" id="repertoar">
      <div class="wrap">
        <div class="lyssna-repertoire-split">
          <div class="lyssna-repertoire-split__copy">
            <h2>Repertoar</h2>
            <p>Vi bygger kvällar kring funk och soul: Stevie Wonder, Ray Charles, Earth, Wind &amp; Fire. Därtill kommer svenska favoriter som Björn Skifs och Tomas Ledin, och repertoaren är bred nog för blandade sällskap och generationer. Vi tar gärna emot önskemål inför bokning, mejla <a href="mailto:halvfjorton@gmail.com">halvfjorton@gmail.com</a> så tar vi dialogen där.</p>
          </div>
          <div class="lyssna-repertoire-split__spotify">
{lyssna_spotify_link_markup()}
          </div>
        </div>
      </div>
    </section>
""",
    )


    faqs = [
        (
            "Spelar ni i Småland och Skåne?",
            "Ja. Vår kärnregion är Växjö, Älmhult, Kalmar, Jönköping, Lund, Malmö och Helsingborg, det vill säga Småland och Skåne.",
        ),
        (
            "Spelar ni utanför ert område?",
            "Oftast ja, om datum och logistik går ihop. Maila plats och datum så återkommer vi med vad som är rimligt.",
        ),
        (
            "Sedan när finns Halv Fjorton?",
            "Bandet grundades 2018 i Växjö. Sedan dess har vi spelat på bröllop, företagsfester och privata fester i hela södra Sverige, och varje december ger vi våra egna julkonserter.",
        ),
        (
            "Hur stort är bandet?",
            "Vi är åtta musiker med sång, rytmsektion och egen blåssektion. Namnet kommer från att vi började som sju, alltså halva fjorton.",
        ),
        (
            "Hur länge spelar ni?",
            "På de flesta fester spelar vi två set partymusik. Mingel eller vigsel utöver det planeras separat i offerten.",
        ),
        (
            "Kan ni spela både mingel och fest?",
            "Ja, det är ett av våra vanligaste upplägg. Mingel i mer återhållen stil, sedan två set dans när rummet är redo.",
        ),
        (
            "Kan ni spela till vigseln?",
            "Ja. Vi kan spela vigselmusik med helband, komp till solist eller kombinera med psalmer. Läs mer under bröllop.",
        ),
        (
            "Kan ni kompa en artist?",
            "Ja. Vi fungerar som kompband för solist, gästsång eller inhyrd artist. Se sidan bröllop.",
        ),
        (
            "Kan ni göra specialarrangemang?",
            "Ja. Första dans, fanfar, musik under middag eller sambatåg går ofta att lösa om ni hör av er i tid.",
        ),
        (
            "Hur bokar man?",
            "Maila halvfjorton@gmail.com med datum, plats och typ av tillställning. Vi återkommer med upplägg och offert, som PDF på begäran.",
        ),
        (
            "Hur löser ni ljud och teknik?",
            f"{LOKAL_TEKNIK_COPY} Detaljer följer i offert och rider närmare spelningen.",
        ),
        (
            "Hur lång framförhållning behövs?",
            "Så tidigt ni kan, särskilt lördagar under bröllopssäsong. Kortare varsel kan funka - fråga hellre än att anta att det är fullt.",
        ),
        (
            "Vem fakturerar?",
            "Halv Fjorton, organisationsnummer 769641-5418. Mejl halvfjorton@gmail.com.",
        ),
    ]
    faq_list = faq_list_two_columns(faqs)

    page(
        "/faq/",
        "Vanliga frågor om Halv Fjorton | bokning, teknik och repertoar",
        "FAQ om Halv Fjorton: bandstorlek, teknik, tillfällen, södra Sverige, bokning, framförhållning och skräddarsydd repertoar.",
        extra_ld=[faq_page_ld(tuple(faqs))],
        extra_scripts='  <script src="/assets/js/faq-accordion.js" defer></script>\n',
        body=f"""    <header class="page-hero compact">
      <div class="page-hero-copy">
        <h1>Vanliga frågor</h1>
        <p class="lead">Svar på det vi oftast får frågor om.</p>
        <p class="page-hero__actions">
          <a class="alt-btn alt-btn--primary" href="/kontakt/">Frågor? Kontakta oss</a>
        </p>
      </div>
    </header>
    <section class="section">
      <div class="wrap alt-faq">
{faq_list}
      </div>
    </section>
""",
    )

    page(
        "/kontakt/",
        "Kontakta Halv Fjorton | boka coverband i södra Sverige",
        "Kontakta Halv Fjorton för bokning: halvfjorton@gmail.com. Coverband till bröllop, företag och fest i Växjö och södra Sverige.",
        extra_ld=[contact_page_ld()],
        extra_scripts='  <script src="/assets/js/tally-embed.js" defer></script>\n',
        body=kontakt_page_body(),
        page_class="alt-page--kontakt alt-page--header-light-top",
    )

    page(
        "/integritetspolicy/",
        "Integritetspolicy | Halv Fjorton",
        "Så behandlar Halv Fjorton personuppgifter från kontaktformuläret: vad vi samlar in, varför, hur länge vi sparar och dina rättigheter.",
        breadcrumb_name="Integritetspolicy",
        body=integritetspolicy_page_body(),
        robots_tag="noindex,follow",
    )

    page(
        "/404.html",
        "Sidan hittades inte | Halv Fjorton",
        "Sidan finns inte. Gå till startsidan eller kontakta Halv Fjorton.",
        outfile=OUT_ROOT / "404.html",
        robots_tag="noindex,nofollow",
        include_canonical=False,
        body="""    <header class="page-hero compact">
      <div class="page-hero-copy">
        <h1>Sidan finns inte</h1>
        <p class="lead">Länken kan vara gammal. Prova startsidan eller kontakta oss om ni letade efter en bokning.</p>
        <div class="actions">
          <a class="btn btn-primary" href="/">Till startsidan</a>
          <a class="btn btn-ghost" href="/kontakt/">Kontakt</a>
        </div>
      </div>
    </header>
""",
    )

    write_redirect_page(
        "/repertoar/",
        "/lyssna/#repertoar",
        title="Repertoar | omdirigering",
        message="Repertoaren finns nu under Lyssna.",
        link_label="Lyssna",
    )
    write_redirect_page(
        "/mingel/",
        "/fest-och-mingel/",
        title="Fest och mingel | omdirigering",
        message="Den gamla adressen /mingel/ pekar nu till Fest och mingel.",
        link_label="Fest och mingel",
    )
    write_redirect_page(
        "/lyssna-på-oss/",
        "/lyssna/",
        title="Lyssna | omdirigering",
        message="Den gamla adressen /lyssna-på-oss/ pekar nu till Lyssna.",
        link_label="Lyssna",
    )


def write_sitemap():
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path in SITEMAP_PATHS:
        priority = "1.0" if path == "/" else "0.8"
        lines.extend(
            [
                "  <url>",
                f"    <loc>{SITE}{path}</loc>",
                "    <changefreq>monthly</changefreq>",
                f"    <priority>{priority}</priority>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    dest = OUT_ROOT / "sitemap.xml"
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", dest.relative_to(OUT_ROOT))


def write_llms_txt():
    text = f"""# Halv Fjorton

> Cover- och partyband med åtta musiker och egen blåssektion från Växjö. Grundat 2018. Soul, funk, rock och svenska klassiker.

## Kontakt
- E-post: halvfjorton@gmail.com
- Org.nr: 769641-5418
- Bokning: en kontakt, offert som PDF på begäran
- Instagram: https://www.instagram.com/halvfjorton/
- YouTube: https://www.youtube.com/@halvfjorton9292

## Område
Bandet utgår från Växjö och spelar på begäran i hela södra Sverige (Småland och Skåne), till exempel Kalmar, Jönköping, Malmö, Lund och Helsingborg. Älmhult och andra orter ingår; spelningar utanför södra Sverige går att diskutera.

## Tjänster
- Bröllop: {SITE}/brollop/
- Företag: {SITE}/foretag/
- Fest och mingel: {SITE}/fest-och-mingel/

## Viktiga sidor
- Startsida: {SITE}/
- FAQ: {SITE}/faq/
- Kontakt: {SITE}/kontakt/
- Konserter: {SITE}/konserter/
- Repertoar: {SITE}/lyssna/#repertoar
"""
    dest = OUT_ROOT / "llms.txt"
    dest.write_text(text, encoding="utf-8")
    print("wrote", dest.relative_to(OUT_ROOT))


def write_home_jsonld():
    home_path = OUT_ROOT / "index.html"
    html = home_path.read_text(encoding="utf-8")
    graph = jsonld_graph_markup([music_group_ld(), breadcrumb_ld([("/", "Hem")])])
    block = f"""  <script type="application/ld+json">
  {graph}
  </script>
"""
    if re.search(r'<script type="application/ld\+json">', html):
        html = re.sub(
            r'  <script type="application/ld\+json">.*?</script>\n',
            block,
            html,
            count=1,
            flags=re.DOTALL,
        )
    else:
        html = html.replace(
            '  <link rel="stylesheet" href="/assets/css/site.css">\n',
            f'  <link rel="stylesheet" href="/assets/css/site.css">\n{block}',
        )
    home_path.write_text(html, encoding="utf-8")
    print("wrote", home_path.relative_to(OUT_ROOT), "(json-ld)")


def patch_home_page():
    home_path = OUT_ROOT / "index.html"
    html = home_path.read_text(encoding="utf-8")
    html = html.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
    )
    logo = "\n".join("        " + line for line in brand_logo_markup().splitlines())
    html = re.sub(
        r'<img src="/assets/img/logo-mark\.png"[^>]*>\s*',
        logo + "\n",
        html,
    )
    html = re.sub(
        r"\s*<svg class=\"brand-mark\".*?</svg>\s*",
        "\n" + logo + "\n",
        html,
        count=1,
        flags=re.DOTALL,
    )
    if 'aria-label="Halv Fjorton"' not in html.split("<header", 1)[-1][:800]:
        html = html.replace(
            '<a class="alt-brand brand" href="/">',
            '<a class="alt-brand brand" href="/" aria-label="Halv Fjorton">',
            1,
        )
    html = html.replace(
        '<span class="alt-facts__placeholder">Grundat [ÅR - fyll i]</span>',
        "<span>Grundat 2018</span>",
    )
    html = re.sub(
        r"      <div class=\"alt-facts\">[\s\S]*?      </div>\n    </section>",
        home_alt_facts_block() + "\n    </section>",
        html,
        count=1,
    )
    if 'name="twitter:card"' not in html:
        twitter_block = (
            '  <meta name="twitter:card" content="summary_large_image">\n'
            '  <meta name="twitter:title" content="Halv Fjorton | Coverband från Växjö">\n'
            '  <meta name="twitter:description" content="Soul, funk, rock och svenska klassiker med åtta musiker. Bröllop, företag och event i södra Sverige.">\n'
            f'  <meta name="twitter:image" content="{OG}">\n'
        )
        html = html.replace(
            '  <meta property="og:image" content="https://halvfjorton.se/assets/img/og.jpg">',
            '  <meta property="og:image" content="https://halvfjorton.se/assets/img/og.jpg">\n' + twitter_block,
            1,
        )
    html = html.replace(
        '  <script src="/assets/js/nav.js"></script>',
        '  <script src="/assets/js/nav.js" defer></script>',
    )
    if 'src="/assets/js/header-scroll.js"' not in html:
        html = html.replace(
            '  <script src="/assets/js/nav.js" defer></script>',
            '  <script src="/assets/js/nav.js" defer></script>\n  <script src="/assets/js/header-scroll.js" defer></script>',
        )
    html = re.sub(
        r'^[ \t]*<nav class="alt-nav" aria-label="Huvudmeny">[\s\S]*?</nav>',
        home_nav_block("/", "#offert"),
        html,
        count=1,
        flags=re.MULTILINE,
    )
    bootstrap = alt_header_scroll_bootstrap_script()
    if "alt-header-state-init" not in html:
        html = html.replace(
            "  </header>\n",
            "  </header>\n" + bootstrap + "\n",
            1,
        )
    if "data-mobile-menu" not in html:
        html = html.replace(
            "  </header>\n\n  <main id=\"innehall\">",
            "  </header>\n\n" + mobile_menu_block("/", "#offert") + "\n\n  <main id=\"innehall\">",
            1,
        )
    else:
        html = re.sub(
            r'  <div class="mobile-menu" id="mobile-menu"[\s\S]*?</div>\n\n  <main',
            mobile_menu_block("/", "#offert") + "\n\n  <main",
            html,
            count=1,
        )
    html = re.sub(
        r'href="mailto:halvfjorton@gmail.com\?subject=Beg%C3%A4r%20offert[^"]*"',
        'href="#offert"',
        html,
    )
    html = re.sub(
        r'    <section class="alt-intro"[\s\S]*?</section>\n\n',
        "",
        html,
        count=1,
    )
    alt_offert = contact_offert_section(
        section_class="alt-contact-offert",
        wrap_class="alt-contact-offert__wrap contact-offert__grid",
        lead="Skriv datum, plats och vad ni planerar, så återkommer vi med tillgänglighet och förslag.",
        usps=HOME_OFFERT_USPS,
    )
    if re.search(r'<section class="alt-contact-offert"', html):
        html = re.sub(
            r'    <section class="alt-contact-offert"[\s\S]*?</section>',
            alt_offert,
            html,
            count=1,
        )
    else:
        html = re.sub(
            r'    <section class="alt-cta"[\s\S]*?</section>',
            alt_offert,
            html,
            count=1,
        )
    if 'tally-embed.js' not in html:
        html = html.replace(
            '  <script src="/assets/js/header-scroll.js" defer></script>',
            '  <script src="/assets/js/header-scroll.js" defer></script>\n  <script src="/assets/js/tally-embed.js" defer></script>',
        )
    home_tw_phrases = esc(
        json.dumps(
            [
                "bröllopsfesten",
                "kickoffen",
                "50-årsfesten",
                "julfesten",
                "företagsfesten",
                "kvällen som aldrig tar slut",
                "oktoberfesten?",
            ],
            ensure_ascii=False,
        )
    )
    html = re.sub(
        r'(<span class="alt-hero__typewriter" data-alt-typewriter)(?!\s+data-typewriter-phrases)',
        rf'\1 data-typewriter-phrases="{home_tw_phrases}"',
        html,
        count=1,
    )
    if 'hero-typewriter.js' not in html:
        html = html.replace(
            '  <script src="/assets/js/header-scroll.js" defer></script>',
            '  <script src="/assets/js/header-scroll.js" defer></script>\n  <script src="/assets/js/hero-typewriter.js" defer></script>',
        )
    if 'section-typewriter.js' not in html:
        html = html.replace(
            '  <script src="/assets/js/hero-typewriter.js" defer></script>',
            '  <script src="/assets/js/hero-typewriter.js" defer></script>\n  <script src="/assets/js/section-typewriter.js" defer></script>',
        )
    toggle = alt_header_mobile_controls_markup("mobile-menu")
    html = re.sub(
        r'<button class="(?:alt-nav-toggle )?nav-toggle"[^>]*>.*?</button>',
        toggle.strip(),
        html,
        count=1,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'\s*<div class="nav-backdrop" data-nav-backdrop hidden></div>\s*',
        "\n",
        html,
        count=1,
    )
    html = re.sub(
        r"  <link rel=\"preconnect\" href=\"https://fonts\.googleapis\.com\">[^\n]*\n(?:  <link rel=\"preconnect\" href=\"https://fonts\.gstatic\.com\" crossorigin>\n)?  <link href=\"https://fonts\.googleapis\.com/css2[^\"]*\" rel=\"stylesheet\">\n",
        font_preloads("/assets") + "\n",
        html,
        count=1,
    )
    if "InterVariable.woff2" not in html:
        html = html.replace(
            '  <link rel="stylesheet" href="/assets/css/site.css">\n',
            font_preloads("/assets") + '\n  <link rel="stylesheet" href="/assets/css/site.css">\n',
        )
    if "static.cloudflareinsights.com" not in html.split("</head>", 1)[0]:
        html = html.replace(
            '  <link rel="stylesheet" href="/assets/css/site.css">\n',
            head_resource_hints() + '  <link rel="stylesheet" href="/assets/css/site.css">\n',
            1,
        )
    html = re.sub(
        r'  <footer class="site-footer"[\s\S]*?  </footer>',
        modern_footer_markup(),
        html,
        count=1,
    )
    html = patch_home_hero_src_sizes(html)
    home_path.write_text(html, encoding="utf-8")
    print("wrote", home_path.relative_to(OUT_ROOT), "(home patches)")


_DASH_CHARS = ("\u2013", "\u2014")  # en dash, em dash


def assert_no_ai_dashes_in_build(target: Path) -> None:
    """Fail the build if typographic dashes remain in shipped site files."""
    extensions = {".html", ".xml", ".txt", ".css", ".js"}
    offenders: list[str] = []
    for file_path in target.rglob("*"):
        if not file_path.is_file() or file_path.suffix not in extensions:
            continue
        text = file_path.read_text(encoding="utf-8")
        for ch in _DASH_CHARS:
            if ch in text:
                offenders.append(f"{file_path.relative_to(target)} ({ch!r})")
                break
    if offenders:
        sample = "\n".join(f"  - {line}" for line in offenders[:20])
        extra = f"\n  ... and {len(offenders) - 20} more" if len(offenders) > 20 else ""
        raise SystemExit(f"Build check failed: en/em dash found in output:\n{sample}{extra}")


_EYEBROW_IN_HTML = re.compile(r"""class\s*=\s*["'][^"']*\beyebrow\b""", re.IGNORECASE)


def assert_offert_bullet_cap(target: Path, max_items: int = 2) -> None:
    offenders: list[str] = []
    for file_path in target.rglob("*.html"):
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8")
        if 'id="offert"' not in text and "contact-offert__grid" not in text:
            continue
        count = text.count('<ul class="list-check">')
        if not count:
            continue
        # Count <li> inside first offert list-check block only (rough slice).
        start = text.find('<ul class="list-check">')
        if start < 0:
            continue
        end = text.find("</ul>", start)
        block = text[start:end] if end > start else ""
        li_count = block.count("<li>")
        if li_count > max_items:
            offenders.append(f"{file_path.relative_to(target)} ({li_count} bullets)")
    if offenders:
        sample = "\n".join(f"  - {line}" for line in offenders[:20])
        raise SystemExit(
            f"Build check failed: offert list-check exceeds {max_items} items:\n{sample}"
        )


_GALLERY_IMG_SRC_STEM = re.compile(
    r'<img[^>]*\ssrc="[^"]*/assets/img/gallery/(halvfjorton-\d+)-\d+w\.webp"',
    re.IGNORECASE,
)


def assert_no_duplicate_gallery_images_on_page(target: Path) -> None:
    offenders: list[str] = []
    for file_path in target.rglob("*.html"):
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8")
        if "alt-service-hero" not in text:
            continue
        hero_match = re.search(
            r'<header class="alt-service-hero">.*?</header>',
            text,
            flags=re.DOTALL,
        )
        hero_text = hero_match.group(0) if hero_match else ""
        body_text = text.replace(hero_text, "", 1) if hero_match else text
        body_stems = _GALLERY_IMG_SRC_STEM.findall(body_text)
        if not body_stems:
            continue
        counts: dict[str, int] = {}
        for stem in body_stems:
            counts[stem] = counts.get(stem, 0) + 1
        dupes = {stem for stem, n in counts.items() if n > 1}
        if dupes:
            offenders.append(
                f"{file_path.relative_to(target)} ({', '.join(sorted(dupes))})"
            )
    if offenders:
        sample = "\n".join(f"  - {line}" for line in offenders[:20])
        raise SystemExit(
            "Build check failed: duplicate gallery image on same page:\n" + sample
        )


def assert_no_eyebrows_in_build(target: Path) -> None:
    offenders: list[str] = []
    for file_path in target.rglob("*.html"):
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8")
        if _EYEBROW_IN_HTML.search(text):
            offenders.append(str(file_path.relative_to(target)))
    if offenders:
        sample = "\n".join(f"  - {line}" for line in offenders[:20])
        extra = f"\n  ... and {len(offenders) - 20} more" if len(offenders) > 20 else ""
        raise SystemExit(f"Build check failed: eyebrow kickers found in output:\n{sample}{extra}")



def assert_integritetspolicy_links_in_build(target: Path) -> None:
    footer_offenders: list[str] = []
    consent_offenders: list[str] = []
    for file_path in target.rglob("*.html"):
        if not file_path.is_file():
            continue
        rel = str(file_path.relative_to(target))
        if (
            rel.startswith("repertoar/")
            or rel.startswith("mingel/")
            or rel.startswith("lyssna-på-oss/")
        ):
            continue
        text = file_path.read_text(encoding="utf-8")
        if 'class="site-footer"' in text:
            if (
                'href="' not in text
                or "integritetspolicy/" not in text
                or ">Integritetspolicy</a>" not in text
            ):
                footer_offenders.append(rel)
        if "data-tally-src" in text or TALLY_EMBED_SRC in text:
            if "contact-offert__consent" not in text or "integritetspolicy/" not in text:
                consent_offenders.append(rel)
    if footer_offenders:
        sample = "\n".join(f"  - {line}" for line in footer_offenders[:20])
        raise SystemExit(
            "Build check failed: footer missing Integritetspolicy link:\n" + sample
        )
    if consent_offenders:
        sample = "\n".join(f"  - {line}" for line in consent_offenders[:20])
        raise SystemExit(
            "Build check failed: contact form missing GDPR consent line:\n" + sample
        )


def assert_valid_jsonld_in_build(target: Path) -> None:
    """Every shipped page with JSON-LD must parse as one object with a @graph array."""
    html_paths = sorted(target.rglob("*.html"))
    offenders: list[str] = []
    for file_path in html_paths:
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(target).as_posix()
        if rel.startswith("home/") or rel.startswith("scripts/"):
            continue
        text = file_path.read_text(encoding="utf-8")
        match = re.search(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            text,
            flags=re.DOTALL,
        )
        if not match:
            continue
        try:
            data = json.loads(match.group(1).strip())
        except json.JSONDecodeError as exc:
            offenders.append(f"{rel}: invalid JSON ({exc})")
            continue
        if not isinstance(data, dict) or "@graph" not in data:
            offenders.append(f"{rel}: missing @graph wrapper")
            continue
        graph = data["@graph"]
        if not isinstance(graph, list) or not graph:
            offenders.append(f"{rel}: @graph must be a non-empty array")
            continue
        for node in graph:
            if not isinstance(node, dict) or "@type" not in node:
                offenders.append(f"{rel}: graph node missing @type")
                break
    if offenders:
        sample = "\n".join(f"  - {line}" for line in offenders[:25])
        raise SystemExit("Build check failed: JSON-LD validation:\n" + sample)


def assert_footer_styles_in_css(site_css: Path) -> None:
    if not site_css.is_file():
        raise SystemExit(f"Build check failed: missing stylesheet {site_css}")
    text = site_css.read_text(encoding="utf-8")
    required = (
        ".alt-page .site-footer__links",
        "list-style: none",
        ".alt-page .site-footer__inner",
    )
    missing = [needle for needle in required if needle not in text]
    if missing:
        raise SystemExit(
            "Build check failed: site.css footer rules missing: " + ", ".join(missing)
        )



def inject_production_cloudflare_analytics(target: Path) -> None:
    """Append Cloudflare Web Analytics before </body> on every shipped HTML page."""
    for file_path in sorted(target.rglob("*.html")):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(target).as_posix()
        if rel.startswith("home/"):
            continue
        text = file_path.read_text(encoding="utf-8")
        if CLOUDFLARE_ANALYTICS_MARKER in text:
            continue
        if "</body>" not in text:
            continue
        file_path.write_text(
            text.replace("</body>", f"{CLOUDFLARE_WEB_ANALYTICS_SNIPPET}</body>", 1),
            encoding="utf-8",
        )


def assert_lyssna_yt_posters_exist() -> None:
    for video_id in ("gm5C41wqYuU", "vV8aavPxYss", "UytyTLnKDWQ"):
        path = LYSSNA_POSTERS_DIR / f"{video_id}.webp"
        if not path.is_file():
            raise SystemExit(f"Build check failed: missing lyssna poster {path.relative_to(ROOT)}")


def remove_legacy_home_publish_dir() -> None:
    """Drop /home/ from site output (homepage source lives under scripts/templates/)."""
    legacy = OUT_ROOT / "home"
    if legacy.is_dir():
        shutil.rmtree(legacy)
        print("removed", legacy.relative_to(OUT_ROOT), "(legacy publish path)")


def run_build(
    output_dir: Path | None = None,
    *,
    inject_cms_stub: bool = False,
) -> None:
    global OUT_ROOT
    OUT_ROOT = output_dir.resolve() if output_dir else ROOT
    if output_dir and OUT_ROOT != ROOT.resolve():
        prepare_output_directory(OUT_ROOT)
    else:
        OUT_ROOT.mkdir(parents=True, exist_ok=True)
        remove_legacy_home_publish_dir()
    assert_lyssna_yt_posters_exist()
    shutil.copy2(HOME_SOURCE, OUT_ROOT / "index.html")
    write_pages()
    write_sitemap()
    write_llms_txt()
    write_home_jsonld()
    patch_home_page()
    run_cms_build_steps(
        OUT_ROOT,
        ROOT,
        inject_cms_stub=inject_cms_stub,
    )
    inject_production_cloudflare_analytics(OUT_ROOT)
    assert_no_ai_dashes_in_build(OUT_ROOT)
    assert_no_eyebrows_in_build(OUT_ROOT)
    assert_no_duplicate_gallery_images_on_page(OUT_ROOT)
    assert_offert_bullet_cap(OUT_ROOT)
    assert_integritetspolicy_links_in_build(OUT_ROOT)
    assert_valid_jsonld_in_build(OUT_ROOT)
    assert_footer_styles_in_css(OUT_ROOT / "assets" / "css" / "site.css")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the Halv Fjorton static site.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Write generated site to this directory (copies assets/ and homepage template first). "
            "Omit for production (halvfjorton.se): build in place at repo root."
        ),
    )
    parser.add_argument(
        "--cms",
        action="store_true",
        help="Inject cms-stub.js on built HTML pages (local/dev CMS editing). Off by default for production.",
    )
    args = parser.parse_args()
    run_build(output_dir=args.output_dir, inject_cms_stub=args.cms)
