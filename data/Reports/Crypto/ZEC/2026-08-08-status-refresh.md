v6 | Supersedes: 2026-07-28-data-correction.md | Trigger: review date 2026-08-04 came due and ran 4 days over; first pass since Ironwood activated (2026-07-28 14:08 UTC) and since FOMC resolved hawkish. Owner also asked for a short-term (pre-September) target band, which is derived here rather than asserted

## Prediction Record

**Verdict:** Hold — every trigger tested and clear, and the thesis leg that was open at v5 has now closed in the call's favour. The Ironwood kill criterion is the story: 1,661,951 ZEC (45.4% of the sealed Orchard pool) has crossed the turnstile in 10.5 days with no supply discrepancy reported, which is the single strongest piece of evidence yet against the four-year counterfeiting bug having been exploited — a risk that was open and unresolvable at v4/v5. Price 507.77 versus a 435 stop (-14.3%) and a 50-MA kill line at 479.23 that the last completed close (2026-08-07, 511.50) cleared by +6.87%. Action NOW: none — no add (risk_off suspends the ladder, and price sits above every rung), no exit signal (nothing triggered). What has changed is not the action but the risk framing: v5 called the 435 stop a comfortable cushion at -6.4%, and on this asset's realized volatility that framing is wrong. At ATR 27.67 (5.4% of spot), 435 is ~2.6 ATR away, and from this exact configuration ZEC has tagged a level that far below within 23 days in 62% of historical episodes. The stop is a level that gets tested, not a floor that sits safely underneath. Next decision point is a daily close below 479.23, which is the downgrade signal — not 435.

**Targets**

| Horizon | Target | Return* | Basis |
|---|---|---|---|
| Near-term (to 2026-08-31) | $588.88 | +16.0% | Confluence: 50-bar high and the 2026-07-15 pivot both sit here, and the blended 14/30d-vol p75 (573.80) lands just under it. Tagged inside 23 days in 49% of comparable episodes — the realistic "it works" destination before September, and the level the standing swing target is NOT |
| Swing (~Q3) | $644.64 | +27.0% | 50-bar resistance retest (technical measured move); unchanged computed level, carried from v1. Reframed on horizon: only a 36% touch probability inside the August window, so this is a Q3/Q4 level and v5's implicit near-term reading of it was too aggressive |
| EOY 2026 (base) | $600 | +18.2% | Analyst mid-to-upper distribution (July aggregate ~$551.56; 2026 range ~$230-850) — carried from v2, unchanged |
| EOY 2026 (bull) | $850 | +67.4% | [UNVERIFIED — analyst-model top-of-range, not a cluster]. Ceiling of published models; low confidence — carried from v2 |

\*Returns from $507.77 (2026-08-08, own computation on OKX OHLCV). CoinGecko aggregate $507.53 and CoinPaprika $506.91 both agree within 0.2%. Close-basis tests below read the last completed daily bar, 2026-08-07 at $511.50, not the live price.

**Entries & risk:**

| Field | Value |
|---|---|
| Direction | Hold (primary). No downside flag: RSI 53.62 is nowhere near the ≥72 exhaustion a short flag requires, and range location 63.2% is ordinary premium, not a blow-off. Momentum turned constructive — MACD 2.5426 over signal 0.3403, histogram +2.20, a bullish cross that replaces the -9.63 histogram v5 carried |
| Regime | risk_off — BTC 64,906 below its 200-MA 70,295 (-7.7%), drawdown -21.2% from the 90-bar high, both deterministic conditions still tripped though both are improving (v3 BTC read -10.2% and -22.8%). Class-wide add suspension stands. ZEC keeps golden posture and the margin has recovered hard: +30.64% vs the 200-MA, against +21.1% at v5 |
| Add levels | Structural pullback ladder, all below price and all suspended by the gate: near $494.64 (-2.59%, 20-MA dynamic), mid $479.23 (-5.62%, 50-MA trend), deep $452.47 (-10.89%, 10-bar swing low). Breakout add: daily close > $588.88 on above-average volume. Rungs arm on touch, stay armed 3 bars, and require a daily close back above with MACD histogram rising — never on touch. Current 2·ATR warning line $452.43 (not the invalidation). There is no low-risk add here: price is extended above every rung, and the base rate below argues against chasing it |
| Stop | $435 — unchanged, NOT breached on any basis; the lowest print in the last 5 bars is $488.81 (2026-08-06). Sits below the 20-bar shelf ($451.80) and inside the June NU6.2 breakout shelf (420-430). Explicitly re-characterised from v5: -14.3% is ~2.6 ATR on ATR 27.67, which is inside normal three-week noise for this asset, not outside it. No reason to move the level; every reason to stop describing it as comfortable |
| Event window | Ironwood (NU6.3) ACTIVATED 2026-07-28 14:08 UTC at block 3,428,144 — resolved, see kill criteria. FOMC 2026-07-28/29 RESOLVED hawkish (held 3.50-3.75%, three dissents for a hike, no forward guidance). Next scheduled macro gate: FOMC 2026-09-15/16, past this review date. No ZEC-specific catalyst dated inside the window — the migration is a continuous process, not an event |
| Confidence | medium — unchanged. The thesis footing improved (kill criterion resolved favourably, momentum crossed up, 200-MA margin restored) but the historical base rate for this exact configuration is unfavourable and the two roughly cancel. Not upgraded to high on one good catalyst |
| Review date | 2026-08-19 — pulled into line with the BTC/ETH/SOL reviews so the coverage set re-tests together, and lands mid-window for the pre-September band above |

