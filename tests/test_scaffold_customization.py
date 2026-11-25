"""Independent, offline tests for per-token layout customization and badge proofs."""
import base64
import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.scaffold_observatory import ProjectError, read_config, scaffold
from tests.test_scaffold import friendly


HAS_PILLOW = importlib.util.find_spec('PIL') is not None

class CustomizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.config_path = self.base / "project.json"
        self.out = self.base / "new-observatory"
        self.cfg = {
            "slug": "sampletoken", "name": "Sample Token", "symbol": "SAMPLE",
            "master": friendly(23), "decimals": 6,
            "github": {"owner": "ExampleOrg", "repo": "SampleToken"},
            "primary_pool": friendly(38),
            "pools": [{"address": friendly(38), "dex": "stonfi", "quote": "TON"}],
            "links": {"telegram": "https://t.me/example"},
        }

        (self.base / "official-logo.webp").write_bytes(base64.b64decode(
            "UklGRi4AAABXRUJQVlA4ICIAAABwAQCdASoEAAQAAoBCJYwCdAFAAAD+9w1pV6vMptIhvQAA"))
        self.cfg.update(logo_file="official-logo.webp", logo_origin="token_metadata",
                             logo_source="https://example.org/token-logo.webp", flag_emoji="🍉")

    def save(self):
        self.config_path.write_text(json.dumps(self.cfg))

    @unittest.skipUnless(HAS_PILLOW, "Pillow is installed only for scaffold QA")
    def test_custom_telegram_and_isolated_settings(self):
        self.save()
        scaffold(self.config_path, self.out)
        page = (self.out / "web/page.html").read_text()
        app = (self.out / "web/app.js").read_text()
        self.assertIn('href="https://t.me/example"', page)
        self.assertNotIn("the1000project", page)
        self.assertNotIn('"project-lang"', app)
        self.assertNotIn('"project-currency"', app)
        self.assertIn("observatory-sampletoken-", app)

        # A missing channel must block setup; a different token keeps isolated settings.
        self.cfg["links"].pop("telegram")
        self.cfg["master"] = friendly(55)
        self.save()
        other_site = self.base / "other"
        with self.assertRaises(ProjectError):
            scaffold(self.config_path, other_site)
        self.cfg["links"]["telegram"] = "https://t.me/another_project"
        self.save()
        scaffold(self.config_path, other_site)
        other = (other_site / "web/page.html").read_text()
        other_js = (other_site / "web/app.js").read_text()
        self.assertNotIn('>Telegram</a>', other)
        self.assertNotIn("the1000project", other)
        self.assertIn("observatory-sampletoken-", other_js)
        self.assertNotEqual(
            app.split('localStorage.getItem(')[1].split(')')[0],
            other_js.split('localStorage.getItem(')[1].split(')')[0],
        )

    @unittest.skipUnless(HAS_PILLOW, "Pillow is installed only for scaffold QA")
    def test_official_staking_link_not_assumed_tvl(self):
        self.cfg["links"]["staking"] = "https://staking.example.org/"
        self.save()
        scaffold(self.config_path, self.out)
        page = (self.out / "web/page.html").read_text()
        app = (self.out / "web/app.js").read_text()
        self.assertIn('href="https://staking.example.org/"', page)
        self.assertIn("Official staking page", page)
        self.assertIn("Официальная страница стейкинга", page)
        self.assertIn('data-brand="project"', page)
        self.assertIn('const brand=anchor.dataset.brand||markFromLink(anchor);', app)
        self.assertIn('id="stakingTotal">—</strong>', page)
        self.assertNotIn("APY", page)
        # The staking link is optional and must never be copied to other projects.
        self.cfg["links"].pop("staking")
        self.save()
        second = self.base / "without-staking"
        scaffold(self.config_path, second)
        other = (second / "web/page.html").read_text()
        self.assertNotIn("staking.example.org", other)
        self.assertNotIn("Official staking page", other)

    @unittest.skipUnless(HAS_PILLOW, "Pillow is installed only for scaffold QA")
    def test_custom_background_and_verified_badges(self):
        webp = base64.b64decode(
            "UklGRi4AAABXRUJQVlA4ICIAAABwAQCdASoEAAQAAoBCJYwCdAFAAAD+9w1pV6vMptIhvQAA")
        gif = base64.b64decode("R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=")
        (self.base / "wallpaper.webp").write_bytes(webp)
        (self.base / "icon.gif").write_bytes(gif)
        self.cfg["background_file"] = "wallpaper.webp"
        self.cfg["badges"] = [
            {"id": "verified_test", "label": "Verified",
             "description_ru": "Проверенная метка проекта",
             "description_en": "Project badge, on-chain verified",
             "icon_file": "icon.gif", "color": "#33aaee",
             "url": "https://example.org/badge", "match": "any",
             "criteria": [
                 {"type": "jetton_min", "master": friendly(41), "min_balance": 200000},
                 {"type": "nft_collection", "collection": friendly(43)},
             ]}
        ]
        self.save()
        scaffold(self.config_path, self.out)
        page = (self.out / "web/page.html").read_text()
        app = (self.out / "web/app.js").read_text()
        collector = (self.out / "badges.py").read_text()
        self.assertIn('data-project-badge="verified_test"', page)
        self.assertIn('data:image/gif;base64,', page)
        self.assertIn('verified_test', app)
        self.assertIn('verified_test', collector)
        self.assertIn('nft_owners', collector)
        self.assertEqual((self.out / "web/project-background.webp").read_bytes(), webp)
        self.assertTrue((self.out / "web/badges/verified_test.gif").exists())
        subprocess.run([sys.executable, "build.py"], cwd=self.out, check=True)
        built = (self.out / "index.html").read_text()
        self.assertIn("data:image/webp;base64,", built)
        self.assertIn("data:image/gif;base64,", built)
        self.assertIn("verified_test", built)
        subprocess.run([sys.executable, "verify.py"], cwd=self.out, check=True)

    def test_reject_invalid_badges_or_image_paths(self):
        self.cfg["badges"] = [
            {"id": "og", "label": "Wrong", "description_ru": "x",
             "description_en": "x", "criteria": [
                {"type": "nft_collection", "collection": friendly(40)}]}
        ]
        self.save()
        with self.assertRaises(ProjectError):
            read_config(self.config_path)
        self.cfg.pop("badges")
        self.cfg["background_file"] = "../other.webp"
        self.save()
        with self.assertRaises(ProjectError):
            read_config(self.config_path)
        self.cfg.pop("background_file")
        self.cfg["badges"] = [
            {"id": "proof", "label": "Proof", "description_ru": "x",
             "description_en": "x", "criteria": [
                {"type": "jetton_min", "master": friendly(45), "min_balance": -1}]}
        ]
        self.save()
        with self.assertRaises(ProjectError):
            read_config(self.config_path)


if __name__ == "__main__":
    unittest.main()
