# /postmortem — Score a resolved call into the calibration loop

Write the event-driven calibration entry the moment a call resolves: stop breached,
target hit, kill criterion triggered, or the owner withdrew the call. This is what feeds the
auto-improvement loop — outcomes scored while fresh, not reconstructed at month-end.

Use it when: the level-watch sweep (`data/Reports/_meta/Level-Watch.md`) or a `/refresh`
flags a stop/target/kill event, or the owner says he exited/got stopped on something.

**Usage:**
- `/postmortem ZEC` — score the most recent resolved Prediction Record for one ticker

## The contract lives in the README

`README.md (repo root)` is the source of truth — Prediction Record format,
calibration methodology, risk rules. Read it and `data/Reports/_meta/calibration.md` first.

## Steps

1. **Parse `$ARGUMENTS`** — one ticker, uppercase. If the resolution event isn't obvious,
   ask the owner one question (what resolved: invalidation / target / kill / withdrawn) — don't guess.

2. **Load the call being scored:**
   - The report in `data/Reports/{Crypto|Equities}/{TICKER}/` whose Prediction Record made
     the now-resolved call — usually the latest, but pick the one that SET the levels
     (entry/stop/target), not a refresh that merely re-tested them.
   - The Watchlist row in `data/Watchlist.md` (entry zone, stop, target, status).
   - `data/Research/{TICKER}.md` for what the owner's own thesis said. **Read-only.**

3. **Pull the resolution price** — the engine lives at `~/Documents/projects/market-research/engine`
   (`. .venv/bin/activate` there, or use the `investments` MCP tools). Run `technicals.py`
   for the live read (`--crypto` for crypto), plus a cited web aggregate if the event was
   intraday. For crypto, also run `funding.py {TICKER}` — positioning at the moment of
   resolution (crowded shorts at a stop-out, crowded longs at a target) is exactly the
   context worth recording.

4. **Score it** per the calibration methodology:
   - **Direction** — right or wrong over the holding window, stated plainly.
   - **Magnitude** — vs the target return, within ±50% or not.
   - **Kill criteria** — walk each one: triggered / clear. Separate trade-discipline
     outcome (stop) from thesis outcome (kill criteria) — they often point opposite ways.
   - **Risk math** — planned R (entry→stop) vs realized R, including slippage/reaction
     lag. Name where the extra loss came from if realized > planned.

5. **Find the mechanical lesson.** The score is for the record; the lesson is for the
   system. Ask: was the stop placement sound? Did rungs sit between entry and stop
   (buying weakness)? Was the regime gate respected? Was the signal found late? One honest paragraph — what the SYSTEM
   (not the market) got right or wrong.

6. **Write the outcome** in `data/Reports/_meta/calibration.md`:
   - **Scoreboard row first** (top of the table): Scored date, ticker, report filename,
     direction, Conf (p) from the report's confidence label (high=0.7 / medium=0.55 /
     low=0.4), Dir hit y/n, Mag hit y/n (±50% of swing target return), realized %, event.
     Parse the report with `python prediction_record.py <report.md> --json` — score the
     typed fields, don't re-read prose.
   - **Then the dated entry** — `### YYYY-MM-DD — {TICKER} {event}` at the TOP of
     Entries: Event, Score, Mechanical findings, updated **Active biases**.
   - **Bias lifecycle:** each bias line carries `added | evidence: N | status`. Add a
     bias only with a named scored call as evidence; retire per the README rules
     (pattern corrected, or prior with no evidence after 5 calls in category). The
     injected context is only the active list — keep it short.

7. **Summarize to the owner, then stop.** Verdict + the one lesson. Do not edit
   `data/Research/{TICKER}.md` or the Watchlist row on your own — ask whether to flip
   Status (`Active` → `Resolved`/`Invalidated`) and apply only what the owner confirms.
