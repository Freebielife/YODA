"""Bounded, resumable backfill of verified swaps, separate from live updates."""
import copy
import time
from urllib.parse import urlencode

import trades

YEAR = 366 * 86400


def refresh(snapshot, now, *, page_budget=4, save=None):
    """Checkpoint each complete page. Never advance a cursor on a failed page.

    Existing rows are retained and use the same swap verifier as recent trades.
    trades.asOf measures the live refresh; backfill must not advance that clock.
    """
    if not 1 <= page_budget <= 20:
        raise ValueError("Invalid history request budget")
    section = snapshot.get("trades")
    if not section or not section.get("asOf") or not section.get("since"):
        return False  # Establish recent coverage before walking into the archive.
    cutoff = max(1, now - YEAR)
    history = copy.deepcopy(snapshot.get("tradeHistory", {}))
    states = history.setdefault("byPool", {})
    for pool in trades.POOLS:
        if pool not in states:
            rows = [r for r in section["rows"] if r.get("pool") == pool]
            cursor = min((int(r["lt"]) for r in rows), default=0)
            states[pool] = {"beforeLt": str(cursor), "since": section["since"],
                            "complete": section["since"] <= cutoff}
    failures = []
    used = 0
    # Round-robin pages keep a busy pool from starving other configured pools.
    while used < page_budget:
        pending = [p for p in trades.POOLS if not states[p]["complete"] and p not in failures]
        if not pending:
            break
        for pool in pending:
            if used >= page_budget:
                break
            used += 1
            state = states[pool]
            before = int(state["beforeLt"])
            params = {"limit": 100}
            if before:
                params["before_lt"] = before
            try:
                if used > 1:
                    time.sleep(1.05)
                page = trades.fetch(f"/accounts/{pool}/events?" + urlencode(params))
                events = page["events"]
                if not isinstance(events, list):
                    raise ValueError("Malformed history page")
                cursor = int(page.get("next_from") or 0)
                if cursor < 0 or (before and cursor >= before):
                    raise ValueError("History cursor did not advance")
                if not events and cursor:
                    raise ValueError("Empty history page with continuation")
                additions = {}
                for event in events:
                    timestamp, lt = int(event["timestamp"]), int(event["lt"])
                    if timestamp <= 0 or timestamp > now or lt <= 0 or (before and lt >= before):
                        raise ValueError("Invalid historical event position")
                    if event["in_progress"]:
                        raise RuntimeError("Unfinalized event in history page")
                    if cutoff <= timestamp <= section["asOf"]:
                        for row in trades.swap_rows(event, pool):
                            additions[row["tx"]] = row
                oldest = min((int(e["timestamp"]) for e in events), default=cutoff)
                complete = not cursor or oldest <= cutoff
                next_state = {"beforeLt": str(cursor),
                              "since": cutoff if complete else min(state["since"], oldest),
                              "complete": complete, "asOf": now}
                merged = {r["tx"]: r for r in section["rows"]}
                for tx, row in additions.items():
                    if tx not in merged or pool == trades.PRIMARY:
                        merged[tx] = row
                # Publish only after the entire page and every swap were verified.
                section["rows"] = sorted(merged.values(),
                    key=lambda r: (r["time"], int(r["lt"]), r["tx"]), reverse=True)
                states[pool] = next_state
                section["since"] = max(cutoff, max(states[p]["since"] for p in trades.POOLS))
                history.update(asOf=now, targetSince=cutoff,
                               complete=all(states[p]["complete"] for p in trades.POOLS),
                               failedPools=list(failures))
                snapshot["tradeHistory"] = copy.deepcopy(history)
                snapshot["updated"] = max(now, snapshot.get("updated", 0))
                if save:
                    save(snapshot)
                print("History page saved:", pool, "rows", len(additions),
                      "coverage since", section["since"], "complete", history["complete"], flush=True)
            except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
                failures.append(pool)
                print("History page unavailable:", pool, type(exc).__name__, flush=True)
    # Failed pools remain retryable at the original cursor next run.
    history["failedPools"] = failures
    history.setdefault("asOf", now)
    history["targetSince"] = cutoff
    history["complete"] = all(states[p]["complete"] for p in trades.POOLS)
    snapshot["tradeHistory"] = history
    if save:
        save(snapshot)
    return bool(failures)
