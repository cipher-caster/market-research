# Calibration Log

Rolling record of how this system's past predictions held up vs reality. Updated on resolution events and monthly.

**How to read this file:** the most recent entry is the current state. Older entries are kept for audit. The "Active biases" section in the latest entry is what gets injected into future Tier 2/3 agent prompts as counter-weighting context.

## Methodology

For each matured Prediction Record (where `review_date` has passed):
- **Direction:** correct if price moved in predicted direction, regardless of magnitude
- **Magnitude:** within ±50% of the target return
- **Kill criteria:** triggered as expected (yes/no/N/A)

Aggregate stats: hit rate by direction, by horizon, by sector; systematic biases.

## Scoreboard

Append-only, most recent first. Conf (p): high = 0.7, medium = 0.55, low = 0.4.

| Scored | Ticker | Report | Direction | Conf (p) | Dir hit | Mag hit | Realized % | Event |
|---|---|---|---|---|---|---|---|---|

## Entries

### 2026-07-26 — System-validation event: decision-rule backtest (no scored calls)

Not a call resolution — the Scoreboard is unchanged (still empty). The decision rules
themselves were backtested on 2017–2026 daily history (BTC/ETH/SOL/ZEC, Binance UTC
klines, engine-parity verified, regime gated on the BTC benchmark per SPEC). Full
study: `2026-07-26-rule-backtest.md` (this folder); rerun via `engine/backtest.py`.

Outcomes applied to `docs/SPEC.md` (owner-approved 2026-07-26):

- **Regime gate validated** — risk_off 90d forward median −4.1% vs +5–9% otherwise;
  not-risk_off beat risk_off by +0.28R (90% CI [+0.08, +0.48]). The only rule with
  measurable edge; operates as a binary (neutral ≈ risk_on). Unchanged.
- **Premium veto retired** — dealing-range zone is location context, not an add gate.
  Within its own domain (golden posture + not-risk_off) the zone predicted nothing:
  SPEC add vs any golden day −0.02R, equal 90d forward medians.
- **Reclaim confirmation kept as downside hygiene** — 3-bar arming window codified;
  no measurable edge inside uptrend pullbacks, kept as knife protection (ZEC-class gap).

Parked hypothesis (NOT a rule, third pass over the same data): death posture + premium
+ benchmark-not-risk_off (early recovery before the golden cross) was the best cell in
the study (+0.48R). Awaits out-of-sample evidence.

**Active biases:** none. (Bias lines require scored live calls; a backtest validates
rules, not calls. The doctrine changes live in `docs/SPEC.md`, not here.)

### 2026-07-19 — Clean slate

System reset with no prior research carried over. No matured predictions. No active biases yet — structural lessons from the previous iteration (regime gate, reclaim-confirmation rungs, alert-driven level watch) are already baked into the spec's rules, not carried as biases.

**Active biases:** none.
