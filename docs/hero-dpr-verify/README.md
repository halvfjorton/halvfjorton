# Hero DPR verification (390×844, DPR 3)

Playwright: `node scripts/capture-hero-verify.mjs <before-root> <after-root>` (needs `playwright` npm package).

## Root cause

Full-bleed `object-fit: cover` heroes on portrait phones need a **layout width well above `100vw`** (roughly `100svh × aspect × Ken Burns scale`). With `sizes="100vw"`, Chromium picked **1200w** assets where **1920w** was required.

## Home hero `currentSrc` (slide 1)

| | Candidate | Decoded `naturalWidth` |
| --- | --- | --- |
| Before (`main` @ #28) | `halvfjorton-01-hero-1200w.webp` | 390 |
| After | `halvfjorton-01-hero-1920w.webp` | 1709 |

Crops: `before-home-hero-crop-390-dpr3.png`, `after-home-hero-crop-390-dpr3.png`.

Full report: `hero-candidates.json`.
