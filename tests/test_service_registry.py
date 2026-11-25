"""Exact custodial attribution, shared export and failure-safe refresh tests."""
import copy
import unittest
from unittest.mock import patch

import service_registry as registry
import observatory


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.book = registry.bundled()
        self.wallet = next(a for a, n in self.book["entries"].items() if n == "Binance")
        self.now = self.book["asOf"] + registry.INTERVAL + 1

    def test_exact_address_not_account_name_is_evidence(self):
        self.assertEqual(observatory.role(self.wallet, {"is_wallet": True}), "Binance")
        self.assertIsNone(observatory.role("0:" + "ef" * 32,
                                          {"is_wallet": True, "name": "Binance"}))
        self.assertIsNone(registry.lookup("0:" + "ff" * 32))

    def test_all_holders_are_attributed_without_network_or_budget(self):
        snap = {"holders": {"holders": [{"wallet": self.wallet}]},
                "identity": {"byWallet": {self.wallet: {"checked": self.now}}}}
        with patch("assets.fetch", side_effect=AssertionError("No account request allowed")):
            registry.apply(snap, self.book)
        record = snap["identity"]["byWallet"][self.wallet]
        self.assertEqual(record["role"], "Binance")
        self.assertEqual(record["checked"], self.now)
        self.assertEqual(record["roleSource"], registry.SOURCE_PAGE)

    def test_daily_refresh_validates_and_removes_upstream_labels(self):
        other = "0:" + "ab" * 32
        rows = [{"address": other, "name": "OKX 99"}]
        snap = {"holders": {"holders": [{"wallet": self.wallet}]}}
        registry.apply(snap, self.book)
        fresh = registry.refresh(self.book, self.now, fetch=lambda *a, **kw: rows)
        registry.apply(snap, fresh)
        self.assertIsNone(snap["identity"]["byWallet"][self.wallet]["role"])
        self.assertNotIn("roleSource", snap["identity"]["byWallet"][self.wallet])
        self.assertEqual(registry.lookup(other, fresh), "OKX 99")
        self.assertEqual(fresh["asOf"], self.now)

    def test_refresh_waits_one_day(self):
        with patch("assets.fetch", side_effect=AssertionError("Too early")):
            self.assertEqual(registry.refresh(self.book, self.now - 2), self.book)

    def test_failed_source_preserves_labels_and_original_time(self):
        snap = {"serviceRegistry": copy.deepcopy(self.book),
                "holders": {"holders": [{"wallet": self.wallet}]}}
        with patch("assets.fetch", side_effect=OSError("unavailable")):
            self.assertEqual(registry.update(snap, self.now), "OSError")
        self.assertEqual(snap["serviceRegistry"], self.book)
        self.assertEqual(snap["identity"]["byWallet"][self.wallet]["role"], "Binance")

    def test_unrelated_names_invalid_addresses_and_conflicts(self):
        for rows in ([], {}, [{"address": "broken", "name": "OKX 1"}],
                     [{"address": self.wallet, "name": "Binance"},
                      {"address": self.wallet, "name": "OKX 1"}],
                     [{"address": self.wallet, "name": "Binance fan club"}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                registry.parse_accounts(rows)

    def test_project_override_has_priority(self):
        snap = {"holders": {"holders": [{"wallet": self.wallet}]}}
        registry.apply(snap, self.book, {self.wallet: "Explicit override"})
        record = snap["identity"]["byWallet"][self.wallet]
        self.assertEqual(record["role"], "Explicit override")
        self.assertNotIn("roleRegistry", record)


if __name__ == "__main__":
    unittest.main()
