# Agent instructions (halvfjorton.se)

This repository is the **public static site only**. Build workflow, CMS, and QA live in **[halvfjorton-tools](https://github.com/ivarlundin/halvfjorton-tools)** (`docs/SITE-WORKFLOW.md`).

## Design and copy (binding)

- **Design is final.** Technical fixes must be **pixel-identical** unless the task explicitly asks for a visual change.
- Never write **"ekonomisk förening"** or **"EK. FÖR."** in copy.
- Do not change **Om oss** content unless explicitly requested.

## Image quality (non-negotiable)

- Never reduce image resolution or quality to gain performance or Lighthouse points; the brand is premium.
- Hero and stage images must be razor sharp on DPR-3 phones (e.g. 390×844 CSS px).
- For `object-fit: cover` or Ken Burns heroes, `sizes` must account for the cover crop and scale (see `hero_cover_sizes()` in `scripts/build.py`), never plain `100vw`.
- WebP exports use high quality (~q90+), from the largest source, never upscaled.
- After any image change, confirm `currentSrc` at 390×844, DPR 3.

## Repository hygiene

- **Never commit agent artifacts here:** verification screenshots, before/after images, JSON reports, `docs/*-verify/` folders, or Playwright/capture scripts not used by `scripts/build.py` or CI.
- Keep those in the agent environment or attach them to the PR description.
- Never commit secrets, keys, or `.env` files.

## Build and CI

```bash
python3 scripts/build.py
```

CI runs the build and requires `git diff --exit-code` (committed output must match the generator).
