# /refresh — Single-asset live status refresh (stocks & crypto)

Re-check ONE asset you already hold or watch: pull the live price + any catalyst since
the last report, diff against that report, and write a short dated refresh that
**explicitly tests the stop and kill criteria**. This is the "is anything broken right
now?" pass — lighter than `/research` (no orchestrator, no 3 workers), narrower than
`/research-watchlist` (one ticker, not the whole list).

Use it when: the owner names one asset and wants the current read, a stop/level may be in play,
a known catalyst date (unlock, earnings, ETF) just hit, or a scheduled review_date came due.

**Usage:**
- `/refresh HYPE` — live refresh of one asset

## The contract lives in the README

`README.md (repo root)` is the source of truth: long-only/no-leverage
rules, the Prediction Record format, the technicals layer, the calibration loop.
**Read it and CLAUDE.md first; never override the owner's documented preferences.** This
command only wires up the inputs — it does not change the rules.

## Steps

1. **Parse `$ARGUMENTS`** — one ticker, uppercase. If more than one is given, refresh
   the first and tell the owner the rest are out of scope (use `/research-watchlist` for many).

2. **Load context** (the asset's full local history — this is a diff pass, so the prior
   report is the baseline you compare against):
   - `data/Trade-Log.md` — the asset's Watchlist row (Status,
     Entry, Target, **Stop**, Type). Note `Type` → `--crypto` flag + `Crypto|Equities` path.
   - `data/Research/{TICKER}.md` — the owner's thesis and current Levels. **Read-only. Never edit here.**
   - The **most recent file** in `data/Reports/{Crypto|Equities}/{TICKER}/` — the baseline.
     Pull its Verdict, levels, kill criteria, and review_date.
   - `data/Reports/_meta/calibration.md` — latest "Active biases" to counter-weight.

3. **Pull the live read:**
   - **Technicals (cited by construction):**
     ```bash
     cd ~/Documents/projects/market-research/engine
     [ -d .venv ] || (python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt)
     . .venv/bin/activate
     python technicals.py {TICKER}            # stock
     python technicals.py {TICKER} --crypto   # crypto
     ```
     Interpret the snapshot; do not recompute. If it errors or returns empty (e.g. a
     crypto symbol Yahoo doesn't carry), **say so plainly and fall back to a cited live
     web price** — do NOT invent levels. Carry the add-ladder/SMC rungs forward from the
     baseline report when the script can't produce fresh ones.
   - **Regime gate (mandatory before any add/entry call):**
     ```bash
     python regime.py            # crypto benchmark (BTC-USD); use SPY for stocks
     ```
     State the regime in the Prediction Record. risk_off = add rungs suspended (stops
     still execute) — see the README's gate rules.
   - **Positioning (crypto only):**
     ```bash
     python funding.py {TICKER}  # funding + OI crowding read (Binance/Bybit)
     ```
     Crowded shorts at a support rung or crowded longs at a target are context the
     verdict must mention; protocol fundamentals via `python defillama.py {slug}`.
   - **Web check:** the live price from a **volume-weighted aggregate** (prefer CoinGecko
     aggregate / a primary feed over a single exchange; if two sources disagree, lead
     with the aggregate and note the conflict). Then any **catalyst since the baseline
     report** — unlock claimed vs scheduled, earnings, ETF flow, regulatory headline.
     Every numeric web claim needs a source URL or an `[UNVERIFIED]` tag (cite-or-fail).

4. **Test the triggers — this is the whole point.** Against the live price, state plainly:
   - **Stop:** is it breached? On an **intraday** print, a **daily close**, or not at all?
     The README's stop rule is *mandatory, no exceptions* — read a hard stop on the
     intraday/hard basis and name the close-basis fork honestly if price is hovering at it.
     A breached stop is a **reduce/exit** call. Per the README, you MAY also add a
     secondary opt-in **short flag** when the exhaustion+premium setup is present (hard
     stop above invalidation + a defined cover target) — but long stays the default.
   - **Kill criteria:** walk each one from the baseline report; mark triggered / near / clear.
   - **Add levels:** if price sits in premium / a no-trade air pocket, say there's no
     low-risk add and name the discount rung instead — never a cost-anchored "a bit below."

5. **Write** `data/Reports/{Crypto|Equities}/{TICKER}/{YYYY-MM-DD}-status-refresh.md`:
   - Provenance header first line (`v{N} | Supersedes: {baseline file} | Trigger: ...` — see README), then `## Prediction Record` at the TOP — Verdict (lead with any stop/kill event; put the
     action NOW + next trigger first), time-bound Targets table, Entries & risk table with
     the **mandatory Stop**, Confidence, **Review date**, Kill criteria.
   - `## What Changed Since Last Report ({baseline date})` — the diff: price move, catalyst
     resolution, whether a trigger flipped.
   - Short `## Self-Critique Pass` — citation coverage + any source conflict resolved
     (which feed you led with and why) + the calibration bias check.
   - Keep it compact. Separate **stopped-out** (trade discipline) from **thesis-dead**
     (fundamentals) when they point opposite ways — honor the stop without auto-killing the thesis.

6. **Summarize to the owner, then stop.** Give the verdict and the one decision he owns. Make
   **no** edits to `data/Research/{TICKER}.md` or the Trade-Log row on your own — a stop/kill
   event is the most tempting moment to rewrite the thesis; don't. Ask whether to:
   - append a dated entry to `data/Research/{TICKER}.md` Updates Log, and/or
   - flip the Watchlist Status (`Holding` → `Exited`/`Invalidated`) and adjust levels.
   Apply only what the owner confirms.
