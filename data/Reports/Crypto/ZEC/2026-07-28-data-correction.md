v5 | Supersedes: 2026-07-28-status-refresh.md | Trigger: data correction — two figures cited in v4 came from a web fetch whose summarizer mangled the source candles; both are restated here against engine-computed OKX bars. The call, the levels and every conclusion are unchanged.

## Prediction Record

**Verdict:** Hold — unchanged from v4; this version exists to correct two cited numbers, not to change the call. The trend-kill line is still live TONIGHT: price $464.28 sits 1.61% below the 50-MA ($471.90), and the kill reads on the 00:00 UTC daily close. The corrected reference bar is the 2026-07-27 close of **$476.71** (v4 said $475.50), which held the line by +1.04% against the 50-MA as of that bar ($471.80) — so the kill is untriggered, exactly as v4 concluded. The stop ($435) is not breached on any basis; today's true intraday low is **$463.00** (v4 said $464.14), leaving -6.3% of cushion. Ironwood has still NOT activated at time of writing: chain height 3,428,107 at 13:18 UTC vs activation block 3,428,143, roughly 50 minutes out. Action NOW: unchanged — no add (risk_off suspends the ladder; the near rung $463.00 needs reclaim confirmation), no exit signal (nothing triggered). The decision remains tonight's close versus $471.90.

**Targets**

| Horizon | Target | Return* | Basis |
|---|---|---|---|
| Swing (~Q3) | $644.64 | +38.8% | 50-bar resistance retest (technical measured move); unchanged computed level |
| EOY 2026 (base) | $600 | +29.2% | Analyst mid-to-upper distribution (July aggregate ~$551.56; 2026 range ~$230-850) — carried from v2 |
| EOY 2026 (bull) | $850 | +83.1% | [UNVERIFIED — analyst-model top-of-range, not a cluster]. Ceiling of published models; low confidence — carried from v2 |

\*Returns from $464.28 (2026-07-28 13:18 UTC, own computation on OKX OHLCV).

**Entries & risk:**

| Field | Value |
|---|---|
| Direction | Hold (primary). No downside flag: RSI 43.2 is far from the ≥72 exhaustion a short flag requires, and location is 54.1% of range — barely premium, not a blow-off. A de-risking flush into a binary event, not a distribution top |
| Regime | risk_off (BTC below its 200-MA — class-wide add suspension; own computation OKX 2026-07-28). ZEC keeps golden posture (+21.1% vs 200-MA) but the margin keeps eroding (was +30.9% at v3) |
| Add levels | Ladder (near): $463.00 (10-bar swing low, -0.28%) — reclaim confirmation required (rung arms on touch, stays armed 3 bars, buy needs a daily close back above it with MACD histogram rising), and suspended by regime regardless. Deeper: $455.00 (20-bar low). Breakout add: daily close > $588.88 on above-average volume. 2·ATR computed stop: $395.18 |
| Stop | $435 — unchanged, NOT breached. Today's true intraday low $463.00 (corrected from v4's $464.14) is 6.4% above it. Sits below the 20-bar shelf ($455) and inside the June NU6.2 breakout shelf (420-430). The structural stop remains the binding one; no reason to move it |
| Event window | Ironwood (NU6.3) activation block 3,428,143 — still PENDING at 13:18 UTC (height 3,428,107, ~50 min out). FOMC decision 2026-07-29. Both inside 36 hours |
| Confidence | medium — conditional on tonight's close, as in v4 |
| Review date | 2026-08-04 (unchanged). The agreed post-FOMC pass over all five crypto calls lands first and re-tests everything here |

**Kill criteria:** unchanged from v4 — none triggered, one live tonight.
- Daily close below the 50-MA ($471.90) kills the idiosyncratic-bull/trend thesis — LIVE: price is 1.61% below the line intraday; the 2026-07-27 close ($476.71) held it. Resolves at 00:00 UTC tonight.
- Loss of the EU AMLR transparent-mode carve-out kills the adoption thesis — effective 2027-07-01. CLEAR for the 2026 horizon.
- A repeat Orchard-class shielded-pool bug around Ironwood — PENDING: the fork has not activated yet; the fresh pool's first hours are the maximum-exposure window. CLEAR as of writing.

