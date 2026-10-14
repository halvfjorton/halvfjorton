#!/usr/bin/env python3
"""Generate the Halv Fjorton static site."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://halvfjorton.se"
OG = f"{SITE}/assets/img/og.jpg"

NAV = [
    ("/", "Hem"),
    ("/brollop/", "Bröllop"),
    ("/foretag/", "Företag"),
    ("/mingel/", "Mingel"),
    ("/for-eventbolag/", "Eventbolag"),
    ("/om-oss/", "Om oss"),
    ("/lyssna/", "Lyssna"),
    ("/faq/", "FAQ"),
    ("/kontakt/", "Kontakt"),
]

ORG_DESC = (
    "Halv Fjorton är ett coverband och partyband med åtta musiker, "
    "rötter i Växjö och medlemmar över södra Sverige. Soul, funk, rock "
    "och svenska klassiker med egen blåssektion."
)

PA_TEKNIK_COPY = (
    "PA ingår vid privata fester, för företagsevent offereras det separat "
    "eller via er egen leverantör."
)


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def music_group_ld() -> str:
    return f"""{{
    "@context": "https://schema.org",
    "@type": ["MusicGroup", "PerformingGroup", "Organization"],
    "name": "Halv Fjorton",
    "legalName": "Halv Fjorton EK. FÖR.",
    "alternateName": "Halv 14",
    "description": "{ORG_DESC}",
    "url": "{SITE}/",
    "image": "{OG}",
    "email": "halvfjorton@gmail.com",
    "genre": ["Soul", "Funk", "Rock", "Coverband", "Partyband"],
    "foundingLocation": {{
      "@type": "Place",
      "name": "Växjö",
      "address": {{
        "@type": "PostalAddress",
        "addressLocality": "Växjö",
        "addressRegion": "Kronoberg",
        "addressCountry": "SE"
      }}
    }},
    "areaServed": "Södra Sverige",
    "sameAs": ["https://www.instagram.com/halvfjorton/"],
    "identifier": {{
      "@type": "PropertyValue",
      "propertyID": "orgnr",
      "value": "769641-5418"
    }}
  }}"""


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
    return f"""{{
    "@context": "https://schema.org",
    "@type": "Service",
    "name": "{name}",
    "description": "{desc}",
    "url": "{SITE}{url}",
    "areaServed": "Södra Sverige",
    "provider": {{
      "@type": "MusicGroup",
      "name": "Halv Fjorton",
      "url": "{SITE}/"
    }}
  }}"""


def page(
    path: str,
    title: str,
    description: str,
    extra_ld: list[str] | None = None,
    body: str = "",
    page_class: str = "",
    outfile: Path | None = None,
):
    canonical = f"{SITE}{path}"
    nav_items = []
    for href, label in NAV:
        current = ' aria-current="page"' if href == path else ""
        nav_items.append(f'          <li><a href="{href}"{current}>{label}</a></li>')
    nav = "\n".join(nav_items)
    graphs = [music_group_ld(), breadcrumb_ld([("/", "Hem")] + ([] if path == "/" else [(path, title.split(" | ")[0])]))]
    if extra_ld:
        graphs.extend(extra_ld)
    jsonld = ",\n  ".join(graphs)
    html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="index,follow">
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
  <link rel="icon" href="/assets/img/favicon.png" type="image/png">
  <link rel="apple-touch-icon" href="/assets/img/favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Syne:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">
  <script type="application/ld+json">
  {jsonld}
  </script>
</head>
<body class="{page_class}">
  <a class="skip-link" href="#innehall">Hoppa till innehållet</a>
  <header class="site-header" data-nav>
    <div class="header-inner">
      <a class="brand" href="/">
        <img class="brand-mark" src="/assets/img/logo-mark.png" alt="" width="42" height="42">
        <span>Halv Fjorton</span>
      </a>
      <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="meny">Meny</button>
      <nav id="meny" aria-label="Huvudmeny">
        <ul class="nav-list" data-nav-panel>
{nav}
        </ul>
      </nav>
    </div>
  </header>
  <main id="innehall">
{body}
  </main>
  <footer class="site-footer">
    <div class="wrap footer-grid">
      <div>
        <p><strong>Halv Fjorton EK. FÖR.</strong></p>
        <p class="small">Coverband och partyband från Växjö, med medlemmar över södra Sverige.</p>
        <p class="small">Organisationsnummer 769641-5418</p>
      </div>
      <div>
        <p><strong>Kontakt</strong></p>
        <ul class="small">
          <li><a href="mailto:halvfjorton@gmail.com">halvfjorton@gmail.com</a></li>
          <li><a href="https://www.instagram.com/halvfjorton/" rel="noopener noreferrer">Instagram @halvfjorton</a></li>
        </ul>
      </div>
      <div>
        <p><strong>Sidor</strong></p>
        <ul class="small">
          <li><a href="/brollop/">Bröllop</a></li>
          <li><a href="/foretag/">Företag</a></li>
          <li><a href="/for-eventbolag/">För eventbolag</a></li>
          <li><a href="/faq/">Vanliga frågor</a></li>
          <li><a href="/kontakt/">Hör av er</a></li>
        </ul>
      </div>
    </div>
  </footer>
  <script src="/assets/js/nav.js"></script>
</body>
</html>
"""
    dest = outfile
    if dest is None:
        dest = ROOT / (path.lstrip("/") + ("index.html" if path.endswith("/") else ""))
        if path == "/":
            dest = ROOT / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    print("wrote", dest.relative_to(ROOT))


