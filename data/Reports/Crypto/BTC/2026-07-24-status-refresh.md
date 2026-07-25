v2 | Supersedes: 2026-07-19-deep-dive.md | Trigger: level-watch sweep 2026-07-24 flagged BTC IN ENTRY ZONE (63100-65500); /refresh to test whether the tag is a confirmed reclaim or passive drift ahead of FOMC 2026-07-28/29

## Prediction Record

**Verdict:** Hold — unchanged from v1. BTC drifted *up* into the 63,100-65,500 entry zone (65,013, +0.9% vs the v1 close) but has NOT confirmed the reclaim: the v1 trigger is a daily close above ~65,508 and price sits just under it. Momentum is the constructive change — MACD histogram has swung clearly positive (+218 vs "turning positive" in v1) and price holds above both the 20-MA and 50-MA in a 35.5%-of-range discount. But regime is still risk_off and FOMC (Jul 28-29) lands in 4 days, so the ladder stays armed-and-suspended. Next action unchanged: a daily close > $65,508 with MACD rising (starter-size only under risk_off), or a regime flip on a reclaim of the 200-MA ($72,455) that restores normal add operation.

**Targets**

| Horizon | Target | Return* | Basis |
|---|---|---|---|
| Swing (~Q3) | $67,924 | +4.5% | 60-bar dealing-range equilibrium (own computation) — first magnet on a confirmed reclaim of $65,508; level ticked down slightly from v1's $67,946 |
| EOY 2026 (base) | $78,101 | +20.1% | 50-bar range high / range resolution, contingent on ETF flow trend confirming positive (worker quant base scenario 68-78k) |
| EOY 2026 (bull) | $100,000 | +53.8% | Sustained 200-MA reclaim ($72,455) + flow reversal holding + MVRV re-expansion off the de-risked 1.19 print (worker quant bull midpoint) |

\*Returns from $65,012.90 (2026-07-24, own computation on OKX OHLCV).

**Entries & risk:**

| Field | Value |
|---|---|
| Direction | Hold — no new entry while regime is risk_off; no downside flag (RSI 53.5 neutral, price in discount at 35.5% of range — the exhaustion/premium setup for a downside flag is absent) |
| Regime | risk_off — BTC 65,013 < 200-MA 72,455 (-10.27%), death cross intact. The gap to the 200-MA has narrowed vs v1 (-11.8% → -10.3%), but partly because the 200-MA itself is declining (73,043 → 72,455), not purely price recovery. Add/buy calls stay suspended |
| Add levels | Rung 1: daily close > $65,508 (20-bar resistance / range equilibrium) — near-term reclaim, starter-size only per risk_off. Rung 2 (regime flip): daily close > $72,455 (200-MA) — restores normal add-ladder. Both fire on reclaim confirmation (close above with MACD histogram rising vs prior bar), never on touch. Current 2·ATR warning line: $61,619 (not the invalidation) |
| Stop | $57,748 — unchanged; 50/60-bar dealing-range low (fresh 50-bar low computed at $57,809, effectively the same). Price sits ~11.2% above it. A weekly close below re-anchors the range lower toward the bear's 44-50k target |
| Event window | FOMC 2026-07-28/29 — 4 days out. A hawkish surprise directly threatens any reclaim; no signal in the days around it should be treated as confirmed until it clears. This is the binary the call is waiting on |
| Confidence | medium (unchanged) |
| Review date | 2026-08-19 (unchanged from v1) |

**Kill criteria:** A weekly close below $57,748 with ETF flows still net negative kills the near-term reclaim thesis and shifts the call to avoid, targeting the 44-50k zone. CLEAR — price ~11% above the level, no breach.

## Token Unlocks

| Asset | Unlock Date | % of Supply | Notes |
|---|---|---|---|
| BTC | N/A | N/A | Fair-launch asset — no unlocks, no vesting, no allocator cliffs. Only structural issuance is continuous post-halving miner emission (~450 BTC/day), not a discrete unlock event. |

## What Changed Since Last Report (2026-07-19)

**Price/technicals:** $64,403 → $65,013 (+0.9%). Death cross intact but price now sits above both the 20-MA (+1.1%) and 50-MA (+2.9%); still -10.3% under the 200-MA. RSI 53.4 → 53.5 (flat, neutral). **MACD histogram +218 — decisively positive now** vs merely "turning positive" in v1; this is the clearest constructive tell in the refresh. Range location 32.7% → 35.5% (still discount — an add zone by location, though gated). Volume -38.8% vs 20-avg (thin; the drift into the zone is not volume-backed accumulation).

**Positioning:** funding neutral (0.0066%/8h, ~7.3% APR; 7d mean ~5% APR), OI +1.8%/24h and +2.3%/7d — mild fresh positioning, no crowding either way. No squeeze setup, no chase signature.

**Regime:** still risk_off, unchanged. The narrowing 200-MA gap is as much the moving average rolling down to meet price as price climbing — not yet a reclaim.

**Triggers:** the sweep's "IN ENTRY ZONE" tag is passive downside-then-sideways drift into the 63,100-65,500 band, NOT a confirmed reclaim. The v1 reclaim trigger ($65,508 daily close) has not fired. No stop breach, no kill.

**Net:** call unchanged (Hold). The refresh nets mildly constructive — MACD momentum built, price reclaimed the 20/50-MA in discount, leverage is clean — but the two things that would change the call (a confirmed $65,508 close and the FOMC print) are both still ahead. Waiting on the event is the correct action, not chasing the entry-zone tag.

## Self-Critique Pass

- **Citation coverage:** technicals/regime/funding are own-computation per the README (as-of 2026-07-24, OKX OHLCV + Binance USD-M). No new web numeric claims introduced this refresh; the target bases carry forward from v1's cited worker scenarios. No `[UNVERIFIED]` items added.
- **Source conflict:** none. Single OKX-aggregate anchor matching the owner's chart; no single-exchange price used for the call.
- **Calibration bias check:** active biases = none (no matured predictions). Guarded against reading the positive MACD swing as a buy signal — it is momentum inside a risk_off gate 4 days before FOMC, not a fired rung.
- **Premortem:** if this Hold-with-trigger is wrong at the 2026-08-19 review, the most likely reason is unchanged from v1 — a hawkish FOMC or tight rate path keeps BTC correlated to a strong dollar and TradFi risk-off, overriding the de-risked on-chain read. That is a regime/correlation miss, not a thesis failure in the MVRV/on-chain case.