## Token Unlocks

Fair-launch PoW asset — no unlock/vesting schedule (unchanged).

| Type | Detail | Source |
|---|---|---|
| Miner emission | 1.5625 ZEC/block, continuous, until the next halving (~late 2028) | Zcash protocol spec (block reward schedule) |
| Dev-fund split (post-NU6) | 80% miners / 8% ECC/Zcash Foundation grants / 12% Zcash lockbox | Zcash NU6 protocol spec |

## What Changed Since Last Report (2026-07-28 v4, same day)

**Two corrected figures — this is the reason for the version.** v4 cited a prior daily close of $475.50 and an intraday low of $464.14. Both were read off a web fetch of OKX candles whose summarizer returned mangled dates (it labelled 2026-07 bars as 2025-04), and both are wrong. The engine's own routed OKX bars give:

| Figure | v4 (wrong) | v5 (engine-computed) | Does any conclusion change? |
|---|---|---|---|
| 2026-07-27 daily close | $475.50 | **$476.71** | No — held the 50-MA either way ($471.80 as of that bar) |
| 2026-07-28 intraday low | $464.14 | **$463.00** | No — stop $435 nowhere near on either figure |

**Why it happened and what stops it recurring:** the engine had no way to print a prior daily close, so a close-basis kill test — the most decision-critical number in a refresh — travelled through the least reliable channel available. Fixed the same day: `technicals.py` now reports the last completed daily close with same-bar MA distances, and `exchange_ohlcv.py --last N` prints dated OHLC rows. Both figures above come from those. See `docs/SPEC.md` ("Close basis vs live price — read the right bar").

**Price/technicals since v4 (hours, not days):** $466.69 → $464.28 (-0.5%); 50-MA gap widened from -1.11% to -1.61%; RSI 43.6 → 43.2; MACD histogram -9.48 → -9.63. Volume still thin (-54% vs 20-avg). Nothing structural moved.

**Catalyst:** Ironwood still pending at 13:18 UTC (36 blocks / ~50 minutes out), so the fork remains mid-flight and the shielded-pool kill criterion stays open.

**Related, outside this report:** the same engine work surfaced that SOL's 50-MA kill line is also in play tonight (2026-07-27 close 74.22 vs its 50-MA 74.19 — held by three cents). That belongs to the SOL call, not this one, but it is the second live trigger in the coverage set tonight and the post-FOMC pass must test it.

**Net:** call unchanged (Hold). The correction tightens the audit trail without moving a level, a target, or the verdict.

## Self-Critique Pass

**Citation coverage:** every number in this version is own computation on OKX OHLCV via the engine (as of 2026-07-28 13:18 UTC) except the chain height (Blockchair Zcash stats API, 3,428,107 at 13:18 UTC) and the analyst-derived EOY targets carried from v2, which stay [UNVERIFIED] as before. The two corrected figures are precisely the ones that previously lacked engine provenance — that is the lesson of this version.

**Source conflict:** none outstanding. The conflict that mattered — engine bars versus a web-summarised candle feed — is resolved in favour of the engine, which is the cited-by-construction path the spec requires; the web feed is retired from this role.

**Calibration bias check:** active biases = none (Scoreboard still empty). The guard specific to this version: a correction is a tempting moment to quietly re-litigate the call while restating numbers. It does not — the verdict, stop, targets, rungs and review date are identical to v4, and the corrections moved nothing. The opposite failure, burying an error rather than versioning it, is what the immutable-report rule exists to prevent.

**Premortem (on the CALL):** unchanged from v4 — if this Hold is wrong by 2026-08-04, the most likely path is tonight's close breaking the 50-MA and the one-bar grace costing 5-8% versus reducing today; second is an Ironwood incident in the fresh pool's first days. Both are timing/event risks, not thesis failures.
