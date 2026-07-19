# CLAUDE.md

## What This Repo Is

A market-research system for stocks and crypto — it issues scoreable buy/hold/avoid calls with invalidation levels; it tracks calls, never positions. One repo holds everything:
the system contract (`README.md`), the research skills (`.claude/commands/`),
the deterministic compute layer (`engine/`), and the data layer (`data/`).

**Read `README.md` first for any research task.** It defines
the tiered agent workflows, the Prediction Record format, risk rules, and the
calibration loop. This file only covers repo mechanics.

**Private repo — never make it public.** `data/` holds the owner's theses, watchlist
levels, and reports.

## Commands

```sh
cd engine
[ -d .venv ] || (python3 -m venv .venv && .venv/bin/pip install -r requirements.txt)
.venv/bin/python test_smoke.py          # health check (live network test)
.venv/bin/python technicals.py NVDA     # stock snapshot
.venv/bin/python technicals.py BTC --crypto
.venv/bin/python regime.py              # crypto regime; regime.py SPY for stocks
.venv/bin/python check_levels.py        # watchlist level sweep
```

Prefer the `investments` MCP tools (`mcp__investments__*`) over the CLI when
available — same math, in-conversation.

## Structure

- `README.md` — the system spec (the contract; read it, follow it)
- `.claude/commands/` — `/research`, `/refresh`, `/postmortem`, `/research-watchlist`, `/report-view` (render a report .md as a private artifact or PDF on request; .md stays canonical)
- `engine/` — Python compute layer; setup in `engine/README.md`
- `data/Watchlist.md` — the calls table (source of truth for levels/status)
- `data/Research/{TICKER}.md` — the owner's own thesis, append-only. NEVER auto-edit.
- `data/Reports/{Crypto|Equities}/{TICKER}/` — agent-generated reports
- `data/Reports/_meta/calibration.md` — active biases; inject into Tier 2/3 prompts
- `docs/` — design references

## Conventions

- No emojis. Direct tone, executive-summary-first.
- Dates `YYYY-MM-DD`; prices in native currency.
- `data/Research/` is the owner's audit trail — append-only, ask before touching.
- Cron writes `data/Reports/_meta/Level-Watch.md` twice daily (08:17 / 20:17);
  commits of report changes are normal after a sweep.
