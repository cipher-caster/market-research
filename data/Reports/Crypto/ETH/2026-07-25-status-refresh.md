v2 | Supersedes: 2026-07-19-deep-dive.md | Trigger: owner request — "update ETH" status check ahead of FOMC 2026-07-28/29

## Prediction Record

**Verdict:** Hold — unchanged from v1, with momentum flattening. ETH sits at $1,859.17, dead flat vs. v1 ($1,864.50, -0.3%), still in premium (59.8% of the 60-bar range) under a risk_off regime, so there is no add here in either direction of the ladder: the reclaim trigger has NOT printed (needs a daily close > $1,957, the 20-bar high, with MACD histogram rising) and price has not pulled back into the $1,729-1,830 discount cluster. The constructive v1 momentum has stalled — MACD histogram has decayed from +12.6 to ~0 (-0.15 on the still-forming 2026-07-25 bar) — while ETH/BTC has ticked UP to 0.0290 from 0.0287, mild relative strength inside the kill/flip band. Next action unchanged: daily close > $1,957 with momentum turning (starter-size only under risk_off), or a confirmed-reclaim entry inside $1,729-1,830. FOMC is 3-4 days out (2026-07-28/29): per v1, no reclaim signal around the meeting counts as confirmed until it clears.

**Targets**

| Horizon | Target | Return* | Basis |
|---|---|---|---|
| Swing (~Q3) | $1,957 | +5.3% | 20-bar dealing-range high / reclaim trigger (own computation; was $1,944 at v1, shelf drifted up) |
| EOY 2026 (base) | $2,050 | +10.3% | Grind-and-stall base case unchanged from v1 — midpoint of $1,900-2,200 as price tests but fails to hold the 200-MA (now $2,147, drifting down toward price) |
| EOY 2026 (bull) | $2,900 | +56.0% | v1 bull basis intact: 200-MA reclaim undoing the death cross + MVRV mean-reversion off the <0.8 print + sustained ETF inflow trend (midpoint of $2,600-3,200; Coinedition, Everstake, TECHi via v1) |

\*returns from $1,859.17 (2026-07-25, own computation on OKX OHLCV).

**Entries & risk:**

| Field | Value |
|---|---|
| Direction | Hold (primary). No downside flag: RSI 54.3 is neutral, not the ≥72 exhaustion the README requires, and 59.8% of range is mid-premium, not the deep 85-90% blow-off — this is a stall inside a range, not a distribution top |
| Regime | risk_off — BTC $64,064 below its 200-MA ($72,302), drawdown -22.7% from the 90-bar high (own computation, OKX). Add rungs suspended across the class; stops still execute |
| Add levels | Rung 1 (reclaim): daily close > $1,957 (20-bar high) with MACD histogram rising — starter-size only while risk_off holds. Rung 2 (regime-defining): daily close > $2,147 (200-MA, down from $2,184 at v1 — the trend cost of going sideways is falling, which lowers the bar the bull case must clear). Quality entry remains the $1,729-1,830 discount cluster (2-ATR line $1,732 confirms the base), on reclaim confirmation only — price at 59.8% premium is not an add |
| Stop | $1,507 — 50-bar dealing-range floor (live 50-bar low $1,504.4 confirms the level still anchors the range). Currently clear by +23%; not near. Weekly close below = structural-impairment confirmation, target zone $1,300-1,500, per v1 |
| Event window | FOMC 2026-07-28/29 — 3-4 days out. High-beta ETH takes a hawkish surprise harder than BTC; treat no signal near the meeting as unconfirmed until it clears |
| Confidence | medium |
| Review date | 2026-08-19 |

**Kill criteria:** unchanged from v1 and both clear: (kill) weekly ETH/BTC close < 0.027 with mainnet fees still under $10M/day → avoid, target $1,300-1,500 — ETH/BTC is at 0.0290 (computed from OKX closes: 1,859.17 / 64,063.8), rising, not falling; (flip) weekly ETH/BTC close > 0.030 with fees back above $25M/day → buy despite the regime gate — not met, 0.0290 < 0.030 and no fresh fee print since v1's ~$10M/day.