**Kill criteria:** walked individually — all three CLEAR, and the one that was open at v5 has now closed favourably rather than merely staying untriggered.
- Daily close below the 50-MA ($479.23) kills the idiosyncratic-bull/trend thesis — CLEAR by +6.87% on the 2026-08-07 close ($511.50). This is the live downgrade signal and the level to watch; it was -1.61% below the line at v5, so the swing is +8.5 points of cushion in eleven days.
- Loss of the EU AMLR transparent-mode carve-out kills the adoption thesis — effective 2027-07-01, outside the horizon. CLEAR.
- A repeat Orchard-class shielded-pool bug around Ironwood — CLEAR, and materially de-risked rather than merely unfired. 45.4% of the sealed pool has passed the turnstile with the accounting rule holding; an exploited Orchard would surface as a withdrawal claim exceeding verifiable deposits, and 10.5 days of migration at ~158K ZEC/day has produced no such report. Residual risk is real but shrinking with every migrated coin; it stops being a live criterion once migration clears a large majority.

## Token Unlocks

Fair-launch PoW asset — no unlock/vesting schedule (unchanged).

| Type | Detail | Source |
|---|---|---|
| Miner emission | 1.5625 ZEC/block, continuous, until the next halving (~late 2028) | Zcash protocol spec (block reward schedule) |
| Dev-fund split (post-NU6) | 80% miners / 8% ECC/Zcash Foundation grants / 12% Zcash lockbox | Zcash NU6 protocol spec |

## What Changed Since Last Report (2026-07-28 v5)

**Price/technicals:** $464.28 → $507.77 (+9.4%). Every read that was deteriorating at v5 has reversed: RSI 43.2 → 53.62, MACD histogram -9.63 → **+2.20 with a bullish cross**, price vs 20-MA -9.9% → +2.65%, vs 50-MA -1.61% → +5.96%, vs 200-MA +21.1% → +30.64%. Range location 54.1% → 63.2%. The 50-MA kill line that was live on the night of v5 was never triggered: the 2026-07-28 close reclaimed it and price has closed above it every session since. Volume remains extremely thin (-96.9% vs the 20-day average, on a still-forming bar), so every level here is lower-conviction than the numbers suggest.

**The Ironwood kill criterion resolved — the substantive change.** Verified against the migration tracker's own status API (`ironwood.live/v1/status`, as of 2026-08-08 02:10 UTC, chain height 3,440,191):

| Metric | Value |
|---|---|
| Orchard balance at activation | 3,660,833 ZEC |
| Orchard balance now | 1,998,882 ZEC |
| Migrated across the turnstile | **1,661,951 ZEC — 45.4% in 10.5 days** (~158,261 ZEC/day) |
| Ironwood pool balance now | 1,792,057 ZEC |

The Ironwood pool holds 130,106 ZEC *more* than has migrated out of Orchard, which is net new shielded value entering from transparent/Sapling — demand for the new pool, not just relocation into it. That is the shielded-adoption re-rating the call was built on, showing up as measured on-chain behaviour rather than narrative.

**Catalyst:** FOMC resolved hawkish, which the BTC v3 refresh already scored. It has not stopped ZEC: this is the coverage set's one asset that decoupled from a hawkish macro print, which is the whole premise of the "idiosyncratic uptrend" framing.

**Positioning:** funding 0.0071%/8h (~7.7% APR), 7d mean 0.0070% — neutral, no crowding, and notably NOT the crowded-long signature a +9.4% move often carries. OI +2.5%/24h, -1.7%/7d: modest fresh interest on rising price, no leverage froth. Cleaner than v5's "fresh positioning into weakness."

