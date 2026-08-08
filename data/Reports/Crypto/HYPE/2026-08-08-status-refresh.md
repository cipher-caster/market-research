v2 | Supersedes: 2026-07-28-deep-dive.md | Trigger: review date 2026-08-07 came due and ran a day over; the 2026-08-06 unlock that the v1 Avoid was built around has now printed, and it resolved roughly 20x smaller than the ceiling-rate precedent v1 assumed

## Prediction Record

**Verdict:** Avoid — unchanged action, but on a materially narrower basis, and the call is now one daily close from its own entry trigger. The central plank of v1's bear case has been removed: the 2026-08-06 unlock was scheduled at 433,000 HYPE (~$22.74M), not the 9.917M ceiling that v1's "two consecutive ceiling prints" precedent projected, so the supply-flow argument that drove the Avoid did not materialise. Price confirmed it by doing nothing — $54.445 at v1, $54.208 now, flat through the event it was told to stand aside for. What has NOT improved is the flywheel: 7-day revenue is $5.68M against the ~$7.5M/week that v1 called the trough, so kill criterion 3 is tracking toward a trigger rather than away from it, and the multiples expanded 12-15% on a flat price purely through decay. Action NOW: still no entry — regime is risk_off, and the reclaim rung at 54.331 has not printed a close above it (last completed close 54.109, short by $0.22). But the MACD histogram is now rising and positive (+0.2455, bullish cross), so the exact trigger v1 defined is live: a daily close above 54.331 fires it, at starter size only per the gate. This is an Avoid with the safety catch off, not an Avoid with conviction behind it.

**Targets**

| Horizon | Target | Return* | Basis |
|---|---|---|---|
| Swing ~Q3 2026 | $64.06 | +18.2% | Dealing-range equilibrium, recomputed on the current 60-bar range (51.153 — 76.975). Replaces v1's $64.81: the range floor dropped from 52.64 to 51.153, pulling the midpoint down. First structural magnet on a confirmed rung reclaim |
| EOY 2026 (base) | $76.98 | +42.0% | Retest of the range high / prior ATH zone. Explicitly contingent on flywheel stabilization (weekly revenue re-accelerating, buyback cadence recovering) — **that contingency has weakened since v1**, not strengthened |
| EOY 2026 (bull) | $150 | +176.7% | [UNVERIFIED] narrative-driven scenario (Arthur Hayes public call), not derived from measured-move technicals or valuation arithmetic — carried from v1 as a tail scenario, not a base case |

\*Returns from $54.208 (2026-08-08, own computation on OKX OHLCV). CoinGecko $54.19 and CoinPaprika $54.197 agree within 0.04%. Close-basis tests read the last completed daily bar, 2026-08-07 at $54.109.

**Entries & risk:**

| Field | Value |
|---|---|
| Direction | Avoid (primary, new entries). No downside flag: RSI 41.17 is soft momentum, not the ≥72 exhaustion plus deep-premium topping setup a short flag requires — and location is 11.8% of range, the opposite end. This stays a regime-and-fundamentals call, not an overbought one |
| Regime | risk_off — BTC 64,906 below its 200-MA 70,295, drawdown -21.2% from the 90-bar high. Add rungs suspended class-wide; new longs starter-size (1%) only at the owner's explicit call. Note the benchmark improved sharply since v1 (BTC 63,443 then, and its ETF flows have flipped from -$61.53M/week to +$626M over three sessions) without flipping the gate |
| Add levels | Rung: **54.331** — armed and unfired, and the closest trigger in the book. Requires a daily close above with MACD histogram rising; the histogram condition is now SATISFIED (+0.2455, crossed above signal), so price is the only missing leg, $0.22 away on the last close. Below: 51.153 (10/20/50-bar low, -5.64%) — note this replaced v1's 52.64 as the structural floor. Breakout add: daily close > 63.505 (20-bar resistance) on above-average volume. Current 2·ATR warning line $48.338 (not the invalidation) |
| Stop | $47.60 — unchanged, NOT breached; the lowest print in the window is 51.153 (2026-08-02), -12.2% above it. Deliberately below the structural low, as in v1, so ATR-scale noise cannot whipsaw it — that placement is now vindicated: the 51.153 print would have taken out a stop set at v1's 52.64 shelf and price recovered 6% within four sessions |
| Event window | 2026-08-06 unlock RESOLVED — 433,000 HYPE scheduled (~$22.74M), ~4.4% of the 9.917M ceiling; actual claimed amount is NOT verifiable on free sources (see Token Unlocks). Next scheduled unlock 2026-09-06, past this review date. CFTC onshoring has partially materialised but sideways to the thesis: Kalshi now lists CFTC-regulated HYPE-tracking perps built via HIP-4, which onshores exposure without routing fee flow to Hyperliquid's own engine |
| Confidence | medium — held, not raised. The action is unchanged and the reasoning is now cleaner (one leg resolved, one leg confirmed), but the two legs point opposite ways and roughly cancel. A downgrade is not warranted with the stop 12.2% away; an upgrade is not warranted with revenue below the trough v1 named |
| Review date | 2026-08-19 — pulled into line with the rest of the book so all five calls re-test together |

