# market-research

An AI-agentic market-research system for stocks and crypto, built on the premise
that an opinionated call you can prove wrong is worth more than a balanced
summary you can't.

Every report opens with a machine-validated Prediction Record: a decisive
**BUY / HOLD / AVOID** verdict, targets that each cite their basis, a mandatory
invalidation level, a review date, and explicit kill criteria. Work is tiered
and always delegated — a refresh runs an analyst plus a verifier; a deep dive
runs three parallel workers (fundamental, quant, and an adversarial bear) into a
synthesizer. The author is never the auditor: a read-only verifier re-derives
every number rather than re-reading it before anything commits. Numbers come
from a deterministic Python engine shared by CLI, cron, and MCP, so the same
question gives the same answer on every path.

Resolved calls are then scored — hit rate by confidence bucket, Brier score —
and the resulting bias list is injected into future prompts, so the system's own
misses argue against it next time. It tracks research calls, never positions.

**Not financial advice.** This is a personal research tool. See
[Disclaimer](#disclaimer).

**The research is published, not just the code.** `data/` is tracked in full —
the watchlist, every report, the calibration log, and the running theses. You
can read the actual calls and see where they were wrong, which is the point: a
calibration loop nobody can inspect is just a claim.

**The system contract is [`docs/SPEC.md`](docs/SPEC.md) — read it first for any
research task.** It defines the tiered agent workflows, the Prediction Record
format, the risk rules, and the calibration loop. This README is only the tour.

## Workflows

Everything runs as a slash command from `.claude/commands/`. The commands are
thin dispatchers — they wire inputs and spawn agents from `.claude/agents/`,
which are the source of truth for how each role works.

| Command | Use when | Runs |
|---|---|---|
| `/research <TICKER>` | First look at an asset, or a thesis-level re-examination | Tier 2 deep dive: 3 parallel workers → synthesizer → verifier |
| `/refresh <TICKER>` | A live call needs re-testing against current data | `asset-analyst` → `report-verifier` |
| `/research-watchlist` | Sweep every active call in one pass | One `asset-analyst` per ticker, in parallel → verifier each |
| `/postmortem <TICKER>` | A call resolved — grade it | Scores the call into `calibration.md` |
| `/report-view <path>` | Read a report as a rendered page or PDF | Renders an existing `.md`; the `.md` stays canonical |
| `/book-view` | See the whole book at a glance | Renders the dashboard artifact at one standing URL |

Research is **always delegated** — the main session orchestrates, spawns, and
summarizes from agent return blocks; it never writes a report itself. The
exceptions (a single price lookup, a conversational question) are listed in
`docs/SPEC.md` under "When NOT to delegate".

## How it works

- **Tiered research** — Refresh & Scan (analyst + verifier; the standing path
  that carries the live call) → Tier 1 quick check (one agent) → Tier 2 deep
  dive (3 parallel workers + synthesizer + verifier; the default) → Tier 3
  high-stakes (opus on judgment and attack).
- **A dedicated adversary** — `bear-worker` argues the asset is a bad bet at
  full strength, with no obligation to be balanced; the synthesizer supplies the
  balance. It runs on every deep dive and on any refresh that *changes* the call
  — the moment of highest risk.
- **The author is never the auditor** — a read-only `report-verifier` audits
  every scoreable report before it commits: it re-derives the numbers rather
  than re-reading them, checks close-basis vs live-price tests, de-overlaps any
  base rate, and writes its own premortem. Blockers loop back to the author.
- **Deterministic compute** (`engine/`) — technicals, market-regime gate,
  funding/OI, on-chain data, level watch. Agents interpret the output, never
  recompute it. Crypto OHLCV comes from the exchange (OKX → Bybit → Binance),
  stocks from Yahoo — one routed path for CLI, cron, and MCP.
- **Scoreable by construction** — every report opens with a machine-validated
  Prediction Record (pydantic schema, enforced in CI): verdict, targets each
  with a basis, a mandatory stop, review date, kill criteria.
- **Calibration loop** — resolved calls are scored into
  `data/Reports/_meta/calibration.md` (`engine/calibration.py` does the
  arithmetic: confidence-bucket hit rate vs implied p, Brier score); the
  active-bias list is injected into future research prompts so past misses
  counter-weight future calls.
- **Guardrails are structural, not advisory** — `.claude/hooks/guard-owner-files.py`
  is a PreToolUse hook that makes `data/Research/` append-only and
  `data/Watchlist.md` overwrite-proof for the main session and agents alike. A
  block from the guard is a correct answer, not an obstacle to route around.

## What a call looks like

Every report opens with the same Prediction Record. Abridged and illustrative:

```markdown
**Verdict:** Hold — regime (risk_off) is the sole governing gate; adds suspended.

| Horizon | Target | Return | Basis |
|---|---|---|---|
| Swing (~Q3) | $83.90 | +10.9% | 50-bar high / 200-MA confluence (own computation, OKX OHLCV) |

| Field | Value |
|---|---|
| Stop | $70.14 — MANDATORY. +2.29 ATR live, +1.48 ATR on close basis |
| Confidence | medium |
| Review date | 2026-09-17 — one day after the FOMC decision, inside the catalyst window |

**Kill criteria:** weekly close below $70.14 AND 30-day fees still decaying
→ flip to avoid. Reclaim above ~$83.9 AND fees stabilizing → flip toward buy.
```

Three properties make it scoreable rather than decorative: every target carries
a **basis** (where the number came from), the stop is **mandatory** and tested
on both live and close basis, and the kill criteria are **falsifiable
conditions** checked one at a time on each refresh. Reports are immutable and
versioned — a refresh writes `v2` and names what it supersedes, so the record of
what was believed when survives.

## Layout

| Path | What |
|---|---|
| `docs/SPEC.md` | The system contract — tiers, Prediction Record, risk rules, calibration |
| `.claude/commands/` | The workflows in the table above — thin dispatchers |
| `.claude/agents/` | The agent roster — one brief per role; **source of truth** for how each works |
| `.claude/assets/` | Templates the commands render from (`book-view.template.html`) |
| `.claude/hooks/` | `guard-owner-files.py` — makes the append-only rules structural |
| `engine/` | Deterministic compute layer (CLI + `investments` MCP server) — `engine/README.md` |
| `data/Watchlist.md` | The calls table (levels + status) — source of truth for live calls |
| `data/Research/{TICKER}.md` | The owner's thesis, append-only; agents add only dated report pointers |
| `data/Reports/{Crypto\|Equities}/{TICKER}/` | Agent reports — immutable, versioned |
| `data/Reports/_meta/` | `calibration.md` (active biases) + `Level-Watch.md` (sweep output) |

## Quick start

```sh
cd engine
[ -d .venv ] || (python3 -m venv .venv && .venv/bin/pip install -e ".[dev]")
.venv/bin/python test_smoke.py           # live health check (hits the network)
.venv/bin/python technicals.py NVDA      # stock snapshot
.venv/bin/python technicals.py BTC --crypto
.venv/bin/python regime.py               # crypto regime gate (SPY for stocks)
.venv/bin/python check_levels.py         # watchlist level sweep
```

In-conversation, the `investments` MCP server exposes the same math as tools
(`mcp__investments__*`) — identical, auditable numbers on both paths. Prefer the
MCP tools over the CLI when they're available.

## Development

CI (`.github/workflows/ci.yml`) runs on every push and PR:

```sh
cd engine
.venv/bin/ruff check .                       # lint
.venv/bin/mypy *.py tests/*.py               # typecheck
.venv/bin/pytest                             # deterministic tests, no network
.venv/bin/python prediction_record.py --all  # validate every report's schema
```

The test suite is offline by design (fixtures under `engine/tests/fixtures`), so
it never fails on a flaky exchange. `test_smoke.py` is the separate live check
and is deliberately not in CI. The `--all` step is what makes "scoreable by
construction" real: a report whose Prediction Record doesn't parse fails the
build.

## Conventions

- No emojis; direct tone; executive summary first; dates `YYYY-MM-DD`; prices in
  native currency.
- Reports are immutable and versioned (provenance header); theses append-only.
- Every numeric claim in an agent report carries a source URL, an
  own-computation stamp, or an `[UNVERIFIED]` tag — cite or fail.
- Market questions get answered boldly when grounded in data: run the
  computation, give a confluence table with a basis per band, name a central
  estimate, put caveats at the end. A quantified band with reasoning beats "it's
  uncertain".
- **The level-watch sweep is manual-only.** The cron was disabled 2026-07-19 at
  the owner's request; it is never run or re-enabled automatically.

## Disclaimer

**This is not financial advice.** Nothing in this repository — the code, the
reports, the watchlist, the calls, or any output of the agents — is investment,
financial, legal, tax, or accounting advice, nor a recommendation, offer, or
solicitation to buy or sell any security, digital asset, or other instrument.

- **No professional relationship.** The author is not a registered investment
  adviser, broker-dealer, or financial professional. Nothing here is
  personalized to anyone's circumstances, objectives, or risk tolerance. Consult
  a licensed professional before making any investment decision.
- **Research output is generated by AI and can be wrong.** Reports are produced
  by language models from third-party data. They can contain hallucinated
  figures, stale prices, broken citations, and flawed reasoning, and they can
  fail silently. The verifier pass and the `[UNVERIFIED]` tagging reduce this
  risk; they do not eliminate it. Verify independently before acting.
- **Data may be inaccurate or delayed.** Market data comes from third-party
  sources (exchange APIs, Yahoo, DefiLlama, and others) with no warranty of
  accuracy, completeness, or timeliness. Prices may be stale, adjusted, or
  wrong.
- **Past performance and calibration scores do not predict future results.** The
  calibration loop measures this system's historical hit rate on its own calls.
  It is a quality-control instrument, not evidence of future accuracy or a
  performance track record.
- **Trading involves substantial risk of loss**, including total loss of
  capital. Crypto assets are especially volatile, may be unregulated in your
  jurisdiction, and can go to zero. Leverage magnifies losses. Do not risk money
  you cannot afford to lose.
- **Your decisions are your own.** Any action taken on the basis of this
  material is taken solely at your own risk. The author accepts no liability for
  any loss or damage arising from its use.
- **No warranty.** The software is provided "as is", without warranty of any
  kind, express or implied, including merchantability, fitness for a particular
  purpose, and non-infringement.
- **Positions.** The author may hold positions in any asset covered here, and
  may change them at any time without notice or updating this repository.
- **Compliance is your responsibility.** Third-party data sources have their own
  terms of service and rate limits; use of this software must comply with them
  and with the laws of your jurisdiction.
