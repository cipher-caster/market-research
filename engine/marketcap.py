#!/usr/bin/env python3
"""Crypto total market cap (TOTAL) + BTC dominance -- the macro backdrop line.

The sweep's regime gate reads BTC alone. That answers "is the benchmark in an
uptrend", not "is capital entering or leaving the asset class", and the two
come apart: BTC can hold its 200-MA while the altcoin tail bleeds, which shows
up as rising dominance against a flat TOTAL. This module supplies that second
read as context for the sweep header.

Context only -- it gates nothing. The regime gate stays on BTC per docs/SPEC.md;
adding a second gate would need a backtest, and no free source carries enough
TOTAL history to run one (see below).

Sources, in fallback order (both free, no key):
  1. CoinPaprika /v1/global  -- total mcap, BTC dominance, 24h change, ATH
  2. CoinGecko  /api/v3/global -- total mcap + dominance only (no ATH/24h change)

HISTORY IS NOT AVAILABLE FREE. CoinGecko's global market_cap_chart is Pro-only
(error 10005) and CoinPaprika has no global history endpoint (404); its per-coin
history is capped at a rolling year. A daily TOTAL series would have to be
reconstructed by summing per-coin market caps (top-100 covers ~97% of TOTAL,
top-30 ~94%, one API call per constituent). Deliberately not done here: this is
a spot reading, so it carries no MAs, no RSI, and no base rates.

Usage:
    python marketcap.py
    python marketcap.py --json
"""
import argparse
import json
import urllib.error
import urllib.request
from datetime import date

PAPRIKA = "https://api.coinpaprika.com/v1/global"
GECKO = "https://api.coingecko.com/api/v3/global"
TIMEOUT = 30


def get(url: str):
    """GET url -> parsed JSON, or None on any error.

    Fail-soft by design: the sweep must still print its levels when a
    third-party aggregator is down. Callers treat None as "no reading".
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "investments-mcp/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None


def fmt_usd(x) -> str:
    """2_307_072_219_825 -> '$2.31T'. Mirrors defillama.fmt_usd, plus trillions."""
    if x is None:
        return "n/a"
    x = float(x)
    for unit, div in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(x) >= div:
            return f"${x / div:,.2f}{unit}"
    return f"${x:,.0f}"


def _from_paprika(d: dict) -> dict | None:
    """CoinPaprika /v1/global -> the full reading, or None if the shape is wrong."""
    cap = d.get("market_cap_usd")
    if not cap:
        return None
    ath = d.get("market_cap_ath_value")
    return {
        "total": float(cap),
        "btc_dominance": d.get("bitcoin_dominance_percentage"),
        "change_24h": d.get("market_cap_change_24h"),
        "ath": float(ath) if ath else None,
        "ath_date": (d.get("market_cap_ath_date") or "")[:10] or None,
        "source": "CoinPaprika",
    }


def _from_gecko(d: dict) -> dict | None:
    """CoinGecko /api/v3/global -> a partial reading (no ATH, no 24h change)."""
    data = d.get("data") or {}
    cap = (data.get("total_market_cap") or {}).get("usd")
    if not cap:
        return None
    return {
        "total": float(cap),
        "btc_dominance": (data.get("market_cap_percentage") or {}).get("btc"),
        "change_24h": data.get("market_cap_change_percentage_24h_usd"),
        "ath": None,
        "ath_date": None,
        "source": "CoinGecko",
    }


def collect() -> dict:
    """The current TOTAL reading. Always returns a dict; 'total' is None if both
    sources failed, which callers render as a one-line note rather than an error."""
    out: dict = {"as_of": str(date.today()), "total": None, "source": None}
    for url, parse in ((PAPRIKA, _from_paprika), (GECKO, _from_gecko)):
        raw = get(url)
        if raw:
            parsed = parse(raw)
            if parsed:
                out.update(parsed)
                return out
    return out


def summary_line(d: dict) -> str:
    """The single sweep-header line. Degrades field by field: a source missing
    ATH still contributes its cap and dominance rather than dropping out."""
    if d.get("total") is None:
        return "- **TOTAL (crypto market cap): DATA ERROR** — no aggregator reachable"
    parts = [f"- **TOTAL (crypto market cap): {fmt_usd(d['total'])}**"]
    if d.get("change_24h") is not None:
        parts[0] += f" ({d['change_24h']:+.2f}% 24h)"
    if d.get("btc_dominance") is not None:
        parts.append(f"BTC dominance {d['btc_dominance']:.2f}%")
    if d.get("ath"):
        pct = (d["total"] / d["ath"] - 1) * 100
        stamp = f" ({d['ath_date']})" if d.get("ath_date") else ""
        parts.append(f"{pct:+.1f}% from ATH {fmt_usd(d['ath'])}{stamp}")
    return "  |  ".join(parts)


def to_markdown(d: dict) -> str:
    return "\n".join([
        f"### Crypto total market cap (as of {d['as_of']})", "",
        summary_line(d), "",
        "- Spot reading only — no history on the free tier, so no MAs, no trend, "
        "no base rates. Context for the regime gate, not a second gate.",
        "",
        f"Source: {d['source'] or 'none reachable'}, as of {d['as_of']}.",
    ])


def main() -> None:
    p = argparse.ArgumentParser(description="Crypto total market cap + BTC dominance")
    p.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = p.parse_args()

    d = collect()
    print(json.dumps(d, indent=2) if args.json else to_markdown(d))


if __name__ == "__main__":
    main()
