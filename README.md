# Halv Fjorton

Statisk webbplats för coverbandet Halv Fjorton. Ren HTML och CSS, lite JavaScript för meny och kontaktformulär. Ingen server, ingen databas.

**Kanonisk adress:** `https://halvfjorton.se` (apex). `www` bör peka hit, inte tvärtom.

## Förhandsgranska lokalt

Från projektroten:

```bash
python3 -m http.server 8080
```

Öppna [http://localhost:8080/](http://localhost:8080/). Undersidor ligger i mappar med avslutande snedstreck, till exempel `/brollop/` och `/foretag/`.

Sidornas HTML genereras av `scripts/build.py` (gemensam meny, SEO-taggar och JSON-LD). Efter copyändringar i skriptet:

```bash
python3 scripts/build.py
```

## Sidor

| Sökväg | Innehåll |
| --- | --- |
| `/` | Startsida |
| `/brollop/` | Bröllop |
| `/foretag/` | Företag, kickoff, personalfest |
| `/mingel/` | Mingel och mottagning |
| `/om-oss/` | Berättelse, medlemmar, förening |
| `/lyssna/` | Film och julkonserter |
| `/for-eventbolag/` | Underlag för bookers |
| `/faq/` | Vanliga frågor |
| `/kontakt/` | Mejl, telefon och förfrågan |

## GitHub Pages

1. I GitHub: **Settings → Pages**.
2. Source: **Deploy from a branch**.
3. Branch: `main` (eller den branch ni publicerar), mapp **`/ (root)`**.
4. Custom domain: `halvfjorton.se`. Filen `CNAME` i roten är redan ifylld.
5. Vänta tills certifikatet för HTTPS blir grönt. Kryssa i **Enforce HTTPS**.

Filen `.nojekyll` finns så att GitHub inte kör Jekyll mot `_`-filer eller statiska tillgångar.

## Domän och DNS

Apex `halvfjorton.se` är **just nu parkerad hos Loopia**. Det är inte bandets sajt – behandla den inte som innehåll. `www.halvfjorton.se` pekar på den gamla Google Sites-sidan.

Rekommendation:

1. Flytta DNS så att **apex** blir den kanoniska adressen (`https://halvfjorton.se`).
2. Peka **www → apex** (CNAME eller redirect), inte tvärtom.
3. Hos GitHub Pages: lägg till `halvfjorton.se` och vänta in TLS.

Typiska A-poster för GitHub Pages (apex):

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

AAAA (IPv6), om ni använder det:

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

`www` som CNAME mot `ivarlundin.github.io` (eller er Pages-värd) fungerar, så länge apex är primär och www redirectar dit.

Uppdatera posterna hos Loopia när parkeringen ska bort. TTL kan vara hög – räkna med fördröjning.

## Bilder och presskit

Scen- och medlemsfoton är hämtade från den nuvarande sajten. Högupplösta pressfoton, logotyppaket och teknisk rider saknas fortfarande; platshållare finns på `/for-eventbolag/`.

Citat från arrangörer är medvetet tomma. Lägg inte in påhittade omdömen eller kundlogotyper.

## Formulär (valfritt)

Kontaktformuläret öppnar `mailto:halvfjorton@gmail.com` i besökarens mejlprogram. Ingen data sparas här.

Vill ni ha ett webbformulär som skickar utan mejlklient kan [Formspree](https://formspree.io) kopplas på senare. Exempel (ersätt `xxxx` med ert formulär-id):

```html
<form action="https://formspree.io/f/xxxx" method="POST">
```

Lägg inte in analys-id:n förrän ni faktiskt har ett konto.

## SEO

Varje sida har unik titel, meta-beskrivning, canonical, Open Graph och `lang="sv"`. Startsida och undersidor bär JSON-LD för MusicGroup/Organization. FAQ har `FAQPage`. `robots.txt` och `sitemap.xml` ligger i roten.
