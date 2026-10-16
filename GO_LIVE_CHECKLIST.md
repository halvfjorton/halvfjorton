# Go-live checklist — halvfjorton.se

Use this before switching production traffic to the new site. Check items off in the PR or a launch issue.

## GitHub Pages

- [ ] Repository **Settings → Pages**: source = **Deploy from branch** `main`, folder **`/ (root)`**.
- [ ] Confirm `CNAME` in the repo contains `halvfjorton.se` (do not change DNS in this repo).
- [ ] Confirm `.nojekyll` is present so Jekyll does not process the site.
- [ ] After merge: wait for Pages deploy; open `https://halvfjorton.se/` and spot-check HTTPS + certificate.

## DNS (owner / registrar — not changed in code)

- [ ] Apex `halvfjorton.se` and `www` still point at GitHub Pages (or Cloudflare proxy in front) per current hosting plan.
- [ ] If using Cloudflare: SSL mode **Full (strict)**; no stale Page Rules sending traffic to the old site root.

## Build & content

- [ ] On `main`: `python3 scripts/build.py` completes with no errors.
- [ ] Run `python3 scripts/find_unused_images.py` if assets changed; review `UNUSED_IMAGES.md`.
- [ ] **404** page works: visit a nonsense path, confirm branded `404.html` and link home.
- [ ] **Redirects** work (built by `scripts/build.py`):
  - `/mingel/` → `/fest-och-mingel/`
  - `/repertoar/` → `/lyssna/#repertoar`
  - Hidden SEO landings redirect per `SERVICE_LINK_REDIRECTS` (e.g. `/kompband/` → `/brollop/`).
- [ ] Plan **redirects for old production URLs** that no longer exist as pages (previous site had `/alt/`, standalone `/mingel/`, etc.). Options: Cloudflare redirect rules or a small `_redirects`/`404` strategy — map top referrers from analytics before cutover.
- [ ] Remove or update any external links still pointing at labs (`labs.ivarlundin.se/testing/halfbandnew2026/`).

## SEO & metadata

- [ ] `sitemap.xml` lists only public paths; submit in [Google Search Console](https://search.google.com/search-console) for `halvfjorton.se`.
- [ ] `robots.txt` references `https://halvfjorton.se/sitemap.xml`.
- [ ] Spot-check `<title>` and meta descriptions — no stale long suffixes from the old site.
- [ ] Canonical and `og:url` on key pages use `https://halvfjorton.se/...` (not labs).
- [ ] `og:image` resolves to `https://halvfjorton.se/assets/img/og.jpg`.

## Forms & third parties

- [ ] **Tally** offert form on `/kontakt/`: submit a test entry; confirm notification and thank-you state.
- [ ] Footer mailto `halvfjorton@gmail.com` and social links open correctly.

## Privacy & analytics

- [ ] **Cloudflare Web Analytics** for `halvfjorton.se`: owner creates account/token, then add the beacon script to the site layout (via `scripts/build.py` / shared head partial) with the site token.
- [ ] Add **one sentence** to `/integritetspolicy/` describing anonymous Cloudflare Web Analytics (no cookies for tracking).
- [ ] In DevTools → Application: after page load, confirm **no** analytics cookies or `localStorage` entries from Cloudflare beacon (Web Analytics is cookieless; re-check after any other scripts).
- [ ] Tally embed: confirm only expected third-party storage; document in integritetspolicy if needed.

## YouTube embeds

- [ ] Switch **all video embed iframes** to `https://www.youtube-nocookie.com/embed/...` (facades in `assets/js/video-facade.js` and `assets/js/lyssna-video-modal.js` already use nocookie — re-grep built HTML after changes).
- [ ] Channel/watch **links** (footer, JSON-LD `contentUrl`) may stay on `youtube.com`; only **embeds** must use nocookie.

## Performance (Lighthouse)

Run Lighthouse (mobile + desktop) on `/`, `/brollop/`, `/kontakt/` **before** and **after** the performance pass; keep scores or PDFs for comparison.

- [ ] **Lazy loading** on below-the-fold images (`loading="lazy"`).
- [ ] **`fetchpriority="high"`** on LCP hero image where appropriate.
- [ ] **`srcset` / `sizes`** on responsive gallery and hero images.
- [ ] Explicit **`width` / `height`** (or aspect-ratio) to reduce CLS.
- [ ] **`decoding="async"`** on non-LCP images where missing.
- [ ] **Caching / CDN**: Cloudflare or GitHub Pages cache headers; long cache for hashed-static assets under `/assets/`.

## Links & QA

- [ ] Crawl or manually test main nav on every public page.
- [ ] `/lyssna/` video modals and wedding facade on `/brollop/`.
- [ ] `/konserter/` ticket links (e.g. Nygatan 6) open in new tab.
- [ ] Mobile menu and horizontal scroll on small viewports.
- [ ] Optional: run `python3 qa_check.py` from repo root if Playwright tooling is installed (see `QA.md`).

## Post-launch

- [ ] Monitor Search Console for crawl errors and 404 spikes.
- [ ] Update Instagram bio / link-in-bio to `https://halvfjorton.se/`.
- [ ] Archive or sunset old site assets in this repo (already replaced in this migration).
