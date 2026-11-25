"""Ownership of canonical four-digit TON DNS NFTs."""
import re
import time
from collections import deque
from urllib.parse import urlencode

from assets import fetch, RAW_ADDRESS

ROOT = "0:b774d95eb20543f186c06b371ab88ad704f7e256130caf96189368a7d0cb6ccf"
DIGITS = re.compile(r"[0-9]{4}\.ton")


def owned(item, collection):
    if item.get("verified") is not True or (item.get("collection") or {}).get("address") != collection:
        return None
    owner = (item.get("owner") or {}).get("address", "")
    return owner if RAW_ADDRESS.fullmatch(owner) else None


def pages(path, params):
    for offset in range(0, 10000, 100):
        items = fetch(path + "?" + urlencode(dict(params, offset=offset, limit=100)), attempts=2)["nft_items"]
        yield from items
        if len(items) < 100:
            return
        time.sleep(1)
    raise RuntimeError("NFT pagination limit reached")


def four_digits(wallet):
    result = set()
    for item in pages("/accounts/" + wallet + "/nfts", {"collection":ROOT}):
        name = (item.get("dns") or "").lower()
        if owned(item, ROOT) == wallet and DIGITS.fullmatch(name):
            result.add(name)
    return sorted(result)


def check_queue(addresses, visible, checked, now, *, checked_at="digitsAt", limit=45):
    """Refresh visible identities hourly while reserving every third slot for history."""
    priority, history = [], []
    for wallet in addresses:
        record = checked[wallet]
        ttl = 3600 if wallet in visible else 86400
        if record.get(checked_at, 0) and now - record[checked_at] < ttl:
            continue
        # Failed requests must rotate too, without exhausting the free API budget.
        if record.get("lastAttempt", 0) and now - record["lastAttempt"] < 1800:
            continue
        (priority if wallet in visible else history).append(wallet)
    age = lambda w: max(checked[w].get(checked_at, 0), checked[w].get("lastAttempt", 0))
    priority, history = deque(sorted(priority, key=age)), deque(sorted(history, key=age))
    result = []
    while (priority or history) and len(result) < limit:
        for queue in (priority, priority, history):
            if queue and len(result) < limit:
                result.append(queue.popleft())
    return result


def enrich(snapshot, now):
    previous = snapshot.get("domains", {})
    holders = [r["wallet"] for r in snapshot.get("holders", {}).get("holders", [])]
    trades = [r["wallet"] for r in snapshot.get("trades", {}).get("rows", [])]
    burns = [r["wallet"] for r in snapshot.get("burns", {}).get("rows", [])]
    addresses = list(dict.fromkeys(holders + trades[:50] + burns + trades))
    visible = set(holders + trades[:50] + burns[:50])
    wanted = set(addresses)
    checked = {w:dict(r) for w,r in previous.get("byWallet", {}).items() if w in wanted}
    for wallet in addresses:
        checked.setdefault(wallet, {"digits": [], "digitsAt": 0})
    due = check_queue(addresses, visible, checked, now)
    end = time.monotonic()+120
    for w in due:
        if time.monotonic() >= end: break
        checked[w]["lastAttempt"] = now
        try:
            checked[w].update(digits=four_digits(w), digitsAt=now)
        except (OSError, ValueError, KeyError, RuntimeError) as exc:
            print("Domain check pending:", w[:10], type(exc).__name__, flush=True)
        time.sleep(1)
    for record in checked.values():
        if now - record.get("digitsAt",0) > 2*86400: record["digits"] = []
    return {"byWallet":checked, "asOf":now}
