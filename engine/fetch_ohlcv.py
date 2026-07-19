#!/usr/bin/env python3
"""Fetch OHLCV from Yahoo Finance for a stock or crypto symbol.

Dumb data layer for the Investments research system: this ONLY pulls raw
OHLCV. Indicator computation (RSI/MACD/ATR/MA posture) is done by the Quant
worker in pandas -- keep this script free of analysis so the numbers stay
auditable.

Usage:
    python fetch_ohlcv.py AAPL
    python fetch_ohlcv.py BTC-USD --period 2y
    python fetch_ohlcv.py NVDA --period 60d --interval 1h   # intraday: <=60d
    python fetch_ohlcv.py MU --stdout                        # print, don't save

Notes:
  - Crypto needs the -USD suffix: BTC-USD, ETH-USD, SOL-USD.
  - Intraday intervals (1h/15m/1m) only return ~60 days from Yahoo; daily/
    weekly go back years. Swing/position work uses 1d, which is the default.
"""
import argparse
import sys
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    sys.exit("yfinance not installed. Run: pip install -r requirements.txt")

DATA_DIR = Path(__file__).parent / "data"


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


def main() -> None:
    p = argparse.ArgumentParser(
        description="Fetch OHLCV -> CSV (stocks & crypto via Yahoo Finance)"
    )
    p.add_argument("ticker", help="e.g. AAPL, NVDA, BTC-USD, ETH-USD")
    p.add_argument("--period", default="1y",
                   help="1mo,3mo,6mo,1y,2y,5y,max (default: 1y)")
    p.add_argument("--interval", default="1d",
                   help="1d,1wk; intraday 1h/15m only ~60d (default: 1d)")
    p.add_argument("--stdout", action="store_true",
                   help="print CSV to stdout instead of writing a file")
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

    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / f"{args.ticker.upper()}_{args.interval}.csv"
    df.to_csv(out)
    last = df.iloc[-1]
    print(f"Wrote {len(df)} rows -> {out}")
    print(f"Latest {df.index[-1].date()}: "
          f"close={last['Close']:.4f} vol={last['Volume']:.0f}")


if __name__ == "__main__":
    main()
