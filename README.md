# market-research

An AI-agentic market-research system for stocks and crypto. It issues decisive,
time-bound, scoreable **BUY / HOLD / AVOID** calls with mandatory invalidation
levels, then scores every call against reality — it tracks research calls,
never positions.

**The system contract is [`docs/SPEC.md`](docs/SPEC.md) — read it first for any
research task.** It defines the tiered agent workflows, the Prediction Record
format, the risk rules, and the calibration loop. This README is only the tour.

**Private repo — never make it public.** `data/` holds the owner's theses,
watchlist levels, and reports.

## How it works

- **Tiered research** — Tier 1 quick check (one agent) → Tier 2 deep dive
  (3 parallel workers + adversarial bear worker + synthesizer; the default) →
  Tier 3 high-stakes (opus synthesizer on the judgment step).
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

## Layout

| Path | What |
|---|---|
| `docs/SPEC.md` | The system contract — tiers, Prediction Record, risk rules, calibration |
| `.claude/commands/` | `/research`, `/refresh`, `/postmortem`, `/research-watchlist`, `/report-view` |
| `engine/` | Deterministic compute layer (CLI + `investments` MCP server) — `engine/README.md` |
| `data/Watchlist.md` | The calls table (levels + status) |
| `data/Research/{TICKER}.md` | The owner's thesis, append-only |
| `data/Reports/{Crypto\|Equities}/{TICKER}/` | Agent reports — immutable, versioned |
| `data/Reports/_meta/` | Calibration log + level watch |

## Quick start

```sh
cd engine
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/python test_smoke.py           # live health check
.venv/bin/python technicals.py NVDA      # stock snapshot
.venv/bin/python technicals.py BTC --crypto
.venv/bin/python regime.py               # crypto regime gate (SPY for stocks)
.venv/bin/python check_levels.py         # watchlist level sweep
```

In-conversation, the `investments` MCP server exposes the same math as tools
(`mcp__investments__*`) — identical, auditable numbers on both paths.

## Conventions

- No emojis; direct tone; executive summary first; dates `YYYY-MM-DD`.
- Reports are immutable and versioned (provenance header); theses append-only.
- Every numeric claim in an agent report carries a source URL, an
  own-computation stamp, or an `[UNVERIFIED]` tag — cite or fail.
