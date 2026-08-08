#!/usr/bin/env python3
"""Watchlist level-watch sweep -- alert-driven monitoring, not calendar-driven.

Reads the calls table in Watchlist.md, pulls live prices, and reports ONLY
the rows where a defined level has triggered (or is within 3%):

  STOP BREACHED / STOP NEAR     price at/under the invalidation level (Active rows)
  STOP BREACHED INTRA-PERIOD    a recent daily low pierced the stop, price recovered
  IN ENTRY ZONE                 price inside/below the entry range
  TARGET HIT / TARGET NEAR      price at/over the target
  TREND KILL LINE IN PLAY       last close held the 50-MA, price is now under it
  TREND KILL PRINTED            a daily close crossed below the 50-MA

The trend-kill checks exist because the Watchlist's levels are static numbers
while the most common kill criterion in this system ("a daily close below the
50-MA") is a MOVING line no static level can express -- ZEC's kill line came
into play on 2026-07-28 with nothing in the sweep able to see it.

Also prints the market regime (regime.py) at the top, because a rung touched
during a market-wide crash is not the same signal as one touched in a calm
uptrend (see ZEC, June 2026).

Rows with TBD levels are listed once at the end as "no levels". Archive rows
are ignored. Resolved/Invalidated rows are checked for entry-zone (re-entry) only.

Usage:
    python check_levels.py            # human output
    python check_levels.py --quiet    # print only if something triggered (for cron)

Exit code: 0 = ran clean (triggers or not), 1 = error. A trigger means "run
/refresh on that ticker", not "trade mechanically".
"""
import argparse
import re

import pandas as pd

import marketcap
from config import WATCHLIST
from fetch_ohlcv import fetch_routed
from regime import GATE, compute_regime

NEAR_PCT = 3.0  # "near" = within 3% of the level
STOP_LOOKBACK = 5  # bars to scan for a pierced stop: the sweep runs twice daily
                   # but the machine can be off for days, so a stop that gapped
                   # through intraday and recovered must still be caught (see ZEC)
TREND_MA = 50  # the moving line most kill criteria key off ("daily close below the 50-MA")
HISTORY = "6mo"  # enough bars for the 50-MA with margin; also covers STOP_LOOKBACK


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
    """Rows of the calls table (stops at the next ## section)."""
    if "## Calls" not in text:
        return []
    section = re.split(r"^## ", text.split("## Calls", 1)[1], flags=re.M)[0]
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
            "call": cols[10] if len(cols) > 10 else "",
        })
    return rows


def live_price(row: dict):
    """(close, low, df) for a row's symbol, or None on a data error.

    Routes by the row's Type: crypto -> exchange, stock -> Yahoo. low is the min
    Low over the last STOP_LOOKBACK bars, not just the latest, so a stop gapped
    through on a day the machine was off is not missed. The frame comes back too,
    so the trend-line check reuses it instead of refetching.
    """
    df, _ = fetch_routed(row["ticker"], HISTORY, crypto=row["type"].lower() == "crypto")
    if df.empty:
        return None
    return float(df["Close"].iloc[-1]), float(df["Low"].iloc[-STOP_LOOKBACK:].min()), df


def trend_line(df) -> dict | None:
    """50-MA kill-line state, or None if history is too short to compute it.

    Kill criteria read on the CLOSE, so the live price crossing the line is not
    the event -- the daily close is. The final bar of a daily frame is still
    forming, so "last close" is the bar before it. Two transitions are worth an
    alert; a call that has simply been below the line for weeks is not one, and
    stays silent (it is already priced into the standing verdict).
    """
    close = df["Close"]
    if len(close) < TREND_MA + 2:
        return None
    ma = close.rolling(TREND_MA).mean()
    live, ma_now = float(close.iloc[-1]), float(ma.iloc[-1])
    last_close, last_ma = float(close.iloc[-2]), float(ma.iloc[-2])
    state: dict[str, float | str | None] = {
        "ma": ma_now, "last_close": last_close, "alert": None,
    }

    # A break that already printed. Scan back over the lookback rather than only
    # the last bar: the machine can be off for days and the cross must still surface.
    for i in range(-2, -2 - STOP_LOOKBACK, -1):
        if i - 1 < -len(close) or pd.isna(ma.iloc[i - 1]):
            break
        c, m, pc, pm = (float(close.iloc[i]), float(ma.iloc[i]),
                        float(close.iloc[i - 1]), float(ma.iloc[i - 1]))
        if c < m and pc >= pm:
            state["alert"] = (f"TREND KILL PRINTED — {df.index[i].date()} close {c:.2f} "
                              f"crossed below the {TREND_MA}-MA {m:.2f}")
            return state

    # Each close is judged against the MA as of its OWN bar: the line moves
    # overnight, and testing yesterday's close against today's MA suppresses the
    # alert whenever the MA rises past a close that actually held it (caught on
    # SOL 2026-07-28, which held by 0.03 and would have gone silent).
    if last_close >= last_ma and live < ma_now:
        state["alert"] = (f"TREND KILL LINE IN PLAY — price {live:.2f} is under the "
                          f"{TREND_MA}-MA {ma_now:.2f}; last close {last_close:.2f} held it "
                          f"(vs {last_ma:.2f} then), so tonight's close decides")
    return state


