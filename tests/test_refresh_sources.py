"""All shared wallet flags are collected and failed sources retain prior proofs."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import refresh_observatory as runner

NOW = 2_000_000_000


class RefreshSourcesTests(unittest.TestCase):
    def run_refresh(self, *, failed_burn=False):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        file = Path(directory.name) / 'snapshot.json'
        old_burn = {'asOf': NOW-7200, 'since': NOW-86400,
                    'rows': [{'tx': 'old-proof', 'time': NOW-8000}]}
        file.write_text(json.dumps({'schema': 1, 'token': runner.assets.MASTER,
                                   'updated': NOW-7200, 'errors': [], 'burns': old_burn}))
        mocks = [
            patch.object(runner, 'SNAPSHOT', file),
            patch.object(runner.time, 'time', return_value=NOW),
            patch.object(runner.assets, 'holders', return_value={'holders': [{'wallet': 'fixture'}]}),
            patch.object(runner.service_registry, 'update', return_value=False),
            patch.object(runner.assets, 'burns', side_effect=OSError('offline') if failed_burn else None,
                         return_value=([], NOW-100)),
            patch.object(runner.observatory, 'zero_burns', return_value={'asOf': NOW, 'rows': []}),
            patch.object(runner.trades, 'collect', return_value={'asOf': NOW, 'rows': []}),
            patch.object(runner.trade_history, 'refresh', return_value=False),
            patch.object(runner.trades, 'rates', return_value=[]),
            patch.object(runner.pools, 'collect', return_value={'asOf': NOW, 'rows': []}),
            patch.object(runner.observatory, 'identity', return_value={'asOf': NOW, 'byWallet': {'fixture': {'checked': NOW}}}),
            patch.object(runner.badges, 'refresh', return_value={'sources': {}, 'failed': []}),
            patch.object(runner.domains, 'enrich', return_value={'asOf': NOW, 'byWallet': {}}),
            patch.object(runner.badges, 'refresh_fragment_numbers', return_value={'asOf': NOW, 'byWallet': {}}),
        ]
        from contextlib import ExitStack
        with ExitStack() as stack:
            for mock in mocks:
                stack.enter_context(mock)
            runner.refresh()
        return json.loads(file.read_text()), copy.deepcopy(old_burn)

    def test_shared_flag_collectors_run_and_clear_missing_source_errors(self):
        snapshot, _ = self.run_refresh()
        for key in ('burns', 'zeroBurns', 'identity', 'domains', 'fragmentNumbers', 'badges'):
            self.assertEqual(snapshot[key]['asOf'], NOW)
            self.assertNotIn(key, snapshot['errors'])

    def test_failed_burn_scan_retains_previous_verified_rows_and_timestamp(self):
        snapshot, previous = self.run_refresh(failed_burn=True)
        self.assertEqual(snapshot['burns'], previous)
        self.assertIn('burns', snapshot['errors'])
        self.assertEqual(snapshot['domains']['asOf'], NOW)


if __name__ == '__main__':
    unittest.main()
