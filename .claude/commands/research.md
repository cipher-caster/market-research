# /research — Asset Research (stocks & crypto)

Run the Investments research workflow for the asset in `$ARGUMENTS`.

**Usage:**
- `/research MU` — deep dive (defaults to Tier 2)
- `/research BTC quick` — Tier 1 quick check
- `/research NVDA tier3` — high-stakes (opus workers)

## The contract lives in the README

`README.md (repo root)` is the source of truth for tiers, the
orchestrator pattern, the Prediction Record format, long-only rules, and the
calibration loop. **Read it and follow it.** This command only wires up the inputs.

## Steps

1. **Parse `$ARGUMENTS`** — extract the ticker (uppercase) and any tier hint
   (`quick`/`tier2`/`tier3`). Triage per the README (default Tier 2).

2. **Load context** — the asset's `data/Watchlist.md` row(s), `data/Research/{TICKER}.md` (the owner's
   thesis), and `data/Reports/_meta/calibration.md` (biases to counter-weight).

3. **Pull technicals** — run the deterministic snapshot. Use `--crypto` if Watchlist
   tags the asset `Type: Crypto`:
   ```bash
   cd ~/Documents/projects/market-research/engine
   [ -d .venv ] || (python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt)
   . .venv/bin/activate
   python technicals.py {TICKER}            # stock
   python technicals.py {TICKER} --crypto   # crypto
   ```
   Feed the snapshot to the Quant worker verbatim; do not recompute indicators.

4. **Run the workflow from the README** for the triaged tier, save the report to
   `data/Reports/{Crypto|Equities}/{TICKER}/`, then summarize to the owner and ask whether to update
   `data/Research/{TICKER}.md` — never auto-edit his thesis.
