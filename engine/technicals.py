#!/usr/bin/env python3
"""Deterministic technicals snapshot for a stock or crypto symbol.

This is the single source of computed technicals for the Investments research
system. The Quant worker runs this and *interprets* the output -- it never
hand-computes indicators, so the numbers are identical and auditable every run.

Usage:
    python technicals.py MU            # stock
    python technicals.py BTC           # crypto -- auto-retries BTC-USD
    python technicals.py NVDA --json   # machine-readable
    python technicals.py NVDA --period 2y

Exits non-zero with a clear message if Yahoo has no data for the symbol.
"""
import argparse
import json
import sys

import pandas as pd
import pandas_ta as ta

from fetch_ohlcv import fetch

# Crypto symbols that ALSO exist as unrelated stock tickers on Yahoo. Passed bare
# (without --crypto), Yahoo returns the *stock* and you get silently wrong data
# (e.g. "BTC" the equity at ~$32, not Bitcoin at ~$73k). Refuse these unless the
# caller is explicit. Not exhaustive -- the /research command passes --crypto for
# anything tagged Type=Crypto in Trade-Log, so this only guards manual CLI use.
AMBIGUOUS_CRYPTO = {
    "BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX", "LINK",
    "DOT", "ATOM", "NEAR", "ARB", "ZEC", "ONDO", "HYPE",
}


# Yahoo assigns numeric-suffixed symbols to some newer tokens, so the plain
# {SYM}-USD form 404s (e.g. HYPE-USD is dead; Hyperliquid lives at HYPE32196-USD).
# Map the user-facing ticker to Yahoo's actual symbol so /refresh HYPE just works.
SYMBOL_OVERRIDE = {
    "HYPE": "HYPE32196-USD",
}


def resolve(ticker: str, crypto: bool) -> str:
    """Map a user symbol to the Yahoo symbol. Explicit, no silent guessing."""
    t = ticker.upper()
    if t.endswith("-USD"):
        return t
    if t in SYMBOL_OVERRIDE:
        return SYMBOL_OVERRIDE[t]
    if crypto:
        return f"{t}-USD"
    return t


def load(ticker: str, period: str, crypto: bool = False):
    """Fetch daily OHLCV for the resolved symbol; retry -USD only if empty."""
    sym = resolve(ticker, crypto)
    df = fetch(sym, period)
    if df.empty and not sym.endswith("-USD"):
        alt = f"{sym}-USD"
        df_alt = fetch(alt, period)
        if not df_alt.empty:
            return alt, df_alt
    return sym, df


def compute(ticker: str, df: pd.DataFrame, range_lookback: int = 60) -> dict:
    close, high, low, vol = df["Close"], df["High"], df["Low"], df["Volume"]
    px = float(close.iloc[-1])

    ma20 = float(close.rolling(20).mean().iloc[-1])
    ma50 = float(close.rolling(50).mean().iloc[-1])
    ma200 = float(close.rolling(200).mean().iloc[-1]) if len(df) >= 200 else None
    rsi = float(ta.rsi(close, length=14).iloc[-1])
    macd = ta.macd(close)
    atr = float(ta.atr(high, low, close, length=14).iloc[-1])
    vol_now = float(vol.iloc[-1])
    vol_avg20 = float(vol.rolling(20).mean().iloc[-1])

    if ma200 is None:
        posture = "n/a (history < 200 bars)"
    elif ma50 > ma200:
        posture = "golden (uptrend)"
    elif ma50 < ma200:
        posture = "death (downtrend)"
    else:
        posture = "neutral"

    rsi_tag = "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral"

    # Pullback add-ladder: in an uptrend, the "next buying opportunity" is a pullback
    # to a structural support BELOW current price, never a cost-anchored guess. Build
    # the ladder deterministically from the nearest real supports: the most recent
    # swing-low shelf (10-bar low), the 20-MA (dynamic), and the 50-MA (trend). Only
    # emitted when posture is golden (uptrend); only levels strictly below price.
    support_10 = float(low.tail(10).min())
    add_ladder = []
    if ma200 is not None and ma50 > ma200:
        candidates = [
            ("recent swing low (10-bar)", support_10),
            ("20-MA (dynamic)", ma20),
            ("50-MA (trend)", ma50),
        ]
        below = sorted(
            [(label, lvl) for label, lvl in candidates if lvl < px],
            key=lambda x: -x[1],  # nearest support first
        )
        depth = ["near", "mid", "deep"]
        for i, (label, lvl) in enumerate(below):
            add_ladder.append({
                "tier": depth[i] if i < len(depth) else f"deep{i}",
                "label": label,
                "level": round(lvl, 4),
                "pct_below": round((lvl / px - 1) * 100, 2),
            })

    # SMC execution sublayer: dealing-range premium/discount (long bias).
    # Draw the current dealing range as the highest high / lowest low over a
    # lookback window (default ~3 months daily); equilibrium is the 50% mid.
    # "discount" (price below mid) is where a long looks to BUY; "premium" is
    # where it trims / avoids adding. This is the WHERE/WHEN on top of the
    # add-ladder's WHAT -- it answers "is this a good place to be adding at all?"
    # (OTE/fib bands are deliberately omitted: in any uptrend they land below the
    # invalidation stop, so they're noise, not a reachable entry.)
    n = min(len(df), range_lookback)
    rng_high = float(high.tail(n).max())
    rng_low = float(low.tail(n).min())
    span = rng_high - rng_low
    if span > 0:
        equilibrium = (rng_high + rng_low) / 2
        dealing_range = {
            "lookback_bars": n,
            "range_high": round(rng_high, 4),
            "range_low": round(rng_low, 4),
            "equilibrium": round(equilibrium, 4),
            "pct_in_range": round((px - rng_low) / span * 100, 1),  # 0=low, 100=high
            "zone": "premium" if px > equilibrium else "discount",
        }
    else:
        dealing_range = None

    return {
        "ticker": ticker,
        "as_of": str(df.index[-1].date()),
        "price": round(px, 4),
        "ma20": round(ma20, 4),
        "ma50": round(ma50, 4),
        "ma200": round(ma200, 4) if ma200 is not None else None,
        "pct_vs_ma20": round((px / ma20 - 1) * 100, 2),
        "pct_vs_ma50": round((px / ma50 - 1) * 100, 2),
        "pct_vs_ma200": round((px / ma200 - 1) * 100, 2) if ma200 else None,
        "ma_posture": posture,
        "rsi14": round(rsi, 2),
        "rsi_tag": rsi_tag,
        "macd": round(float(macd["MACD_12_26_9"].iloc[-1]), 4),
        "macd_signal": round(float(macd["MACDs_12_26_9"].iloc[-1]), 4),
        "macd_hist": round(float(macd["MACDh_12_26_9"].iloc[-1]), 4),
        "atr14": round(atr, 4),
        "stop_long_2atr": round(px - 2 * atr, 4),
        "stop_long_2atr_pct": round(-2 * atr / px * 100, 2),
        "support_10": round(support_10, 4),
        "support_20": round(float(low.tail(20).min()), 4),
        "resistance_20": round(float(high.tail(20).max()), 4),
        "support_50": round(float(low.tail(50).min()), 4),
        "resistance_50": round(float(high.tail(50).max()), 4),
        "add_ladder": add_ladder,
        "dealing_range": dealing_range,
        "volume": round(vol_now, 0),
        "volume_vs_avg20_pct": round((vol_now / vol_avg20 - 1) * 100, 2) if vol_avg20 else None,
    }


