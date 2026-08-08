# /research-watchlist — Scheduled watchlist sweep (stocks & crypto)

Refresh every watchlist asset in one run: one `asset-analyst` per ticker in parallel, one
`report-verifier` per report, then **you** write the consolidated ranked digest. The
cross-asset read is the one part that stays in the main session — only it holds every return
block at once.

Designed to run on a schedule (local cron, headless), and also on demand.

**Usage:**
- `/research-watchlist` — full watchlist (all Status rows except `Resolved`/`Invalidated`)
- `/research-watchlist active` — only `Status: Active` rows (live calls; the nightly scope)
- `/research-watchlist all` — explicit full sweep (the weekly scope)

## The contract lives in docs/SPEC.md

`docs/SPEC.md` is the source of truth: the tiers, the risk rules, the Prediction Record format,
the technicals layer, the orchestration rules, and the calibration loop. The **agent briefs in
`.claude/agents/`** are the source of truth for how each role works — this command does not
restate them. **Read the spec and CLAUDE.md first; never override the owner's documented
preferences.**

There is **no `min_conviction=56`** in this system — conviction is the spec's high/medium/low
confidence scale. Use that; do not invent a numeric floor.

## Steps

1. **Parse `$ARGUMENTS`** — scope is `active`, `all`, or empty (treat empty as `all`).

2. **Load shared context once** (not per ticker):
   - `data/Watchlist.md` — the calls table.
   - `data/Reports/_meta/calibration.md` — the latest **Active biases**, verbatim, to inject
     into every agent brief.
   - Select tickers: rows whose Status is not `Resolved` or `Invalidated`. If scope is
     `active`, keep only `Status: Active`. Note each ticker's `Type` — it decides the
     `--crypto` flag and the `Crypto|Equities` path — and its most recent report (the baseline
     filename and version).

3. **Bootstrap the venv ONCE, before spawning anything** (parallel agents creating a venv race
   each other):
   ```bash
   cd engine && [ -d .venv ] || (python3 -m venv .venv && .venv/bin/pip install -e ".[dev]")
   .venv/bin/python test_smoke.py
   ```
   If `test_smoke.py` fails, stop and report — do not spawn agents against a broken data layer.

4. **Spawn one `asset-analyst` per selected ticker, all in a single message** so they run in
   parallel. Each brief carries: ticker, Type, asset-class path, the baseline report path and
   version, the Watchlist stop/entry/target, today's date, the active calibration biases
   verbatim, and the trigger (`scheduled sweep`). Output filename:
   `{YYYY-MM-DD}-watchlist-scan.md`. Tell each one to keep the body compact — this is a sweep,
   not a Tier 2 deep dive.

   Do **not** run the full Tier 2 worker trio per ticker; the sweep is one analyst per ticker
   by design.

5. **Spawn one `report-verifier` per returned report**, again in a single parallel message.
   `NEEDS FIX` → send the blockers back to that ticker's `asset-analyst` via `SendMessage` so
   it keeps its context, then re-verify. Loop until every report PASSes. A ticker still failing
   after two rounds gets flagged in the digest rather than blocking the sweep.

6. **Write the digest yourself** (step "Digest" below), from the return blocks — do not read
   the report bodies back.

7. **Commit — main session only, agents never run git.** One commit after every agent has
   returned: the per-ticker reports, the digest, and a dated one-line pointer appended to each
   `data/Research/{TICKER}.md` Updates Log (pure-append Edit; pointers only, never analysis).

8. **Surface the ranked table inline, then stop.** Make **no** changes to Watchlist levels,
   Research/ theses, or any config — those need the owner's explicit confirmation. Name the
   decisions he owns.

## Digest

Write `data/Reports/_meta/Watchlist-Scan/{YYYY-MM-DD}.md`:

- **One-line header:** date, scope (active/all), tickers covered, regime.
- **Ranked table** — best opportunity → worst. Columns: Rank | Ticker | Direction |
  Confidence | Verdict (one line) | Swing target (+%) | Stop | What changed.
- **Correlation flag** — when 3+ Active calls share one beta cluster (all crypto = BTC beta;
  multiple AI-infra equities), say so in one line: each call in a cluster is weaker than it
  looks alone, and a `risk_off` regime hits the whole cluster at once. This is the read no
  single-ticker agent can produce, which is why it lives here.
- **Flags** — any ticker where the technicals layer errored or fell back, any `[UNVERIFIED]`
  numbers, any thesis whose kill criteria are near, any report that did not reach verifier PASS.
- Ranking logic: Active calls with a triggered/near kill criterion rank first (action needed),
  then highest-confidence long setups at or near a confirmed rung reclaim, then watching/no-op.
