# Migration from peperipaperika

The new Halv Fjorton site was developed in [peperipaperika](https://github.com/ivarlundin/peperipaperika) under `_src/halfbandnew2026/` with labs preview at `https://labs.ivarlundin.se/testing/halfbandnew2026/`.

This repository (`ivarlundin/halvfjorton`) is now the **production** home:

| Item | Location |
| --- | --- |
| Site source | Repository root (`scripts/`, `assets/`, `home/`, …) |
| Build output | Same root (`index.html`, page folders, `sitemap.xml`, …) |
| Custom domain | `CNAME` → `halvfjorton.se` |
| Jekyll bypass | `.nojekyll` at repo root |

## Production build

```bash
python3 scripts/build.py
```

No `--output-dir` or `--subpath` — canonical URLs and sitemap already target `https://halvfjorton.se/`.

## Labs build (reference only)

In peperipaperika:

```bash
cd _src/halfbandnew2026
python3 scripts/build.py \
  --output-dir ../../testing/halfbandnew2026 \
  --subpath /testing/halfbandnew2026
```

Do not push to peperipaperika from this migration work.
