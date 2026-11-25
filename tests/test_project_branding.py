"""Official hero assets, separate confirmed flags, and required project channels."""
import base64
import io
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from scripts.project_branding import BrandingError, validate_config, prepare, channel_url
from scripts.scaffold_observatory import scaffold
from tests.test_scaffold import friendly

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'assets/icon-pack/approved-brand-atlas.json'


@unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow is a factory setup dependency")
class BrandingTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.base=Path(self.directory.name)
        from PIL import Image
        for name,color in [('logo.webp','red'),('flag.webp','blue')]:
            Image.new('RGB',(16,16),color).save(self.base/name,'WEBP')
        self.cfg={'slug':'brand-test','name':'Brand Test','symbol':'TEST','master':friendly(23),
                  'decimals':9,'github':{'owner':'ExampleOrg','repo':'BrandTest'},
                  'primary_pool':friendly(38),'pools':[{'address':friendly(38),'dex':'stonfi','quote':'TON'}],
                  'links':{'telegram':'https://t.me/example_project'},'logo_file':'logo.webp',
                  'logo_origin':'token_metadata','logo_source':'https://example.org/logo.webp','flag_file':'flag.webp'}

    def test_missing_channel_flag_or_official_logo_blocks_setup(self):
        for field in ('flag_file','logo_file','logo_source'):
            cfg=dict(self.cfg);cfg.pop(field)
            with self.subTest(field=field), self.assertRaises(BrandingError):
                validate_config(cfg,self.base,ATLAS)
        cfg={**self.cfg,'links':{}}
        with self.assertRaises(BrandingError): validate_config(cfg,self.base,ATLAS)
        cfg={**self.cfg,'flag_catalog_key':'absent'};cfg.pop('flag_file')
        with self.assertRaisesRegex(BrandingError,'ask the user'): validate_config(cfg,self.base,ATLAS)
        cfg={**self.cfg,'flag_emoji':'привет'};cfg.pop('flag_file')
        with self.assertRaises(BrandingError): validate_config(cfg,self.base,ATLAS)
        with self.assertRaises(BrandingError): channel_url('https://example.org/channel')

    def test_metadata_logo_has_priority_and_website_can_supply_fallback(self):
        logo=(self.base/'logo.webp').read_bytes()
        website=b'<html><link rel="icon" href="/logo.webp"><a href="https://t.me/example_project">Channel</a></html>'
        def read(url):
            if url=='https://example.org/':return website
            return logo
        cfg={'links':{}}
        prepare(cfg,self.base,metadata_image='https://example.org/metadata.webp',website='https://example.org/',flag_emoji='🍉',read=read)
        self.assertEqual(cfg['logo_origin'],'token_metadata')
        self.assertEqual(cfg['links']['telegram'],'https://t.me/example_project')
        cfg={'links':{}}
        prepare(cfg,self.base,metadata_image=None,website='https://example.org/',flag_emoji='🍉',read=read)
        self.assertEqual(cfg['logo_origin'],'project_website')
        self.assertEqual(cfg['logo_source'],'https://example.org/logo.webp')

    def test_flag_stays_separate_from_hero_and_channel_appears_twice(self):
        config=self.base/'project.json';config.write_text(json.dumps(self.cfg))
        site=self.base/'site';scaffold(config,site)
        self.assertNotEqual((site/'web/project-logo.webp').read_bytes(),(site/'web/project-flag.webp').read_bytes())
        css=(site/'web/telegram-taste.css').read_text()
        self.assertIn('background:var(--project-flag)',css)
        self.assertNotIn('background:var(--project-art) center/contain no-repeat!important;',css)
        page=(site/'web/page.html').read_text()
        self.assertEqual(page.count('href="https://t.me/example_project"'),2)
        self.assertEqual(page.count('data-t="projectChannel"'),2)
        branding=json.loads((site/'project.json').read_text())['branding']
        self.assertEqual(branding['hero']['source'],'https://example.org/logo.webp')
        self.assertEqual(branding['sectionFlag']['file'],'web/project-flag.webp')
        import subprocess,sys
        subprocess.run([sys.executable,'build.py'],cwd=site,check=True,capture_output=True)
        previous=(site/'index.html').read_bytes()
        (site/'web/project-logo.webp').unlink()
        result=subprocess.run([sys.executable,'build.py'],cwd=site,capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual((site/'index.html').read_bytes(),previous)
