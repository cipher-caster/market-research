# /research-watchlist — Scheduled watchlist sweep (stocks & crypto)

Refresh every watchlist asset in one run: pull fresh technicals, write a compact
scoreable deep-dive per ticker, and finish with one consolidated **ranked** summary.

Designed to run on a schedule (local cron, headless), and also on demand.

**Usage:**
- `/research-watchlist` — full watchlist (all Status rows except `Resolved`/`Invalidated`)
- `/research-watchlist active` — only `Status: Active` rows (live calls; the nightly scope)
- `/research-watchlist all` — explicit full sweep (the weekly scope)

## The contract lives in the README

`README.md (repo root)` is the source of truth: long-only/no-leverage
rules, the Prediction Record format, the technicals layer, and the calibration loop.
**Read it and CLAUDE.md first, and never override the owner's documented preferences.**

There is **no `min_conviction=56`** in this vault — conviction is the README's 1–5 /
high-med-low confidence scale. Use that; do not invent a numeric floor.

## Steps

1. **Parse `$ARGUMENTS`** — scope is `active`, `all`, or empty (treat empty as `all`).

2. **Load shared context once** (not per ticker):
   - `data/Watchlist.md` — the Watchlist table.
   - `data/Reports/_meta/calibration.md` — inject the latest "Active biases" into every
     worker prompt as counter-weighting context.
   - Select tickers: from the Watchlist, take rows whose Status is not `Resolved` or
     `Invalidated`. If scope is `active`, keep only `Status: Active`. Note each
     ticker's `Type` (Stock / Crypto) — it decides the `--crypto` flag and the
     `data/Reports/Equities|Crypto/` path.

3. **Bootstrap the venv ONCE, before spawning anything** (avoids a concurrent-create
   race across parallel agents):
   ```bash
   cd ~/Documents/projects/market-research/engine
   [ -d .venv ] || (python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]")
   . .venv/bin/activate && python test_smoke.py
   ```
   If `test_smoke.py` fails, stop and report — do not spawn agents against a broken
   data layer.

4. **Spawn one sonnet agent per selected ticker, in parallel** (all Agent calls in a
   single message). Each agent gets the per-ticker brief below. Do NOT run full Tier 2
   (orchestrator + 3 workers) per ticker — this sweep is one agent per ticker by design.

5. **Consolidate** — after all agents return, write the ranked digest (step "Digest").
   Then surface the ranked summary to the owner. Make **no** changes to Watchlist levels,
   Research/ theses, or any config — those need the owner's explicit confirmation.

## Per-ticker agent brief (fill {TICKER}, {TYPE}, {ASSET_CLASS}, {CALIBRATION})

> You are researching **{TICKER}** ({TYPE}) for the owner's watchlist sweep. Follow
> `README.md (repo root)` exactly — long-primary (a losing bull case
> defaults to REDUCE/TRIM/WAIT/SKIP); you MAY add a secondary opt-in **short flag** only
> when the README's exhaustion+premium setup is present, with its own hard stop and cover
> target. Decisive and time-bound, stop mandatory on every long or short.
>
> 1. **Technicals (cited by construction):** the venv is already set up. Run:
>    ```bash
>    cd ~/Documents/projects/market-research/engine && . .venv/bin/activate
>    python technicals.py {TICKER}{CRYPTO_FLAG}
>    ```
>    The snapshot self-validates: if it errors or returns empty, say so plainly and fall
>    back to cited web numbers — do NOT invent levels. Read the add-ladder and SMC
>    premium/discount; do not recompute. Premium zone = not a low-risk add; name the
>    discount rung instead.
> 2. **Context:** read `data/Research/{TICKER}.md` (the owner's thesis — never edit it) and the most
>    recent file in `data/Reports/{ASSET_CLASS}/{TICKER}/`. Counter-weight these documented
>    biases: {CALIBRATION}
> 3. **Web check:** confirm price/catalyst freshness. Every numeric web claim needs a
>    source URL or an `[UNVERIFIED]` tag (cite-or-fail). Technicals output is pre-cited.
> 4. **Write** `data/Reports/{ASSET_CLASS}/{TICKER}/{YYYY-MM-DD}-watchlist-scan.md` with the
>    README's mandatory sections: the one-line Provenance header (v{N} / Supersedes / Trigger), then `## Prediction Record` at the TOP (Verdict, time-bound
>    Targets table, Entries & risk table with mandatory Stop, Confidence, Review date,
>    Kill criteria) and a short `## Self-Critique Pass` at the end. Keep the body compact
>    — this is a sweep, not a Tier 2 deep dive.
> 5. **Validate:** `python prediction_record.py <your report.md>` (from engine/, venv active) — must print OK before you finish.
> 6. **Return to the orchestrator** (do not print the whole report): one line each for —
>    ticker, Verdict, Direction, Confidence, swing target + %, stop, and a one-phrase
>    "what changed since last report / since the owner's thesis."

`{CRYPTO_FLAG}` is ` --crypto` for Type=Crypto, empty for Stock. `{ASSET_CLASS}` is
`Crypto` or `Equities`.

## Digest

Write `data/Reports/_meta/Watchlist-Scan/{YYYY-MM-DD}.md`:

- **One-line header:** date, scope (active/all), tickers covered.
- **Ranked table** — sort best opportunity → worst. Columns: Rank | Ticker | Direction |
  Confidence | Verdict (one line) | Swing target (+%) | Stop | What changed.
- **Flags** — any ticker where the technicals layer errored/fell back, any
  `[UNVERIFIED]` numbers, any thesis that may be invalidated (kill criteria near).
- Ranking logic: Active calls with a triggered/near kill-criterion rank first (action
  needed), then highest-confidence long setups sitting in discount, then watching/no-op.

Then give the owner the ranked table inline. End there — no auto-edits to thesis, levels, or config.