**New analysis — the short-term band (owner request).** Derived from 2,698 daily bars of Binance ZECUSDT history (2019-03 → 2026-08-08), because the OKX series only reaches back to 2025-11 and cannot support base rates. Realized vol is 63% (14d) / 82% (30d) annualized, so σ over the 23 days to 2026-08-31 is ~18.3% blended.

| Band | Level | Basis |
|---|---|---|
| Upside stretch | 644.64 | Standing swing target; 36% touch probability in-window |
| Upside target | 575-590 | Blended-vol p75 573.80 on the 50-bar high 588.88; 49% touch |
| **Central** | **480-510** | Vol model p50 507.30 (zero drift) tempered by a de-overlapped base-rate median of -8.5% (→464). Modal path is a drift back into the 20-MA/50-MA band |
| Downside | 448-457 | Blended-vol p25 448.50 |
| Invalidation | 435 | The stop; blended-vol p10 is 401, so a break has room below it |

The base rate is the uncomfortable part and is reported rather than buried: scored one observation per episode (n=39 episodes, golden posture with close above the 50-MA), ZEC's median 23-day forward return is **-8.5% with only 38% of episodes closing up**. ZEC chops and mean-reverts after strength more often than it extends. That argues against adding here — it does not argue for selling a held position, because the same distribution carries a fat right tail (episodes like 2025-10 ran +155% and +183%).

**Net:** the call is unchanged, and unlike v4/v5 it is unchanged from a position of strength rather than on the letter of an untriggered rule. What this version corrects is the risk description, not the action: v5's "comfortable" stop cushion was a percentage read that ignored this asset's volatility, and the honest framing is that 435 is inside three-week noise.

## Self-Critique Pass

**Citation coverage:** technicals, regime, funding/OI, dealing range, the vol bands and every base rate are own computation (OKX OHLCV, Binance USD-M, Binance ZECUSDT daily history) as of 2026-08-08 and count as cited per the spec. The migration figures come from the Ironwood tracker's own status API, a primary on-chain source, not from press. Analyst-derived EOY targets remain [UNVERIFIED], carried from v2 without re-endorsement.

**Source conflict — material, and resolved against the press.** Three different migration figures were in circulation, spanning a 1,100x range: a search summary citing "roughly 40,207 ZEC" migrated, [CoinDesk](https://www.coindesk.com/tech/2026/07/28/zcash-seals-usd1-7-billion-shielded-pool-as-ironwood-upgrade-activates) reporting "1,500 ZEC" on activation day, and a report of "more than 1 million ZEC." All three are stale snapshots of a fast-moving process rather than contradictions — CoinDesk's number is from 2026-07-28 itself. Rather than pick one, the figure was taken from the tracker's `/v1/status` endpoint and cross-checked internally: `orchard_at_activation` minus current `orchard` reconciles to the reported Ironwood pool balance within the expected margin of net new inflow. This is the v5 lesson applied — the most decision-critical number in the report goes through the most reliable channel available, not through a summarizer. Price: OKX 507.77 vs CoinGecko 507.53 vs CoinPaprika 506.91, all within 0.2%; led with OKX for continuity with the engine's computed levels.

**Calibration bias check:** active biases = none (Scoreboard still empty). Two specific guards this pass. First, the mirror of v5's error: v5 under-weighted a deteriorating tape by leaning on an untriggered rule, so v6 must not over-weight an improving one — hence confidence stays medium despite five indicators turning, and the unfavourable base rate is given equal billing with the favourable catalyst. Second, the base rate itself was nearly over-read: the day-weighted sample for "golden posture + BTC risk_off" showed a -26.3% median with P(up) 14%, which looked decisive and is an artifact — 99 observations across only 15 episodes, dominated by two long runs. De-overlapped to one observation per episode it collapses to 5 up / 9 down with a median near -6%. A "vol-compressed" cell showing -13.6% failed the same test (74 observations, ~3 effective). Neither is quoted as evidence; only the n=39 de-overlapped figure is. The spec's own backtest warns that overlapping windows inflate confidence, and that warning caught two false signals here.

**Premortem (on the CALL):** if this Hold is wrong at 2026-08-19, the most likely path is the base rate simply asserting itself — a drift back through 479 on thin August volume with no catalyst to react to, which the 50-MA downgrade line is designed to catch and which costs roughly 5-6% from here. Second is correlation: ZEC is one idiosyncratic uptrend inside a risk_off tape, and a BTC break of its 62,268 base would likely drag it regardless of migration data. Third, and least likely but most damaging, is a supply discrepancy surfacing in the remaining 54.6% of the Orchard pool — the one risk that price cannot front-run and that no amount of technical cushion protects against.