def to_markdown(s: dict) -> str:
    ma200 = f"{s['ma200']} ({s['pct_vs_ma200']:+}%)" if s["ma200"] else "n/a"
    lines = [
        f"### Technicals — {s['ticker']} (daily, as of {s['as_of']})",
        "",
        f"- **Price:** {s['price']}",
        f"- **MA posture:** {s['ma_posture']}  |  vs 20-MA {s['ma20']} ({s['pct_vs_ma20']:+}%)  |  vs 50-MA {s['ma50']} ({s['pct_vs_ma50']:+}%)  |  vs 200-MA {ma200}",
        f"- **RSI(14):** {s['rsi14']} ({s['rsi_tag']})",
        f"- **MACD(12,26,9):** {s['macd']} / signal {s['macd_signal']} / hist {s['macd_hist']}",
        f"- **ATR(14):** {s['atr14']}  →  long stop (2·ATR): {s['stop_long_2atr']} ({s['stop_long_2atr_pct']}%)",
        f"- **Support / Resistance:** 10-bar low {s['support_10']}  |  20-bar {s['support_20']} / {s['resistance_20']}  |  50-bar {s['support_50']} / {s['resistance_50']}",
        f"- **Volume:** {s['volume']:.0f} ({s['volume_vs_avg20_pct']:+}% vs 20-avg)",
    ]
    if s.get("add_ladder"):
        rungs = "  |  ".join(
            f"{r['tier']} {r['level']} ({r['pct_below']:+}%, {r['label']})"
            for r in s["add_ladder"]
        )
        lines.append(f"- **Uptrend pullback add-ladder (structural, below price):** {rungs}")
    dr = s.get("dealing_range")
    if dr:
        lines.append(
            f"- **Dealing range ({dr['lookback_bars']}-bar):** {dr['range_low']} — "
            f"eq {dr['equilibrium']} — {dr['range_high']}  |  price at **{dr['pct_in_range']}%** "
            f"of range → **{dr['zone']}** (discount = add zone, premium = don't chase)"
        )
    lines += [
        "",
        f"Source: own computation on Yahoo Finance OHLCV, as of {s['as_of']}.",
    ]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Deterministic technicals snapshot (stocks & crypto)")
    p.add_argument("ticker", help="e.g. MU, NVDA, BTC-USD, or BTC with --crypto")
    p.add_argument("--crypto", action="store_true", help="treat as crypto (appends -USD)")
    p.add_argument("--period", default="1y", help="1y,2y,5y,max (default: 1y; needs >=200 bars for 200-MA)")
    p.add_argument("--range-lookback", type=int, default=60, help="bars for the SMC dealing range (default: 60)")
    p.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = p.parse_args()

    bare = args.ticker.upper()
    if not args.crypto and not bare.endswith("-USD") and bare in AMBIGUOUS_CRYPTO:
        sys.exit(
            f"'{bare}' is ambiguous: a crypto symbol that is also a stock ticker on "
            f"Yahoo. Pass --crypto (or '{bare}-USD') for the coin; rename if you really "
            f"meant the equity."
        )

    ticker, df = load(args.ticker, args.period, args.crypto)
    if df.empty:
        sys.exit(f"No data for '{args.ticker}' (tried -USD suffix too). Check the symbol.")
    if len(df) < 50:
        sys.exit(f"Only {len(df)} bars for {ticker}; need >=50 for a meaningful snapshot.")

    snapshot = compute(ticker, df, range_lookback=args.range_lookback)
    print(json.dumps(snapshot, indent=2) if args.json else to_markdown(snapshot))


if __name__ == "__main__":
    main()
