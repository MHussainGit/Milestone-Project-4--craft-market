"""
Generate CraftMarket PWA icons without any third-party imaging library.

Draws the brand mark — a cream "C" ring on the warm accent background —
at the sizes a PWA needs, writing valid PNGs via zlib + manual chunks.

Run from the project root:  python scripts/gen_pwa_icons.py
"""

import math
import struct
import zlib
from pathlib import Path

ACCENT = (139, 94, 60)      # --accent  #8b5e3c
CREAM = (250, 248, 244)     # --bg      #faf8f4

OUT_DIR = Path(__file__).resolve().parent.parent / "static" / "icons"


def _png(width, height, pixels):
    """Encode an RGBA pixel grid (list of rows of (r,g,b,a)) as PNG bytes."""
    raw = bytearray()
    for row in pixels:
        raw.append(0)  # filter type 0 (None) for this scanline
        for r, g, b, a in row:
            raw += bytes((r, g, b, a))

    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def _draw(size, maskable=False):
    """Render the icon at `size`. Maskable keeps the mark inside a safe area."""
    n = size
    cx = cy = (n - 1) / 2
    # Maskable icons get a tighter mark so it survives a circular OS mask.
    scale = 0.30 if maskable else 0.36
    outer = n * scale
    inner = n * (scale - 0.13)
    mid = (outer + inner) / 2
    stroke = (outer - inner) / 2
    gap = math.radians(42)  # opening of the "C" on the right

    # End-cap centres so the C terminals look rounded, not chopped.
    caps = [
        (cx + mid * math.cos(a), cy + mid * math.sin(a))
        for a in (gap, -gap)
    ]

    rows = []
    for y in range(n):
        row = []
        for x in range(n):
            dx, dy = x - cx, y - cy
            dist = math.hypot(dx, dy)
            on_mark = False
            if inner <= dist <= outer:
                ang = math.atan2(dy, dx)
                if abs(ang) > gap:  # outside the mouth gap
                    on_mark = True
            if not on_mark:
                for ex, ey in caps:
                    if math.hypot(x - ex, y - ey) <= stroke:
                        on_mark = True
                        break
            row.append((*CREAM, 255) if on_mark else (*ACCENT, 255))
        rows.append(row)
    return _png(n, n, rows)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    targets = [
        ("icon-192.png", 192, False),
        ("icon-512.png", 512, False),
        ("icon-maskable-512.png", 512, True),
        ("apple-touch-icon.png", 180, False),
        ("favicon-32.png", 32, False),
    ]
    for name, size, maskable in targets:
        (OUT_DIR / name).write_bytes(_draw(size, maskable))
        print(f"wrote {name} ({size}x{size})")


if __name__ == "__main__":
    main()
