# Decision-Rule Backtest — 2017–2026, BTC/ETH/SOL/ZEC

System-level study | Trigger: owner request ("can you backtest the approach?") | Not a call — no Prediction Record. Owner-approved outcomes applied to `docs/SPEC.md` on 2026-07-26. Reproduce with `engine/backtest.py`.

## Executive summary

The system's three execution rules were replayed over 11,393 asset-days of exchange history with engine-parity verification (no reimplementation, no lookahead). Results, in evidence order:

1. **Regime gate: validated — the one rule with measurable teeth.** Benchmark risk_off predicts poor forward returns on all four assets (90d forward median −4.1% vs +5–9% otherwise; not-risk_off beats risk_off by +0.28R, 90% CI [+0.08, +0.48]). The gate operates as a binary — neutral ≈ risk_on. **Kept unchanged.**
2. **Premium/discount zone: null within its own domain — veto retired.** Unconditionally, premium "beats" discount (+0.36R) — but that is a trend confound, not the doctrine. Conditioned on the asset's own golden posture and not-risk_off (the doctrine's actual domain), the SPEC add (discount rung + confirmed reclaim) matches simply adding on any golden day (−0.02R gap, P=46%) and 90d forward medians are equal (+5.7% vs +5.4%). The zone predicts nothing; the veto blocked adds for no measurable benefit. **Retired as a gate; kept as reported location context.**
3. **Reclaim confirmation: hygiene, not edge.** Right sign unconditionally (+0.10R over bare touch, positive on all four assets) but its value lives in downtrends — largely redundant with the regime gate. Inside uptrend pullbacks it adds nothing (−0.09R vs bare touch, P=38%). **Kept as cheap knife insurance; 3-bar arming window codified** (same-bar-strict fired 57 times in 9 years and tested negative).

## Method

**Data.** Paginated Binance daily klines (UTC), cross-checked against Yahoo:

| Asset | Bars | From | To | vs Yahoo median close diff |
|---|---|---|---|---|
| BTC | 3,266 | 2017-08-17 | 2026-07-26 | 0.089% |
| ETH | 3,266 | 2017-08-17 | 2026-07-26 | 0.095% |
| SOL | 2,176 | 2020-08-11 | 2026-07-26 | 0.091% |
| ZEC | 2,685 | 2019-03-21 | 2026-07-26 | 0.144% |

Consistent with the repo's 2026-06-11 exchange-vs-Yahoo validation (<0.1% on BTC/ZEC/HYPE).

**Engine parity (the anti-lookahead guarantee).** The rules were not reimplemented — the vectorized state was verified bar-for-bar against `technicals.compute()` and `regime.compute_regime()` run on prefix frames `df[:t+1]` at 6–8 sample dates per asset. All 51 numeric deviations found are explained bit-for-bit by the engine's own display rounding (max relative deviation 8.5e-3 = `pct_in_range` rounded to 1 decimal); regime labels and dealing-range zones match exactly. Every indicator is causal (trailing rolling/EMA/Wilder windows); rung levels use the prior bar's 10-bar low.

**Regime alignment.** The gate is computed on BTC as the class benchmark (per SPEC) and aligned by date to each asset — so for ETH/SOL/ZEC this tests the rule as written, out-of-benchmark.

**Two layers** (the system issues calls, not positions):

- **Layer A** — forward returns at 30/60/90/180 bars conditional on system state (overlapping windows; effective N ≈ shown N ÷ horizon).
- **Layer B** — call resolution: enter at signal close, stop = the engine's own 2·ATR, target 2R, first touch inside 180 bars, same-bar tie → stop (worst case), non-overlapping per state per asset. The 2R/2·ATR template is a scoring choice, not a SPEC rule.

**Baseline to beat:** buy-any-day = +0.21R pooled (+0.26R on BTC alone), 41% win rate. Crypto's secular updrift means any rule below this is subtracting value.

## Results — pooled (436 baseline calls)

| State | Calls | Win% | E(R) | 90d fwd median |
|---|---|---|---|---|
| baseline (any day) | 436 | 41% | +0.21 | +2.5% |
| benchmark risk_on | 242 | 43% | +0.29 | +5.3% |
| benchmark neutral | 191 | 46% | +0.36 | +9.4% |
| benchmark risk_off | 217 | 35% | **+0.04** | **−4.1%** |
| zone discount (unconditional) | 233 | 34% | +0.01 | +1.1% |
| zone premium (unconditional) | 387 | 42% | +0.26 | +4.7% |
| rung touch, no confirmation | 264 | 37% | +0.09 | +0.0% |
| rung reclaim (3-bar arming) | 238 | 40% | +0.19 | −0.2% |

Bootstrapped gaps (10k resamples, seed 42):

| Gap | Effect | 90% CI | P(gap>0) |
|---|---|---|---|
| not risk_off − risk_off | +0.28R | [+0.08, +0.48] | 99% |
| risk_on − risk_off | +0.25R | [+0.03, +0.47] | 97% |
| premium − discount (unconditional — confounded, see below) | +0.36R | [+0.10, +0.62] | 99% |
| reclaim − bare touch | +0.10R | [−0.11, +0.31] | 79% |

