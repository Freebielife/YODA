"""Token-independent incremental TON Observatory data refresh.

Reuse the same code for all generated tokens. Never fabricate absent burns,
NFT ownership, vesting or native-chain staking. Each completed section is
committed atomically before the next network operation so a later timeout does
not silently delete valid prior data.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import assets
import service_registry
import observatory
import pools
import trades
import trade_history
import badges
import domains
from scripts.project_runtime import read_project, check_identity, decorate_snapshot

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/snapshot.json"
UNINDEXED = {"burns", "zeroBurns", "domains", "fragmentNumbers"}


def save(snapshot: dict) -> None:
    project = read_project(ROOT)
    check_identity(snapshot, project)
    decorate_snapshot(snapshot, project)
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    temp = SNAPSHOT.with_suffix(".tmp")
    temp.write_text(json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"),
                               allow_nan=False), encoding="utf-8")
    os.replace(temp, SNAPSHOT)


def refresh() -> dict:
    now = int(time.time())
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if snap.get("schema") != 1 or snap.get("token") != assets.MASTER:
        raise ValueError("Generated token identity or snapshot schema mismatch")
    check_identity(snap, read_project(ROOT))
    errors = set(snap.get("errors", ()))
    errors.update(key for key in UNINDEXED if key not in snap)

    def stage(key, read, *, interval=0):
        prior = snap.get(key, {})
        snap.setdefault("refreshStatus", {})[key] = {"attemptedAt": now, "ok": None}
        if prior and now - int(prior.get("asOf", 0)) < interval:
            return
        try:
            result = read(prior)
            if not isinstance(result, dict) or int(result.get("asOf", 0)) <= 0:
                raise ValueError(key + " response must have a verified asOf")
            if key == "holders" and not result.get("holders"):
                raise ValueError("Empty holder snapshot")
            if key == "identity" and not any(
                rec.get("checked") for rec in result.get("byWallet", {}).values()):
                raise ValueError("No verified account identities yet")
            snap[key] = result
            if key == "badges" and result.get("failed"):
                errors.add(key)
            else:
                errors.discard(key)
            snap["updated"] = int(time.time())
            snap["errors"] = sorted(errors)
            snap["refreshStatus"][key].update(ok=key not in errors, lastSuccess=result["asOf"])
            save(snap)
            print(key, "SAVED", flush=True)
        except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
            errors.add(key)
            snap["refreshStatus"][key].update(ok=False, error=type(exc).__name__, lastSuccess=prior.get("asOf"))
            snap["errors"] = sorted(errors)
            print(key, "UNAVAILABLE", type(exc).__name__, str(exc)[:200], flush=True)

    stage("holders", lambda _: {**assets.holders(), "asOf": now})
    if service_registry.update(snap, now, observatory.KNOWN_SERVICES):
        errors.add("serviceRegistry")
    else:
        errors.discard("serviceRegistry")
    save(snap)
    def collect_burns(previous):
        since = max(1, int(previous.get("asOf", now - 7 * 86400)) - 3600)
        rows, covered = assets.burns(previous.get("rows", []), since)
        return {"asOf": now, "since": min(int(previous.get("since", covered)), covered),
                "rows": rows}

    stage("burns", collect_burns, interval=1800)
    stage("zeroBurns", lambda previous: observatory.zero_burns(previous, now),
          interval=6*3600)
    stage("trades", lambda previous: trades.collect(previous, now - trade_history.YEAR,
                                                      now, max_pages=35))
    if trade_history.refresh(snap, now, save=save):
        errors.add("tradeHistory")
    else:
        errors.discard("tradeHistory")
    snap["errors"] = sorted(errors)
    save(snap)
    stage("rates", lambda _: {"asOf": now, "rows": trades.rates()},
          interval=6*3600)
    stage("pools", lambda _: pools.collect(now), interval=24*3600)
    # Deep account metadata is verified slowly across many refreshes; a large
    # balance alone must never be used to assert a named service.
    stage("identity", lambda _: observatory.identity(snap, now, budget=6, pace=0.2))
    stage("badges", lambda previous: {**badges.refresh(previous, now), "asOf": now},
          interval=6*3600)
    stage("domains", lambda _: domains.enrich(snap, now), interval=1800)
    stage("fragmentNumbers", lambda _: badges.refresh_fragment_numbers(snap, now),
          interval=1800)
    snap["errors"] = sorted(errors)
    if any(snap.get(key) for key in ("holders", "trades", "rates", "pools")):
        snap["updated"] = int(time.time())
    save(snap)
    print("Refresh finished; incomplete:", snap["errors"], flush=True)
    return snap


if __name__ == "__main__":
    refresh()
