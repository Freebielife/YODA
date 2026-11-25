"""Build a reusable, token-neutral atlas from owner-approved TONecoFlags.

Only common ecosystem service flags may be carried into a new observatory.
Ludoman/KITO/GRAM and owner-selected placeholder tiles are physically removed
from the image, not merely hidden behind missing position labels.

Pillow is a build-time dependency. Generated HTML remains fully offline.
"""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

COMMON_KEYS = frozenset((
    "ton", "usdt", "ston", "dedust", "tonco", "jvault", "getgems",
    "fragment", "gecko", "gramorg", "dexscreener", "tonviewer",
    "telegram", "x",
))
EXPECTED_FLAG_NUMBERS = {
    "ton": 2, "ston": 19, "dedust": 20, "tonco": 21, "jvault": 167,
    "getgems": 7, "fragment": 5, "usdt": 33, "dexscreener": 104,
    "tonviewer": 91, "telegram": 1, "x": 126,
}


def build_common_atlas(path: Path) -> dict:
    from PIL import Image
    old = json.loads(path.read_text(encoding="utf-8"))
    if old.get("format") != "image/webp":
        raise ValueError("Expected vetted WebP source atlas")
    src_bytes = base64.b64decode(old["image_base64"], validate=True)
    if not src_bytes.startswith(b"RIFF") or src_bytes[8:12] != b"WEBP":
        raise ValueError("Invalid WebP source atlas")
    cols, rows, size = (old[k] for k in ("columns", "rows", "cell_size"))
    if (cols, rows, size) != (6, 4, 40):
        raise ValueError("Unexpected vetted atlas grid layout")
    with Image.open(io.BytesIO(src_bytes)) as img:
        if img.size != (cols * size, rows * size):
            raise ValueError("Atlas dimension mismatch")
        source = img.convert("RGBA")
    target = Image.new("RGBA", source.size, (0, 0, 0, 0))
    positions = {}
    sources = {}
    for key in sorted(COMMON_KEYS):
        if key not in old["positions"]:
            raise ValueError("Common flag missing: " + key)
        number = EXPECTED_FLAG_NUMBERS.get(key)
        provenance = old.get("sources", {}).get(key, "")
        if number is not None and f"#{number:03d}" not in provenance:
            raise ValueError("Unexpected flag provenance: " + key)
        x, y = old["positions"][key]
        crop = source.crop((x * size, y * size, (x + 1) * size, (y + 1) * size))
        target.paste(crop, (x * size, y * size))
        positions[key] = [x, y]
        sources[key] = provenance
    out = io.BytesIO()
    target.save(out, "WEBP", quality=92, method=6)
    payload = out.getvalue()
    if len(payload) > 128000:
        raise ValueError("Shared atlas too large")
    return {
        "schema": 1, "project": "TON Observatory / common TONecosystem services",
        "columns": cols, "rows": rows, "cell_size": size, "format": "image/webp",
        "image_base64": base64.b64encode(payload).decode("ascii"),
        "positions": positions, "sources": sources,
        "note": ("Only independently selected common ecosystem assets. "
                 "All token artwork and generic placeholder tiles are erased.")
    }
