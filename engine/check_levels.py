#!/usr/bin/env python3
"""Watchlist level-watch sweep -- alert-driven monitoring, not calendar-driven.

Reads the Watchlist table in Trade-Log.md, pulls live prices, and reports ONLY
the rows where a defined level has triggered (or is within 3%):

  STOP BREACHED / STOP NEAR     price at/under the stop (Holding rows)
  IN ENTRY ZONE                 price inside/below the entry range
  TARGET HIT / TARGET NEAR      price at/over the target

Also prints the market regime (regime.py) at the top, because a rung touched
during a market-wide crash is not the same signal as one touched in a calm
uptrend (see ZEC, June 2026).

Rows with TBD levels are listed once at the end as "no levels". Archive rows
are ignored. Exited rows are checked for entry-zone (re-entry) only.

Usage:
    python check_levels.py            # human output
    python check_levels.py --quiet    # print only if something triggered (for cron)

Exit code: 0 = ran clean (triggers or not), 1 = error. A trigger means "run
/refresh on that ticker", not "trade mechanically".
"""
import argparse
import re
import sys

from config import TRADE_LOG
from fetch_ohlcv import fetch
from regime import compute_regime, GATE
from technicals import resolve

NEAR_PCT = 3.0  # "near" = within 3% of the level


def parse_number(cell: str):
    """'443' -> 443.0; '504-471' -> (471.0, 504.0); 'TBD'/'' -> None."""
    cell = cell.strip().replace(",", "")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", cell)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        return (min(a, b), max(a, b))
    m = re.fullmatch(r"\d+(?:\.\d+)?", cell)
    return float(cell) if m else None


def parse_watchlist(text: str) -> list[dict]:
    """Rows of the active Watchlist table (stops at the next ## section)."""
    section = re.split(r"^## ", text.split("## Watchlist / Thesis", 1)[1],
                       flags=re.M)[0]
    rows = []
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 10 or cols[0] in ("Date", "") or set(cols[0]) <= {"-"}:
            continue
        m = re.search(r"\[\[(\w+)\]\]", cols[1])
        if not m:
            continue
        rows.append({
            "ticker": m.group(1),
            "type": cols[2],
            "entry": parse_number(cols[5]),
            "target": parse_number(cols[6]),
            "stop": parse_number(cols[7]),
            "status": cols[9],
        })
    return rows


def check_row(row: dict) -> list[str] | None:
    """Trigger strings for one row, [] if levels exist but nothing fired,
    None if the row has no usable levels."""
    entry, target, stop = row["entry"], row["target"], row["stop"]
    if entry is None and target is None and stop is None:
        return None

    sym = resolve(row["ticker"], crypto=row["type"].lower() == "crypto")
    df = fetch(sym, "1mo")
    if df.empty:
        return [f"DATA ERROR — no Yahoo data for {sym}"]
    px = float(df["Close"].iloc[-1])
    lo = float(df["Low"].iloc[-1])

    holding = row["status"].lower() == "holding"
    exited = row["status"].lower() == "exited"
    fired = []

    if stop is not None and holding:
        s = stop if isinstance(stop, float) else stop[0]
        if px <= s or lo <= s:
            fired.append(f"STOP BREACHED — price {px:.2f} (low {lo:.2f}) vs stop {s}")
        elif px <= s * (1 + NEAR_PCT / 100):
            fired.append(f"STOP NEAR — price {px:.2f} within {NEAR_PCT}% of stop {s}")

    if entry is not None and not holding:
        e_lo, e_hi = entry if isinstance(entry, tuple) else (entry, entry)
        if px <= e_hi:
            tag = "re-entry" if exited else "entry"
            where = "inside" if px >= e_lo else "BELOW"
            fired.append(f"IN {tag.upper()} ZONE — price {px:.2f} {where} {e_lo}-{e_hi}"
                         + (" (check why it overshot)" if px < e_lo else ""))

    if target is not None and holding:
        t = target if isinstance(target, float) else target[1]
        if px >= t:
            fired.append(f"TARGET HIT — price {px:.2f} vs target {t}")
        elif px >= t * (1 - NEAR_PCT / 100):
            fired.append(f"TARGET NEAR — price {px:.2f} within {NEAR_PCT}% of target {t}")

    return fired


def main() -> None:
    p = argparse.ArgumentParser(description="Watchlist level-watch sweep")
    p.add_argument("--quiet", action="store_true",
                   help="print nothing unless a level triggered (cron mode)")
    args = p.parse_args()

    rows = parse_watchlist(TRADE_LOG.read_text())
    if not rows:
        # An empty watchlist is a valid state (fresh Trade-Log) — nothing to watch.
        if not args.quiet:
            print("Watchlist is empty — nothing to watch.")
        return

    has_crypto = any(r["type"].lower() == "crypto" for r in rows)
    has_stock = any(r["type"].lower() == "stock" for r in rows)

    triggers, no_levels = [], []
    for row in rows:
        fired = check_row(row)
        if fired is None:
            no_levels.append(f"{row['ticker']} ({row['status']})")
        else:
            triggers += [f"**{row['ticker']}** ({row['status']}): {t}" for t in fired]

    if args.quiet and not triggers:
        return

    lines = ["### Level-watch sweep", ""]
    for bench, wanted in (("BTC-USD", has_crypto), ("SPY", has_stock)):
        if not wanted:
            continue
        bdf = fetch(bench, "2y")
        if bdf.empty:
            lines.append(f"- Regime ({bench}): DATA ERROR")
            continue
        r = compute_regime(bdf)
        lines.append(f"- **Regime ({bench}): {r['regime'].upper()}** — "
                     f"{'; '.join(r['reasons'])}. Gate: {GATE[r['regime']]}")
    lines.append("")

    if triggers:
        lines.append("**Triggers (run /refresh on these, don't trade mechanically):**")
        lines += [f"- {t}" for t in triggers]
    else:
        lines.append("No levels triggered.")
    if no_levels:
        lines += ["", f"No levels defined (skipped): {', '.join(no_levels)}"]

    print("\n".join(lines))


if __name__ == "__main__":
    main()
