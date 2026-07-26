#!/usr/bin/env python3
"""Backtest the system's decision rules (regime gate, dealing-range zone, rung
reclaim) on long daily crypto history.

This is the harness behind data/Reports/_meta/2026-07-26-rule-backtest.md. It
does NOT reimplement the rules: every indicator is causal, and the vectorized
state is verified bar-for-bar against technicals.compute() and
regime.compute_regime() on prefix frames -- the backtest state IS the engine
state, no lookahead.

Two layers (the system issues calls, not positions):
  A -- forward returns at 30/60/90/180 bars conditional on system state
  B -- call resolution: enter at signal close, stop = the engine's own 2*ATR,
       target 2R, first touch inside 180 bars, same-bar tie -> stop (worst
       case), non-overlapping per state per asset

The regime gate is computed on the CLASS BENCHMARK (default BTC, per
docs/SPEC.md) and aligned by date to each asset. History comes from paginated
Binance daily klines (UTC; ~0.1% median close diff vs Yahoo/OKX, validated
2026-07-26), refetched each run -- no cache files. The 2R/2*ATR template is a
scoring choice, not a SPEC rule; expectancies are template-dependent (see the
report's caveats).

Manual-run only -- never wire into cron (owner policy 2026-07-19).

Usage:
    python backtest.py                    # default: BTC ETH SOL ZEC
    python backtest.py BTC ZEC
    python backtest.py --end 2026-07-26   # pin the window for reproducibility
"""
import argparse
import json
import time
import urllib.request

import numpy as np
import pandas as pd
import pandas_ta as ta

import regime as R
import technicals as T

RANGE_LOOKBACK = 60
HORIZONS = [30, 60, 90, 180]
MAX_BARS = 180
TIMEOUT = 30


