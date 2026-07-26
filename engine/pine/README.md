# MR System Overlay — chart guide

How to install and read `mr-system-overlay.pine`. The Python engine is the
source of truth; this overlay mirrors the decision layer in `docs/SPEC.md`
(SPEC-synced 2026-07-26 — re-sync the .pine by hand whenever SPEC changes).

**Nothing on this chart is a trade signal. A marker or alert means "run
`/refresh` on that ticker", never "trade mechanically".**

## Install (once)

1. TradingView → open any chart → `Pine Editor` (bottom panel)
2. Paste the whole of `mr-system-overlay.pine` → `Save` → `Add to chart`
3. Use the **daily** chart of the venue symbols the engine reads
   (`OKX:BTCUSDT`, `OKX:ETHUSDT`, `OKX:SOLUSDT`, `OKX:ZECUSDT`).
   The table shows a red warning row if the chart isn't daily.
4. Per chart, open the indicator settings and fill the **Watchlist call
   levels** inputs from `data/Watchlist.md` (0 = off). Snapshot as of
   2026-07-26 — always check Watchlist.md for current:

   | Chart | Entry lo/hi | Stop | Target |
   |---|---|---|---|
   | OKX:BTCUSDT | 63100 / 65500 | 57748 | 78101 |
   | OKX:ETHUSDT | 1729 / 1830 | 1507 | 2154 |
   | OKX:SOLUSDT | 70 / 72 | 70.14 | 87.79 |
   | OKX:ZECUSDT | 470 / 501 | 435 | 644.64 |

5. Alerts: right-click chart → `Add alert` → Condition = `MR System` → pick
   the event → set trigger to **"Once per bar close"** (everything in this
   system is close-confirmed; intrabar values are still developing).
   If the free-tier alert cap bites, keep **regime changed** and **stop
   breached** — the two the backtest says you can't afford to miss.

## The 60-second read (in priority order)

1. **Background tint** — the regime gate, the only rule with backtested edge.
   Faint red = RISK_OFF: adds suspended, stops still execute, full stop —
   nothing else on the chart can override this. Faint green = RISK_ON. No
   tint = NEUTRAL (adds need reclaim confirmation, which is mandatory anyway).
2. **Status table, top row** — same gate, in words. Computed on the
   benchmark (BTC daily), NOT the charted asset. All four charts show the
   same regime by design.
3. **Markers on recent bars** — is anything armed or confirmed? (below)
4. **Your levels** — where price sits vs the green entry band, red stop,
   blue target.
5. **Zone / RSI / MACD rows** — context only. Zone never gates an add
   (premium veto retired 2026-07-26).

## Markers

| Marker | Meaning | What you do |
|---|---|---|
| Gray dot (below bar) | Rung touched — **armed, awaiting reclaim** | Nothing. A touch that keeps falling is distribution, not support |
| Teal **ADD** triangle | Confirmed reclaim (close back above rung + MACD hist rising, within 3 bars of the touch) **and** the gate is open | Run `/refresh` — this is the system's add setup |
| Orange **GATED** triangle | Same confirmed reclaim, but regime is risk_off | Noted, never fired. Watch for the regime to turn |
| Maroon **CHK** (above bar) | RSI ≥ 72 + MACD hist falling + ≥ 85% of range | Walk the SPEC Call Style downside checklist — the script can't see catalysts or structural bids, so this is a prompt, not a short signal |

## Lines

| Line | What it is |
|---|---|
| Gray / orange / blue | 20 / 50 / 200-SMA. Blue vs orange = posture: 50 above 200 = golden (uptrend) |
| Teal step line (orange when armed) | The add rung — 10-bar swing low, drawn only in golden posture. No line = no uptrend ladder = no add setups exist here |
| Faint gray band + mid | 60-bar dealing range + equilibrium. **Location context only** |
| Faint red | 2·ATR stop suggestion for a fresh long (engine's default) |
| Green shaded band / red / blue | Your entry zone / stop / target from Watchlist.md |

## Status table rows

| Row | Reading |
|---|---|
| Regime (benchmark) | RISK_OFF / NEUTRAL / RISK_ON — from BTC daily, not this chart |
| Gate | What the regime permits, in SPEC's words |
| Posture | golden / death / neutral — this asset's own trend |
| Range location | premium/discount + % of range. Context, never a gate |
| RSI(14) | Turns orange at ≥ 72 (overbought input to the CHK flag) |
| MACD hist | rising (green) / falling (orange) — the confirmation ingredient |
| Rung | clear / ARMED / CONFIRMED / GATED — the whole reclaim state in one cell |
| 2·ATR stop | Suggested invalidation for a fresh long at current price |
| Entry zone, Stop / Target | Your levels with live distance % |

## Alerts → actions

| Alert | Action |
|---|---|
| ADD — reclaim confirmed, gate open | `/refresh` the ticker before acting |
| Reclaim confirmed but GATED | Nothing; re-check when regime changes |
| Benchmark regime changed | Re-check the gate on every open call |
| Price entered the entry zone | `/refresh` |
| STOP breached (close basis) | Reduce/exit call per SPEC → `/refresh` + `/postmortem` |
| Target hit | `/refresh` to resolve the call |

## Known limits

- Last-bar values develop intraday; everything confirms at the daily UTC
  close. Small drift vs engine output on the live bar is expected;
  completed bars should match to rounding (same math: SMA posture, Wilder
  RSI/ATR, EMA MACD, same venue candles).
- The port is a mirror: if `docs/SPEC.md` changes, update the .pine and its
  SPEC-synced stamp by hand.
- Deliberately excluded: the death+premium early-recovery pattern (parked
  hypothesis, not a rule) and anything auto-trading.
