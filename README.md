# halvfjorton.se

Static site for **Halv Fjorton** (cover- och bröllopsband). Source and built HTML live in this repository root; GitHub Pages serves `main` at [https://halvfjorton.se/](https://halvfjorton.se/) via `CNAME`.

## Build

From the repository root:

```bash
python3 scripts/build.py
```

This regenerates page HTML, `sitemap.xml`, `llms.txt`, `404.html`, redirects, and `assets/cms/image-manifest.json`. Root-relative URLs stay at `/` (no labs subpath).

Optional labs-style output (not used for production):

```bash
python3 scripts/build.py --output-dir /path/to/out --subpath /testing/halfbandnew2026
```

## Edit workflow

1. Change copy in `scripts/build.py`, layout/CSS/JS/images under `assets/`, or `home/index.html` (startsida source).
2. Run `python3 scripts/build.py`.
3. Commit source and generated HTML together.

Do not commit secrets (`.env`, API keys).

## Local preview

```bash
python3 scripts/build.py
python3 -m http.server 8080
```

Open [http://localhost:8080/](http://localhost:8080/).

## Reports

- `UNUSED_IMAGES.md` — run `python3 scripts/find_unused_images.py` after a build.
- `GO_LIVE_CHECKLIST.md` — pre-launch tasks for production.

See `MIGRATION.md` for how this site moved from `peperipaperika`.
