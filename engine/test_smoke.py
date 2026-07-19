#!/usr/bin/env python3
"""Smoke test for the Investments data layer.

Run:  python test_smoke.py   (inside the venv; hits Yahoo live, needs network)

Exits non-zero if anything is broken -- this is the "is it still working?" check
for when Yahoo/yfinance changes. Not a unit suite; just enough to catch silent rot.
"""
import subprocess
import sys

from check_levels import WATCHLIST, parse_number, parse_watchlist
from fetch_ohlcv import fetch
from regime import GATE, compute_regime
from technicals import load, compute, resolve

_failed = False


def check(name: str, cond: bool) -> None:
    global _failed
    print(f"{'PASS' if cond else 'FAIL'}  {name}")
    if not cond:
        _failed = True


# --- fetch: stock + crypto both return data ---
check("fetch stock (MU) non-empty", len(fetch("MU", "6mo")) > 50)
check("fetch crypto (BTC-USD) non-empty", len(fetch("BTC-USD", "6mo")) > 50)

# --- resolve: explicit, no silent guessing ---
check("resolve --crypto appends -USD", resolve("ETH", True) == "ETH-USD")
check("resolve passes -USD through", resolve("BTC-USD", False) == "BTC-USD")
check("resolve leaves stock bare", resolve("MU", False) == "MU")

# --- snapshot shape + sane values ---
sym, df = load("MU", "1y")
snap = compute(sym, df)
required = {"price", "ma50", "ma200", "rsi14", "macd", "atr14",
            "stop_long_2atr", "support_20", "resistance_20", "as_of", "ma_posture"}
check("snapshot has all fields", required <= set(snap))
check("RSI in [0,100]", 0 <= snap["rsi14"] <= 100)
check("ATR positive", snap["atr14"] > 0)
check("stop below price (long)", snap["stop_long_2atr"] < snap["price"])

# --- SMC dealing range: present and internally consistent ---
dr = snap.get("dealing_range")
check("dealing_range present", dr is not None)
check("range_low <= eq <= range_high", dr["range_low"] <= dr["equilibrium"] <= dr["range_high"])
check("zone matches pct_in_range", (dr["zone"] == "premium") == (dr["pct_in_range"] > 50))

# --- regime gate: valid label + sane fields on real BTC data ---
reg = compute_regime(fetch("BTC-USD", "2y"))
check("regime label valid", reg["regime"] in GATE)
check("regime has reasons", len(reg["reasons"]) > 0)
check("regime drawdown <= 0", reg["drawdown_90bar_pct"] <= 0)

# --- level-watch: number parsing + live Watchlist table parses ---
check("parse_number plain", parse_number("443") == 443.0)
check("parse_number range", parse_number("504-471") == (471.0, 504.0))
check("parse_number TBD", parse_number("TBD") is None)
wl = parse_watchlist(WATCHLIST.read_text())
check("watchlist parses", isinstance(wl, list))
if wl:  # empty watchlist is a valid state (fresh Watchlist)
    check("watchlist row shape", {"ticker", "type", "entry", "target", "stop", "status"} <= set(wl[0]))

# --- CLI exit codes ---
def cli(*args) -> int:
    return subprocess.run([sys.executable, "technicals.py", *args],
                          capture_output=True).returncode

check("bogus ticker exits non-zero", cli("FAKETICKER") != 0)
check("bare ambiguous BTC refused", cli("BTC") != 0)
check("BTC --crypto succeeds", cli("BTC", "--crypto") == 0)

print("-" * 40)
print("FAILED" if _failed else "ALL PASS")
sys.exit(1 if _failed else 0)
