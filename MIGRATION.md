# Halv Fjorton → peperipaperika (labs)

This archive is the **source** for the Halv Fjorton static site. The **built** site is published under GitHub Pages at **`/testing/halfbandnew2026/`** in [ivarlundin/peperipaperika](https://github.com/ivarlundin/peperipaperika).

Keep **source** and **output** as siblings in that repo so the live preview path stays clean and deploys only replace the output folder.

## Suggested layout in `peperipaperika`

```text
peperipaperika/
├── CNAME                    # unchanged (production / other sites)
├── index.html               # unchanged (repo root site)
├── ns-midihelper/           # unchanged
├── halfbandnew2026/         # ← unzip halfbandnew2026-source.zip here (this tree)
│   ├── scripts/build.py
│   ├── assets/
│   ├── alt/
│   ├── …
│   └── MIGRATION.md
└── testing/
    └── halfbandnew2026/     # ← build output only (do not edit by hand)
        ├── index.html
        ├── assets/
        └── …
```

You can rename `halfbandnew2026/` to another folder name; adjust the `--output-dir` path below accordingly.

## Build into the labs subpath

From the **source** directory inside `peperipaperika`:

```bash
python3 scripts/build.py \
  --output-dir ../testing/halfbandnew2026 \
  --subpath /testing/halfbandnew2026
```

What this does:

1. Writes a fresh tree under `testing/halfbandnew2026/` (copies `assets/`, seeds `alt/`, regenerates HTML from `scripts/build.py`).
2. Rewrites root-relative URLs (`/assets/…`, `/kontakt/`, etc.) to `/testing/halfbandnew2026/…` so links work on GitHub Pages.

Preview locally (from repo root):

```bash
python3 -m http.server 8080
```

Open `http://localhost:8080/testing/halfbandnew2026/`.

## Edit workflow

1. Change copy or structure in **`scripts/build.py`** (most pages) and/or **`alt/index.html`** (alternative homepage).
2. Edit **`assets/`** (CSS, JS, images, fonts, `assets/schema/organization.json`).
3. Run the build command above.
4. Commit **source** changes under `halfbandnew2026/` and **output** under `testing/halfbandnew2026/` (or rely on GitHub Actions in `halvfjorton` after merge to `main`).

## CI from `halvfjorton` (optional)

After `LABS_DEPLOY_TOKEN` is configured, pushes to **`main`** in `ivarlundin/halvfjorton` can deploy automatically via `.github/workflows/deploy-labs.yml`, syncing only `testing/halfbandnew2026/` in `peperipaperika`.

## Archives

| Archive | Purpose |
| --- | --- |
| `halfbandnew2026-source.zip` | Full editable source (this tree). |
| `halfbandnew2026.zip` | Pre-built `testing/halfbandnew2026/` payload for a one-shot deploy. |

Do not commit secrets or `.git` history into `peperipaperika`.