**Kill criteria:** walked individually — one did NOT trigger (favourably), one fired and reversed, one is tracking toward a trigger.
- Sustained daily closes below 52.64 confirming a lower-low structure into the bear-proven zone — **FIRED THEN REVERSED, and must be reported as such.** Two closes printed below the level (2026-08-01 at 52.226, 2026-08-02 at 52.614) and the intraday low made a genuine lower low at 51.153, which is now the 50-bar floor. But price reclaimed immediately and has closed above 52.64 in all five sessions since, topping at 56.979. Two bars under followed by a reclaim is a whipsaw, not the "sustained" break the criterion requires — the same reading the BTC v3 refresh applied to its own 50-MA print, applied consistently here. Not triggered; the level to re-test is now 51.153, not 52.64.
- The 2026-08-06 unlock prints near ceiling for a third straight month while AF buyback cadence stays pinned near ~$1-1.5M/day — **NOT TRIGGERED, and this is the version's main news.** The unlock came in at roughly 4.4% of ceiling. The structural-dilution thesis this criterion was designed to confirm is unconfirmed, and the burden of proof has shifted back to the bear case.
- Weekly protocol revenue fails to stabilize above ~$10M/week into September — **TRACKING TOWARD TRIGGER.** 7d revenue is $5.68M, below the ~$7.5M/week v1 called the current trough, and 24h revenue $963K sits under the $1-1.5M/day buyback midpoint the AF needs to sustain its pace. The criterion resolves in September and is not yet callable, but it is moving the wrong way and is now the load-bearing leg of the Avoid.

## Token Unlocks

