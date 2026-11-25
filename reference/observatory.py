"""Verified wallet identities and transfers to the TON zero address."""
import base64
import service_registry
import time
from urllib.parse import urlencode

from assets import DOMAIN, MASTER, MASTER_RAW, fetch, raw_address, resolved_domain, token_amount
from domains import DIGITS
from badges import POOL_RAW, ZERO, decode_address, raw_friendly

TONCENTER = "https://toncenter.com/api/v3"
RAFFLES = "https://api.tonraffles.app"
TONRAFFLES_LOCKS = {
    raw_friendly(address) for address in (
        "EQDmlSInlyrr0yg5uMXu47cqkxgZvh0DckZszzu2QLN9zROT",
        "EQCdo790wlAoVT8EFlXlaTtNry4OatOFgBOHl7tb2shaLooQ",
        "EQAXoHB5rqxLORE9obonGlMpsvqNMNxeel80ajqJ4DdGNhSI",
    )
}
ROLES = {"dedust_vault": "DeDust Vault", "stonfi_router_v2": "STON.fi Router V2",
         "stonfi_router_v1": "STON.fi Router V1", "dedust_pool": "DeDust Pool",
         "stonfi_pool_v2": "STON.fi Pool V2", "stonfi_pool_v1": "STON.fi Pool V1"}
RECOVERABLE = (OSError, ValueError, KeyError, RuntimeError)


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
                    "tx": tx, "wallet": wallet, "name": None, "ludoman": token_amount(amount)}
    return None


def zero_burns(previous, now):
    start = max(1, previous.get("asOf", 1) - 3600)
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


# User-provided CryptoCheck bot address; explicit mapping, not guessed from volume.
KNOWN_SERVICES = {
    "0:2d7075bcc5a3baceff8d869f9c466be6f0ee699700859811ad9da68f6aacc89a": "CryptoCheck",
}

def role(wallet, account, registry=None):
    if wallet in KNOWN_SERVICES:
        return KNOWN_SERVICES[wallet]
    custody = service_registry.lookup(wallet, registry)
    if custody:
        return custody
    if wallet == POOL_RAW:
        return "JVault Staking Pool"
    if wallet in TONRAFFLES_LOCKS:
        lock = fetch(f"/blockchain/accounts/{wallet}/methods/get_contract_data", attempts=2)
        if lock.get("success") and len(lock.get("stack", [])) >= 9:
            return "TonRaffles Lock"
    return next((ROLES[i] for i in account.get("interfaces", []) if i in ROLES), None)


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


def vesting(now):
    payload = fetch(f"/api/v2/lock/{MASTER}", api=RAFFLES)
    if payload["token"]["address"] != MASTER or int(payload["token"]["decimals"]) != 9:
        raise ValueError("Unexpected TonRaffles token")
    records = payload["lockRecords"]
    if len({r["address"] for r in records}) != len(records):
        raise ValueError("Duplicate TonRaffles locks")
    expected = sum(max(0, int(r["initialTokens"]) - int(r["claimedTokens"])) for r in records)
    if expected != int(payload["totalLockedTokens"]):
        raise ValueError("TonRaffles lock records do not match total")
    amounts = []
    for record in records:
        contract = record["address"]
        info = fetch(f"/blockchain/accounts/{contract}/methods/get_contract_data", attempts=2)
        time.sleep(1.05)
        if not info.get("success"):
            if int(record["claimedTokens"]) == int(record["initialTokens"]):
                continue
            raise ValueError("Outstanding lock contract could not be read")
        stack = info["stack"]
        amount = int(stack[8]["num"], 16)
        if amount:
            wallet = decode_address(stack[1])
            data = fetch(f"/blockchain/accounts/{wallet}/methods/get_wallet_data", attempts=2)
            values = data["stack"]
            if (not data["success"] or decode_address(values[1]) != raw_friendly(contract)
                    or decode_address(values[2]) != MASTER_RAW):
                raise ValueError("Unexpected jetton wallet for TonRaffles lock")
            amounts.append(min(amount, int(values[0]["num"], 16)))
            time.sleep(1.05)
    return {"asOf": now, "reserved": token_amount(sum(amounts)), "reported": token_amount(expected)}


def period_balances(cell):
    """Read the Coins value at the start of each 32-bit lock-period entry."""
    boc = bytes.fromhex(cell)
    if boc[:4] != bytes.fromhex("b5ee9c72") or not 1 <= boc[4] <= 4 or not 1 <= boc[5] <= 4:
        raise ValueError("Unexpected lock periods BOC header")
    ref_size, offset_size = boc[4:6]
    pos = 6

    def read(length):
        nonlocal pos
        end = pos + length
        if end > len(boc):
            raise ValueError("Truncated lock periods BOC")
        chunk = boc[pos:end]
        pos = end
        return chunk

    def integer(length):
        return int.from_bytes(read(length), "big")

    count, roots, absent = (integer(ref_size) for _ in range(3))
    size = integer(offset_size)
    if not 1 <= count <= 256 or roots != 1 or absent or integer(ref_size) != 0 or size != len(boc) - pos:
        raise ValueError("Unexpected lock periods BOC structure")
    cells = []
    for i in range(count):
        refs, descriptor = read(2)
        if refs not in (0, 2):
            raise ValueError("Unexpected lock periods cell")
        bits = "".join(f"{byte:08b}" for byte in read((descriptor + 1) // 2))
        if descriptor % 2:
            bits = bits[:bits.rindex("1")]
        children = [integer(ref_size) for _ in range(refs)]
        if any(child <= i or child >= count for child in children):
            raise ValueError("Invalid lock period cell reference")
        cells.append((bits, children))
    if pos != len(boc):
        raise ValueError("Unexpected data after lock period cells")

    def walk(index, remaining):
        bits, refs = cells[index]
        if bits[0] == "0":
            length = bits[1:].index("0")
            skip = length * 2 + 2
        else:
            width = remaining.bit_length()
            repeated = bits[1] == "1"
            offset = 3 if repeated else 2
            length = int(bits[offset:offset + width] or "0", 2)
            skip = offset + width + (0 if repeated else length)
        if length > remaining or len(bits) < skip:
            raise ValueError("Invalid lock period key")
        remaining -= length
        if remaining:
            if len(refs) != 2 or len(bits) != skip:
                raise ValueError("Invalid lock period branch")
            for child in refs:
                yield from walk(child, remaining - 1)
        else:
            if refs:
                raise ValueError("Invalid lock period leaf")
            balance_length = 8 * int(bits[skip:skip + 4], 2)
            if len(bits) < skip + 4 + balance_length:
                raise ValueError("Truncated lock period balance")
            yield int(bits[skip + 4:skip + 4 + balance_length] or "0", 2)

    return list(walk(0, 32))


def staking(now):
    result = fetch(f"/blockchain/accounts/{POOL_RAW}/methods/get_storage_data")
    stack = result["stack"]
    if not result["success"] or len(stack) != 19 or int(stack[1]["num"], 16) != 216:
        raise ValueError("Unexpected Ludoman staking pool")
    # Period balances include requested withdrawals until the payout is sent.
    principal = sum(period_balances(stack[13]["cell"]))
    active = int(stack[6]["num"], 16)
    if principal < active:
        raise ValueError("Lock-period principal below active JVault TVL")
    return {"asOf": now, "principal": token_amount(principal), "active": token_amount(active)}
