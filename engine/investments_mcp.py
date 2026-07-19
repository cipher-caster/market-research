#!/usr/bin/env python3
"""Investments MCP server — the deterministic data layer, callable in-conversation.

Exposes the same audited computation the CLI scripts use (technicals.compute,
regime.compute_regime, funding.analyze, check_levels sweep, defillama.collect)
as MCP tools, so the assistant pulls live numbers directly instead of the user
running `python ...` by hand. Nothing here recomputes indicators — it reuses
the existing functions verbatim, so MCP output and CLI output stay identical.

Crypto OHLCV comes from the exchange (OKX -> Bybit -> Binance, see
exchange_ohlcv.py) so the numbers match the user's TradingView crypto charts;
stocks stay on Yahoo Finance. Validated 2026-06-11: exchange vs Yahoo agreed to
<0.1% on BTC/ZEC/HYPE, identical regime calls.

Run: python investments_mcp.py   (stdio; registered via `claude mcp add`)
"""
import io
import os
import re
import sys
from contextlib import redirect_stdout

# Make sibling scripts importable regardless of the launcher's cwd.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)

from mcp.server.fastmcp import FastMCP

import check_levels as levels_mod
import defillama as defillama_mod
import funding as funding_mod
import regime as regime_mod
import technicals
from exchange_ohlcv import base_ticker, fetch_crypto
from fetch_ohlcv import fetch

mcp = FastMCP("investments")

# Matches both stamp variants: technicals' bare stamp and regime's "(SYMBOL)" suffix,
# consuming up to the ", as of" so neither leaves a doubled venue label.
_YF_STAMP_RE = re.compile(r"Source: own computation on Yahoo Finance OHLCV[^,]*")


def _retag(md: str, venue: str) -> str:
    """Swap the Yahoo source stamp for the real exchange venue (crypto path)."""
    return _YF_STAMP_RE.sub(
        f"Source: own computation on {venue} OHLCV (matches your TradingView {venue} chart)",
        md,
    )


@mcp.tool()
def technicals_snapshot(ticker: str, asset_type: str = "crypto",
                        period: str = "1y", range_lookback: int = 60) -> str:
    """Deterministic technicals snapshot: price, MA posture, RSI, MACD, ATR + 2·ATR
    stop, support/resistance, uptrend add-ladder, and the SMC dealing range
    (premium/discount). asset_type 'crypto' pulls exchange data (OKX/Bybit/Binance,
    matches TradingView); 'stock' pulls Yahoo Finance. period: 1y/2y/5y/max."""
    if asset_type.lower() == "crypto":
        df, src = fetch_crypto(ticker, period)
        if df.empty:
            return f"No exchange data for '{ticker}' (OKX/Bybit/Binance). Check the symbol."
        if len(df) < 50:
            return f"Only {len(df)} bars for {ticker}; need >=50 for a snapshot."
        snap = technicals.compute(base_ticker(ticker), df, range_lookback=range_lookback)
        return _retag(technicals.to_markdown(snap), src)
    # stock
    sym, df = technicals.load(ticker, period, crypto=False)
    if df.empty:
        return f"No Yahoo data for '{ticker}'. Check the symbol."
    if len(df) < 50:
        return f"Only {len(df)} bars for {sym}; need >=50 for a snapshot."
    return technicals.to_markdown(technicals.compute(sym, df, range_lookback=range_lookback))


@mcp.tool()
def market_regime(market: str = "crypto") -> str:
    """Market regime gate (risk_on / neutral / risk_off) on the benchmark — the
    'is this a place to be adding risk at all?' check. market 'crypto' uses BTC
    (exchange data); 'stocks' uses SPY (Yahoo). risk_off => add rungs suspended."""
    if market.lower() in ("crypto", "btc"):
        df, src = fetch_crypto("BTC", "2y")
        if df.empty or len(df) < 60:
            return "No/insufficient BTC exchange data for a regime read."
        r = regime_mod.compute_regime(df)
        r["gate"] = regime_mod.GATE[r["regime"]]
        return _retag(regime_mod.to_markdown(f"BTC ({src})", r), src)
    # stocks
    df = fetch("SPY", "2y")
    if df.empty or len(df) < 60:
        return "No/insufficient SPY data for a regime read."
    r = regime_mod.compute_regime(df)
    r["gate"] = regime_mod.GATE[r["regime"]]
    return regime_mod.to_markdown("SPY", r)


@mcp.tool()
def funding_oi(ticker: str) -> str:
    """Perp funding rate + open interest (crowding read) for a crypto ticker.
    Binance USD-M primary, Bybit linear fallback. Negative funding at support =
    squeeze fuel; elevated positive into resistance = chase risk. Not a signal alone."""
    sym = base_ticker(ticker) + "USDT"
    raw = funding_mod.from_binance(sym) or funding_mod.from_bybit(sym)
    if raw is None:
        return (f"No perp data for '{sym}' on Binance or Bybit (native-venue assets "
                "may only trade perps on their own chain).")
    a = funding_mod.analyze(raw)
    return funding_mod.to_markdown(sym, a)


@mcp.tool()
def watchlist_levels() -> str:
    """Level-watch sweep: parse the calls table in Watchlist.md, pull live prices,
    report only triggered levels (stop breached/near, entry/re-entry zone, target
    hit/near) with the market regime on top. A trigger means 'run /refresh', not
    'trade'. Reuses the same sweep the cron job runs."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            levels_mod.main()
        except SystemExit as e:
            if e.code not in (0, None):
                return f"Sweep error: {e}"
    out = buf.getvalue().strip()
    return out or "Sweep ran; no output (no rows or all clean in quiet mode)."


@mcp.tool()
def defillama_protocol(slug: str) -> str:
    """On-chain protocol metrics from DefiLlama (free, citable): TVL, fees, revenue,
    DEX volume. slug = the name in the defillama.com URL (e.g. 'hyperliquid').
    Derivatives/perps share is paid-tier — not returned, cite the gap."""
    return defillama_mod.to_markdown(defillama_mod.collect(slug.lower()))


if __name__ == "__main__":
    mcp.run()