## Token Unlocks

| Asset | Unlock Date | % of Supply | Notes |
|---|---|---|---|
| ETH | N/A | N/A | Fair-launch PoS asset — no unlock schedule (v1). Validator entry/exit queue remains flow context, not an unlock. |

## What Changed Since Last Report (2026-07-19)

- **Price: nothing.** $1,864.50 → $1,859.17 (-0.3%) over six days. The range itself shifted under a flat price: 60-bar range is now $1,504-2,097 (was anchored higher), putting the same price at 59.8% of range vs. 55.3% — slightly deeper into premium without moving.
- **Momentum: the v1 tailwind is gone.** MACD histogram +12.6 → -0.15 and RSI 59 → 54.3. Caveat: the 2026-07-25 daily bar is still forming (snapshot taken ~03:18 UTC), so the histogram print and the -96.9% volume figure are partial-bar artifacts — read this as "momentum flattened," not "bearish cross confirmed." Last completed bar: 2026-07-24.
- **Relative strength: mildly better.** ETH/BTC 0.0287 → 0.0290 (own computation from OKX closes). First upward tick since coverage began; still inside the 0.027-0.030 decision band, resolving nothing yet.
- **ETF flows: no new data, prior print confirmed.** The +$105.44M week (Jul 13-17, best since April 2026, ETHA +$135.31M) that v1 cited is confirmed by [The Market Periodical](https://themarketperiodical.com/2026/07/20/crypto-etfs-ethereum-etfs-post-105m-in-weekly-net-inflows/) and [KuCoin](https://www.kucoin.com/news/flash/ethereum-spot-etfs-record-105m-inflows-best-since-april-2026); the Jul 20-24 week's full print is not yet published as of this refresh. The two-week inflow inflection stands but has not yet compounded a third week on record.
- **Catalyst calendar: slightly worse than v1 assumed.** The Glamsterdam upgrade is reported pushed to Q3 2026 and the Ethereum Foundation cut its budget 40% with 20% staff layoffs (June 23) [UNVERIFIED — prediction-page sourcing quality, no primary source found; predates v1 but was not in it]. Directionally consistent with v1's "empty near-term catalyst calendar" — the empirical resolvers stay the levels, not the roadmap.
- **Positioning: clean.** Funding 0.0067%/8h now, 7d mean 0.0022% (~2.4% APR) — neutral, no crowding either way; OI flat (24h -1.4%, 7d +1.9%). Nobody is paying up on either side ahead of FOMC (Binance USD-M, 2026-07-25).
- **Triggers tested:** Stop $1,507 — clear by +23%, not near. Kill (ETH/BTC < 0.027) — clear, ratio rising. Flip (> 0.030) — not met. Reclaim trigger ($1,957) — not printed. Discount cluster ($1,729-1,830) — not reached. Nothing is in play; the call is idle by construction until a level or FOMC moves it.

## Self-Critique Pass

- **Citation coverage:** ~90% — technicals, regime, funding, and ETH/BTC are own computation (cited by construction: OKX OHLCV / Binance USD-M); ETF flow numbers carry source URLs; the EF-budget/Glamsterdam item is explicitly tagged [UNVERIFIED] (secondary prediction-page sourcing, no primary).
- **Source conflict:** OKX $1,859.17 (2026-07-25 partial bar) vs. Fortune's aggregate ~$1,868 (Jul 24) — ~0.5% apart on different timestamps; led with the exchange number per the repo's canonical-venue rule. The partial-bar caveat on momentum is flagged inline rather than presenting a forming candle as a completed signal.
- **Calibration bias check:** active biases — none (clean slate 2026-07-19); nothing to counter-weight yet.
