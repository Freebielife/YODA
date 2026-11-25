"""Build a static LUDOMAN snapshot. Each source keeps its last good result on failure."""
import json
import sys
import time
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import assets
import service_registry
import badges
import domains
import observatory
import pools
import trades
import trade_history

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "snapshot.json"
YEAR = 366 * 86400
PROJECT_DATA_INTERVAL = 86400


def save(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False))
    temporary.replace(path)


def holder_ranks(section):
    return {row["wallet"]: rank for rank, row in enumerate(section.get("holders", [])[:20], 1)}


def seller_ranks(section):
    end = section.get("asOf", 0)
    rows = section.get("rows", [])
    previous = {}
    for days in (1, 7, 30):
        totals = defaultdict(Decimal)
        for row in rows:
            if row["kind"] == "sell" and end - days * 86400 < row["time"] <= end:
                totals[row["wallet"]] += Decimal(row["ludoman"])
        ordered = sorted(totals, key=lambda wallet: (-totals[wallet], wallet))
        previous[str(days)] = {wallet: rank for rank, wallet in enumerate(ordered[:20], 1)}
    return previous


def refresh():
    now = int(time.time())
    snapshot = json.loads(DATA.read_text()) if DATA.exists() else {"schema": 1, "token": assets.MASTER}
    errors = []
    project_updated = False
    for key, read in (("pools", pools.collect), ("vesting", observatory.vesting), ("staking", observatory.staking)):
        if now - snapshot.get(key, {}).get("asOf", 0) >= PROJECT_DATA_INTERVAL:
            try:
                snapshot[key] = read(now)
                project_updated = True
            except Exception as error:
                errors.append(key)
                print(f"{key} FAILED: {error}", flush=True)
    core_error_count = len(errors)
    for key in ("holders", "burns", "trades"):
        try:
            old = snapshot.get(key, {})
            if key == "holders":
                result = assets.holders()
                if not result.get("holders") or not result.get("totalSupply"):
                    raise ValueError("missing token balances")
                section = {**result, "asOf": now}
            elif key == "trades":
                cutoff = now - YEAR
                previous = old if old.get("since", cutoff) <= cutoff else {}
                section = trades.collect(previous, cutoff, now)
            else:
                start_at = max(1, old["asOf"] - 3600) if old.get("since") == 1 else 1
                rows, _ = assets.burns(old.get("rows", []), start_at)
                section = {"rows": rows, "since": 1, "asOf": now}
            if key == "holders":
                section["previousRanks"] = holder_ranks(old)
            elif key == "trades":
                section["previousRanks"] = seller_ranks(old)
            snapshot[key] = section
            print(key, "OK", len(section.get("rows", section.get("holders", []))), flush=True)
        except Exception as error:
            errors.append(key)
            print(key, "FAILED:", error, file=sys.stderr, flush=True)
    core_updated = len(errors) - core_error_count < 3
    if trade_history.refresh(snapshot, now, save=lambda value: save(DATA, value)):
        errors.append("tradeHistory")
    if service_registry.update(snapshot, now, observatory.KNOWN_SERVICES):
        errors.append("serviceRegistry")
    if core_updated:
        try:
            snapshot["domains"] = domains.enrich(snapshot, now)
        except Exception as error:
            errors.append("domains")
            print("domains FAILED:", error, file=sys.stderr, flush=True)
        try:
            snapshot["rates"] = {"asOf": now, "rows": trades.rates()}
        except Exception as error:
            errors.append("rates")
            print("rates FAILED:", error, file=sys.stderr, flush=True)
        snapshot["badges"] = badges.refresh(snapshot.get("badges", {}), now)
        if snapshot["badges"]["failed"]:
            errors.append("badges")
        try:
            snapshot["zeroBurns"] = observatory.zero_burns(snapshot.get("zeroBurns", {}), now)
        except Exception as error:
            errors.append("zeroBurns")
            print("Zero-address burns:", error, flush=True)
        snapshot["fragmentNumbers"] = badges.refresh_fragment_numbers(snapshot, now)
        snapshot["identity"] = observatory.identity(snapshot, now)
    if core_updated or (project_updated and DATA.exists()):
        snapshot.update(schema=1, token=assets.MASTER, updated=now, errors=errors)
        DATA.parent.mkdir(exist_ok=True)
        save(DATA, snapshot)
    return bool(errors)


if __name__ == "__main__":
    sys.exit(refresh())
