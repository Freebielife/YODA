"""Shared TONecosystem flag atlas integrity and project isolation tests."""
import base64
import io
import unittest
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None
from scripts.build_common_flags import COMMON_KEYS, build_common_atlas

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(Image is None, "Pillow is a build-only dependency; full QA installs it")
class CommonFlagsTest(unittest.TestCase):
    def test_shared_flags_have_no_foreign_token_art(self):
        sprite = build_common_atlas(ROOT / "assets/icon-pack/approved-brand-atlas.json")
        self.assertEqual(set(sprite["positions"]), COMMON_KEYS)
        self.assertFalse({"ludoman", "kito", "gram", "usda", "rton", "web"} &
                         set(sprite["positions"]))
        data = base64.b64decode(sprite["image_base64"], validate=True)
        with Image.open(io.BytesIO(data)) as png:
            picture = png.convert("RGBA")
            for x, y in ((0, 0), (1, 0), (3, 0), (5, 0), (0, 1)):
                # Coordinates are project-specific or generic placeholders in
                # the Ludoman source atlas, so they must be transparent here.
                box = picture.crop((x*40, y*40, x*40+40, y*40+40))
                self.assertIsNone(box.getbbox(), (x, y))
            for name in ("ton", "ston", "dedust", "telegram", "x"):
                x, y = sprite["positions"][name]
                box = picture.crop((x*40, y*40, x*40+40, y*40+40))
                self.assertIsNotNone(box.getbbox(), name)

if __name__ == "__main__":
    unittest.main()
