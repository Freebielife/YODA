"""Successful direct GRAM/LUDOMAN swaps from tracked pool events."""
import re
import time
from urllib.parse import urlencode

from assets import MASTER_RAW, fetch, raw_address, token_amount

PRIMARY = "EQDUK1q0zadi3cWKYZrqtIIavMazqgYKIFYRDBBhlIPTxQAV"
POOLS = {
    PRIMARY: ("stonfi", "STON.fi"),
    "EQAVfl9Mvs1XL1umqTGi98ZliQaUnv9bi17UBI15gQbO78JD": ("dedust", "DeDust"),
    "EQDIJ0ZY3yMhKdWoTLVVtSPBJmvAURRJ1n40-8Cj8ybDiRf8": ("dedust", "DeDust"),
}
TX_HASH = re.compile(r"[a-f0-9]{64}")


def swap_rows(event, pool):
    if event["in_progress"]:
        return
    dex, label = POOLS[pool]
    for action in event["actions"]:
        if action["type"] != "JettonSwap" or action["status"] != "ok":
            continue
        swap = action["JettonSwap"]
        if swap["dex"] != dex:
            continue
        source = (swap.get("jetton_master_in") or {}).get("address")
        target = (swap.get("jetton_master_out") or {}).get("address")
        if target == MASTER_RAW and source is None and swap.get("ton_in"):
            kind, jetton, gram = "buy", swap["amount_out"], swap["ton_in"]
        elif source == MASTER_RAW and target is None and swap.get("ton_out"):
            kind, jetton, gram = "sell", swap["amount_in"], swap["ton_out"]
        else:
            continue
        # The action's first underlying transaction also distinguishes actions in one trace.
        tx = action["base_transactions"][0]
        if not TX_HASH.fullmatch(tx):
            raise ValueError("Invalid swap transaction hash")
        jetton, gram = token_amount(jetton), token_amount(gram)
        if jetton != "0" and gram != "0":
            yield {"kind": kind, "time": int(event["timestamp"]), "tx": tx,
                   "lt": str(event["lt"]), "wallet": raw_address(swap["user_wallet"]["address"]),
                   "ludoman": jetton, "ton": gram, "dex": label, "pool": pool}


def collect_pool(pool, start, end, max_pages):
    rows = {}
    before = None
    for _ in range(max_pages):
        params = {"limit": 100}
        if before is not None:
            params["before_lt"] = before
        path = f"/accounts/{pool}/events?" + urlencode(params)
        page = fetch(path)
        events = page["events"]
        for event in events:
            if start <= event["timestamp"] <= end:
                for row in swap_rows(event, pool):
                    rows[row["tx"]] = row
        if not events or min(e["timestamp"] for e in events) < start:
            return rows, start
        cursor = int(page["next_from"])
        if not cursor:
            return rows, start
        if before is not None and cursor >= before:
            raise ValueError("Pool event cursor did not advance")
        before = cursor
        time.sleep(1)
    raise RuntimeError(f"Pool history page limit reached: {pool}")


def collect(previous, cutoff, now, max_pages=180):
    # Bootstrap a bounded recent window; the separate backfill extends it.
    start = max(cutoff, previous["asOf"] - 6 * 3600) if previous.get("asOf") else max(cutoff, now - 86400)
    rows = {row["tx"]: row for row in previous.get("rows", []) if cutoff <= row["time"] < start}
    for pool in POOLS:
        fresh, _ = collect_pool(pool, start, now, max_pages)
        for tx, row in fresh.items():
            if tx not in rows or pool == PRIMARY:
                rows[tx] = row
    since = max(cutoff, min(start, previous.get("since", start)))
    return {"rows": sorted(rows.values(), key=lambda r: (r["time"], int(r["lt"]), r["tx"]), reverse=True),
            "since": since, "asOf": now}


def rates():
    data = fetch("/coins/the-open-network/market_chart?vs_currency=usd&days=365",
                 api="https://api.coingecko.com/api/v3")
    # CoinGecko returns daily closes at UTC boundaries and a final intraday quote.
    prices = [[int(ms) // 1000, float(usd)] for ms, usd in data["prices"]]
    if len(prices) < 2 or any(not 0 < price < 1000 for _, price in prices):
        raise ValueError("Invalid GRAM/USD history")
    return sorted(prices)
