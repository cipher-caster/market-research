# /refresh — Single-asset live status refresh (stocks & crypto)

Re-check ONE asset with an active call: pull the live price + any catalyst since the last
report, diff against that report, and write a short dated refresh that **explicitly tests the
stop and kill criteria**. This is the "is anything broken right now?" pass.

This runs as **one `asset-analyst` plus one `report-verifier`** — the Refresh & Scan tier in
`docs/SPEC.md`. You orchestrate; you do not write the report yourself.

Use it when: the owner names one asset and wants the current read, a stop/level may be in play,
a known catalyst date (unlock, earnings, ETF) just hit, or a scheduled review_date came due.

**Usage:**
- `/refresh HYPE` — live refresh of one asset

## The contract lives in docs/SPEC.md

`docs/SPEC.md` is the source of truth: the tiers, the Prediction Record format, the technicals
layer, the orchestration rules, the calibration loop. The **agent briefs in `.claude/agents/`**
are the source of truth for how each role works. This command only wires up the inputs — it
does not restate either.

## Steps

1. **Parse `$ARGUMENTS`** — one ticker, uppercase. If more than one is given, refresh the first
   and tell the owner the rest are out of scope (use `/research-watchlist` for many).

2. **Resolve the inputs** (cheap reads, main session — the analyst re-reads what it needs):
   - `data/Watchlist.md` — the asset's row. `Type` decides the `--crypto` flag and the
     `Crypto|Equities` path. If there is no row, or Status is `Resolved`/`Invalidated`, say so
     and ask before proceeding.
   - The most recent file in `data/Reports/{Crypto|Equities}/{TICKER}/` — the baseline filename
     and its version number. If none exists, this is a first call: run `/research` instead.
   - `data/Reports/_meta/calibration.md` — the latest **Active biases**, verbatim.

3. **Bootstrap the venv ONCE, before spawning:**
   ```bash
   cd engine && [ -d .venv ] || (python3 -m venv .venv && .venv/bin/pip install -e ".[dev]")
   .venv/bin/python test_smoke.py
   ```
   If the smoke test fails, stop and report — never spawn against a broken data layer.

4. **Spawn `asset-analyst`.** The brief must carry: ticker, Type, asset-class path, the
   baseline report path and version, the Watchlist stop/entry/target, today's date, the active
   calibration biases verbatim, and the trigger for this refresh (owner request / review date
   due / level event / catalyst). State the output filename: `{YYYY-MM-DD}-status-refresh.md`.

5. **Spawn `report-verifier`** on the returned report path, with the same date and biases.
   - `NEEDS FIX` → send the blockers back to the `asset-analyst` (`SendMessage`, so it keeps
     its context) and re-verify. Loop until PASS.
   - If the verifier's independent premortem names a different primary failure mode than the
     author's, both belong in the Self-Critique Pass.

6. **If the call changed** — verdict flip or confidence upgrade versus the baseline — spawn a
   `bear-worker` before accepting it, and have the analyst answer its strongest hit in the
   report. A changing call is the highest-risk moment in this system.

7. **Commit — main session only, agents never run git.** After the report validates
   (`prediction_record.py` prints OK) and the verifier PASSes: append the dated one-line
   pointer (version, verdict, report path) to `data/Research/{TICKER}.md` Updates Log via a
   pure-append Edit, and commit the report + pointer together. Pointers only, never analysis.

8. **Summarize, then stop.** Give the owner the verdict and the one decision he owns, from the
   analyst's return block — do not paste the report. Everything else is ask-first; a stop/kill
   event is the most tempting moment to rewrite the thesis, so don't. Ask whether to:
   - add any thesis-content entry to `data/Research/{TICKER}.md` beyond the pointer, and/or
   - flip the Watchlist Status (`Active` → `Resolved`/`Invalidated`) and adjust levels.

   Apply only what the owner confirms.
