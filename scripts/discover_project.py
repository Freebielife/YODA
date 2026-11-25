"""Create a project config from a mainnet jetton; never invent missing metadata.

TonAPI verifies token identity and swap evidence. GeckoTerminal discovers
candidate native TON pools. Unsupported or unverified pairs stop generation.
"""
import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urlencode

from scripts.http_json import fetch
from scripts.project_runtime import VERSION, canonical_address
from scripts.project_branding import prepare as prepare_branding
from scripts.project_description import from_metadata, validate as validate_description

GECKO = "https://api.geckoterminal.com/api/v2"
NATIVE = "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"
DEXES = {"ston-fi": "stonfi", "stonfi": "stonfi", "stonfi-v2": "stonfi", "dedust": "dedust"}


def discover(master, owner, repo, *, read=fetch):
    raw = canonical_address(master)
    # Emit one stable friendly encoding for all generated consumers.
    import base64, binascii
    body = bytes([0x11, 0]) + bytes.fromhex(raw[2:])
    master = base64.urlsafe_b64encode(body + binascii.crc_hqx(body, 0).to_bytes(2, "big")).decode()
    token = read("/jettons/" + master)
    meta = token["metadata"]
    if canonical_address(meta["address"]) != raw:
        raise ValueError("Token metadata address mismatch")
    decimals = int(meta["decimals"])
    symbol, name = meta["symbol"], meta["name"]
    if not 0 <= decimals <= 18 or not re.fullmatch(r"[A-Z0-9_]{2,12}", symbol):
        raise ValueError("Unsupported token metadata; use an explicit reviewed project config")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 -]{0,45}", name):
        raise ValueError("Token display name needs an explicit reviewed project config")
    candidates = []
    sources = ["https://tonapi.io/v2/jettons/" + master]
    for page in range(1, 11):
        path = f"/networks/ton/tokens/{master}/pools?" + urlencode({"page": page})
        response = read(path, api=GECKO)
        sources.append(GECKO + path)
        for pool in response["data"]:
            rel, attrs = pool["relationships"], pool["attributes"]
            sides = [canonical_address(rel[k]["data"]["id"].removeprefix("ton_")) for k in ("base_token", "quote_token")]
            dex = DEXES.get(rel["dex"]["data"]["id"])
            if sorted(sides) != sorted([raw, canonical_address(NATIVE)]) or not dex:
                continue
            address = attrs["address"]
            canonical_address(address)
            events = read(f"/accounts/{address}/events?limit=100")
            proven = False
            for event in events["events"]:
                if event.get("in_progress"):
                    continue
                for action in event.get("actions", []):
                    if action.get("type") != "JettonSwap" or action.get("status") != "ok":
                        continue
                    swap = action["JettonSwap"]
                    incoming = (swap.get("jetton_master_in") or {}).get("address")
                    outgoing = (swap.get("jetton_master_out") or {}).get("address")
                    buy = outgoing and canonical_address(outgoing) == raw and incoming is None and int(swap.get("ton_in", 0)) > 0
                    sell = incoming and canonical_address(incoming) == raw and outgoing is None and int(swap.get("ton_out", 0)) > 0
                    if swap.get("dex") == dex and (buy or sell):
                        proven = True
            if proven:
                from decimal import Decimal
                liquidity = Decimal(attrs.get("reserve_in_usd") or "0")
                if not liquidity.is_finite() or liquidity < 0:
                    raise ValueError("Invalid candidate liquidity")
                candidates.append((liquidity, {"address": address, "dex": dex, "quote": "TON",
                    "evidence": "https://tonapi.io/v2/accounts/" + address + "/events?limit=100"}))
        if len(response["data"]) < 20:
            break
    else:
        raise ValueError("Pool discovery pagination limit; use reviewed configuration")
    if not candidates:
        raise ValueError("No supported TON pair with verified successful swaps; no site generated")
    unique = {}
    for liquidity, pool in sorted(candidates, key=lambda item: (-item[0], item[1]["address"])):
        unique.setdefault(canonical_address(pool["address"]), pool)
    pools = list(unique.values())
    cfg = {"slug": re.sub(r"[^a-z0-9-]", "-", repo.lower()), "name": name, "symbol": symbol,
            "master": master, "decimals": decimals, "github": {"owner": owner, "repo": repo},
            "pools": pools, "primary_pool": pools[0]["address"], "links": {}, "services": {},
            "_metadata_image": meta.get("image"), "engine_version": VERSION, "discovery": {"checkedAt": int(time.time()), "sources": sources,
                "primaryPoolPolicy": "largest indexed USD liquidity among swap-verified supported TON pools"}}
    description = from_metadata(meta, sources[0])
    if description:
        cfg["project_description"] = description
    return cfg


def main():
    parser = argparse.ArgumentParser(description="Create a TON observatory from its token contract")
    parser.add_argument("--token", required=True)
    parser.add_argument("--github", required=True, help="owner/repository for snapshot updates")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--prepare-only", action="store_true", help="Generate sources without live collection/build")
    parser.add_argument("--website", help="Official project website for fallback logo/channel discovery")
    parser.add_argument("--channel", help="Project channel, https://t.me/channel")
    parser.add_argument("--description-file", type=Path,
                        help="Reviewed description JSON: text, origin, sources, checked_at")
    flags = parser.add_mutually_exclusive_group(required=True)
    flags.add_argument("--flag-key", help="Explicitly confirmed key in the bundled flag catalogue")
    flags.add_argument("--flag-file", type=Path, help="User-provided custom emoji image, WebP/GIF")
    flags.add_argument("--flag-emoji", help="Explicitly chosen Unicode emoji")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9_.-]{2,31}", args.github):
        parser.error("Expected owner/repository")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output must be empty")
    try:
        cfg = discover(args.token, *args.github.split("/"))
        if args.description_file:
            description = json.loads(args.description_file.read_text())
            validate_description(description)
            if description is None:
                raise ValueError("Description file must contain an object")
            cfg["project_description"] = description
        import tempfile
        from scripts.scaffold_observatory import scaffold
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            prepare_branding(cfg, directory, metadata_image=cfg.pop("_metadata_image", None),
                             website=args.website, channel=args.channel, flag_key=args.flag_key,
                             flag_file=args.flag_file, flag_emoji=args.flag_emoji)
            config = directory / "project.json"
            config.write_text(json.dumps(cfg, ensure_ascii=False))
            scaffold(config, args.output)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        parser.error(str(error))
    if not args.prepare_only:
        import subprocess, sys
        for command in ([sys.executable, "-m", "scripts.refresh_observatory"],
                        [sys.executable, "build.py"], [sys.executable, "verify.py"]):
            subprocess.run(command, cwd=args.output, check=True)
        print("Created standalone HTML:", args.output / "index.html")
        print("Inspect section freshness and incomplete-source warnings before deployment.")
    else:
        print("Created", args.output, "Run refresh, build and verify before publishing.")


if __name__ == "__main__":
    main()
