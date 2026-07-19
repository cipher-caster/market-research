# Calibration Log

Rolling record of how this system's past predictions held up vs reality. Updated on resolution events and monthly.

**How to read this file:** the most recent entry is the current state. Older entries are kept for audit. The "Active biases" section in the latest entry is what gets injected into future Tier 2/3 agent prompts as counter-weighting context.

## Methodology

For each matured Prediction Record (where `review_date` has passed):
- **Direction:** correct if price moved in predicted direction, regardless of magnitude
- **Magnitude:** within ±50% of the target return
- **Kill criteria:** triggered as expected (yes/no/N/A)

Aggregate stats: hit rate by direction, by horizon, by sector; systematic biases.

## Entries

### 2026-07-19 — Clean slate

System reset with no prior research carried over. No matured predictions. No active biases yet — structural lessons from the previous iteration (regime gate, reclaim-confirmation rungs, alert-driven level watch) are already baked into the spec's rules, not carried as biases.

**Active biases:** none.
