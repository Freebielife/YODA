"""Resumable archive coverage and atomic page verification, without network."""
import copy
import unittest
from unittest.mock import patch

import trade_history
import trades

NOW = 2000000000
POOL = "synthetic-pool"


def row(lt, age=1, pool=POOL):
    return {"tx": f"{lt:064x}", "lt": str(lt), "time": NOW-age*86400,
            "pool": pool, "kind": "buy", "wallet": "0:"+"a"*64}


def event(lt, age):
    return {"lt": str(lt), "timestamp": NOW-age*86400, "in_progress": False}


def snapshot():
    return {"updated": NOW-60, "trades": {
        "since": NOW-7*86400, "asOf": NOW-60, "rows": [row(100, 6)]}}


class HistoryTests(unittest.TestCase):
    def setUp(self):
        pause = patch.object(trade_history.time, "sleep")
        pause.start()
        self.addCleanup(pause.stop)
        self.patch_pools = patch.dict(trades.POOLS, {POOL: ("synthetic", "Synthetic")}, clear=True)
        self.patch_pools.start()
        self.addCleanup(self.patch_pools.stop)
        self.primary = patch.object(trades, "PRIMARY", POOL)
        self.primary.start()
        self.addCleanup(self.primary.stop)
        self.parser = patch.object(trades, "swap_rows", side_effect=lambda e, p:
            [dict(row(int(e["lt"]), pool=p), time=e["timestamp"])])
        self.parser.start()
        self.addCleanup(self.parser.stop)

    def test_resume_from_oldest_cursor_and_preserve_live_freshness(self):
        s = snapshot()
        with patch.object(trades, "fetch", return_value={"events": [event(90, 10)], "next_from": 90}) as fetch:
            self.assertFalse(trade_history.refresh(s, NOW, page_budget=1))
            self.assertIn("before_lt=100", fetch.call_args.args[0])
        self.assertEqual(s["trades"]["asOf"], NOW-60)
        self.assertEqual(s["trades"]["since"], NOW-10*86400)
        self.assertEqual(len(s["trades"]["rows"]), 2)
        with patch.object(trades, "fetch", return_value={"events": [event(80, 20)], "next_from": 80}) as fetch:
            trade_history.refresh(s, NOW, page_budget=1)
            self.assertIn("before_lt=90", fetch.call_args.args[0])
        self.assertEqual(s["trades"]["since"], NOW-20*86400)

    def test_failed_later_page_retains_previous_checkpoint_and_retries(self):
        s, saved = snapshot(), []
        with patch.object(trades, "fetch", side_effect=[
            {"events": [event(90, 10)], "next_from": 90}, OSError("offline")]):
            self.assertTrue(trade_history.refresh(s, NOW, page_budget=2,
                                                 save=lambda v: saved.append(copy.deepcopy(v))))
        self.assertEqual(saved[0]["tradeHistory"]["byPool"][POOL]["beforeLt"], "90")
        self.assertEqual(s["tradeHistory"]["byPool"][POOL]["beforeLt"], "90")
        self.assertEqual(len(s["trades"]["rows"]), 2)
        with patch.object(trades, "fetch", return_value={"events": [], "next_from": 0}) as fetch:
            self.assertFalse(trade_history.refresh(s, NOW))
            self.assertIn("before_lt=90", fetch.call_args.args[0])
        self.assertTrue(s["tradeHistory"]["complete"])

    def test_malformed_swap_cannot_partially_advance_page(self):
        s, before = snapshot(), snapshot()
        with patch.object(trades, "fetch", return_value={"events": [event(90, 10), event(80, 20)], "next_from": 80}), \
             patch.object(trades, "swap_rows", side_effect=[[row(90, 10)], ValueError("wrong token")]):
            self.assertTrue(trade_history.refresh(s, NOW))
        self.assertEqual(s["trades"], before["trades"])
        self.assertEqual(s["tradeHistory"]["byPool"][POOL]["beforeLt"], "100")

    def test_coverage_waits_for_every_pool(self):
        s = snapshot()
        with patch.dict(trades.POOLS, {"other-pool": ("synthetic", "Synthetic")}), \
             patch.object(trades, "fetch", return_value={"events": [event(90, 10)], "next_from": 90}):
            trade_history.refresh(s, NOW, page_budget=1)
        self.assertEqual(s["trades"]["since"], NOW-7*86400)
        self.assertFalse(s["tradeHistory"]["complete"])

    def test_exhausted_pool_and_year_cutoff_stop_requests(self):
        for response in ({"events": [], "next_from": 0},
                         {"events": [event(90, 400)], "next_from": 90}):
            s = snapshot()
            with patch.object(trades, "fetch", return_value=response):
                trade_history.refresh(s, NOW)
            self.assertTrue(s["tradeHistory"]["complete"])
            self.assertEqual(s["trades"]["since"], NOW-trade_history.YEAR)
            self.assertEqual(len(s["trades"]["rows"]), 1)
            with patch.object(trades, "fetch", side_effect=AssertionError("Already done")):
                trade_history.refresh(s, NOW+1800)

    def test_repeated_or_forward_cursor_does_not_claim_coverage(self):
        s = snapshot()
        with patch.object(trades, "fetch", return_value={"events": [event(90, 10)], "next_from": 100}):
            self.assertTrue(trade_history.refresh(s, NOW))
        self.assertEqual(s["trades"]["since"], NOW-7*86400)

    def test_live_collection_keeps_archived_rows_and_coverage(self):
        s = snapshot()["trades"]
        s["rows"].append(row(50, 100))
        s["since"] = NOW-100*86400
        with patch.object(trades, "collect_pool", return_value=({}, NOW-6*3600)):
            result = trades.collect(s, NOW-trade_history.YEAR, NOW)
        self.assertEqual(result["since"], NOW-100*86400)
        self.assertIn(row(50, 100), result["rows"])

    def test_first_collection_is_bounded_then_backfill_extends_it(self):
        with patch.object(trades, "collect_pool", return_value=({}, NOW-86400)) as collect:
            result = trades.collect({}, NOW-trade_history.YEAR, NOW)
        self.assertEqual(collect.call_args.args[1], NOW-86400)
        self.assertEqual(result["since"], NOW-86400)


if __name__ == "__main__":
    unittest.main()
