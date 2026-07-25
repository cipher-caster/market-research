v3 | Supersedes: 2026-07-20-status-refresh.md | Trigger: level-watch sweep 2026-07-24 flagged ZEC IN ENTRY ZONE (470-501); /refresh to test whether the pullback is a buyable dip or momentum rolling over ahead of Ironwood + FOMC 2026-07-28/29

## Prediction Record

**Verdict:** Hold — unchanged call, degraded character. ZEC pulled back 7.1% to $501.25 (from $539.29 at v2), dropping into the top edge of the 470-501 entry zone. But this is momentum rolling over, not a buyable reclaim: price is now BELOW the 20-MA (514.72), the MACD has crossed bearish (hist -4.55 vs +5.24 at v2), and RSI cooled to 49.5. Location is still premium (62.3% of range) so it is not an add zone regardless, and regime is still risk_off so the ladder stays suspended. The 50-MA kill line ($466.49) cushion has narrowed from ~13% to ~7.4%. Next action unchanged: a daily close > $588.88 on above-average volume (breakout add) OR a regime flip that un-suspends the rungs on reclaim confirmation. The Ironwood/FOMC window (2026-07-28/29, 4 days out) is the decision, not this level.

**Targets**

| Horizon | Target | Return* | Basis |
|---|---|---|---|
| Swing (~Q3) | $644.64 | +28.6% | 50-bar resistance retest (technical measured move); unchanged computed level |
| EOY 2026 (base) | $600 | +19.7% | Analyst mid-to-upper distribution (July aggregate ~$551.56; 2026 range ~$230-850) — unchanged from v2 |
| EOY 2026 (bull) | $850 | +69.6% | [UNVERIFIED — analyst-model top-of-range, not a cluster]. Ceiling of published models; low confidence — unchanged from v2 |

\*Returns from $501.25 (2026-07-24, own computation on OKX OHLCV).

**Entries & risk:**

| Field | Value |
|---|---|
| Direction | Hold (primary). No downside flag: despite the bearish MACD cross, RSI 49.5 is neutral (not the ≥72 exhaustion the README requires) and location is mid-premium, not the deep 85-90% blow-off a downside flag needs. This is a cooling uptrend, not a distribution top |
| Regime | risk_off (BTC 65,013 < 200-MA 72,455 — class-wide add suspension). ZEC still the one idiosyncratic bull in the book: golden cross, +30.9% vs 200-MA. Rungs armed but SUSPENDED until the gate flips, or the owner overrides at starter size (1%) |
| Add levels | Ladder (near→mid): 496.48 (10-bar swing low, -0.95%) / 466.49 (50-MA, -6.93%) — reclaim confirmation required, suspended by regime regardless of touch. Rungs ticked down vs v2 as the pullback pulled the swing low in. Breakout add: daily close > $588.88 (20-bar resistance) on above-average volume. 2·ATR computed stop: $426.76 |
| Stop | $435 — unchanged. Sits below the 50-MA rung (466.49) and below the 2·ATR level (426.76 is now marginally under it — the ATR stop and the structural stop have nearly converged). Inside the June NU6.2 breakout shelf (420-430). No reason to move it |
| Event window | Ironwood (NU7) hard fork 2026-07-28, block 3,428,143, ~8am EST — new patched-Orchard shielded pool, quantum recoverability, Tachyon scaling. Collides with FOMC 2026-07-28/29. Both inside 4 days. The fresh shielded pool is both the fix and the fresh attack surface |
| Confidence | medium (unchanged) |
| Review date | 2026-08-04 (unchanged — right after the event window resolves) |

**Kill criteria:** walked individually below — all still CLEAR, but the trend kill has meaningfully less cushion.
- Daily close below $466.49 (50-MA) kills the idiosyncratic-bull/trend thesis — price ~7.4% above it (was ~13% at v2; cushion halved). CLEAR but the closest it has been.
- Loss of the EU AMLR transparent-mode carve-out kills the adoption thesis — effective 2027-07-01, ~1yr out; ZEC retains major US listings on the transparent-layer argument. CLEAR for the 2026 horizon.
- A repeat Orchard-class shielded-pool bug, especially around Ironwood — CLEAR now, but structurally the highest-probability source of a review-date surprise given the fork ships in 4 days.

## Token Unlocks

Fair-launch PoW asset — no unlock/vesting schedule (unchanged).

| Type | Detail | Source |
|---|---|---|
| Miner emission | 1.5625 ZEC/block, continuous, until the next halving (~late 2028) | Zcash protocol spec (block reward schedule) |
| Dev-fund split (post-NU6) | 80% miners / 8% ECC/Zcash Foundation grants / 12% Zcash lockbox | Zcash NU6 protocol spec |

## What Changed Since Last Report (2026-07-20)

**Price/technicals:** $539.29 → $501.25 (-7.1%). Still a golden cross (+30.9% vs 200-MA), but price lost the 20-MA (now -2.6% below it, was above at v2). **MACD flipped bearish: hist +5.24 → -4.55, MACD (15.33) now below signal (19.88)** — the momentum easing flagged in v2 has become a cross. RSI 56.98 → 49.46 (cooling continues). Range location 65% → 62.3% (still premium). Volume -75.5% vs 20-avg — even thinner than v2; this is a low-conviction drift into the event window, not volume-backed distribution.

**Positioning:** funding neutral (0.0078%/8h, ~8.5% APR), OI +0.7%/24h but -1.8%/7d — the position unwind noted in v2 continued at the margin. No squeeze, no crowded chase.

**Kill-line cushion narrowed:** the 50-MA rose (v2 466.49 → today 466.49, flat) while price fell, so the cushion to the trend kill halved from ~13% to ~7.4%. Nothing triggered, but this is the metric to watch through the fork.

**Catalyst:** Ironwood confirmed for 2026-07-28 (block 3,428,143), colliding with FOMC. No new verification needed since v2. Cypherpunk treasury leg (290,062 ZEC, ~1.76% of supply toward a stated 5% goal) unchanged.

**Net:** call unchanged (Hold), but the refresh is net *less* constructive than v2 — the constructive leverage-unwind read from v2 has given way to a bearish momentum cross and a halved kill-cushion, on very thin volume, right into a binary event. The entry-zone tag is a pullback with momentum rolling over, not a buyable dip — exactly the "touch, don't buy mechanically" case, doubly so under risk_off + premium.

## Self-Critique Pass

**Citation coverage:** technicals/funding/regime are own-computation per the README (as-of 2026-07-24, OKX OHLCV + Binance USD-M). No new web claims this refresh; catalyst/treasury facts carry forward from v2's cited sources. Bull/base targets remain analyst-model directional inputs, [UNVERIFIED] as before.

**Source conflict:** none material. Single OKX-aggregate anchor matching the owner's chart.

**Calibration bias check:** active biases = none (no matured predictions). The v2 refresh explicitly guarded against reading an OI unwind as bullish; this refresh guards the mirror error — over-reading a single bearish MACD cross on -75% volume as a reason to flip the call or raise a downside flag. It is a cooling uptrend into thin holiday-grade volume, and the call does not lean on it either way.

**Premortem:** if this Hold is wrong by 2026-08-04, the most likely path is an Ironwood technical hiccup (a bug in the fresh shielded pool or a messy fork) inside the event window — the kill criterion that is CLEAR now but structurally most exposed in the next 4 days, and one the price/leverage read cannot front-run. Second most likely is the mirror of v1's opportunity-cost miss: a clean fork + benign FOMC lets ZEC reclaim 588.88 while still gated risk_off/premium, and discipline correctly says no-add into a move that runs.
