"""The factory must operate without a network or the live Ludoman repository."""
import base64
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.check_reference import check_reference
from scripts.scaffold_observatory import scaffold, source_file, REFERENCE
from tests.test_scaffold import friendly

ROOT=Path(__file__).resolve().parents[1]


class IndependenceTests(unittest.TestCase):
    def test_all_token_source_templates_are_local_and_manifest_pinned(self):
        self.assertEqual(check_reference(),13)
        for name in ('assets.py','trades.py','badges.py','observatory.py','web/app.js','web/page.html'):
            self.assertTrue(source_file(name).is_relative_to(REFERENCE))
        self.assertFalse((ROOT/'index.html').exists())
        self.assertFalse((ROOT/'data/snapshot.json').exists())
        self.assertNotIn('from assets import', (ROOT/'scripts/discover_project.py').read_text())
        self.assertNotIn('ludomanDev', (REFERENCE/'web/app.js').read_text())

    @unittest.skipUnless(importlib.util.find_spec('PIL'),'Pillow required for generation')
    def test_offline_generation_has_no_live_project_source_or_badges(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            (base/'logo.webp').write_bytes(base64.b64decode('UklGRi4AAABXRUJQVlA4ICIAAABwAQCdASoEAAQAAoBCJYwCdAFAAAD+9w1pV6vMptIhvQAA'))
            cfg={'slug':'independent-test','name':'Independent Test','symbol':'INDEP','master':friendly(23),'decimals':6,
                 'github':{'owner':'ExampleOrg','repo':'IndependentTest'},'primary_pool':friendly(38),
                 'pools':[{'address':friendly(38),'dex':'stonfi','quote':'TON'}],
                 'logo_file':'logo.webp','logo_origin':'token_metadata','logo_source':'https://example.org/logo.webp',
                 'flag_emoji':'🍉','links':{'telegram':'https://t.me/example_project'}}
            file=base/'project.json';file.write_text(json.dumps(cfg))
            with patch('socket.create_connection',side_effect=AssertionError('Factory must not contact upstream')):
                site=scaffold(file,base/'site')
            for file in ('web/app.js','web/page.html','web/snapshot-loader.js','assets.py','trades.py','observatory.py','badges.py'):
                text=(site/file).read_text()
                self.assertNotIn('Freebielife/Ludoman',text)
                self.assertNotIn('ludomanDev',text)
                self.assertNotIn('the1000ludoman',text)
            project=json.loads((site/'project.json').read_text())
            self.assertEqual(project['template_repository'],'Freebielife/TON-Observatory-Template')
