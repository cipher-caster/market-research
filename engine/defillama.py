#!/usr/bin/env python3
"""DefiLlama protocol metrics -- the citable on-chain layer for crypto reports.

Closes the recurring '[UNVERIFIED] protocol revenue' gap: pulls TVL, fees,
revenue and DEX volume from DefiLlama's free API. Output counts as cited:
'Source: DefiLlama API, as of {date}' -- same rule as technicals.py's
own-computation stamp.

Derivatives volume / perps market share moved behind DefiLlama Pro (paid) --
NOT available here. Reports must cite that limitation explicitly instead of
tagging the number [UNVERIFIED]; fees + DEX volume are the free proxies.

Usage:
    python defillama.py hyperliquid
    python defillama.py uniswap --json

The argument is the DefiLlama protocol slug (the name in the defillama.com
URL). Endpoints that 404 for a protocol are skipped, not fatal.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import date

BASE = "https://api.llama.fi"
TIMEOUT = 30


def get(path: str):
    """GET {BASE}{path} -> parsed JSON, or None on 404/error."""
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        return None


def fmt_usd(x) -> str:
    if x is None:
        return "n/a"
    x = float(x)
    for unit, div in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(x) >= div:
            return f"${x / div:,.2f}{unit}"
    return f"${x:,.0f}"


def summary_block(kind: str, slug: str, data_type: str | None = None) -> dict | None:
    """One /summary/{kind}/{slug} call -> {total24h, total7d, total30d}."""
    path = f"/summary/{kind}/{slug}"
    if data_type:
        path += f"?dataType={data_type}"
    d = get(path)
    if not d or d.get("total24h") is None:
        return None
    return {k: d.get(k) for k in ("total24h", "total7d", "total30d")}


def collect(slug: str) -> dict:
    proto = get(f"/protocol/{slug}")
    name = proto.get("name") if proto else None
    tvl = get(f"/tvl/{slug}")

    return {
        "slug": slug,
        "name": name or slug,
        "as_of": str(date.today()),
        "tvl": float(tvl) if isinstance(tvl, (int, float)) else None,
        "fees": summary_block("fees", slug),
        "revenue": summary_block("fees", slug, data_type="dailyRevenue"),
        "dex_volume": summary_block("dexs", slug),
    }


def to_markdown(d: dict) -> str:
    lines = [f"### DefiLlama — {d['name']} (as of {d['as_of']})", ""]
    if d["tvl"] is not None:
        lines.append(f"- **TVL:** {fmt_usd(d['tvl'])}")
    for key, label in (("fees", "Fees"), ("revenue", "Revenue"),
                       ("dex_volume", "DEX volume")):
        b = d.get(key)
        if b:
            lines.append(f"- **{label}:** 24h {fmt_usd(b['total24h'])}  |  "
                         f"7d {fmt_usd(b['total7d'])}  |  30d {fmt_usd(b['total30d'])}")
    if len(lines) == 2:
        lines.append(f"- No data on any endpoint for slug '{d['slug']}' — check the "
                     "slug in the defillama.com URL.")
    else:
        lines.append("- Derivatives volume / perps share: behind DefiLlama Pro — "
                     "cite as 'not available (paid tier)', do not guess.")
    lines += ["", f"Source: DefiLlama API (api.llama.fi), as of {d['as_of']}."]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="DefiLlama protocol metrics (citable)")
    p.add_argument("slug", help="DefiLlama protocol slug, e.g. hyperliquid")
    p.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = p.parse_args()

    d = collect(args.slug.lower())
    print(json.dumps(d, indent=2) if args.json else to_markdown(d))


if __name__ == "__main__":
    main()
