v2 | Supersedes: 2026-07-19-deep-dive.md | Trigger: owner request — continue coverage; 1 trading day of new data + verification of the v1 open items (Ironwood date, AMLR carve-out, bull-target cluster, current-leg leverage)

## Prediction Record

**Verdict:** Hold — unchanged from v1. ZEC pulled back 2.7% to $539.29 on very thin volume while the v1 "futures-led leg" leverage tell unwound (OI -3.9%/24h, funding back to ~neutral) rather than blowing off, which is mildly constructive but low-conviction on this volume. Regime is still risk_off, location is still premium (65% of range), so the ladder stays armed-and-suspended. Next action is unchanged: a daily close >588.88 on above-average volume (breakout add) OR a regime flip to neutral/risk_on that un-suspends the rungs on reclaim confirmation. The decision that matters now is the Ironwood/FOMC event window (2026-07-28/29), not a level.

**Targets**

| Horizon | Target | Return* | Basis |
|---|---|---|---|
| Swing (~Q3) | $644.64 | +19.5% | 50-bar resistance retest (technical measured move); v1 was $640.28, computed level ticked up |
| EOY 2026 (base) | $600 | +11.3% | Trimmed from v1's $620 toward the analyst mid-to-upper distribution (July-2026 aggregate estimate ~$551.56; 2026 range ~$230-850, mid consensus ~$280-500) |
| EOY 2026 (bull) | $850 | +57.6% | [UNVERIFIED — analyst-model top-of-range, not a cluster]. Downgraded from v1's $925: the fresh survey shows $850 is the *ceiling* of published models, so $925+ overstates the tail. Low confidence |

\*Returns from $539.29 (2026-07-20).

**Entries & risk:**

| Field | Value |
|---|---|
| Direction | Hold (primary) |
| Regime | risk_off (BTC 64,999.90 < 200-MA 72,970 — class-wide add suspension, unchanged from v1). ZEC still the one idiosyncratic bull trend in the coverage set: golden cross, +40.9% vs 200-MA. Rungs armed but SUSPENDED until the gate flips to neutral/risk_on, or the owner overrides at starter size per the README risk_off rule |
| Add levels | Ladder (near→deep): 500.59 (20-MA) / 490.47 (10-bar swing low) / 470.03 (50-MA) — reclaim confirmation required, suspended by regime regardless of touch. Rungs ticked up ~1.5% vs v1 as the MAs rose. Breakout add: daily close >588.88 (20-bar resistance) on above-average volume |
| Stop | $435 — unchanged. The v1 structural stop (below the 470.03 50-MA rung, inside the June NU6.2 breakout shelf 420-430) still sits below the fresh 2·ATR computed stop ($457.25) and below all three ladder rungs. No reason to move it |
| Event window | CONFIRMED: Ironwood (NU7) hard fork activates 2026-07-28 at block 3,428,143, ~8am EST — new Ironwood shielded pool (patched Orchard), quantum recoverability, Tachyon scaling. Collides with FOMC 2026-07-28/29. Both land inside 8 days |
| Confidence | Medium (unchanged) |
| Review date | 2026-08-04 (right after the event window resolves) |

**Kill criteria:** All three CLEAR as of this refresh — walked individually below.
- Daily close below $470.03 (50-MA) kills the idiosyncratic-bull/trend thesis — price is ~13% above it. CLEAR.
- Loss of the EU AMLR transparent-mode carve-out kills the fundamental/adoption thesis — REFRAMED: AMLR applies from 2027-07-01, ~1 year out, not a 2026 event. ZEC's transparent addresses + viewing keys give exchanges a compliance argument Monero lacks; Coinbase, Robinhood, Phemex still list ZEC (XMR removed). Untested but not imminent. CLEAR for the 2026 horizon.
- A repeat Orchard-class shielded-pool bug, especially around the Ironwood upgrade, kills confidence in the tech — CLEAR now, but this is the single highest-probability source of a review-date surprise given Ironwood ships in 8 days. Ironwood *is* the patched-Orchard replacement, so the upgrade is both the fix and the fresh attack surface.

## Token Unlocks

Fair-launch PoW asset — no unlock/vesting schedule (unchanged from v1).

| Type | Detail | Source |
|---|---|---|
| Miner emission | 1.5625 ZEC/block, continuous, until the next halving (~late 2028) | Zcash protocol spec (block reward schedule) |
| Dev-fund split (post-NU6) | 80% miners / 8% Electric Coin Co./Zcash Foundation grants / 12% Zcash lockbox | Zcash NU6 protocol spec |

## What Changed Since Last Report (2026-07-19)

**Price/technicals:** $554.10 → $539.29 (-2.7%). Still a confirmed golden cross. RSI 60 → 56.98 (cooling). MACD histogram +7.87 → +5.24 (contracting — momentum easing, not reversing). Range location 69.9% → 65.0% (still premium, marginally less stretched). ATR 37.84 → 41.02. Volume -62.3% vs 20-avg (very thin — this is a low-conviction drift, not distribution or accumulation).

