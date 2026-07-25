#!/usr/bin/env python3
"""Routed OHLCV for the Investments research system: crypto from the exchange,
stocks from Yahoo Finance.

Dumb data layer: this ONLY pulls raw OHLCV. Indicator computation
(RSI/MACD/ATR/MA posture) is done by the Quant worker in pandas -- keep this
script free of analysis so the numbers stay auditable.

Two entry points:
  fetch(ticker, period)                 -- raw Yahoo OHLCV (stocks; also the
                                           crypto last-resort fallback)
  fetch_routed(ticker, period, crypto)  -> (df, source) -- the ONE routed path
                                           the CLI, cron, and MCP all share:
                                           crypto -> exchange (OKX/Bybit/Binance
                                           via exchange_ohlcv), Yahoo {BASE}-USD
                                           only if every venue fails; stocks ->
                                           Yahoo. `source` names the real venue.

Usage:
    python fetch_ohlcv.py AAPL
    python fetch_ohlcv.py BTC-USD --period 2y
    python fetch_ohlcv.py NVDA --period 60d --interval 1h   # intraday: <=60d
    python fetch_ohlcv.py MU --stdout                       # raw CSV instead of a summary

Notes:
  - Crypto needs the -USD suffix: BTC-USD, ETH-USD, SOL-USD.
  - Intraday intervals (1h/15m/1m) only return ~60 days from Yahoo; daily/
    weekly go back years. Swing/position work uses 1d, which is the default.
"""
import argparse
import sys

import pandas as pd

from exchange_ohlcv import base_ticker, fetch_crypto

try:
    import yfinance as yf
except ImportError:
    sys.exit('yfinance not installed. Run: pip install -e ".[dev]"')


# Yahoo assigns numeric-suffixed symbols to some newer tokens, so the plain
# {SYM}-USD form 404s (e.g. HYPE-USD is dead; Hyperliquid lives at HYPE32196-USD).
# Map the user-facing ticker to Yahoo's actual symbol so the crypto fallback (and
# technicals.resolve) hit a live symbol. Lives here, the Yahoo layer, so the
# router can resolve the fallback without importing technicals (no import cycle).
SYMBOL_OVERRIDE = {
    "HYPE": "HYPE32196-USD",
}


def fetch(ticker: str, period: str, interval: str = "1d"):
    """Return an OHLCV DataFrame, or an empty DataFrame if Yahoo has no data.

    Does not exit -- callers decide how to handle empty (the CLI errors out;
    technicals.py retries with a -USD suffix). Keeps this importable and reusable.
    """
    df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
    if df.empty:
        return df
    df = df[["Open", "High", "Low", "Close", "Volume"]].round(8)
    df.index.name = "Date"
    return df


def fetch_routed(ticker: str, period: str, crypto: bool) -> tuple[pd.DataFrame, str]:
    """Routed daily OHLCV + the source venue name.

    Crypto -> exchange (OKX -> Bybit -> Binance via exchange_ohlcv); if every
    venue is empty, fall back to Yahoo {BASE}-USD. Stocks -> Yahoo. This is the
    single data path the CLI, cron sweep, and MCP tools share, so their numbers
    and source stamps agree. `source` is the venue ("OKX"/"Bybit"/"Binance") or
    "Yahoo Finance".
    """
    if not crypto:
        return fetch(ticker, period), "Yahoo Finance"
    df, venue = fetch_crypto(ticker, period)
    if not df.empty:
        return df, venue
    base = base_ticker(ticker)
    return fetch(SYMBOL_OVERRIDE.get(base, f"{base}-USD"), period), "Yahoo Finance"


def main() -> None:
    p = argparse.ArgumentParser(
        description="Fetch OHLCV (stocks & crypto via Yahoo Finance)"
    )
    p.add_argument("ticker", help="e.g. AAPL, NVDA, BTC-USD, ETH-USD")
    p.add_argument("--period", default="1y",
                   help="1mo,3mo,6mo,1y,2y,5y,max (default: 1y)")
    p.add_argument("--interval", default="1d",
                   help="1d,1wk; intraday 1h/15m only ~60d (default: 1d)")
    p.add_argument("--stdout", action="store_true",
                   help="print CSV instead of a summary")
    args = p.parse_args()

    df = fetch(args.ticker, args.period, args.interval)
    if df.empty:
        sys.exit(
            f"No data for '{args.ticker}' (period={args.period}, "
            f"interval={args.interval}). Crypto needs a -USD suffix, e.g. BTC-USD."
        )

    if args.stdout:
        print(df.to_csv())
        return

    last = df.iloc[-1]
    print(f"{args.ticker.upper()}: {len(df)} rows, "
          f"latest {df.index[-1].date()} close={last['Close']:.4f} vol={last['Volume']:.0f}")


if __name__ == "__main__":
    main()