Per-asset gate edge (not-risk_off E(R) minus baseline): BTC +0.09, ETH +0.18, SOL −0.02, ZEC +0.14. SOL's exception is likely sample truncation — its history starts 2020-08 and never sees the 2018/2022 bears, the exact conditions the gate exists for.

## The decomposition that changed the conclusion

The unconditional premium-vs-discount comparison is confounded: SPEC applies the zone doctrine *inside an uptrend* (the add-ladder only exists in golden posture), but premium days are disproportionately uptrends and discount days disproportionately crashes — so the unconditional gap mostly re-measures momentum. The fair test is zone × the asset's own trend posture, gated not-risk_off:

| Cell | Days | Calls | E(R) | 90d fwd mean | 90d fwd median |
|---|---|---|---|---|---|
| golden + premium | 2,936 | 213 | +0.32 | +31.4% | +5.4% |
| golden + discount | 979 | 75 | +0.00 | +63.7% | +5.7% |
| death + premium | 957 | 75 | +0.48 | +17.8% | +13.9% |
| death + discount | 326 | 31 | +0.35 | +15.4% | +6.5% |
| golden+disc, bare touch | 176 | 52 | +0.38 | +63.0% | +4.1% |
| golden+disc, confirmed reclaim (**the SPEC add**) | 120 | 44 | +0.30 | +51.8% | +5.7% |
| golden any-day | 3,915 | 228 | +0.32 | +39.4% | +5.5% |
| death + discount, any regime (knife bucket) | 3,323 | 135 | +0.20 | +5.5% | −3.7% |

Head-to-heads:

| Gap | Effect | 90% CI | P(gap>0) |
|---|---|---|---|
| SPEC add − add in premium | −0.03R | [−0.43, +0.37] | 45% |
| SPEC add − golden any-day | −0.02R | [−0.42, +0.38] | 46% |
| confirmation − bare touch, within golden+discount | −0.09R | [−0.60, +0.41] | 38% |
| golden+premium − golden+discount | +0.32R | [−0.00, +0.64] | 95% |

The last row overstates: the 90d forward *medians* of the two cells are equal (+5.4% vs +5.7%), golden+discount's forward *mean* is far higher (+63.7% — early-bull recoveries), and per-asset the split is not unanimous (golden+discount: BTC +0.29, ETH −0.12, SOL −0.17, ZEC −0.05). The E(R) gap is substantially a stop-width artifact — volatile pullbacks sweep a 2·ATR bracket before recovering, which a call scored at review-date would still count as a hit. Layer A medians are closer to how the calibration loop actually scores.

**Corrected finding: zone is a null within its domain, not an inverted signal.** Neither "wait for discount" nor "premium is better" survives conditioning.

## Withdrawn intermediate claims (recorded for audit)

- *"Premium/discount is decisively backwards, costs 0.36R as written"* (BTC-then-pooled unconditional runs) — withdrawn; trend confound.
- *"Discount + reclaim is the best cell in the study (+0.45R)"* (BTC-only, N=15) — withdrawn; did not replicate (pooled +0.07R, P=61%).

## Parked hypothesis — explicitly NOT a rule

Death + premium + benchmark-not-risk_off (early recovery off a bear bottom, before the golden cross confirms) is the best cell in the study (+0.48R; BTC +0.71, ETH +0.91). This dataset has now been mined three times; this pattern goes down as a hypothesis awaiting out-of-sample data, not a spec change.

## What this study does NOT license

- No change to the downside-flag criteria (Call Style) — "deep premium ≥85–90%" as exhaustion evidence was not tested (long adds only).
- No change to any live call, level, stop, or target on the Watchlist.
- No extension to equities — crypto-only sample, gated on the crypto benchmark.
- No autonomy changes — the backtest is manual-run only.

## Caveats

- **Correlation:** four BTC-correlated survivors sharing two bears and two recoveries — effective independent sample closer to 1.5–2 assets than 4; every CI above is optimistic. The per-asset unanimity checks matter more than the pooled intervals.
- **Survivorship:** all four are still-listed, still-liquid assets; these rules on a dead alt would look worse.
- **Template dependence:** Layer B expectancy is entangled with the 2R/2·ATR bracket (demonstrated by the golden+discount mean/median divergence).
- **Multiple passes:** the same data was queried three times (BTC run → pooled run → decomposition). The 3-bar arming window was tuned on BTC after the strict form failed, then held on ETH/SOL/ZEC (+0.16/+0.12/+0.29 vs touch +0.08/+0.07/+0.19) — partially out-of-sample, still a tuned rule.
- **Overlap:** Layer A windows overlap; treat the shown N accordingly.

Source: own computation on paginated Binance UTC daily klines, cross-checked vs Yahoo Finance; engine parity vs `technicals.compute()` / `regime.compute_regime()`, as of 2026-07-26.
