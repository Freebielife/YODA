"""Safety regressions: identity, budgets, evidence-based discovery, atomic output."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.project_runtime import canonical_address, publish_html, check_identity, decorate_snapshot
from scripts.discover_project import discover, NATIVE
from tests.test_scaffold import friendly


class FoundationTests(unittest.TestCase):
    def test_same_address_formats_and_bad_crc(self):
        address = friendly(23)
        self.assertEqual(canonical_address(address), '0:'+'17'*32)
        import base64, binascii
        body=bytes([0x51,0])+bytes([23])*32
        alternate=base64.urlsafe_b64encode(body+binascii.crc_hqx(body,0).to_bytes(2,'big')).decode()
        self.assertEqual(canonical_address(address),canonical_address(alternate))
        with self.assertRaises(ValueError):
            canonical_address(address[:-1]+'!')

    def test_foreign_snapshot_or_pool_rejected(self):
        project={'master':friendly(23),'pools':[{'address':friendly(38)}]}
        snap={'schema':1,'token':friendly(24)}
        with self.assertRaises(ValueError): check_identity(snap,project)
        snap['token']=friendly(23)
        snap['trades']={'rows':[{'pool':friendly(39)}]}
        with self.assertRaises(ValueError): check_identity(snap,project)

    def test_oversize_and_external_dependency_keep_last_good_html(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'web').mkdir()
            project={'master':friendly(23),'pools':[],'max_html_bytes':250000}
            (root/'project.json').write_text(json.dumps(project))
            (root/'index.html').write_text('last-good')
            snap={'schema':1,'token':friendly(23)}
            for page in ('x'*250001,'<img src="https://example.org/a.webp">'):
                with self.assertRaises(ValueError): publish_html(root,page,snap)
                self.assertEqual((root/'index.html').read_text(),'last-good')
            publish_html(root,'<html>valid</html>',snap)
            self.assertEqual((root/'index.html').read_text(),'<html>valid</html>')

    def test_discovery_requires_exact_token_native_pair_and_swap_proof(self):
        token,pool=friendly(23),friendly(38)
        metadata={'metadata':{'address':canonical_address(token),'name':'Sample Token','symbol':'SAMPLE','decimals':'6'}}
        candidate={'attributes':{'address':pool,'reserve_in_usd':'100'},'relationships':{
            'base_token':{'data':{'id':'ton_'+token}},'quote_token':{'data':{'id':'ton_'+NATIVE}},'dex':{'data':{'id':'ston-fi'}}}}
        event={'in_progress':False,'actions':[{'type':'JettonSwap','status':'ok','JettonSwap':{
            'dex':'stonfi','jetton_master_out':{'address':canonical_address(token)},'ton_in':'1000000000'}}]}
        events={'events':[event]}
        def read(path,**kwargs):
            if path.startswith('/jettons/'): return copy.deepcopy(metadata)
            if path.startswith('/networks/'): return {'data':[copy.deepcopy(candidate)]}
            return copy.deepcopy(events)
        for dex_id in ('ston-fi', 'stonfi', 'stonfi-v2'):
            with self.subTest(dex_id=dex_id):
                candidate['relationships']['dex']['data']['id'] = dex_id
                cfg=discover(token,'ExampleOrg','SampleToken',read=read)
                self.assertEqual(cfg['primary_pool'],pool)
                self.assertEqual(cfg['decimals'],6)
                self.assertEqual(cfg['pools'][0]['dex'],'stonfi')
        events['events'][0]['actions'][0]['JettonSwap']['jetton_master_out']['address']=canonical_address(friendly(24))
        with self.assertRaises(ValueError): discover(token,'ExampleOrg','SampleToken',read=read)

    def test_contract_provenance_does_not_invent_exchange_name(self):
        wallet=canonical_address(friendly(23))
        snap={'identity':{'byWallet':{wallet:{'role':'unclassified_contract'}}}}
        decorate_snapshot(snap,{'services':{},'pools':[]})
        record=snap['identity']['byWallet'][wallet]
        self.assertEqual(record['serviceCategory'],'contract')
        self.assertIn('/accounts/',record['roleSource'])
        self.assertEqual(record['role'],'unclassified_contract')
