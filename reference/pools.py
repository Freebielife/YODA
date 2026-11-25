"""Discover indexed trading pools by jetton master without changing the trade feed."""
from decimal import Decimal
from urllib.parse import urlencode

from assets import MASTER, fetch
from badges import raw_friendly

API = "https://api.geckoterminal.com/api/v2"
NATIVE = "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"


def collect(now, master=MASTER):
    token = raw_friendly(master)
    rows = {}
    for page in range(1, 11):
        query = urlencode({"include": "base_token,quote_token,dex", "page": page})
        result = fetch(f"/networks/ton/tokens/{master}/pools?{query}", api=API)
        included = {item["id"]: item["attributes"] for item in result.get("included", [])}
        for entry in result["data"]:
            attributes, relations = entry["attributes"], entry["relationships"]
            bases = [relations[k]["data"]["id"] for k in ("base_token", "quote_token")]
            tokens = [id_.removeprefix("ton_") for id_ in bases]
            sides = [raw_friendly(address) for address in tokens]
            if sides.count(token) != 1:
                raise ValueError("Unexpected assets in pool")
            other = 1 - sides.index(token)
            address = attributes["address"]
            dex = relations["dex"]["data"]["id"]
            reserve = attributes.get("reserve_in_usd")
            if reserve is not None and (not Decimal(reserve).is_finite() or Decimal(reserve) < 0):
                raise ValueError("Invalid liquidity")
            rows[raw_friendly(address)] = {
                "address": address,
                "token": tokens[other],
                "symbol": "GRAM (TON)" if tokens[other] == NATIVE else included[bases[other]]["symbol"],
                "dex": included.get(dex, {}).get("name", dex),
                "liquidityUsd": reserve,
            }
        if len(result["data"]) < 20:
            return {"asOf": now, "rows": list(rows.values())}
    raise RuntimeError("Pool pagination limit reached")
