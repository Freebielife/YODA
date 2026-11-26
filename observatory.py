"""Zero-address burns and identified TON accounts. No staking assumptions."""
import base64
import time
import service_registry
from urllib.parse import urlencode
from assets import DOMAIN, MASTER, MASTER_RAW, fetch, raw_address, resolved_domain, token_amount
from domains import DIGITS
from badges import ZERO

TONCENTER = "https://toncenter.com/api/v3"
ROLES = {"dedust_vault":"DeDust Vault","stonfi_router_v2":"STON.fi Router V2",
         "stonfi_router_v1":"STON.fi Router V1","dedust_pool":"DeDust Pool",
         "stonfi_pool_v2":"STON.fi Pool V2","stonfi_pool_v1":"STON.fi Pool V1"}
RECOVERABLE = (OSError, ValueError, KeyError, RuntimeError)

KNOWN_SERVICES = {'0:f8b8635d0786b77f9da660e65fd31d670a675dd4302facba692f46b571eb5360': 'Binance', '0:cf7ea235ed6f6517edce98026ef7618e9f6d81a1331d4e65ba718e2cd15f80ad': 'Bybit'}
def role(wallet, account, registry=None):
    if wallet in KNOWN_SERVICES:
        return KNOWN_SERVICES[wallet]
    custody = service_registry.lookup(wallet, registry)
    if custody:
        return custody
    known = next((ROLES[i] for i in account.get("interfaces", []) if i in ROLES), None)
    if known:
        return known
    # Generic contracts are not automatically a named service or human wallet.
    if account.get("status") == "active" and account.get("is_wallet") is False:
        return "unclassified_contract"
    return None
def hash_hex(value):
    result = base64.b64decode(value, validate=True)
    if len(result) != 32:
        raise ValueError("Invalid transaction hash")
    return result.hex()


def to_zero(row):
    tx = hash_hex(row["transaction_hash"])
    wallet = raw_address(row["source"])
    amount = int(row["amount"])
    if row["transaction_aborted"] or amount <= 0 or wallet == ZERO:
        return None
    if raw_address(row["destination"]) != ZERO or raw_address(row["jetton_master"]) != MASTER_RAW:
        raise ValueError("Unexpected zero-address transfer")
    event = fetch("/events/" + hash_hex(row["trace_id"]))
    if event["in_progress"]:
        raise ValueError("Zero-address transfer has not finalized")
    for action in event["actions"]:
        if action["type"] != "JettonTransfer" or action["status"] != "ok" or tx not in action["base_transactions"]:
            continue
        transfer = action["JettonTransfer"]
        if ((transfer.get("sender") or {}).get("address") == wallet
                and (transfer.get("recipient") or {}).get("address") == ZERO
                and transfer["jetton"]["address"] == MASTER_RAW and int(transfer["amount"]) == amount):
            return {"kind": "burn", "method": "zero", "time": int(row["transaction_now"]),
                    "tx": tx, "wallet": wallet, "name": None, "tokenAmount": token_amount(amount)}
    return None


def zero_burns(previous, now):
    start = max(1, previous.get("asOf", now - 7 * 86400) - 3600)
    answers = {r["tx"]: r for r in previous.get("rows", []) if r["time"] < start}
    old = {r["tx"]: r for r in previous.get("rows", [])}
    for offset in range(0, 10000, 100):
        query = urlencode({"jetton_master": MASTER, "owner_address": ZERO, "direction": "in",
                           "start_utime": start, "end_utime": now, "offset": offset, "limit": 100})
        rows = fetch("/jetton/transfers?" + query, api=TONCENTER)["jetton_transfers"]
        for item in rows:
            key = hash_hex(item["transaction_hash"])
            if key in answers:
                continue
            row = old.get(key) or to_zero(item)
            if row:
                answers[key] = row
            if key not in old:
                time.sleep(1)
        if len(rows) < 100:
            return {"asOf": now, "rows": sorted(answers.values(), key=lambda r: (-r["time"], r["tx"]))}
    raise RuntimeError("Zero-address pagination limit")


def activation(wallet):
    cursor = 0
    for _ in range(5):
        page = fetch(f"/blockchain/accounts/{wallet}/transactions?sort_order=asc&limit=25&after_lt={cursor}", attempts=2)["transactions"]
        for tx in page:
            if tx["end_status"] == "active":
                if tx["account"]["address"] != wallet or tx["orig_status"] not in ("nonexist", "uninit"):
                    return None
                return int(tx["utime"])
        if len(page) < 25:
            return None
        next_cursor = int(page[-1]["lt"])
        if next_cursor <= cursor:
            raise ValueError("Activation cursor did not advance")
        cursor = next_cursor
    return None


def identity(snapshot, now, budget=32, pace=1.05):
    previous = snapshot.get("identity", {}).get("byWallet", {})
    holders = snapshot.get("holders", {}).get("holders", [])[:100]
    rows = snapshot.get("trades", {}).get("rows", [])[:50] + snapshot.get("burns", {}).get("rows", [])[:50] + snapshot.get("zeroBurns", {}).get("rows", [])[:50]
    visible = list(dict.fromkeys(r["wallet"] for r in holders[:5] + rows + holders[5:]))
    top = {r["wallet"] for r in holders[:30]}
    records = {w: dict(r) for w, r in previous.items()}
    for w in visible:
        records.setdefault(w, {})
        if w in KNOWN_SERVICES:
            records[w]["role"] = KNOWN_SERVICES[w]
    queue = sorted(visible, key=lambda w: (w not in top, records[w].get("checked", 0)))
    checks = 0
    for wallet in queue:
        record = records[wallet]
        if checks >= budget:
            break
        if now - record.get("checked", 0) < (4 * 3600 if record.get("domain") else 12 * 3600):
            continue
        checks += 1
        try:
            account = fetch(f"/accounts/{wallet}", attempts=2)
            time.sleep(pace)
            label = role(wallet, account, snapshot.get("serviceRegistry"))
            names = fetch(f"/accounts/{wallet}/dns/backresolve", attempts=2)["domains"] if account["is_wallet"] else []
            domain = None
            linked_digits = []
            candidates = list(dict.fromkeys([*names, (account.get("name") or "").lower()]))
            for name in candidates:
                numeric = DIGITS.fullmatch(name)
                if not DOMAIN.fullmatch(name) or (domain and not numeric):
                    continue
                time.sleep(pace)
                validated = resolved_domain({"address": wallet, "name": name}, strict=True)
                if validated:
                    domain = domain or validated
                    if numeric:
                        linked_digits.append(validated)
            at = record.get("activated")
            if not at and account["is_wallet"] and account.get("status") == "active":
                time.sleep(pace)
                at = activation(wallet)
            record.update(checked=now, domain=domain, linkedDigits=linked_digits, role=label, activated=at)
        except RECOVERABLE as exc:
            print("Identity check:", wallet[:12], exc, flush=True)
        time.sleep(pace)
    return {"byWallet": records, "asOf": now}
