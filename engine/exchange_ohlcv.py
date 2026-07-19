#!/usr/bin/env python3
"""Crypto OHLCV straight from the exchange — the data your TradingView charts show.

TradingView's crypto candles ARE exchange klines, so reading the exchange
directly (no scraping, free, no key) gives data that matches what you chart.
This is the crypto counterpart to fetch_ohlcv.py's Yahoo layer; same DataFrame
shape (Open/High/Low/Close/Volume, UTC daily index, oldest->newest) so every
downstream consumer — technicals.compute, regime.compute_regime — reuses it
unchanged.

Venue order (owner's stack): OKX primary (main venue), Bybit fallback (HYPE and
others charted there), Binance last. All daily bars are UTC-aligned so they
line up with Yahoo and with each other.

Usage:
    python exchange_ohlcv.py BTC
    python exchange_ohlcv.py HYPE --period 1y --stdout
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

import pandas as pd

TIMEOUT = 30
PERIOD_DAYS = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825, "max": 1500}


def _get(url: str):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "investments-mcp/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None


def base_ticker(ticker: str) -> str:
    """'HYPE32196-USD' -> 'HYPE'; 'BTC-USD' -> 'BTC'; 'BTC' -> 'BTC'."""
    t = ticker.upper().split("-")[0]
    # strip any Yahoo numeric suffix (HYPE32196 -> HYPE)
    i = len(t)
    while i > 0 and t[i - 1].isdigit():
        i -= 1
    return t[:i] if i > 0 else t


def _df(rows: list[tuple]) -> pd.DataFrame:
    """rows = list of (ts_ms, o, h, l, c, v); build the standard OHLCV frame."""
    df = pd.DataFrame(rows, columns=["ts", "Open", "High", "Low", "Close", "Volume"])
    df["Date"] = pd.to_datetime(df["ts"], unit="ms", utc=True).dt.tz_localize(None)
    df = df.drop(columns="ts").set_index("Date").sort_index()
    df.index.name = "Date"
    return df[["Open", "High", "Low", "Close", "Volume"]].astype(float)


def from_okx(base: str, limit: int) -> pd.DataFrame | None:
    # 1Dutc = UTC-aligned daily (matches Yahoo/Bybit/Binance). Max limit 300.
    url = (f"https://www.okx.com/api/v5/market/candles"
           f"?instId={base}-USDT&bar=1Dutc&limit={min(limit, 300)}")
    d = _get(url)
    if not d or d.get("code") != "0" or not d.get("data"):
        return None
    rows = [(int(c[0]), c[1], c[2], c[3], c[4], c[5]) for c in d["data"]]
    return _df(rows) if rows else None


def from_bybit(base: str, limit: int) -> pd.DataFrame | None:
    url = (f"https://api.bybit.com/v5/market/kline?category=spot"
           f"&symbol={base}USDT&interval=D&limit={min(limit, 1000)}")
    d = _get(url)
    lst = (d or {}).get("result", {}).get("list") or []
    if not lst:
        return None
    rows = [(int(c[0]), c[1], c[2], c[3], c[4], c[5]) for c in lst]
    return _df(rows)


def from_binance(base: str, limit: int) -> pd.DataFrame | None:
    for host in ("https://api.binance.com", "https://data-api.binance.vision"):
        d = _get(f"{host}/api/v3/klines?symbol={base}USDT&interval=1d&limit={min(limit, 1000)}")
        if isinstance(d, list) and d:
            rows = [(int(c[0]), c[1], c[2], c[3], c[4], c[5]) for c in d]
            return _df(rows)
    return None


SOURCES = (("OKX", from_okx), ("Bybit", from_bybit), ("Binance", from_binance))


def fetch_crypto(ticker: str, period: str = "1y") -> tuple[pd.DataFrame, str]:
    """Daily OHLCV for a crypto ticker, trying OKX -> Bybit -> Binance.

    Returns (df, source_name). df is empty and source '' if every venue failed.
    """
    base = base_ticker(ticker)
    limit = PERIOD_DAYS.get(period, 365) + 5
    for name, fn in SOURCES:
        df = fn(base, limit)
        if df is not None and not df.empty:
            return df, name
    return pd.DataFrame(), ""


def main() -> None:
    p = argparse.ArgumentParser(description="Crypto OHLCV from the exchange (OKX/Bybit/Binance)")
    p.add_argument("ticker", help="e.g. BTC, HYPE, ZEC")
    p.add_argument("--period", default="1y", help="1mo,3mo,6mo,1y,2y,5y,max (default 1y)")
    p.add_argument("--stdout", action="store_true", help="print CSV instead of a summary")
    args = p.parse_args()

    df, src = fetch_crypto(args.ticker, args.period)
    if df.empty:
        sys.exit(f"No exchange data for '{args.ticker}' on OKX/Bybit/Binance.")
    if args.stdout:
        print(df.to_csv())
        return
    last = df.iloc[-1]
    print(f"{base_ticker(args.ticker)} via {src}: {len(df)} daily bars, "
          f"latest {df.index[-1].date()} close={last['Close']:.4f}")


if __name__ == "__main__":
    main()
