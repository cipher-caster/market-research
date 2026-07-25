#!/usr/bin/env python3
"""Market regime gate -- is this market a place to be ADDING risk at all?

The per-asset layer (technicals.py) answers "where are the levels on this
chart". This script answers the question the system never asked during the
June 2026 crash: "is the MARKET in a state where add rungs should fire?"
Deterministic, same rules every run.

Regime rules (computed on the benchmark, default BTC-USD for crypto):

  risk_off  -- price below 200-MA, OR drawdown from 90-bar high >= 20%
  risk_on   -- price above 50-MA AND 50-MA above 200-MA (golden)
               AND drawdown from 90-bar high < 10%
  neutral   -- everything else

Gate (enforced by the README, reported here):
  risk_off -> add-ladder rungs SUSPENDED. Stops and exits still execute.
              New longs: starter size only, at the owner's explicit call.
  neutral  -> rungs need reclaim confirmation (mandatory anyway).
  risk_on  -> normal operation.

Usage:
    python regime.py                # crypto regime (BTC-USD)
    python regime.py SPY            # equities regime
    python regime.py --json
"""
import argparse
import json
import sys

import pandas_ta as ta

from fetch_ohlcv import fetch_routed

DRAWDOWN_LOOKBACK = 90
RISK_OFF_DRAWDOWN = -20.0  # % from lookback high
RISK_ON_DRAWDOWN = -10.0


def compute_regime(df) -> dict:
    close, high = df["Close"], df["High"]
    px = float(close.iloc[-1])
    ma50 = float(close.rolling(50).mean().iloc[-1])
    ma200 = float(close.rolling(200).mean().iloc[-1]) if len(df) >= 200 else None
    hi = float(high.tail(DRAWDOWN_LOOKBACK).max())
    drawdown = (px / hi - 1) * 100
    ret20 = (px / float(close.iloc[-21]) - 1) * 100 if len(df) > 21 else None
    rsi = float(ta.rsi(close, length=14).iloc[-1])

    reasons = []
    if ma200 is None:
        regime = "neutral"
        reasons.append("history < 200 bars; cannot judge trend, defaulting neutral")
    elif px < ma200:
        regime = "risk_off"
        reasons.append(f"price below 200-MA ({px:.0f} < {ma200:.0f})")
    elif drawdown <= RISK_OFF_DRAWDOWN:
        regime = "risk_off"
        reasons.append(
            f"drawdown {drawdown:.1f}% from {DRAWDOWN_LOOKBACK}-bar high (>= 20%)"
        )
    elif px > ma50 and ma50 > ma200 and drawdown > RISK_ON_DRAWDOWN:
        regime = "risk_on"
        reasons.append("price > 50-MA, golden cross, drawdown < 10%")
    else:
        regime = "neutral"
        if px < ma50:
            reasons.append(f"price below 50-MA ({px:.0f} < {ma50:.0f})")
        if drawdown <= RISK_ON_DRAWDOWN:
            reasons.append(f"drawdown {drawdown:.1f}% from {DRAWDOWN_LOOKBACK}-bar high")
        if ma200 is not None and ma50 <= ma200:
            reasons.append("50-MA below 200-MA (death cross)")
        if not reasons:
            reasons.append("mixed signals")

    return {
        "as_of": str(df.index[-1].date()),
        "price": round(px, 2),
        "ma50": round(ma50, 2),
        "ma200": round(ma200, 2) if ma200 is not None else None,
        "drawdown_90bar_pct": round(drawdown, 1),
        "ret20_pct": round(ret20, 1) if ret20 is not None else None,
        "rsi14": round(rsi, 1),
        "regime": regime,
        "reasons": reasons,
    }


GATE = {
    "risk_off": "add rungs SUSPENDED; stops/exits still execute; new longs starter-size only at the owner's explicit call",
    "neutral": "rungs fire only on reclaim confirmation (touch + daily close back above + MACD hist rising)",
    "risk_on": "normal operation",
}


def to_markdown(symbol: str, r: dict, source: str = "Yahoo Finance") -> str:
    ma200 = f"{r['ma200']}" if r["ma200"] is not None else "n/a"
    return "\n".join([
        f"### Market regime — {symbol} (as of {r['as_of']})",
        "",
        f"- **Regime: {r['regime'].upper()}** — {'; '.join(r['reasons'])}",
        f"- **Gate:** {GATE[r['regime']]}",
        f"- Price {r['price']}  |  50-MA {r['ma50']}  |  200-MA {ma200}  |  "
        f"drawdown {r['drawdown_90bar_pct']}% from 90-bar high  |  "
        f"20-bar return {r['ret20_pct']}%  |  RSI {r['rsi14']}",
        "",
        f"Source: own computation on {source} OHLCV ({symbol}), as of {r['as_of']}.",
    ])


def main() -> None:
    p = argparse.ArgumentParser(description="Market regime gate (default benchmark: BTC-USD)")
    p.add_argument("symbol", nargs="?", default="BTC-USD",
                   help="benchmark symbol (default BTC-USD; use SPY for equities)")
    p.add_argument("--period", default="2y", help="needs >=200 bars (default: 2y)")
    p.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = p.parse_args()

    symbol = args.symbol.upper()
    # -USD benchmark (default BTC-USD) => exchange, matching MCP; SPY etc. => Yahoo.
    df, source = fetch_routed(symbol, args.period, crypto=symbol.endswith("-USD"))
    if df.empty:
        sys.exit(f"No data for '{args.symbol}'. Crypto needs -USD suffix.")
    if len(df) < 60:
        sys.exit(f"Only {len(df)} bars for {args.symbol}; need >=60.")

    r = compute_regime(df)
    r["symbol"] = symbol
    r["gate"] = GATE[r["regime"]]
    print(json.dumps(r, indent=2) if args.json else to_markdown(symbol, r, source=source))


if __name__ == "__main__":
    main()
