"""Shared TON custodial labels, attributed to Tonkeeper's curated address book.

Exact address matches only. Labels are external attribution, not on-chain proof
of ownership. No inference from account names, balances or counterparties.
"""
import hashlib
import json
import re
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/tonkeeper/ton-assets/main/accounts.json"
SOURCE_PAGE = "https://github.com/tonkeeper/ton-assets/blob/main/accounts.json"
INTERVAL = 86400
ADDRESS = re.compile(r"(?:0|-1):[0-9a-f]{64}")
# Only these custodial families from the curated book qualify as services.
# Anchored suffixes exclude unrelated names that merely mention an exchange.
FAMILIES = (
    "Binance", "OKX", "Bybit", "MEXC", "Gate.io", "Bitget", "Kucoin",
    "Huobi", "HTX", "BingX", "Bitfinex", "CoinEx", "Crypto.com", "EXMO",
    "FTX", "BitMart", "Nobitex", "Bitpin", "Coinone", "Paribu", "TIDEX",
    "QMall", "BIT", "Bitforex", "OMPFinex", "Bitrue", "Coinspot", "BigOne",
    "Farhad Exchange", "BitTime", "Foxbit", "Richamster", "Flipster", "Ourbit",
    "lbank.info", "bit.com", "Crypto Bot", "CryptoBot", "Wallet Bot",
    "Wallet in Telegram", "xRocket Bot", "CWallet", "Matrixport",
)
NAME = re.compile(r"(?:" + "|".join(re.escape(n) for n in FAMILIES) +
                  r")(?:\s*(?:\d+|Hot Wallet|Cold Storage(?: \d+)?|Deposit|Withdrawal))?"
                  r"(?: \(Old\))?", re.I)


def parse_accounts(accounts):
    if not isinstance(accounts, list) or not 1 <= len(accounts) <= 20000:
        raise ValueError("Malformed curated account list")
    entries = {}
    for row in accounts:
        if not isinstance(row, dict):
            raise ValueError("Malformed curated account")
        name = row.get("name", "")
        if not isinstance(name, str) or not NAME.fullmatch(name):
            continue
        address = row.get("address", "")
        if not isinstance(address, str) or not ADDRESS.fullmatch(address):
            raise ValueError("Invalid curated custody address")
        if address in entries and entries[address] != name:
            raise ValueError("Conflicting curated custody labels")
        entries[address] = name
    if not entries:
        raise ValueError("Empty custody registry")
    return entries


def validate(registry):
    if (registry.get("source") != SOURCE_PAGE or
            not isinstance(registry.get("asOf"), int) or registry["asOf"] <= 0 or
            not re.fullmatch(r"[0-9a-f]{64}", registry.get("sha256", ""))):
        raise ValueError("Invalid registry provenance")
    entries = registry.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise ValueError("Missing registry entries")
    parsed = parse_accounts([{"address": a, "name": n} for a, n in entries.items()])
    if parsed != entries:
        raise ValueError("Unsupported registry label")
    return registry


def bundled():
    return validate(json.loads(Path(__file__).with_name("common-services.json").read_text()))


def lookup(wallet, registry=None):
    return (registry if registry is not None else bundled())["entries"].get(wallet)


def refresh(previous, now, fetch=None):
    previous = validate(previous) if previous else bundled()
    if now - previous["asOf"] < INTERVAL:
        return previous
    if fetch is None:
        from assets import fetch
    accounts = fetch("", attempts=2, api=SOURCE)
    entries = parse_accounts(accounts)
    digest = hashlib.sha256(json.dumps(accounts, sort_keys=True, separators=(",", ":"),
                                      ensure_ascii=False).encode()).hexdigest()
    return {"asOf": now, "source": SOURCE_PAGE, "sha256": digest, "entries": entries}


def apply(snapshot, registry, overrides=None):
    """Label the entire tracked address set without spending per-wallet API quota."""
    overrides = overrides or {}
    registry = validate(registry)
    identity = snapshot.setdefault("identity", {"byWallet": {}})
    records = identity.setdefault("byWallet", {})
    wallets = set(records)
    for section, key in (("holders", "holders"), ("trades", "rows"),
                         ("burns", "rows"), ("zeroBurns", "rows")):
        wallets.update(r["wallet"] for r in snapshot.get(section, {}).get(key, []))
    for wallet in wallets:
        label = overrides.get(wallet) or lookup(wallet, registry)
        record = records.get(wallet, {})
        if record.pop("roleRegistry", False):
            # A removed upstream attribution must not survive in the identity cache.
            record.update(role=None)
            record.pop("roleSource", None)
            record.pop("roleChecked", None)
        if label:
            record["role"] = label
            if wallet not in overrides:
                record.update(roleRegistry=True, roleSource=registry["source"],
                              roleChecked=registry["asOf"])
            records[wallet] = record


def update(snapshot, now, overrides=None):
    """Retain last good labels on source failure, without falsifying their age."""
    registry = snapshot.get("serviceRegistry") or bundled()
    try:
        registry = refresh(registry, now)
        error = None
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        error = type(exc).__name__
        print("Service registry refresh unavailable:", error, flush=True)
    snapshot["serviceRegistry"] = registry
    apply(snapshot, registry, overrides)
    return error
