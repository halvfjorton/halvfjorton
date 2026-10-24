#!/usr/bin/env python3
"""Re-export hero gallery WebP variants from the largest on-disk source (no upscaling)."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "assets/img/gallery"
WIDTHS = (480, 800, 1200, 1920)
QUALITY = 92

# Stems used in home carousel or service hero banners (build.py).
HERO_STEMS = (
    "halvfjorton-01-hero",
    "halvfjorton-03-hero",
    "halvfjorton-04-hero",
    "halvfjorton-05-hero",
    "halvfjorton-05",
    "halvfjorton-trumpet-barn-wedding",
    "halvfjorton-trumpet-sax-bw-stage",
)


def native_size(path: Path) -> tuple[int, int]:
    out = subprocess.check_output(
        ["identify", "-format", "%w %h", str(path)],
        text=True,
    ).strip()
    w, h = out.split()
    return int(w), int(h)


def _identify_ok(path: Path) -> bool:
    try:
        subprocess.run(
            ["identify", str(path)],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _decodable_webp(path: Path) -> bool:
    try:
        subprocess.run(
            ["dwebp", str(path), "-o", "/dev/null"],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def largest_source(stem: str) -> Path | None:
    candidates: list[Path] = []
    bare = GALLERY / f"{stem}.webp"
    if bare.is_file():
        candidates.append(bare)
    candidates.extend(sorted(GALLERY.glob(f"{stem}-*w.webp")))
    readable = [p for p in candidates if _identify_ok(p)]
    if not readable:
        return None
    return max(readable, key=lambda p: native_size(p)[0])


def decode_to_png(source: Path, png: Path) -> None:
    if _decodable_webp(source):
        subprocess.run(["dwebp", str(source), "-o", str(png)], check=True)
        return
    subprocess.run(["convert", str(source), str(png)], check=True)


def reencode_stem(stem: str) -> None:
    source = largest_source(stem)
    if not source:
        print("skip (no files)", stem)
        return
    native_w, native_h = native_size(source)
    png = GALLERY / f".reencode-{stem}.png"
    decode_to_png(source, png)
    legacy_1920 = GALLERY / f"{stem}-1920w.webp"
    for target_w in WIDTHS:
        out = GALLERY / f"{stem}-{target_w}w.webp"
        out_w = target_w
        if target_w > native_w:
            # Keep standard srcset slot names without upscaling pixel data.
            if target_w in (800, 1200, 1600, 1920) and native_w > 480:
                out_w = native_w
            else:
                continue
        if target_w == 1920 and native_w < 1920 and legacy_1920.is_file():
            out = legacy_1920
            out_w = native_w
        scale = out_w / native_w
        out_h = max(1, round(native_h * scale))
        subprocess.run(
            [
                "cwebp",
                "-q",
                str(QUALITY),
                "-sharp_yuv",
                "-resize",
                str(out_w),
                str(out_h),
                str(png),
                "-o",
                str(out),
            ],
            check=True,
        )
        print("wrote", out.relative_to(ROOT), f"({out_w}x{out_h})")
    png.unlink(missing_ok=True)


def main() -> None:
    for stem in HERO_STEMS:
        reencode_stem(stem)


if __name__ == "__main__":
    main()