| Date | Ceiling | Scheduled / claimed | % of ceiling | Note |
|---|---|---|---|---|
| 2026-06-06 | 9.917M | 9.92M | ~100% | [UNVERIFIED] inferred from ceiling match in v1, never directly confirmed |
| 2026-07-06 | 9.917M | 9.92M (~$645M) | 100% | Confirmed ([DEXTools](https://www.dextools.io/news/hyperliquid-hype-unlock-july-2026-buyback-fund-onchain-data)) |
| 2026-08-06 | 9.917M | **433,000 scheduled (~$22.74M)** | ~4.4% | Two sources agree on the scheduled figure ([Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/3-token-unlocks-watch-first-090731956.html), [CryptoRank](https://cryptorank.io/news/feed/de67b-august-week-1-token-unlocks)), both sourcing Tokenomist, and both note the actual claim is historically smaller than scheduled. **The claimed amount is [UNVERIFIED]** — DefiLlama's emissions API and Tokenomist's event history are both paywalled, so it cannot be confirmed on free sources |
| 2026-09-06 | 9.917M | scheduled | — | Core contributors; amount discretionary [UNVERIFIED] |

Core contributors hold 238M HYPE (23.8% of 1B total supply), vesting via monthly discretionary claims on the 6th. Sources: [tokenomist.ai](https://tokenomist.ai/hyperliquid), unlocks.app, DEXTools.

## Valuation — the decay, quantified

| Metric | v1 (2026-07-28) | v2 (2026-08-08) | Change |
|---|---|---|---|
| Price | $54.445 | $54.208 | -0.4% |
| Ann. fees (30d × 12) | $630.72M | $560.04M | **-11.2%** |
| Ann. revenue (30d × 12) | $442.56M | $389.52M | **-12.0%** |
| P/F (circulating) | 19.2x | 21.5x | +12.0% |
| P/S (circulating) | 27.4x | 31.0x | +13.1% |
| FDV/fees | 86.3x | 96.8x | +12.2% |

Mcap $12.06B (CoinGecko), FDV $54.19B on the 1B supply v1 standardized on; fees/revenue own computation on the DefiLlama API 2026-08-08. The point is the shape: the price did not move, so every multiple expanded purely through denominator decay. HYPE got ~12% more expensive in eleven days without a candle to show for it.

## What Changed Since Last Report (2026-07-28)

**The unlock — the reason this version exists.** v1 weighted flow over stock explicitly ("the review window is a flow-timescale question") and built the Avoid on 9.917M tokens hitting a float whose AF buyback could absorb ~8.5% of it. The actual event was ~433K scheduled. The flow argument was correct analysis applied to a month that did not happen. Worth stating plainly for the calibration record: v1's precedent rested on one confirmed ceiling print (July, DEXTools) and one [UNVERIFIED] inference (June), and a two-month pattern with one verified member was thinner evidence than v1's framing conveyed.

**Price/technicals:** $54.445 → $54.208 (-0.4%), but the path matters — a flush to 51.153 on 2026-08-02, a run to 56.979 by 2026-08-05, then back to 54.11. RSI 34.8 → 41.17. **MACD histogram turned positive (+0.2455) with a bullish cross** (MACD -2.147 over signal -2.3925), against v1's "negative and widening." Price is still below the 20-MA (-3.61%) and well below the 50-MA (-12.4%), so the broken short-term trend v1 named is intact; the 50-MA at 61.88 is the real overhead problem and nothing here touches it. Range location moved 60-bar: price now sits at **11.8% of range — discount**, the only discount asset in the book, because the range top rolled down from 76.975's shadow while the floor fell to 51.153.

**Positioning — the notable shift.** Funding has flipped **negative: -0.0039%/4h (~-8.6% APR)** against a 7d mean of +0.0043% (~+9.3% APR), while open interest rose +3.6%/24h and **+10.3%/7d**. Shorts are paying to hold a position into a catalyst that already resolved benignly. v1 recorded no crowding in either direction; this is the first crowded read on the book and it points up, not down. Not a signal alone, and explicitly not the basis for the call — but it is squeeze fuel sitting under an armed reclaim rung.

**Fundamentals:** TVL $6.29B → $6.27B, flat. Fees 7d $7.94M against a 30d weekly run-rate of ~$10.9M (-27%); revenue 7d $5.68M against a 30d weekly rate of $7.58M (-25%). The deceleration v1 measured has not stopped or stabilized — it has continued at roughly the same slope.

**Catalyst:** the CFTC path partially delivered but not in HYPE's favour as modelled. v1 called US onshoring "the largest asymmetric upside catalyst." What arrived is Kalshi listing CFTC-regulated perps that *track* HYPE via HIP-4, plus existing Bitwise/21Shares spot funds — onshore exposure to the price without US persons trading on Hyperliquid itself, so the geofenced TAM that v1 valued remains geofenced. Directionally positive for the asset, materially smaller than the catalyst as v1 framed it.

**Net:** v1 was an Avoid resting on three legs — broken trend, imminent supply, decaying flywheel. The supply leg is gone, the trend leg has softened into "still below the MAs but momentum crossed up," and the flywheel leg has strengthened as a bear argument. The Avoid survives on fundamentals and the regime gate, not on the event risk that motivated it, and it sits $0.22 from its own trigger.

## Self-Critique Pass

**Citation coverage:** technicals, regime, funding/OI, the dealing range and the per-bar close tests are own computation (OKX OHLCV, Binance USD-M) as of 2026-08-08. Fees/revenue/TVL are the DefiLlama API, same date. Market cap is CoinGecko, cross-checked against CoinPaprika within 0.04%. The unlock figure carries two source URLs but both trace to a single upstream (Tokenomist), so it is corroborated in publication and not in provenance — flagged rather than treated as two independent confirmations. The actual claimed amount is tagged [UNVERIFIED] and was not estimated.

**Source conflict:** the material one is v1's own record versus the August print — a 9.917M ceiling precedent against a 433K schedule, a 23x gap that free sources cannot fully explain (whether the schedule itself stepped down or the claim did). Rather than pick an explanation, this version reports the figure, marks the claim unverifiable, and draws the only conclusion that holds under either reading: the third consecutive ceiling print the kill criterion required did not occur. A second, smaller conflict: DefiLlama-derived annualized revenue ($389.5M) still conflicts with the ~$1.3B figure v1 flagged from a fundamental brief; unchanged and still [UNVERIFIED], and this report continues to use the DefiLlama basis.

**Calibration bias check:** active biases = none (Scoreboard still empty). The specific trap this pass is the sunk-cost read — v1 committed to Avoid, the feared event did not happen, and the temptation is either to defend the call by finding new reasons for it or to over-correct into a Buy because the scary thing passed. The report does neither: the kill criterion is explicitly marked NOT TRIGGERED and the bear case is described as having lost its main plank, while the action stays Avoid strictly because the regime gate and the unfired rung say so. The second guard, carried from the BTC v3 lesson, is consistency of reading: the 52.64 break is called a whipsaw on the same two-bars-then-reclaim standard BTC's 50-MA print was, rather than being scored strictly because it suits a bearish call.

**Premortem (on the CALL):** if this Avoid is wrong at 2026-08-19, the most likely path is the obvious one — price closes above 54.331 within days, the negative funding and +10.3% OI build fuel a squeeze toward the 20-MA at 56.24 and then the 63.5 breakout level, and the Avoid misses 10-15% because it deferred to a regime gate on a name whose own catalyst risk had already cleared. That is a known and accepted cost of the gate, not a modelling error. The second path is slower and worse for the thesis: revenue keeps sliding, September's criterion triggers, and the discount location turns out to be correctly priced decay rather than a dislocation.
