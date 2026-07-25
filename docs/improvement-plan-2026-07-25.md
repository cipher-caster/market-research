# Improvement Plan — 2026-07-25 review

Source: full-repo critique (spec, all engine modules, tests, CI, data layer),
second-pass verified. Work is delegated in batches; statuses updated as they land.

## A. Confirmed bugs

- **A1 — `downside_flag` parses inverted.** `engine/prediction_record.py:153`
  matches the substring "downside flag", but every real report states the
  *absence* of one in the Direction cell ("no downside flag", "Downside flag:
  none") — all parse as `True`. Scoreboard is still empty, so nothing is
  corrupted yet; it would mis-record at first scoring (first review dates
  ~2026-09-30). Fix: affirmative-only, negation-aware parse + regression tests
  covering the real phrasings (the schema test never asserted this field).
- **A2 — return sign dropped.** `engine/prediction_record.py:55` `_NUM` has no
  sign group, so `-12%` parses as `12.0`. Latent (no negative target returns
  yet) but will misrecord a downside flag's reversal return. Fix with A1.
- **A3 — stop breach only sees the latest bar's low.** `engine/check_levels.py`
  `live_price` reads `Low.iloc[-1]`; a stop gapped through intraday and
  recovered before the next sweep reports nothing — the exact ZEC failure mode
  ("stop found 2% late"). Fix: check the min low over the last ~5 daily bars
  for Active rows; report an intra-period breach distinctly.

## B. Consistency debt

- **B1 — CLI/cron crypto still reads Yahoo; MCP reads the exchange.** Already
  flagged in `README.md` ("known minor inconsistency"). `technicals.py`,
  `regime.py`, `check_levels.py` route crypto through `fetch_ohlcv.fetch`
  (Yahoo); MCP uses `exchange_ohlcv.fetch_crypto` (OKX→Bybit→Binance). The
  cron `Level-Watch.md` stamps the wrong source and depends on the fragile
  `HYPE32196-USD` override. Fix: one dispatch (crypto→exchange, stock→Yahoo)
  reused by all three; delete the README note; re-validate live afterwards.

## C. Enhancements

- **C1 — deterministic calibration scoring (`calibration.py`).** The monthly
  sweep's stats (hit rate per confidence bucket vs implied p, Brier,
  breakdowns) are agent-computed arithmetic — exactly what the system says
  should be a script. Scope: parse the Scoreboard table → typed rows → stats.
  YAGNI note: Scoreboard has zero rows; keep this minimal and last, or defer
  until the first scored calls exist (post-2026-09).
- **C2 — enforce the report contract in CI.** Add `prediction_record.py --all`
  as a CI step. Required first: exclude Tier 1 `-quick-` reports in the
  validator's `--all` glob (Tier 1 has no Prediction Record by contract — the
  gate would break on the first quick report otherwise).

## D. Test-coverage gaps (deterministic, no network)

- **D1** `funding.analyze` — interval inference + APR annualization untested.
- **D2** `exchange_ohlcv.base_ticker` + `_df` shape untested.
- **D3** `defillama.fmt_usd` / `summary_block` untested.
- **D4** `prediction_record` — downside-flag assertions + signed-return case
  (ships with A1/A2).

## E. Hygiene / doc rot

- **E1** `engine/market_research_engine.egg-info/` is tracked — `git rm -r
  --cached` + gitignore.
- **E2** `engine/README.md:26` references removed `TRADE_LOG`.
- **E3** `engine/fetch_ohlcv.py:27` error says `requirements.txt` (gone; it's
  pyproject now).
- **E4** `engine/fetch_ohlcv.py` CSV path `engine/data/` collides in name with
  the repo's real `data/` — remove or rename the dead path.

## F. Longer-term / flagged risks

- **F1** `pandas-ta` 0.3.14b0 unmaintained (numpy-pin symptoms already in the
  engine README). Consider migrating RSI/MACD/ATR/MA to ~30 lines of pandas;
  goldens must be re-verified. Record the decision either way.
- **F2** CI tests only 3.12; dev runs 3.11 — a small matrix would catch drift.
- **F3** `check_levels` stop logic is long-only; a downside call's stop sits
  above price. Revisit when the first downside flag goes live.
- **F4** `_downside_flag` residual heuristic edge (accepted 2026-07-25): a
  whole-word negator within ~30 chars *before* a genuinely raised flag (e.g.
  "no adds; downside flag: reversal target 420") still parses False. All
  observed and specified phrasings pass; if a report ever raises a real flag,
  keep negating clauses out of the 30 chars before "Downside flag:" or the
  parse drops it.

## Batches

| Batch | Items | Status |
|---|---|---|
| 1 — data integrity | A1, A2, A3, D4 | done (2026-07-25) — implemented, reviewed (one review loop on `_downside_flag`), verified: 39 tests, ruff+mypy clean |
| 2 — CI + hygiene | C2 (with quick-report exclusion), E1–E4 | done (2026-07-25) — implemented, reviewed clean, verified: 45 tests, `--all` gate green in CI |
| 3 — crypto source consistency | B1 + live re-validation | in progress (2026-07-25) — owner approved one sweep run as end-to-end check |
| 4 — calibration engine | C1 (trimmed), D1–D3 | pending (may defer C1 to post-2026-09) |

Order: 1 → 2 → 3 → 4. Integrity first; enhancements last.
