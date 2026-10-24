# Mobile image verification (390×844 CSS px, DPR 3)

Playwright capture: `node scripts/capture-mobile-screenshots.mjs <before-root> <after-root>` (requires local `playwright` npm package).

## PR #27 regression (stage gallery tile)

| State | Markup | File intrinsic size | `currentSrc` at 390px DPR 3 | Decoded `naturalWidth`×`naturalHeight` |
| --- | --- | --- | --- | --- |
| Pre–PR #27 / this fix | `stage.jpg` (no `srcset`) | 960×858 JPEG | `/assets/img/stage.jpg` | 960×858 |
| Post–PR #27 (main) | WebP `srcset` 480/800/960w | 960×858 max WebP | `/assets/img/stage-960w.webp` | 280×250 (browser downscaled; lossy WebP) |

PR #27 was the only change that altered image assets or `<img>` markup on the site. Other images and `sizes`/`srcset` pairs were unchanged.

## Screenshots

- `before-hem-390-dpr3.png` — `main` at merge `3abcc78`
- `after-hem-390-dpr3.png` — restored `stage.jpg`
- `before-foretag-390-dpr3.png` / `after-foretag-390-dpr3.png` — subpage control (unchanged images)

Full per-image `currentSrc` dump: `image-candidates.json`.

## Julkonsert page vs Konserter card (390×DPR3)

Screenshots: `konserter-card-390-dpr3.png` and `julkonsert-page-390-dpr3.png` (same `soulful_christmas_ticket_card()` markup).
