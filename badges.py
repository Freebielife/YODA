"""TON/DNS/Fragment and project-configured badge proofs. No foreign NFTs."""
import base64
import binascii
import re
import time
from assets import fetch, raw_address
from domains import pages, owned, check_queue

ZERO = "0:" + "0" * 64
FRAGMENT_NUMBERS = "0:0e41dc1dc3c9067ed24248580e12b3359818d83dee0304fabcf80845eafafdb2"

BADGE_RULES = {}

def refresh(previous, now):
    # Recheck expensive on-chain holder/NFT sources at most every six hours.
    # A failing source does not grant an unconfirmed badge.
    old = previous.get("sources", {})
    sources = {key: old[key] for key in BADGE_RULES if key in old}
    failed = []
    for key, spec in BADGE_RULES.items():
        last = sources.get(key, {})
        if last.get("asOf", 0) > now - 6 * 3600:
            continue
        try:
            sets = []
            for criterion in spec["criteria"]:
                if criterion["type"] == "jetton_min":
                    wallets = holders(criterion["master"], True, criterion["min_balance"])
                elif criterion["type"] == "nft_collection":
                    wallets = nft_owners(criterion["collection"], False)
                else:
                    raise ValueError("Unrecognized badge proof")
                sets.append(set(wallets))
            qualifying = (set.intersection(*sets) if spec["match"] == "all"
                          else set.union(*sets))
            sources[key] = {"asOf": now, "wallets": {wallet: True for wallet in qualifying}}
        except (OSError, ValueError, KeyError, RuntimeError) as error:
            failed.append(key)
            print("Badge source failed:", key, type(error).__name__, flush=True)
    return {"sources": sources, "failed": failed}
def raw_friendly(address):
    data = base64.urlsafe_b64decode(address)
    if len(data) != 36 or binascii.crc_hqx(data[:34], 0) != int.from_bytes(data[34:], "big"):
        raise ValueError("Invalid friendly address")
    return f"{int.from_bytes(data[1:2], 'big', signed=True)}:{data[2:34].hex()}"


def decode_address(item):
    # TonAPI serializes a plain MsgAddressInt as one 267-bit cell without refs.
    match = re.fullmatch(r"b5ee9c72010101010024000043([0-9a-f]{68})", item.get("cell", ""))
    if not match:
        raise ValueError("Unexpected address cell")
    value = int(match[1], 16)
    if value >> 269 != 4 or value & 31 != 16:
        raise ValueError("Unexpected MsgAddressInt tag")
    workchain = ((value >> 261) & 255).to_bytes(1, "big")
    return f"{int.from_bytes(workchain, 'big', signed=True)}:{(value >> 5) & ((1 << 256) - 1):064x}"


def fragment_number_owner(wallet):
    if wallet == ZERO:
        return False
    items = pages(f"/accounts/{wallet}/nfts", {"collection": FRAGMENT_NUMBERS})
    return any(owned(item, FRAGMENT_NUMBERS) == wallet for item in items)


def refresh_fragment_numbers(snapshot, now):
    groups = [
        [row["wallet"] for row in snapshot.get(key, {}).get(rows, [])]
        for key, rows in (("holders", "holders"), ("trades", "rows"), ("burns", "rows"), ("zeroBurns", "rows"))
    ]
    visible = set(wallet for group in groups for wallet in group[:50])
    addresses = list(dict.fromkeys(wallet for group in groups for wallet in group))
    previous = snapshot.get("fragmentNumbers", {}).get("byWallet", {})
    records = {wallet: dict(previous.get(wallet, {})) for wallet in addresses}
    deadline = time.monotonic() + 65
    for wallet in check_queue(addresses, visible, records, now, checked_at="checkedAt", limit=30):
        if time.monotonic() >= deadline:
            break
        record = records[wallet]
        record["lastAttempt"] = now
        try:
            record.update(owns=fragment_number_owner(wallet), checkedAt=now)
        except (OSError, ValueError, KeyError, RuntimeError) as error:
            print(f"Fragment number ownership pending: {type(error).__name__}", flush=True)
        time.sleep(1)
    return {"asOf": now, "byWallet": {wallet: record for wallet, record in records.items() if record}}


def holders(master, inclusive, threshold=200_000):
    jetton = fetch(f"/jettons/{master}")["metadata"]
    if jetton["address"] != raw_friendly(master):
        raise ValueError("Wrong jetton metadata")
    limit = threshold * 10 ** int(jetton["decimals"])
    owners = {}
    for offset in range(0, 9000, 100):
        data = fetch(f"/jettons/{master}/holders?limit=100&sort_by=balance&offset={offset}")
        rows = data["addresses"]
        for row in rows:
            balance = int(row["balance"])
            if balance < limit or (balance == limit and not inclusive):
                return owners
            owner = raw_address(row["owner"]["address"])
            if owner != ZERO:
                owners[owner] = True
        if len(rows) < 100:
            if offset + len(rows) < data["total"]:
                raise ValueError("Truncated jetton holder list")
            return owners
        time.sleep(0.6)
    raise RuntimeError("Jetton holder pagination limit")


def nft_owners(collection, keep_item):
    collection_raw = raw_friendly(collection)
    owners = {}
    for offset in range(0, 10000, 100):
        rows = fetch(f"/nfts/collections/{collection}/items?limit=100&offset={offset}")["nft_items"]
        for row in rows:
            owner = (row.get("owner") or {}).get("address")
            if not owner or owner == ZERO or row.get("verified") is not True:
                continue
            if (row.get("collection") or {}).get("address") != collection_raw:
                raise ValueError("Unexpected NFT collection")
            owner = raw_address(owner)
            candidate = (int(row["index"]), raw_address(row["address"]))
            if owner not in owners or candidate < owners[owner]:
                owners[owner] = candidate
        if len(rows) < 100:
            return {owner: item if keep_item else True for owner, (_, item) in owners.items()}
        time.sleep(0.6)
    raise RuntimeError("NFT pagination limit")