# ------------------------------------------------------------------ history
def fetch_full_history(base: str, start: str = "2017-01-01") -> pd.DataFrame:
    """Paginate Binance daily klines from `start` to now (UTC-aligned)."""
    start_ms = int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
    rows: list[tuple] = []
    while True:
        url = (f"https://data-api.binance.vision/api/v3/klines?symbol={base}USDT"
               f"&interval=1d&limit=1000&startTime={start_ms}")
        req = urllib.request.Request(url, headers={"User-Agent": "investments-mcp/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            d = json.loads(r.read())
        if not isinstance(d, list) or not d:
            break
        rows += [(int(c[0]), c[1], c[2], c[3], c[4], c[5]) for c in d]
        if len(d) < 1000:
            break
        start_ms = int(d[-1][0]) + 86_400_000
        time.sleep(0.2)
    df = pd.DataFrame(rows, columns=["ts", "Open", "High", "Low", "Close", "Volume"])
    df["Date"] = pd.to_datetime(df["ts"], unit="ms", utc=True).dt.tz_localize(None)
    df = df.drop(columns="ts").set_index("Date").sort_index()
    df = df[~df.index.duplicated(keep="last")]
    df.index.name = "Date"
    return df.astype(float)


# --------------------------------------------------------------- indicators
def panel(df: pd.DataFrame) -> pd.DataFrame:
    """Causal restatement of the engine's per-bar state (verified by verify())."""
    c, h, l = df["Close"], df["High"], df["Low"]
    p = pd.DataFrame(index=df.index)
    p["close"], p["high"], p["low"] = c, h, l
    p["ma20"] = c.rolling(20).mean()
    p["ma50"] = c.rolling(50).mean()
    p["ma200"] = c.rolling(200).mean()
    p["rsi"] = ta.rsi(c, length=14)
    p["macd_hist"] = ta.macd(c)["MACDh_12_26_9"]
    p["atr"] = ta.atr(h, l, c, length=14)
    p["dd90"] = (c / h.rolling(R.DRAWDOWN_LOOKBACK).max() - 1) * 100
    rh, rl = h.rolling(RANGE_LOOKBACK).max(), l.rolling(RANGE_LOOKBACK).min()
    p["pct_in_range"] = (c - rl) / (rh - rl) * 100
    p["zone"] = np.where(c > (rh + rl) / 2, "premium", "discount")
    # the rung is the PRIOR bar's 10-bar swing low (today can't define the
    # level it is reclaiming)
    p["rung"] = l.rolling(10).min().shift(1)
    return p


def regime_series(p: pd.DataFrame) -> pd.Series:
    """Vectorized restatement of regime.compute_regime's rules."""
    px, ma50, ma200, dd = p["close"], p["ma50"], p["ma200"], p["dd90"]
    out = pd.Series("neutral", index=p.index, dtype=object)
    out[(px > ma50) & (ma50 > ma200) & (dd > R.RISK_ON_DRAWDOWN)] = "risk_on"
    out[(px < ma200) | (dd <= R.RISK_OFF_DRAWDOWN)] = "risk_off"
    out[ma200.isna()] = None
    return out


def verify(df, p, reg, ticker, n_checks=6) -> float:
    """Assert the panel reproduces the engine's compute() on prefix frames.

    Returns the max relative deviation (should be display-rounding scale,
    ~1e-3). Any zone/regime label mismatch raises.
    """
    worst = 0.0
    for i in np.linspace(250, len(df) - 1, n_checks, dtype=int):
        sub = df.iloc[: i + 1]
        s = T.compute(ticker, sub, range_lookback=RANGE_LOOKBACK)
        row = p.iloc[i]
        for a, b in [(s["price"], row["close"]), (s["ma20"], row["ma20"]),
                     (s["ma50"], row["ma50"]), (s["ma200"], row["ma200"]),
                     (s["rsi14"], row["rsi"]), (s["macd_hist"], row["macd_hist"]),
                     (s["atr14"], row["atr"]),
                     (s["dealing_range"]["pct_in_range"], row["pct_in_range"])]:
            worst = max(worst, abs(a - b) / max(abs(b), 1e-9))
        assert s["dealing_range"]["zone"] == row["zone"], (ticker, i, "zone")
        if reg is not None:
            assert R.compute_regime(sub)["regime"] == reg.iloc[i], (ticker, i, "regime")
    return worst


# ------------------------------------------------------------------ signals
def signals(p: pd.DataFrame, reg: pd.Series) -> dict[str, pd.Series]:
    golden = p["ma50"] > p["ma200"]
    death = p["ma50"] < p["ma200"]
    disc = p["zone"] == "discount"
    prem = ~disc
    not_off = reg != "risk_off"
    rising = p["macd_hist"] > p["macd_hist"].shift(1)
    touch = p["low"] <= p["rung"]
    # a touched rung stays armed 3 bars (the tested form; SPEC 2026-07-26)
    armed3 = touch.rolling(3).max().fillna(0).astype(bool)
    reclaim3 = armed3 & (p["close"] > p["rung"]) & rising
    return {
        "baseline (any day)": pd.Series(True, index=p.index),
        "benchmark risk_on": reg == "risk_on",
        "benchmark neutral": reg == "neutral",
        "benchmark risk_off": reg == "risk_off",
        "rung touch, no confirmation": touch,
        "rung reclaim (3-bar arming)": reclaim3,
        # zone x own-trend 2x2, gated not-risk_off (the doctrine's fair test)
        "golden + premium (not risk_off)": golden & prem & not_off,
        "golden + discount (not risk_off)": golden & disc & not_off,
        "death + premium (not risk_off)": death & prem & not_off,
        "death + discount (not risk_off)": death & disc & not_off,
        "golden+disc: bare touch (not risk_off)": golden & disc & touch & not_off,
        "golden+disc: confirmed reclaim (SPEC add)": golden & disc & reclaim3 & not_off,
        "golden any-day (not risk_off)": golden & not_off,
    }


# ------------------------------------------------------------------- layers
def fwd_series(p: pd.DataFrame, mask: pd.Series, hz: int) -> pd.Series:
    f = (p["close"].shift(-hz) / p["close"] - 1) * 100
    return f[mask & f.notna()]


def resolve_calls(p, mask, ticker, r_multiple=2.0) -> pd.DataFrame:
    """Layer B: bracket each signal close with the engine's 2*ATR stop and a
    2R target; first touch resolves, timeout scores at the window close."""
    c, h, l, atr = (p["close"].values, p["high"].values,
                    p["low"].values, p["atr"].values)
    idx = np.where(mask.values & ~np.isnan(atr))[0]
    trades, busy = [], -1
    for i in idx:
        if i + 1 >= len(c) or i <= busy or np.isnan(atr[i]):
            continue
        entry = c[i]
        stop = entry - 2 * atr[i]
        risk = entry - stop
        if risk <= 0:
            continue
        target = entry + r_multiple * risk
        end = min(i + MAX_BARS, len(c) - 1)
        outcome, exit_i = None, end
        for j in range(i + 1, end + 1):
            if l[j] <= stop:            # same-bar tie -> stop (worst case)
                outcome, exit_i = "stop", j
                break
            if h[j] >= target:
                outcome, exit_i = "target", j
                break
        rr = (-1.0 if outcome == "stop" else r_multiple) if outcome \
            else (c[end] - entry) / risk
        trades.append({"ticker": ticker, "date": p.index[i],
                       "outcome": outcome or "timeout", "R": rr,
                       "bars": exit_i - i})
        busy = exit_i
    return pd.DataFrame(trades)


def boot(x, y, label_a, label_b, n=10000) -> None:
    """Bootstrap the expectancy gap between two trade sets (seed fixed)."""
    rng = np.random.default_rng(42)
    d = np.array([rng.choice(x, len(x)).mean() - rng.choice(y, len(y)).mean()
                  for _ in range(n)])
    lo, hi = np.percentile(d, [5, 95])
    print(f"- {label_a} minus {label_b}: **{x.mean() - y.mean():+.2f}R**, "
          f"90% CI [{lo:+.2f}, {hi:+.2f}], P(gap>0) = {(d > 0).mean() * 100:.0f}% "
          f"(N {len(x)} vs {len(y)})")


# ------------------------------------------------------------------- report
def main() -> None:
    ap = argparse.ArgumentParser(
        description="Backtest the system's decision rules on long crypto history")
    ap.add_argument("tickers", nargs="*", default=["BTC", "ETH", "SOL", "ZEC"],
                    help="crypto tickers (default: BTC ETH SOL ZEC)")
    ap.add_argument("--benchmark", default="BTC",
                    help="regime-gate benchmark (default BTC, per SPEC)")
    ap.add_argument("--end", default=None,
                    help="last bar YYYY-MM-DD (default: latest; pin to reproduce)")
    args = ap.parse_args()
    tickers = [t.upper() for t in args.tickers]

    bdf = fetch_full_history(args.benchmark)
    if args.end:
        bdf = bdf[bdf.index <= args.end]
    breg = regime_series(panel(bdf))
    w = verify(bdf, panel(bdf), breg, f"{args.benchmark}-USD")
    print(f"# Rule backtest — {', '.join(tickers)} "
          f"(benchmark {args.benchmark}, to {bdf.index[-1].date()})\n")
    print(f"Engine-parity ({args.benchmark}): max relative deviation {w:.1e} "
          f"(display rounding); regime + zone labels match on all checks.\n")

    trades: dict[str, list] = {}
    fwds: dict[str, list] = {}
    days: dict[str, int] = {}
    print("| Asset | Bars | From | Parity dev |")
    print("|---|---|---|---|")
    for tk in tickers:
        df = bdf if tk == args.benchmark else fetch_full_history(tk)
        if args.end:
            df = df[df.index <= args.end]
        p = panel(df)
        reg = breg.reindex(p.index)
        wd = verify(df, p, None, f"{tk}-USD")
        print(f"| {tk} | {len(df)} | {df.index[0].date()} | {wd:.1e} |")
        for name, m in signals(p, reg).items():
            trades.setdefault(name, []).append(resolve_calls(p, m, tk))
            fwds.setdefault(name, []).append(fwd_series(p, m, 90))
            days[name] = days.get(name, 0) + int(m.sum())
    print()

    pooled = {k: pd.concat(v, ignore_index=True) for k, v in trades.items()}
    pooledf = {k: pd.concat(v) for k, v in fwds.items()}

    print("## Pooled — Layer B (2*ATR stop / 2R target / 180-bar window)\n")
    print("| State | Days | Calls | Win% | E(R) | 90d fwd median |")
    print("|---|---|---|---|---|---|")
    for name, t in pooled.items():
        if t.empty:
            print(f"| {name} | {days[name]} | 0 | - | - | - |")
            continue
        print(f"| {name} | {days[name]} | {len(t)} | {(t.R > 0).mean() * 100:.0f}% | "
              f"{t.R.mean():+.2f} | {pooledf[name].median():+.1f}% |")
    print()

    print("## Bootstraps (pooled; CIs optimistic — assets are correlated)\n")
    not_off = pd.concat([pooled["benchmark risk_on"], pooled["benchmark neutral"]])
    boot(not_off.R, pooled["benchmark risk_off"].R, "not risk_off", "risk_off")
    boot(pooled["golden + premium (not risk_off)"].R,
         pooled["golden + discount (not risk_off)"].R,
         "golden+premium", "golden+discount")
    boot(pooled["golden+disc: confirmed reclaim (SPEC add)"].R,
         pooled["golden any-day (not risk_off)"].R,
         "SPEC add", "golden any-day")
    boot(pooled["rung reclaim (3-bar arming)"].R,
         pooled["rung touch, no confirmation"].R, "reclaim", "bare touch")
    boot(pooled["golden+disc: confirmed reclaim (SPEC add)"].R,
         pooled["golden+disc: bare touch (not risk_off)"].R,
         "golden+disc reclaim", "golden+disc bare touch")
    print()

    print("## Per-asset E(R) (N), key states\n")
    key = ["baseline (any day)", "benchmark risk_off",
           "golden + premium (not risk_off)", "golden + discount (not risk_off)",
           "golden+disc: confirmed reclaim (SPEC add)", "golden any-day (not risk_off)"]
    print("| State | " + " | ".join(tickers) + " |")
    print("|---" * (len(tickers) + 1) + "|")
    for name in key:
        cells = []
        for i in range(len(tickers)):
            t = trades[name][i]
            cells.append(f"{t.R.mean():+.2f} ({len(t)})" if not t.empty else "- (0)")
        print(f"| {name} | " + " | ".join(cells) + " |")
    print("\nInterpretation contract: the regime gate is the validated rule; zone is "
          "location context (veto retired 2026-07-26); confirmation is downside "
          "hygiene. See data/Reports/_meta/2026-07-26-rule-backtest.md before "
          "reading anything new into a rerun.")


if __name__ == "__main__":
    main()