**The v1 leverage tell reversed — constructively.** v1 flagged the current leg as futures-led: OI +18%/24h with negative funding (~-0.0102%/8h) read as squeeze fuel *and* a chase-risk signature. As of today OI is -3.9%/24h and funding is back to ~neutral (-0.0033%/8h, ~-3.6% APR). The froth came out through position unwinding while price held within 3% — that de-risks the "buy-the-rumor / sell-the-news into FOMC" scenario somewhat, because a lot of the speculative long that would have sold the news is already gone. Caveat: it happened on the lightest volume in the window, so read it as air coming out of a thin market, not as a strong bid stepping in.

**Catalyst verification (the v1 open items):**
- *Ironwood:* v1 "~2026-07-28" now CONFIRMED — 2026-07-28, block 3,428,143.
- *AMLR:* v1 "unresolved carve-out" now dated — effective 2027-07-01; ZEC currently retains major US listings on the transparent-layer argument. Moved from an ambiguous risk to a known-timeline, not-yet-2026 risk.
- *Cypherpunk treasury:* accumulation accelerating — holdings now 290,062 ZEC (1.76% of supply), after adding 56,418 ZEC (~$29M); stated goal is 5% of network. Supports the real-bid leg of the thesis.
- *Bull target:* v1's $850-1,000 EOY cluster does not survive the fresh survey — published models top out near $850, so the tail was overstated. Bull target trimmed $925 → $850, base $620 → $600.

**Triggers:** no stop breach (price $539.29 vs stop $435, ~19% of headroom). No kill criterion triggered. Price is sitting almost exactly on the $540 level several chart analysts cite as the bull must-hold into an ATH push — worth watching as a sentiment line through the event.

**Net:** call unchanged (Hold). The refresh nets slightly constructive on process (leverage de-risked, AMLR pushed to 2027) and slightly less constructive on momentum (cooling into a thin tape), which cancel to the same Hold, same suspended ladder, same $435 stop.

## Self-Critique Pass

**Citation coverage:** Technicals/funding/regime are own-computation per the README (as-of 2026-07-20, OKX OHLCV + Binance USD-M). The four verified web items each carry named sources below; the Ironwood block height and AMLR effective date are the highest-confidence web claims (multiple concurring outlets). The bull/base target revision leans on aggregated third-party price models, which are directional-sentiment inputs, not hard valuation — flagged [UNVERIFIED] as in v1. No single-exchange price was used as the anchor; the technicals snapshot is the OKX aggregate that matches the owner's chart.

**Source conflict:** none material. Analyst price ranges vary widely by outlet ($230 floor to $850 ceiling); I led with the range rather than any single point estimate and used it only to trim the tail, not to set the call.

**Calibration bias check:** active biases = none (no matured predictions yet). Guarded against the obvious trap of this refresh — reading the OI/funding unwind as bullish. It is thin-volume air release, not demonstrated demand, and the call does not lean on it.

**Premortem:** if this refresh is wrong by 2026-08-04, the most likely path is an Ironwood technical hiccup (a bug in the fresh shielded pool, or a messy fork) inside the event window — the one kill criterion that is CLEAR now but structurally most exposed in the next 8 days. That would hit confidence in the tech directly and is not something the price/leverage read can front-run. Second most likely is the same regime-vs-trend miss as v1: a clean Ironwood + benign FOMC lets ZEC break 588.88 while still gated risk_off/premium, and discipline correctly says no-add into a move that runs — an opportunity-cost miss, not a thesis miss.

---
Sources (web-verified this refresh):
- Ironwood date/block: [crypto.news](https://crypto.news/zcash-confirms-july-28-ironwood-activation-after-orchard-bug/), [cryptotimes.io](https://www.cryptotimes.io/2026/07/10/zcash-confirms-july-28-ironwood-activation-zec-trades-near-500/), [zcashtracker.com](https://zcashtracker.com/news/zcash-nu7-introduces-tachyon-scaling-quantum-recoverability-new-ironwood-pool)
- AMLR / privacy-coin listing status: [leodex.io](https://leodex.io/learn/delistings/eu-privacy-coin-ban-2027), [ccn.com](https://www.ccn.com/education/crypto/countries-banning-privacy-coins-monero-zcash-2026/)
- Cypherpunk treasury: [prnewswire.com](https://www.prnewswire.com/news-releases/cypherpunk-accelerates-zcash-accumulation-increases-treasury-holdings-to-290-062-67-zec-302650408.html), [cryptorank.io](https://cryptorank.io/news/feed/677d3-zec-price-surges-as-zcash-treasury-cypherpunk-boost-holdings-to-290062-zec)
- Analyst forecasts: [coincodex.com](https://coincodex.com/crypto/zcash/price-prediction/), [changelly.com](https://changelly.com/blog/zcash-zec-price-prediction/)