def write_pages():
    page(
        "/",
        "Halv Fjorton | Sveriges svängigaste coverband",
        "Halv Fjorton är ett coverband med åtta musiker från södra Sverige. Soul, funk, rock och svenska klassiker till bröllop, företag och fest i Växjö och hela södern.",
        body=f"""    <section class="hero">
      <div class="hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">Coverband från Växjö</p>
          <h1>Sveriges svängigaste coverband</h1>
          <p class="lead">Åtta musiker med blås, soul och svenska klassiker. Bröllop, företag och fest i södra Sverige.</p>
          <div class="actions">
            <a class="btn btn-primary" href="/kontakt/">Hör av er</a>
            <a class="btn btn-ghost" href="/lyssna/">Lyssna</a>
          </div>
        </div>
        <figure class="hero-media">
          <img src="/assets/img/hero.jpg" alt="Halv Fjorton på scen i blått ljus, sångare och blåssektion framför publiken">
        </figure>
      </div>
    </section>

    <section class="section" aria-labelledby="vad-ar" data-reveal>
      <div class="wrap">
        <h2 id="vad-ar">Vad är Halv Fjorton?</h2>
        <div class="facts">
          <div class="fact surface"><strong>8 musiker</strong><p>Komplett band med sång, rytmsektion och blås. Namnet kommer från att vi började som sju, halva fjorton.</p></div>
          <div class="fact"><strong>Soul, funk och rock</strong><p>Stevie Wonder, Ray Charles, Earth, Wind &amp; Fire plus svenska klassiker som Björn Skifs och Tomas Ledin.</p></div>
          <div class="fact"><strong>Egen blåssektion</strong><p>Trumpet, saxofon och kör som ger festen det extra svänget.</p></div>
          <div class="fact"><strong>Södra Sverige</strong><p>Rötter i Växjö, medlemmar utspridda i södern. Bröllop, kickoffer och fester i hela regionen.</p></div>
          <div class="fact"><strong>PA och teknik</strong><p>{PA_TEKNIK_COPY}</p></div>
          <div class="fact"><strong>Ekonomisk förening</strong><p>Halv Fjorton EK. FÖR., org.nr 769641-5418. Tydlig motpart för par och företag.</p></div>
        </div>
      </div>
    </section>

    <section class="section section-alt" aria-labelledby="erbjudanden" data-reveal>
      <div class="wrap">
        <h2 id="erbjudanden">Vanliga upplägg</h2>
        <div class="offer-grid">
          <article class="offer-feature">
            <img src="/assets/img/fest.jpg" alt="Två bandmedlemmar i vita skjortor under en fest med konfetti, en med litet bastrumma">
            <h3><a href="/brollop/">Bröllop</a></h3>
            <p>Festen, vigseln, psalmer och komp till solist om ni vill. Upplägget skräddarsys efter er dag.</p>
            <p><a href="/brollop/">Till bröllop</a></p>
          </article>
          <article>
            <h3><a href="/mingel/">Mingel</a></h3>
            <p>Från traditionell jazz till svenska klassiker. Passar konferensmiddagar, mottagningar och bröllopsmingel.</p>
            <p><a href="/mingel/">Till mingel</a></p>
          </article>
          <article>
            <h3><a href="/foretag/">Fest och företag</a></h3>
            <p>Personalfest, kickoff, jubileum eller födelsedag. Gärna kombinerat med mingel tidigare under kvällen.</p>
            <p><a href="/foretag/">Till företag</a></p>
          </article>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="kort-om" data-reveal>
      <div class="wrap">
        <h2 id="kort-om">Kort om oss</h2>
        <p>Vi är Halv Fjorton, ett coverband på åtta medlemmar från södra Sverige. Grunden ligger i soul, funk och rock, med tillräcklig bredd för att hela rummet ska känna igen sig.</p>
        <p>Här är ett litet smakprov. Mer finns på lyssna-sidan, bland annat <em>Signed Sealed Delivered</em> från 2025 och vår reel från 2022.</p>
        <div class="embed" style="margin-top:1.4rem;border-radius:16px;overflow:hidden">
          <iframe src="https://www.youtube-nocookie.com/embed/V2Nb8jMKUCk" title="Signed Sealed Delivered - Halv Fjorton 2025" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>
        </div>
        <div class="actions">
          <a class="btn btn-ghost" href="/om-oss/">Möt bandet</a>
        </div>
      </div>
    </section>

    <section class="section section-alt" aria-labelledby="skraeddarsy" data-reveal>
      <div class="wrap split">
        <img src="/assets/img/stage.jpg" alt="Scen i lila ljus med mikrofonstativ och keyboard">
        <div>
          <h2 id="skraeddarsy">Tillsammans skräddarsyr vi ert event</h2>
          <p>Utöver repertoaren tar vi fram speciallösningar när det behövs. Musik under middagen? Ett sambatåg genom lokalen? Hör av er så ser vi hur vi kan lägga upp kvällen.</p>
          <p>{PA_TEKNIK_COPY} Behöver ni teknik utöver det som ingår hjälper vi till via uthyrare vi redan samarbetar med.</p>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="boka" data-reveal>
      <div class="wrap">
        <h2 id="boka">Vill ni att vi spelar på ert bröllop, fest eller annan tillställning?</h2>
        <p>Berätta datum, plats och vad ni är ute efter. Vi återkommer med ett förslag.</p>
        <div class="actions">
          <a class="btn btn-primary" href="/kontakt/">Hör av er</a>
          <a class="btn btn-ghost" href="/faq/">Vanliga frågor</a>
        </div>
      </div>
    </section>
""",
    )

    page(
        "/brollop/",
        "Bröllopsband i Växjö och södra Sverige | Halv Fjorton",
        "Boka Halv Fjorton som bröllopsband. Fest, vigsel, psalmer och komp till solist. Åtta musiker, blåssektion och egen teknik i Växjö och södra Sverige.",
        extra_ld=[
            service_ld(
                "Bröllopsband",
                "Liveband till bröllopsfest, vigsel, psalmer och komp av solist i södra Sverige.",
                "/brollop/",
            )
        ],
        body="""    <header class="page-hero">
      <div class="page-hero-copy">
        <p class="eyebrow">Bröllop</p>
        <h1>Ett bröllopsband som får hela släkten på dansgolvet</h1>
        <p class="lead">Vi har mångårig erfarenhet av att spela på bröllop och vet hur man får igång hela sällskapet - ung som gammal. Upplägget skräddarsys efter era önskemål.</p>
      </div>
    </header>
    <section class="section">
      <div class="wrap grid-2">
        <div>
          <h2>Vad vi kan göra på er dag</h2>
          <ul class="list-check">
            <li>Spelning på bröllopsfesten - dans, soul, funk, rock och svenska klassiker.</li>
            <li>Musik vid vigseln, psalmer och komp av solist om ni vill - vi erbjuder också kompband för artist.</li>
            <li>Mingel före middagen, från jazz till lågmälda svenska favoriter.</li>
            <li>PA ingår vid privata fester som bröllopsfesten.</li>
          </ul>
        </div>
        <div>
          <h2>Så lägger vi upp det</h2>
          <p>Ni berättar hur dagen ser ut: kyrka eller borgerligt, om ni vill ha oss redan vid vigseln, hur länge festen ska pågå och om det finns låtar som måste med. Vi tar fram ett förslag på tider, sättning och repertoar.</p>
          <p>Vi utgår från Växjö och spelar i hela södra Sverige. Boka gärna i god tid - särskilt lördagar under bröllopssäsongen.</p>
        </div>
      </div>
    </section>
    <section class="section section-alt">
      <div class="wrap">
        <h2>Vanliga önskemål</h2>
        <div class="faq-grid">
          <article><h3>Första dansen</h3><p>Vi lär in er låt om den inte redan finns i repertoaren, så länge den funkar live med band.</p></article>
          <article><h3>Generationsmix</h3><p>Samma kväll rymmer både Earth, Wind &amp; Fire och Tomas Ledin. Det är poängen.</p></article>
          <article><h3>Vigsel och fest</h3><p>Ett band genom hela dagen ger en röd tråd och en kontaktperson istället för tre olika akter.</p></article>
        </div>
        <div class="actions">
          <a class="btn btn-primary" href="/kontakt/">Hör av er</a>
          <a class="btn btn-ghost" href="/mingel/">Kombinera med mingel</a>
        </div>
      </div>
    </section>
""",
    )

    page(
        "/foretag/",
        "Coverband till företagsfest, kickoff och jubileum | Halv Fjorton",
        "Halv Fjorton spelar på personalfest, kickoff, jubileum och konferens i södra Sverige. Åtta musiker och egen blåssektion.",
        extra_ld=[
            service_ld(
                "Coverband till företagsevent",
                "Liveband till personalfest, kickoff, jubileum och konferens i södra Sverige.",
                "/foretag/",
            )
        ],
        body=f"""    <header class="page-hero">
      <div class="page-hero-copy">
        <p class="eyebrow">Företag och fest</p>
        <h1>Ett liveband som lyfter personalfesten</h1>
        <p class="lead">Personalfest, jubileum, kickoff eller födelsedag. Gärna mingel först, sedan dans när rummet är redo.</p>
      </div>
    </header>
    <section class="section">
      <div class="wrap">
        <h2>När företag bokar oss</h2>
        <div class="faq-grid">
          <article><h3>Personalfest och julbord</h3><p>Kvällar där kollegor faktiskt dansar. Soul och funk som fungerar även om gästlistan är blandad.</p></article>
          <article><h3>Kickoff och konferens</h3><p>Mingel till fördrinken, mer tryck efter middagen. Vi anpassar volym och repertoar efter lokalen och programmet.</p></article>
          <article><h3>Jubileum och kundkväll</h3><p>När ni vill visa något mer än en spellista. Ett komplett band med blås ger tyngd utan att bli stelt.</p></article>
        </div>
      </div>
    </section>
    <section class="section section-alt">
      <div class="wrap split">
        <div>
          <h2>Det som brukar avgöra</h2>
          <ul class="list-check">
            <li><strong>Blåssektion.</strong> Trumpet, sax och kör - mer än gitarr, bas och trummor i ett hörn.</li>
            <li><strong>Teknik och PA.</strong> {PA_TEKNIK_COPY}</li>
            <li><strong>Bred repertoar.</strong> Från Stevie Wonder till Björn Skifs. Det gör att både vd och sommarjobbare känner igen något.</li>
            <li><strong>Södra Sverige som hemmaplan.</strong> Växjö i botten, medlemmar i bland annat Malmö och Skåne. Rimliga restider i södern.</li>
            <li><strong>En motpart.</strong> Ekonomisk förening med organisationsnummer, faktura och en bokningskontakt.</li>
          </ul>
        </div>
        <div>
          <h2>Ett typiskt upplägg</h2>
          <p>Mingel 45-90 minuter medan gästerna kommer in. Paus under middag och tal. Därefter ett längre dansblock. Tider justeras efter er agenda - inte tvärtom.</p>
          <p>Vill ni ha fanfar, extra akt eller bakgrund under mingelmat? Säg till. Vi tar fram ett konkret förslag när vi vet datum, plats, antal gäster och ungefärlig sluttid.</p>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <h2>Praktiskt för den som bokar</h2>
        <div class="grid-2">
          <article class="card">
            <h3>Vad som följer med</h3>
            <p>Band och liveupplevelse med blåssektion. {PA_TEKNIK_COPY} Behöver ni extra täckning i en stor sal har vi uthyrare vi redan jobbar med.</p>
          </article>
          <article class="card">
            <h3>Vad vi behöver av er</h3>
            <p>Datum, adress, ungefärligt antal, om det är mingel plus fest, och om lokalen har begränsningar. Resten kan vi ta i ett samtal.</p>
          </article>
        </div>
        <div class="quote-placeholder">
          <p><strong>Citat från arrangörer | läggs till</strong></p>
          <p>Här kan referenser från företag och eventbyråer publiceras när de finns. Inga påhittade omdömen.</p>
        </div>
        <div class="actions">
          <a class="btn btn-primary" href="/kontakt/">Hör av er</a>
          <a class="btn btn-ghost" href="/for-eventbolag/">Information till eventbolag</a>
        </div>
      </div>
    </section>
""",
    )

    page(
        "/mingel/",
        "Mingelband och jazz till mottagning | Halv Fjorton",
        "Halv Fjorton spelar mingel med jazz och svenska klassiker. Passar konferensmiddag, bröllopsmottagning och företagsmingel i södra Sverige.",
        extra_ld=[
            service_ld(
                "Mingel och mottagning",
                "Live mingelmusik från traditionell jazz till svenska klassiker.",
                "/mingel/",
            )
        ],
        body="""    <header class="page-hero">
      <div class="page-hero-copy">
        <p class="eyebrow">Mingel</p>
        <h1>Musik som fyller rummet utan att ta över samtalet</h1>
        <p class="lead">Vi erbjuder spelning vid mingel med blandad repertoar. Allt från traditionell jazz till svenska klassiker. Upplägget passar konferensmiddagar, bröllopsmottagningar och andra sammankomster där gästerna ska kunna prata - och ändå känna att det händer något.</p>
      </div>
    </header>
    <section class="section">
      <div class="wrap grid-2">
        <div>
          <h2>När mingel är rätt val</h2>
          <p>Innan middagen, under fördrink, i foajén eller på en sommaräng. Vi spelar lägre, mer akustiskt i känslan, men med samma musiker - så kvällen kan växa till fest utan att byta band.</p>
          <ul class="list-check">
            <li>Bröllopsmottagning mellan vigsel och middag</li>
            <li>Konferensmiddag och after work</li>
            <li>Jubileum där första timmen ska vara samtal, inte diskotek</li>
          </ul>
        </div>
        <div>
          <h2>Repertoaren i korthet</h2>
          <p>Jazzstandard, soul i dämpat tempo, svenska visor och klassiker. Vill ni ha en tydlig tråd - till exempel bara jazz, eller mest svenskt - säger ni det så styr vi dit.</p>
          <p>Många bokar mingel plus fest samma kväll. Det är vårt vanligaste kombinerade upplägg, och det vi rekommenderar när tiden räcker.</p>
          <div class="actions">
            <a class="btn btn-primary" href="/kontakt/">Hör av er</a>
            <a class="btn btn-ghost" href="/brollop/">Se bröllop</a>
          </div>
        </div>
      </div>
    </section>
""",
    )

    page(
        "/om-oss/",
        "Om Halv Fjorton | partyband från Växjö",
        "Halv Fjorton är ett partyband med rötter i Växjö och åtta medlemmar i södra Sverige. Soul, funk och svenska klassiker med blåssektion.",
        body="""    <header class="page-hero compact">
      <div class="page-hero-copy">
        <p class="eyebrow">Om oss</p>
        <h1>Vilka är Halv Fjorton?</h1>
        <p class="lead">Ett partyband med rötter i Växjö. Medlemmarna är spridda över södra Sverige. Namnet kan låta knepigt, men det är enkelt: ursprungligen var vi sju - halva fjorton. Numera är vi åtta, även om vi inte gör någon stor sak av det.</p>
      </div>
    </header>
    <section class="section">
      <div class="wrap">
        <h2>Musiken</h2>
        <p>Vårt mål är fester som blir minnesvärda. Vi brinner för att dela musikalisk glädje. Som ett komplett band med dynamisk blåssektion har vi en bred repertoar. Huvudinriktningen är funk och soul: Stevie Wonder, Ray Charles, Earth, Wind &amp; Fire. Därtill svenska favoriter som Björn Skifs och Tomas Ledin.</p>
        <p>Styrkan är mångsidigheten. Det som behövs för att göra festen speciell, det ställer vi upp på. När ni bokar oss ska kvällen kännas unik - inte som en slumpmässig coverkväll.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <h2>Föreningen</h2>
        <p>Vi är <strong>Halv Fjorton EK. FÖR.</strong>, organisationsnummer <strong>769641-5418</strong>. Kontakt: <a href="mailto:halvfjorton@gmail.com">halvfjorton@gmail.com</a>, Instagram <a href="https://www.instagram.com/halvfjorton/">@halvfjorton</a>.</p>
      </div>
    </section>
""",
    )

    page(
        "/lyssna/",
        "Lyssna på Halv Fjorton | film, reel och julkonserter",
        "Se Halv Fjorton live: Signed Sealed Delivered 2025, reel 2022 och julkonserterna A Soulful Christmas.",
        body="""    <header class="page-hero compact">
      <div class="page-hero-copy">
        <p class="eyebrow">Media</p>
        <h1>Lyssna på oss</h1>
        <p class="lead">Filmer från scen och julkonserter. Samma band som ni bokar till bröllop, företag och mingel.</p>
      </div>
    </header>
    <section class="section">
      <div class="wrap media-grid">
        <article class="media-card">
          <div class="embed">
            <iframe src="https://www.youtube-nocookie.com/embed/V2Nb8jMKUCk" title="Signed Sealed Delivered - Halv Fjorton 2025" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>
          </div>
          <div class="meta">
            <h2>Signed Sealed Delivered - 2025</h2>
            <p>Aktuell livevideo. Ett smakprov på sound, blås och sång.</p>
          </div>
        </article>
        <article class="media-card">
          <div class="embed">
            <iframe src="https://www.youtube-nocookie.com/embed/gm5C41wqYuU" title="Halv Fjorton Reel 2022" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>
          </div>
          <div class="meta">
            <h2>Reel 2022</h2>
            <p>Kortare klipp från spelningar - bra att skicka vidare till den som inte var med.</p>
          </div>
        </article>
      </div>
    </section>
    <section class="section section-alt">
      <div class="wrap">
        <h2>Lyssna på våra julkonserter</h2>
        <p class="muted">A Soulful Christmas och en julmässa med vänner. Inbäddade från bandets tidigare mediasida.</p>
        <div class="media-grid">
          <article class="media-card">
            <div class="embed"><iframe src="https://www.youtube-nocookie.com/embed/vV8aavPxYss" title="A Soulful Christmas 2024 - 8 december, Nygatan 6" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe></div>
            <div class="meta"><h3>A Soulful Christmas 2024</h3><p>8 december, Nygatan 6.</p></div>
          </article>
          <article class="media-card">
            <div class="embed"><iframe src="https://www.youtube-nocookie.com/embed/UytyTLnKDWQ" title="A Soulful Christmas 2023 - 3 december, Nygatan 6" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe></div>
            <div class="meta"><h3>A Soulful Christmas 2023</h3><p>3 december, Nygatan 6.</p></div>
          </article>
          <article class="media-card">
            <div class="embed"><iframe src="https://www.youtube-nocookie.com/embed/lAmSo6wGjqo" title="Halv Fjorton med vänner och mässa - 26 december 2022" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe></div>
            <div class="meta"><h3>Med vänner och mässa</h3><p>26 december 2022.</p></div>
          </article>
          <article class="media-card">
            <div class="embed"><iframe src="https://www.youtube-nocookie.com/embed/R0fqTXcAbgc" title="A Soulful Christmas 2018" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe></div>
            <div class="meta"><h3>A Soulful Christmas 2018</h3><p>Tidigare julkonsert.</p></div>
          </article>
        </div>
        <p class="small muted">Fler klipp och pressbilder kan läggas här. Se även <a href="https://www.instagram.com/halvfjorton/">Instagram @halvfjorton</a>.</p>
      </div>
    </section>
""",
    )

    page(
        "/for-eventbolag/",
        "Boka Halv Fjorton via eventbolag | underlag för bookers",
        "Underlag för eventbolag och bookers: kort bio, vad som ingår, teknik, presskit, organisationsuppgifter och bokningsgång för Halv Fjorton.",
        extra_ld=[
            service_ld(
                "Bokning via eventbolag",
                "Coverband för eventbyråer och bookers i södra Sverige.",
                "/for-eventbolag/",
            )
        ],
        body=f"""    <header class="page-hero compact">
      <div class="page-hero-copy">
        <p class="eyebrow">För eventbolag och bookers</p>
        <h1>Ett komplett partyband ni kan sätta i offerten utan att gissa</h1>
        <p class="lead">Halv Fjorton är åtta musiker med egen blåssektion. Rötter i Växjö, spelningar i södra Sverige. Soul, funk, rock och svenska klassiker.</p>
      </div>
    </header>
    <section class="section">
      <div class="wrap grid-2">
        <div>
          <h2>Kort bio att återanvända</h2>
          <p>Halv Fjorton är ett cover- och partyband från södra Sverige. Bandet har åtta permanenta medlemmar, egen blåssektion och en repertoar med tyngdpunkt i soul och funk - Stevie Wonder, Ray Charles, Earth, Wind &amp; Fire - plus svenska klassiker som Björn Skifs och Tomas Ledin. Vanliga bokningar: bröllop (även vigsel/psalmer), mingel, personalfest, kickoff och jubileum.</p>
        </div>
        <div>
          <h2>Vad kunden får</h2>
          <ul class="list-check">
            <li>8 musiker på scen (sång, gitarr, bas, trummor, klaviatur, slagverk, trumpet, saxofon)</li>
            <li>{PA_TEKNIK_COPY}</li>
            <li>Möjlighet att kombinera mingel och dansspelning samma kväll</li>
            <li>Specialönskemål: middag, sambatåg, fanfar, utvald första dans</li>
          </ul>
        </div>
      </div>
    </section>
    <section class="section section-alt">
      <div class="wrap">
        <h2>Teknik i korthet</h2>
        <p>{PA_TEKNIK_COPY} Exakt inputlista, scenskiss och strömbehov skickas per spelning - underlaget här är en sammanfattning, inte ett färdigt rider.</p>
        <div class="faq-grid">
          <article><h3>Ljud</h3><p>{PA_TEKNIK_COPY} Extra täckning eller linjearray via samarbetande uthyrare vid behov.</p></article>
          <article><h3>Scen</h3><p>Åtta musiker på scen. Bekräfta scendmått och bärväg i lokalen så att vi inte gissar lastning.</p></article>
          <article><h3>Rider</h3><p><em>Teknisk rider, kanallista och scenskiss läggs till som nedladdningsbara PDF:er här.</em></p></article>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap grid-2">
        <div>
          <h2>Presskit</h2>
          <ul class="list-check">
            <li>Film: <a href="/lyssna/">Signed Sealed Delivered 2025</a> och <a href="/lyssna/">Reel 2022</a></li>
            <li>Foton: scenfoton på den här sajten</li>
            <li><em>Högupplösta pressfoton och logotyppaket läggs till</em></li>
            <li>Instagram: <a href="https://www.instagram.com/halvfjorton/">@halvfjorton</a></li>
          </ul>
        </div>
        <div>
          <h2>Organisation och avtal</h2>
          <p>Halv Fjorton EK. FÖR.<br>Org.nr 769641-5418<br><a href="mailto:halvfjorton@gmail.com">halvfjorton@gmail.com</a></p>
          <p>Faktura mot företag och byrå. En bokningskontakt från vår sida. Inga påhittade referenslogotyper här - be oss om aktuella referenser till liknande event.</p>
        </div>
      </div>
    </section>
    <section class="section section-alt">
      <div class="wrap">
        <h2>Bokningsgång</h2>
        <div class="faq-grid">
          <article><h3>Förfrågan</h3><p>Datum, ort, typ av event, antal gäster, mingel plus fest eller bara en del, sluttid.</p></article>
          <article><h3>Förslag</h3><p>Vi återkommer om tillgänglighet, sättning och ett konkret upplägg. Därefter offert.</p></article>
          <article><h3>Bekräftelse</h3><p>Skriftlig bokning. Teknikdetaljer och tidsplan närmare eventet. Deposition enligt överenskommelse.</p></article>
        </div>
        <p>Säsongstoppar är lördagar vår-sommar och julperioder. Hör av er tidigt om datumet är låst.</p>
        <div class="actions">
          <a class="btn btn-primary" href="/kontakt/">Hör av er</a>
          <a class="btn btn-ghost" href="/faq/">FAQ</a>
        </div>
      </div>
    </section>
""",
    )

    faqs = [
        (
            "Hur stort är bandet?",
            "Halv Fjorton är åtta permanenta medlemmar: sång, gitarr, bas, trummor, klaviatur, slagverk, trumpet och saxofon - plus kör. Namnet kommer från att vi började som sju, alltså halva fjorton.",
        ),
        (
            "Ingår teknik och PA?",
            f"Ja, för en medryckande liveupplevelse. {PA_TEKNIK_COPY} Behöver ni teknik utöver det som ingår hjälper vi till via uthyrare vi redan samarbetar med.",
        ),
        (
            "Kan ni vara kompband för artist?",
            "Ja. Vi kan kompa solist eller artist på bröllop, fest och andra tillställningar - till exempel vid vigsel, psalmer eller när någon i sällskapet vill sjunga med fullt band.",
        ),
        (
            "Vilka tillställningar spelar ni på?",
            "Bröllop (fest, och vid behov vigsel, psalmer och komp till solist), mingel, personalfest, kickoff, jubileum, konferens, födelsedag och andra fester. Vi tar även specialupplägg som musik under middag eller sambatåg.",
        ),
        (
            "Var i Sverige spelar ni?",
            "Vi har rötter i Växjö och medlemmar spridda över södra Sverige. Det är vår hemmaplan. Andra orter går att diskutera - hör av er med platsen så säger vi vad som är rimligt.",
        ),
        (
            "Hur går en bokning till?",
            "Skicka datum, plats och typ av tillställning via mejl eller formuläret. Vi kollar tillgänglighet, återkommer med ett upplägg och därefter en offert. När ni säger ja bekräftar vi skriftligt.",
        ),
        (
            "Hur lång framförhållning behövs?",
            "Så tidigt ni kan, särskilt lördagar under bröllopssäsong och kring jul. Ibland finns det luckor med kortare varsel - fråga hellre än att anta att det är fullt.",
        ),
        (
            "Kan ni skräddarsy repertoaren?",
            "Ja. Vi utgår från soul, funk, rock och svenska klassiker och anpassar efter publiken. Första dans, obligatoriska låtar och temakvällar går ofta att lösa. Hör av er i tid om något måste läras in.",
        ),
        (
            "Kan vi kombinera mingel och fest?",
            "Ja, och det är ett av våra vanligaste upplägg. Mingel i mer återhållen stil, sedan dansspelning när rummet är redo. Samma band genom kvällen.",
        ),
        (
            "Vad kostar en spelning?",
            "Det beror på datum, restid, hur länge vi spelar och om det är mingel, fest eller båda. Vi ger pris i offerten när underlaget finns - inte som en fast lista här.",
        ),
        (
            "Vem fakturerar?",
            "Halv Fjorton EK. FÖR., organisationsnummer 769641-5418. Mejl halvfjorton@gmail.com.",
        ),
    ]
    faq_items = "\n".join(
        f"""        <article class="faq-item">
          <h3>{q}</h3>
          <p>{a}</p>
        </article>"""
        for q, a in faqs
    )
    faq_ld_entities = ",\n".join(
        f'''      {{
        "@type": "Question",
        "name": "{q}",
        "acceptedAnswer": {{
          "@type": "Answer",
          "text": "{a.replace('"', '\\"')}"
        }}
      }}'''
        for q, a in faqs
    )
    faq_ld = f"""{{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
{faq_ld_entities}
    ]
  }}"""

    page(
        "/faq/",
        "Vanliga frågor om Halv Fjorton | bokning, teknik och repertoar",
        "FAQ om Halv Fjorton: bandstorlek, teknik, tillfällen, södra Sverige, bokning, framförhållning och skräddarsydd repertoar.",
        extra_ld=[
            faq_ld,
            service_ld(
                "Kompband för artist",
                "Livekompri för solist eller artist på bröllop, fest och event i södra Sverige.",
                "/faq/",
            ),
        ],
        body=f"""    <header class="page-hero compact">
      <div class="page-hero-copy">
        <p class="eyebrow">FAQ</p>
        <h1>Vanliga frågor</h1>
        <p class="lead">Korta svar för par, företag och eventbolag. Saknas er fråga finns den i mejlen.</p>
      </div>
    </header>
    <section class="section">
      <div class="wrap faq-grid">
{faq_items}
      </div>
    </section>
""",
    )

    page(
        "/kontakt/",
        "Kontakta Halv Fjorton | boka coverband i södra Sverige",
        "Kontakta Halv Fjorton för bokning: halvfjorton@gmail.com. Coverband till bröllop, företag och fest i Växjö och södra Sverige.",
        body="""    <header class="page-hero compact">
      <div class="page-hero-copy">
        <p class="eyebrow">Kontakt</p>
        <h1>Hör av er</h1>
        <p class="lead">Berätta datum, plats och vad ni är ute efter. Vi återkommer så snart vi kan.</p>
      </div>
    </header>
    <section class="section">
      <div class="wrap contact-grid">
        <div>
          <h2>Direkt</h2>
          <p><a href="mailto:halvfjorton@gmail.com">halvfjorton@gmail.com</a><br>
          <a href="https://www.instagram.com/halvfjorton/" rel="noopener noreferrer">Instagram @halvfjorton</a></p>
          <p>Halv Fjorton EK. FÖR.<br>Organisationsnummer 769641-5418</p>
          <h3>Bra att ha med i mejlet</h3>
          <ul class="list-check">
            <li>Datum och ungefärliga tider</li>
            <li>Ort och lokal om ni redan vet</li>
            <li>Bröllop, företag, mingel eller annat</li>
            <li>Ungefärligt antal gäster</li>
            <li>Om ni vill kombinera mingel och fest</li>
          </ul>
        </div>
        <form data-mailto-form>
          <h2>Skicka en förfrågan</h2>
          <p class="small muted">Formuläret öppnar ert mejlprogram med uppgifterna ifyllda. Ingen data sparas på sajten.</p>
          <label for="name">Namn</label>
          <input id="name" name="name" autocomplete="name" required>
          <label for="email">E-post</label>
          <input id="email" name="email" type="email" autocomplete="email" required>
          <label for="phone">Telefon</label>
          <input id="phone" name="phone" type="tel" autocomplete="tel">
          <label for="date">Datum</label>
          <input id="date" name="date" type="date">
          <label for="place">Plats</label>
          <input id="place" name="place" placeholder="Ort och lokal">
          <label for="type">Typ av tillställning</label>
          <select id="type" name="type">
            <option value="Bröllop">Bröllop</option>
            <option value="Företag">Företag</option>
            <option value="Mingel">Mingel</option>
            <option value="Fest">Fest</option>
            <option value="Annat">Annat</option>
          </select>
          <label for="message">Meddelande</label>
          <textarea id="message" name="message" required placeholder="Tid, antal gäster, önskemål…"></textarea>
          <div class="actions">
            <button class="btn btn-primary" type="submit">Öppna mejl</button>
          </div>
        </form>
      </div>
    </section>
""",
    )

    page(
        "/404.html",
        "Sidan hittades inte | Halv Fjorton",
        "Sidan finns inte. Gå till startsidan eller kontakta Halv Fjorton.",
        outfile=ROOT / "404.html",
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


if __name__ == "__main__":
    write_pages()
