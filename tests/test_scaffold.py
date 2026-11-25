"""Offline regression tests for the new observatory factory.

These use synthetic CRC-correct addresses: no real token or DEX is claimed.
"""
import base64
import binascii
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.scaffold_observatory import ProjectError, read_config, scaffold, raw_address

ROOT = Path(__file__).resolve().parents[1]
HAS_PILLOW = importlib.util.find_spec('PIL') is not None


def friendly(seed):
    raw = bytes([0x11, 0]) + bytes([seed]) * 32
    return base64.urlsafe_b64encode(raw + binascii.crc_hqx(raw, 0).to_bytes(2, "big")).decode()


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.config_path = self.base / "project.json"
        self.out = self.base / "new-observatory"
        self.config = {
            "slug": "sampletoken", "name": "Sample Token", "symbol": "SAMPLE",
            "master": friendly(23), "decimals": 6,
            "github": {"owner": "ExampleOrg", "repo": "SampleToken"},
            "primary_pool": friendly(38),
            "pools": [
                {"address": friendly(38), "dex": "stonfi", "quote": "TON", "fee": "1%"},
                {"address": friendly(39), "dex": "dedust", "quote": "TON"}
            ],
            "links": {"website": "https://example.org/sample", "telegram": "https://t.me/example"},
            "services": {friendly(99): "Verified example service"}
        }

        (self.base / "official-logo.webp").write_bytes(base64.b64decode(
            "UklGRi4AAABXRUJQVlA4ICIAAABwAQCdASoEAAQAAoBCJYwCdAFAAAD+9w1pV6vMptIhvQAA"))
        self.config.update(logo_file="official-logo.webp", logo_origin="token_metadata",
                             logo_source="https://example.org/token-logo.webp", flag_emoji="🍉")

    def save(self):
        self.config_path.write_text(json.dumps(self.config))

    def test_address_crc_and_input_guards(self):
        self.assertEqual(raw_address(friendly(23)), "0:" + "17" * 32)
        with self.assertRaises(ProjectError):
            raw_address(friendly(23)[:-1] + ("x" if friendly(23)[-1] != "x" else "y"))
        self.config["pools"][0]["quote"] = "USDT"
        self.save()
        with self.assertRaises(ProjectError):
            read_config(self.config_path)

    @unittest.skipUnless(HAS_PILLOW, "Pillow is installed only for scaffold QA")
    def test_clean_independent_export_builds_offline(self):
        self.config["project_description"] = {
            "text": "Synthetic project description for offline QA.",
            "origin": "reviewed_sources", "sources": ["https://example.org/sample"],
            "checked_at": "2026-11-22"}
        self.save()
        scaffold(self.config_path, self.out)
        readme = (self.out / "README.md").read_text()
        self.assertIn(self.config["project_description"]["text"], readme)
        self.assertIn("https://example.org/sample", readme)
        self.assertEqual(json.loads((self.out / "project.json").read_text())["project_description"],
                         self.config["project_description"])
        page = (self.out / "web/page.html").read_text()
        app = (self.out / "web/app.js").read_text()
        snapshot = (self.out / "data/snapshot.json").read_text()
        self.assertIn("SAMPLE", page)
        self.assertTrue((self.out / "trade_history.py").is_file())
        self.assertTrue((self.out / "tests/test_trade_history.py").is_file())
        self.assertIn("now - trade_history.YEAR", (self.out / "scripts/refresh_observatory.py").read_text())
        self.assertTrue((self.out / "common-services.json").is_file())
        self.assertTrue((self.out / "service_registry.py").is_file())
        self.assertTrue((self.out / "tests/test_service_registry.py").is_file())
        self.assertIn("service_registry.update", (self.out / "scripts/refresh_observatory.py").read_text())
        self.assertIn("import service_registry", (self.out / "observatory.py").read_text())
        self.assertIn(self.config["master"], app)
        self.assertIn(self.config["primary_pool"], (self.out / "trades.py").read_text())
        self.assertIn('DECIMALS = 6', (self.out / "assets.py").read_text())
        self.assertIn('githubusercontent.com/ExampleOrg/SampleToken/', (self.out / "web/snapshot-loader.js").read_text())
        self.assertNotIn("author NFT", page)
        self.assertNotIn("blueNft", page)
        self.assertNotIn("LUDOMAN", page)
        self.assertNotIn("1000ludoman.xyz", page)
        self.assertNotIn("CryptoCheck", (self.out / "observatory.py").read_text())
        self.assertEqual([p.name for p in (self.out / "web").glob("*.webp")], ["project-logo.webp"])
        self.assertNotIn("socool.ton", (self.out / "assets.py").read_text())
        self.assertNotIn("JVault", app)
        self.assertNotIn("VNUK", app)
        self.assertIn("const required=['trades','holders'];", app)
        self.assertIn("Некоторые разделы пока не проиндексированы.", app)
        self.assertNotIn("const times=['trades','burns','holders']", app)
        self.assertIn('"updated": 1', snapshot)
        commands = [
            [sys.executable, "-m", "compileall", "-q", "."],
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
            [sys.executable, "build.py"],
            [sys.executable, "verify.py"],
            ["node", "--check", "web/app.js"],
            ["node", "--test", "tests/market-cap.test.cjs", "tests/snapshot-loader.test.cjs"],
        ]
        for args in commands:
            with self.subTest(command=args):
                done = subprocess.run(args, cwd=self.out, capture_output=True, text=True, timeout=60)
                self.assertEqual(done.returncode, 0, done.stdout[-2000:] + done.stderr[-2000:])
        index = (self.out / "index.html").read_text()
        self.assertIn(self.config["master"], index)
        for foreign in ("LUDOMAN", "VNUK", "ARNI", "NAPIWAS",
                        "Joystick", "Phoenix", "JVault", "CryptoCheck",
                        "1000ludoman", "socool.ton", "author NFT"):
            self.assertNotIn(foreign, index, foreign)
        self.assertIn("OBSERVATORY_BRAND_ATLAS", index)
        sprite = json.loads((self.out / "assets/icon-pack/approved-brand-atlas.json").read_text())
        self.assertEqual(sprite["project"], "TON Observatory / common TONecosystem services")
        for key in ("ton", "ston", "dedust", "telegram", "gecko", "usdt"):
            self.assertIn(key, sprite["positions"])
        for foreign in ("ludoman", "kito", "gram", "usda", "rton", "web", "tonraffles"):
            self.assertNotIn(foreign, sprite["positions"])
        self.assertNotIn("mRvnukICHlife", index)
        self.assertIn('if(host==="example.org")return"project";', index)
        self.assertIn('data-quote-address="EQAAAAAAAA', index)
        self.assertIn('unclassified_contract', (self.out / "observatory.py").read_text())
        self.assertIn('poolChecked").textContent=""', index)
        self.assertIn("OBSERVATORY_BRAND_ATLAS", index)
        self.assertIn("https://github.com/ExampleOrg/SampleToken", index)
        self.assertFalse((self.out / "web/ludoman.webp").exists())

    def test_refuse_overwrite_and_original_repo(self):
        self.save()
        with self.assertRaises(ProjectError):
            scaffold(self.config_path, ROOT)
        self.out.mkdir()
        (self.out / "important.txt").write_text("original")
        with self.assertRaises(ProjectError):
            scaffold(self.config_path, self.out)
        self.assertEqual((self.out / "important.txt").read_text(), "original")


if __name__ == "__main__":
    unittest.main()
