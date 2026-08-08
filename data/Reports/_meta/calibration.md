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

### 2026-08-08 — Audit event: first independent verification pass (no scored calls)

Not a call resolution — the Scoreboard is unchanged (still empty). This records the first
run of the mandatory `report-verifier` stage introduced 2026-08-08, and what it found.

Five reports audited: ETH v3 and SOL v2 pre-commit, plus BTC v4, ZEC v6 and HYPE v2
retrospectively (all three written the same day under the old inline process, already
committed in `fdbf0f5`, and therefore immutable — corrected via dated
`*-audit-correction.md` reports rather than edits).

**Ten blockers, zero noise.** Every finding was reproduced from primary data. The
consequential ones inverted a claim rather than polishing it:

- **HYPE v2** — the 54.331 reclaim trigger was described as pending "$0.22 away" when it
  had fired 08-05/06 and reversed 08-07. The report applied "fired then reversed" scoring
  to its own bear trigger but not its bull trigger.
- **ZEC v6** — the n=39 de-overlapped base rate was correct and independently reproduced,
  but the +155%/+183% fat-tail figures quoted beside it were within-episode double-counts
  of a single already-counted episode: the exact overlapping-window artifact the report
  claimed to have discarded.
- **SOL v2** — an undisclosed EOY-base target cut (87.79 → 83.98) that never referenced the
  live Watchlist row and would have reached the owner invisibly.
- **BTC v4** — the 65,508 reclaim rung described as "armed since 07-26" when its 3-bar
  window expired unconfirmed at the 07-28 close, carried word-for-word from v3.

**Three defect classes recurred across different authors and tickers**, so they were fixed
as code rather than prose: Self-Critique heading completeness, ATR multiple on the Stop,
premortem classification label. Now gated by `prediction_record.py --strict` (WARN by
default so the immutable back catalogue still validates). Of the eight non-clean reports,
*every one* is missing `Internal consistency` specifically — the check that would have
caught both the SOL target cut and the HYPE trigger contradiction.

**Adversarial value runs both ways.** Correction authors caught errors in the verifiers: a
premortem resting on "six straight up-closes" that were actually 4 up / 2 down; a decay
figure computed against a 30-day window containing its own comparison period. One found a
gate-semantics error no prior pass saw — `risk_off` is an OR-gate, so v4's "closer to
flipping than ever" addressed only the drawdown leg while the 200-MA leg was binding and
nowhere near clearing. Neither the author nor the auditor is presumed right; both re-derive.

**Active biases:** none. (Bias lines still require scored live calls — this is a process
audit, not a resolution. The doctrine and tooling changes live in `docs/SPEC.md` and
`engine/prediction_record.py`, not here.)

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