def check_row(row: dict, px: float, lo: float) -> list[str] | None:
    """Trigger strings for one row, [] if levels exist but nothing fired,
    None if the row has no usable levels. lo is the min low over the lookback
    window, so a stop pierced intra-period still fires even after a recovery."""
    entry, target, stop = row["entry"], row["target"], row["stop"]
    if entry is None and target is None and stop is None:
        return None

    active = row["status"].lower() == "active"
    fired = []

    if stop is not None and active:
        s = stop if isinstance(stop, float) else stop[0]
        if px <= s:  # current breach takes precedence over an intra-period pierce
            fired.append(f"STOP BREACHED — price {px:.2f} (low {lo:.2f}) vs stop {s}")
        elif lo <= s:
            fired.append(f"STOP BREACHED INTRA-PERIOD — low {lo:.2f} pierced stop {s}, "
                         f"price recovered to {px:.2f}")
        elif px <= s * (1 + NEAR_PCT / 100):
            fired.append(f"STOP NEAR — price {px:.2f} within {NEAR_PCT}% of stop {s}")

    if entry is not None:
        e_lo, e_hi = entry if isinstance(entry, tuple) else (entry, entry)
        if px <= e_hi:
            tag = "entry" if active else "re-entry"
            where = "inside" if px >= e_lo else "BELOW"
            fired.append(f"IN {tag.upper()} ZONE — price {px:.2f} {where} {e_lo}-{e_hi}"
                         + (" (check why it overshot)" if px < e_lo else ""))

    if target is not None and active:
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

    rows = parse_watchlist(WATCHLIST.read_text())
    if not rows:
        # An empty watchlist is a valid state (fresh Watchlist) — nothing to watch.
        if not args.quiet:
            print("Watchlist is empty — nothing to watch.")
        return

    has_crypto = any(r["type"].lower() == "crypto" for r in rows)
    has_stock = any(r["type"].lower() == "stock" for r in rows)

    triggers, no_levels = [], []
    table: list[tuple[dict, float | None, dict | None]] = []
    for row in rows:
        pxlo = live_price(row)
        if pxlo is None:
            triggers.append(f"**{row['ticker']}** ({row['status']}): DATA ERROR — no price data")
            table.append((row, None, None))
            continue
        px, lo, df = pxlo
        trend = trend_line(df) if row["status"].lower() == "active" else None
        table.append((row, px, trend))
        fired = check_row(row, px, lo)
        if fired is None:
            no_levels.append(f"{row['ticker']} ({row['status']})")
        else:
            triggers += [f"**{row['ticker']}** ({row['status']}): {t}" for t in fired]
        if trend and trend["alert"]:
            triggers.append(f"**{row['ticker']}** ({row['status']}): {trend['alert']}")

    if args.quiet and not triggers:
        return

    lines = ["### Level-watch sweep", ""]
    for bench, wanted in (("BTC-USD", has_crypto), ("SPY", has_stock)):
        if not wanted:
            continue
        bdf, bsrc = fetch_routed(bench, "2y", crypto=bench.endswith("-USD"))
        if bdf.empty:
            lines.append(f"- Regime ({bench}): DATA ERROR")
            continue
        r = compute_regime(bdf)
        lines.append(f"- **Regime ({bench} via {bsrc}): {r['regime'].upper()}** — "
                     f"{'; '.join(r['reasons'])}. Gate: {GATE[r['regime']]}")
    if has_crypto:
        # Context under the crypto regime line: the gate reads BTC alone, which
        # can hold while the tail bleeds. Gates nothing (see marketcap.py).
        lines.append(marketcap.summary_line(marketcap.collect()))
    lines.append("")

    if triggers:
        lines.append("**Triggers (run /refresh on these, don't trade mechanically):**")
        lines += [f"- {t}" for t in triggers]
    else:
        lines.append("No levels triggered.")
    if no_levels:
        lines += ["", f"No levels defined (skipped): {', '.join(no_levels)}"]

    def lvl(px, level, hi=False):
        """'443 (-8.2%)' — signed % distance from price to the level."""
        if level is None or px is None:
            return "—"
        v = (level[1] if hi else level[0]) if isinstance(level, tuple) else level
        txt = f"{level[0]:g}-{level[1]:g}" if isinstance(level, tuple) else f"{v:g}"
        return f"{txt} ({(v / px - 1) * 100:+.1f}%)"

    lines += ["", "**All calls:**", "",
              f"| Ticker | Call | Status | Price | Entry | Invalidation | Target | {TREND_MA}-MA |",
              "|---|---|---|---|---|---|---|---|"]
    for row, px, trend in table:
        lines.append(
            f"| {row['ticker']} | {row['call'] or '—'} | {row['status']} | "
            f"{px:g} | {lvl(px, row['entry'])} | {lvl(px, row['stop'])} | "
            f"{lvl(px, row['target'], hi=True)} | {lvl(px, trend['ma']) if trend else '—'} |"
            if px is not None else
            f"| {row['ticker']} | {row['call'] or '—'} | {row['status']} | "
            f"DATA ERROR | — | — | — | — |")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
