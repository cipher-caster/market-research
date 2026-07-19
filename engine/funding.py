#!/usr/bin/env python3
"""Perp funding rate + open interest -- the positioning/crowding layer (crypto).

Funding tells you who is PAYING to hold the trade: deeply negative funding at a
support level is squeeze fuel (shorts crowded); heavily positive funding into
resistance means longs are paying up (chase risk). OI tells you whether moves
are driven by new positioning or by closing. Neither is a trade signal alone --
the Quant worker combines them with technicals.py levels and the regime gate.

Free public endpoints, no keys: Binance USD-M futures primary, Bybit linear
fallback. Output counts as cited ('Source: {venue} public API, as of {date}').

Usage:
    python funding.py BTC          # maps to BTCUSDT perp
    python funding.py HYPE --json
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime

TIMEOUT = 30
HISTORY_POINTS = 21  # 7 days of 8h funding intervals


def get(url: str):
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        return None


def from_binance(symbol: str) -> dict | None:
    base = "https://fapi.binance.com"
    prem = get(f"{base}/fapi/v1/premiumIndex?symbol={symbol}")
    if not prem or "lastFundingRate" not in prem:
        return None
    hist = get(f"{base}/fapi/v1/fundingRate?symbol={symbol}&limit={HISTORY_POINTS}") or []
    oi = get(f"{base}/fapi/v1/openInterest?symbol={symbol}")
    oi_hist = get(f"{base}/futures/data/openInterestHist"
                  f"?symbol={symbol}&period=1d&limit=8") or []
    return {
        "venue": "Binance USD-M futures",
        "mark_price": float(prem["markPrice"]),
        "funding_now": float(prem["lastFundingRate"]),
        "funding_history": [(int(h["fundingTime"]), float(h["fundingRate"])) for h in hist],
        "oi_now": float(oi["openInterest"]) if oi and "openInterest" in oi else None,
        "oi_history": [(int(h["timestamp"]), float(h["sumOpenInterest"])) for h in oi_hist],
    }


def from_bybit(symbol: str) -> dict | None:
    base = "https://api.bybit.com/v5/market"
    tick = get(f"{base}/tickers?category=linear&symbol={symbol}")
    rows = (tick or {}).get("result", {}).get("list") or []
    if not rows or not rows[0].get("fundingRate"):
        return None
    t = rows[0]
    hist = (get(f"{base}/funding/history?category=linear&symbol={symbol}"
                f"&limit={HISTORY_POINTS}") or {}).get("result", {}).get("list") or []
    oi_hist = (get(f"{base}/open-interest?category=linear&symbol={symbol}"
                   f"&intervalTime=1d&limit=8") or {}).get("result", {}).get("list") or []
    return {
        "venue": "Bybit linear perps",
        "mark_price": float(t["markPrice"]),
        "funding_now": float(t["fundingRate"]),
        "funding_history": [(int(h["fundingRateTimestamp"]), float(h["fundingRate"]))
                            for h in hist],
        "oi_now": float(t["openInterest"]) if t.get("openInterest") else None,
        "oi_history": [(int(h["timestamp"]), float(h["openInterest"])) for h in oi_hist],
    }


def analyze(raw: dict) -> dict:
    hist = sorted(raw["funding_history"])  # oldest first
    rates = [r for _, r in hist]

    # Funding interval from consecutive history timestamps (8h typical, but some
    # symbols run 4h/1h) -- annualization is wrong without it.
    if len(hist) >= 2:
        interval_h = (hist[-1][0] - hist[-2][0]) / 3.6e6
    else:
        interval_h = 8.0
    per_year = 365 * 24 / interval_h
    rate_8h_equiv = raw["funding_now"] * (8 / interval_h)

    if rate_8h_equiv <= -0.0001:
        tag = "NEGATIVE — shorts pay longs; squeeze fuel if price sits at a support/rung"
    elif rate_8h_equiv >= 0.0005:
        tag = "ELEVATED — longs crowded and paying up; chase risk"
    else:
        tag = "neutral (near the 0.01%/8h baseline)"

    oi_hist = sorted(raw["oi_history"])
    oi_now = raw["oi_now"]
    oi_chg_24h = oi_chg_7d = None
    if oi_now and len(oi_hist) >= 2:
        oi_chg_24h = (oi_now / oi_hist[-2][1] - 1) * 100
        oi_chg_7d = (oi_now / oi_hist[0][1] - 1) * 100

    return {
        "venue": raw["venue"],
        "as_of": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "mark_price": round(raw["mark_price"], 4),
        "funding_interval_h": round(interval_h, 1),
        "funding_now_pct": round(raw["funding_now"] * 100, 4),
        "funding_now_apr_pct": round(raw["funding_now"] * per_year * 100, 1),
        "funding_7d_mean_pct": round(sum(rates) / len(rates) * 100, 4) if rates else None,
        "funding_7d_mean_apr_pct": round(sum(rates) / len(rates) * per_year * 100, 1)
                                   if rates else None,
        "crowding": tag,
        "open_interest": round(oi_now, 1) if oi_now else None,
        "oi_change_24h_pct": round(oi_chg_24h, 1) if oi_chg_24h is not None else None,
        "oi_change_7d_pct": round(oi_chg_7d, 1) if oi_chg_7d is not None else None,
    }


def to_markdown(symbol: str, a: dict) -> str:
    lines = [
        f"### Funding & OI — {symbol} ({a['venue']}, as of {a['as_of']})",
        "",
        f"- **Mark price:** {a['mark_price']}",
        f"- **Funding now:** {a['funding_now_pct']}% per {a['funding_interval_h']}h "
        f"(~{a['funding_now_apr_pct']}% APR)  |  7d mean {a['funding_7d_mean_pct']}% "
        f"(~{a['funding_7d_mean_apr_pct']}% APR)",
        f"- **Crowding read:** {a['crowding']}",
    ]
    if a["open_interest"] is not None:
        chg24 = f"{a['oi_change_24h_pct']:+}%" if a["oi_change_24h_pct"] is not None else "n/a"
        chg7 = f"{a['oi_change_7d_pct']:+}%" if a["oi_change_7d_pct"] is not None else "n/a"
        lines.append(f"- **Open interest:** {a['open_interest']} (base units)  |  "
                     f"24h {chg24}  |  7d {chg7}")
        lines.append("- OI rising while price falls = fresh positioning into weakness; "
                     "OI falling on a bounce = short-covering, not new demand. "
                     "Combine with technicals.py trend, never read alone.")
    lines += ["", f"Source: {a['venue']} public API, as of {a['as_of']}."]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Perp funding + OI (Binance, Bybit fallback)")
    p.add_argument("symbol", help="e.g. BTC (maps to BTCUSDT), or a full perp symbol")
    p.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = p.parse_args()

    sym = args.symbol.upper()
    if not sym.endswith("USDT"):
        sym += "USDT"

    raw = from_binance(sym) or from_bybit(sym)
    if raw is None:
        sys.exit(f"No perp data for '{sym}' on Binance or Bybit. "
                 "Check the symbol (native-venue assets like HYPE may only trade "
                 "perps on their own chain).")

    a = analyze(raw)
    a["symbol"] = sym
    print(json.dumps(a, indent=2) if args.json else to_markdown(sym, a))


if __name__ == "__main__":
    main()
